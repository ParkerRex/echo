import type { VideoSummary } from "@/types/api";
import { VideoListItem } from "./VideoListItem";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton"; // For loading state

interface VideoListProps {
  videos: VideoSummary[];
  isLoading: boolean;
  error?: Error | null;
  hasNextPage?: boolean;
  isFetchingNextPage?: boolean;
  fetchNextPage?: () => void;
  showUploadButton?: boolean; // Optional: if the empty state upload button is handled here
  onTriggerUpload?: () => void; // Callback to open upload dialog
}

export function VideoList({
  videos,
  isLoading,
  error,
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  showUploadButton = false, // Default to false, dashboard can control its own dialog trigger
  onTriggerUpload,
}: VideoListProps) {
  if (isLoading && videos.length === 0) { // Initial loading state
    return (
      <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
        {[...Array(6)].map((_, index) => (
          <div key={index} className="rounded-lg border border-border p-4 space-y-3">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="aspect-video w-full rounded-md" />
            <Skeleton className="h-4 w-1/2" />
            <div className="flex space-x-2">
              <Skeleton className="h-8 w-24" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center py-10">
        Error loading videos: {error.message}
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <p className="text-muted-foreground mb-4">
          No videos found in your library.
        </p>
        {showUploadButton && onTriggerUpload && (
            <Button variant="outline" onClick={onTriggerUpload}>Upload your first video</Button>
        )}
      </div>
    );
  }

  return (
    <>
      <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
        {videos.map((video) => (
          <VideoListItem key={video.id} video={video} />
        ))}
      </div>
      {hasNextPage && fetchNextPage && (
        <div className="flex justify-center mt-6">
          <Button onClick={fetchNextPage} disabled={isFetchingNextPage || isLoading}>
            {isFetchingNextPage ? "Loading more..." : "Load More"}
          </Button>
        </div>
      )}
    </>
  );
} 