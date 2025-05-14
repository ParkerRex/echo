"""Parallel processing utilities for AI services."""

import asyncio
import concurrent.futures
import functools
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar

from video_processor.infrastructure.monitoring import structured_log
from video_processor.utils.profiling import Timer

# Type variables
T = TypeVar("T")
R = TypeVar("R")


class ParallelProcessor:
    """Parallel processor for AI requests.

    This class provides methods for processing multiple AI requests in parallel,
    using either threading or asyncio.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        timeout: float = 60.0,
    ):
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker threads (default: None = CPU count)
            timeout: Timeout in seconds for each request (default: 60.0)
        """
        self.max_workers = max_workers
        self.timeout = timeout

    def map_threaded(self, func: Callable[[T], R], items: List[T], **kwargs) -> List[R]:
        """Process items in parallel using threads.

        Args:
            func: Function to call for each item
            items: List of items to process
            **kwargs: Additional keyword arguments to pass to func

        Returns:
            List of results in the same order as the input items
        """
        with Timer("parallel_map_threaded") as timer:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            ) as executor:
                # Wrap function to include kwargs
                if kwargs:
                    func_with_kwargs = functools.partial(func, **kwargs)
                else:
                    func_with_kwargs = func

                # Submit all tasks
                future_to_index = {
                    executor.submit(func_with_kwargs, item): i
                    for i, item in enumerate(items)
                }

                # Prepare results list with placeholders
                results = [None] * len(items)

                # Process completed futures as they complete
                for future in concurrent.futures.as_completed(
                    future_to_index, timeout=self.timeout
                ):
                    index = future_to_index[future]
                    try:
                        results[index] = future.result()
                    except Exception as exc:
                        structured_log(
                            "error",
                            f"Error processing item {index}: {exc}",
                            {"error": str(exc), "item_index": index},
                        )
                        results[index] = None

        structured_log(
            "info",
            f"Processed {len(items)} items in {timer.end_time - timer.start_time:.2f} seconds using threads",
            {
                "item_count": len(items),
                "duration": timer.end_time - timer.start_time,
                "throughput": len(items) / (timer.end_time - timer.start_time),
            },
        )

        return results

    async def map_async(
        self, func: Callable[[T], R], items: List[T], **kwargs
    ) -> List[R]:
        """Process items in parallel using asyncio.

        Note: This requires that the function `func` is a standard synchronous function,
        not a coroutine function. It will be run in a thread pool.

        Args:
            func: Function to call for each item (must be a regular function, not a coroutine)
            items: List of items to process
            **kwargs: Additional keyword arguments to pass to func

        Returns:
            List of results in the same order as the input items
        """
        with Timer("parallel_map_async") as timer:
            loop = asyncio.get_event_loop()

            # Prepare results list with placeholders
            results = [None] * len(items)

            # Create a semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_workers or 10)

            async def process_item(index: int, item: T) -> None:
                """Process a single item with semaphore limiting."""
                async with semaphore:
                    try:
                        # Run synchronous function in a thread pool
                        if kwargs:
                            result = await loop.run_in_executor(
                                None, functools.partial(func, **kwargs), item
                            )
                        else:
                            result = await loop.run_in_executor(None, func, item)

                        results[index] = result
                    except Exception as exc:
                        structured_log(
                            "error",
                            f"Error processing item {index}: {exc}",
                            {"error": str(exc), "item_index": index},
                        )
                        results[index] = None

            # Create tasks for all items
            tasks = [process_item(i, item) for i, item in enumerate(items)]

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

        structured_log(
            "info",
            f"Processed {len(items)} items in {timer.end_time - timer.start_time:.2f} seconds using asyncio",
            {
                "item_count": len(items),
                "duration": timer.end_time - timer.start_time,
                "throughput": len(items) / (timer.end_time - timer.start_time),
            },
        )

        return results


class AsyncBatcher:
    """Batches async operations and processes them together.

    This class is useful for batching together multiple similar AI requests,
    which can lead to better utilization of API quotas and network resources.
    """

    def __init__(
        self,
        batch_size: int = 10,
        max_wait_time: float = 0.5,
    ):
        """Initialize the batcher.

        Args:
            batch_size: Maximum number of items in a batch (default: 10)
            max_wait_time: Maximum time to wait for a batch to fill (default: 0.5 seconds)
        """
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.batch: List[Dict[str, Any]] = []
        self.lock = asyncio.Lock()
        self.batch_event = asyncio.Event()
        self.batch_task = None
        self.processing = False

    async def add_item(
        self, item: Any, processor: Callable[[List[Any]], List[Any]]
    ) -> Any:
        """Add an item to the current batch and wait for processing.

        Args:
            item: Item to process
            processor: Function to process a batch of items

        Returns:
            The processed result for this item
        """
        # Create a future to get the result for this item
        result_future = asyncio.Future()

        async with self.lock:
            # Add the item and its result future to the batch
            batch_index = len(self.batch)
            self.batch.append(
                {
                    "item": item,
                    "future": result_future,
                    "added_at": time.time(),
                }
            )

            # Start the batch processor task if not already running
            if not self.processing:
                self.processing = True
                self.batch_task = asyncio.create_task(self._process_batch(processor))

            # If batch is full, trigger processing immediately
            if len(self.batch) >= self.batch_size:
                self.batch_event.set()

        # Wait for the result
        try:
            return await result_future
        except Exception as e:
            structured_log(
                "error",
                f"Error getting batch result: {str(e)}",
                {"error": str(e)},
            )
            raise

    async def _process_batch(self, processor: Callable[[List[Any]], List[Any]]) -> None:
        """Process the current batch.

        Args:
            processor: Function to process a batch of items
        """
        while True:
            # Wait for the batch to fill or timeout
            try:
                # Check if we should process the batch
                should_process = False

                async with self.lock:
                    if len(self.batch) > 0:
                        # Process if batch is full or oldest item has waited too long
                        if len(self.batch) >= self.batch_size:
                            should_process = True
                        else:
                            oldest_time = self.batch[0]["added_at"]
                            if time.time() - oldest_time >= self.max_wait_time:
                                should_process = True

                if should_process:
                    await self._do_process_batch(processor)
                else:
                    # Wait a bit and check again
                    await asyncio.sleep(0.1)

                # Reset event
                self.batch_event.clear()

                # Break if no items left
                async with self.lock:
                    if len(self.batch) == 0:
                        self.processing = False
                        break

            except Exception as e:
                structured_log(
                    "error",
                    f"Error in batch processor: {str(e)}",
                    {"error": str(e)},
                )

                # Reset processing flag after error
                async with self.lock:
                    self.processing = False
                    break

    async def _do_process_batch(
        self, processor: Callable[[List[Any]], List[Any]]
    ) -> None:
        """Process the current batch and resolve futures.

        Args:
            processor: Function to process a batch of items
        """
        current_batch = []
        futures = []

        # Get current batch under lock
        async with self.lock:
            current_batch = [item["item"] for item in self.batch]
            futures = [item["future"] for item in self.batch]
            self.batch = []

        # Process the batch
        try:
            with Timer("batch_processing") as timer:
                results = processor(current_batch)

            structured_log(
                "info",
                f"Processed batch of {len(current_batch)} items in {timer.end_time - timer.start_time:.2f} seconds",
                {
                    "batch_size": len(current_batch),
                    "duration": timer.end_time - timer.start_time,
                },
            )

            # Set results for each future
            for i, future in enumerate(futures):
                if i < len(results):
                    future.set_result(results[i])
                else:
                    future.set_exception(
                        IndexError(
                            "Batch processor returned fewer results than expected"
                        )
                    )

        except Exception as e:
            structured_log(
                "error",
                f"Error processing batch: {str(e)}",
                {"error": str(e), "batch_size": len(current_batch)},
            )

            # Set exception for all futures
            for future in futures:
                if not future.done():
                    future.set_exception(e)


# Create a default parallel processor
default_processor = ParallelProcessor()


def parallel_map(func: Callable[[T], R], items: List[T], **kwargs) -> List[R]:
    """Process items in parallel using threads.

    This is a convenience function that uses the default parallel processor.

    Args:
        func: Function to call for each item
        items: List of items to process
        **kwargs: Additional keyword arguments to pass to func

    Returns:
        List of results in the same order as the input items
    """
    return default_processor.map_threaded(func, items, **kwargs)


async def parallel_map_async(
    func: Callable[[T], R], items: List[T], **kwargs
) -> List[R]:
    """Process items in parallel using asyncio.

    This is a convenience function that uses the default parallel processor.

    Args:
        func: Function to call for each item (must be a regular function, not a coroutine)
        items: List of items to process
        **kwargs: Additional keyword arguments to pass to func

    Returns:
        List of results in the same order as the input items
    """
    return await default_processor.map_async(func, items, **kwargs)
