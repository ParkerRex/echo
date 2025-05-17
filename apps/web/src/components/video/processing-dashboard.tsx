import { Button } from "@/components/ui/button";
import { Link } from "@tanstack/react-router";
import { PlusIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { getProcessingJobs } from "@/lib/api";
import type { VideoJobSchema } from "@/types/api";
import type { Step } from "@/components/ui/progress-steps";
import {
	ProcessingStepId,
	createMockProcessingSteps,
} from "./processing-steps";
import { VideoProgressCard } from "./video-progress-card";

// Map backend processing stages to frontend steps
const stageToStepMap: Record<string, number> = {
	uploaded: 0,
	audio_extraction: 1,
	transcript_generation: 2,
	subtitle_generation: 3,
	shownote_generation: 4,
	chapter_generation: 5,
	title_generation: 6,
	youtube_upload: 7,
	completed: 8,
};

// Helper to determine the current step index based on backend stage
function getCurrentStepIndex(jobStatus: VideoJobSchema['status'], stages?: VideoJobSchema['processing_stages']): number {
	if (jobStatus === "COMPLETED") return 8; // Max steps
	if (jobStatus === "FAILED") return 0; // Or a specific error step
	if (typeof stages === 'object' && stages !== null && !Array.isArray(stages)) {
		return Object.keys(stages).length;
	}
	if (Array.isArray(stages)) {
		return stages.length;
	}
	return 0;
}

function getProgressCardStatus(
	jobStatus: VideoJobSchema['status'],
): "processing" | "completed" | "error" | "paused" {
	switch (jobStatus) {
		case "COMPLETED": return "completed";
		case "FAILED": return "error";
		case "PENDING": return "processing"; // Or a specific "pending" visual state if desired
		case "PROCESSING": return "processing";
		default: return "processing"; // Fallback
	}
}

type ProcessingDashboardProps = {
	className?: string;
};

export function ProcessingDashboard({ className }: ProcessingDashboardProps) {
	const { 
		data: processingJobs, 
		isLoading, 
		error: fetchError,
	} = useQuery<VideoJobSchema[], Error>({
		queryKey: ['processingJobs'],
		queryFn: getProcessingJobs,
	});

	const handlePauseResume = (videoId: string) => {
		console.log(
			"Pause/resume functionality is not currently supported by the backend.",
			videoId,
		);
	};

	return (
		<div className={className}>
			<div className="flex items-center justify-between mb-8">
				<div>
					<h1 className="text-2xl font-bold tracking-tight">
						Video Processing
					</h1>
					<p className="text-muted-foreground text-sm mt-1">
						Track the status of your video processing tasks
					</p>
				</div>
				<Button asChild>
					<Link to="/upload">
						<PlusIcon className="h-4 w-4 mr-2" />
						Upload New Video
					</Link>
				</Button>
			</div>

			{fetchError && (
				<div className="py-10">
					<Alert variant="destructive" className="max-w-lg mx-auto">
						<AlertTitle>Error Fetching Processing Videos</AlertTitle>
						<AlertDescription>{fetchError.message}</AlertDescription>
					</Alert>
				</div>
			)}

			{isLoading && !fetchError ? (
				<div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
					{[...Array(3)].map((_, index) => (
						<Card key={index} className="animate-pulse">
							<CardHeader className="pb-2">
								<div className="flex items-start justify-between">
									<div className="space-y-1 flex-grow pr-2">
										<Skeleton className="h-5 w-3/4" />
										<Skeleton className="h-4 w-1/2" />
									</div>
									<Skeleton className="h-14 w-24 shrink-0 rounded-md" />
								</div>
							</CardHeader>
							<CardContent>
								<Skeleton className="h-6 w-full mb-2" />
								<Skeleton className="h-4 w-1/2" /> 
							</CardContent>
							<CardFooter className="flex justify-between pt-0">
								<Skeleton className="h-8 w-20" />
								<Skeleton className="h-8 w-24" />
							</CardFooter>
						</Card>
					))}
				</div>
			) : !fetchError && processingJobs && processingJobs.length === 0 ? (
				<div className="flex flex-col items-center justify-center py-20 text-center">
					<p className="text-muted-foreground mb-4">
						No videos currently processing
					</p>
					<Button asChild variant="outline">
						<Link to="/upload">Upload a new video</Link>
					</Button>
				</div>
			) : !fetchError && processingJobs ? (
				<div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
					{processingJobs.map((job) => {
						const cardStatus = getProgressCardStatus(job.status);
						
						const simplifiedSteps: Step[] = [];
						let currentDisplayStepId: string | undefined = undefined;

						if (cardStatus === 'processing' && job.processing_stages) {
							if (Array.isArray(job.processing_stages)) {
							} else if (typeof job.processing_stages === 'object' && job.processing_stages !== null) {
							}
						} else if (cardStatus === 'completed') {
						}

						return (
							<VideoProgressCard
								key={job.id}
								videoId={String(job.id)}
								videoTitle={job.metadata?.title || job.video?.original_filename || "Untitled Video"}
								thumbnailUrl={job.metadata?.thumbnail_file_url || undefined}
								uploadedAt={job.created_at ? new Date(job.created_at) : new Date()}
								status={cardStatus}
								processingSteps={simplifiedSteps}
								currentStepId={currentDisplayStepId}
								onPauseResume={() => handlePauseResume(String(job.id))}
							/>
						);
					})}
				</div>
			) : null}
		</div>
	);
}
