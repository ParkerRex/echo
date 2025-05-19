import { Button } from "~/components/ui/button";
import { PlusIcon } from "lucide-react";
import { useEffect, useState, useRef } from "react";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Skeleton } from "~/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardHeader,
  CardFooter,
} from "~/components/ui/card";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getProcessingJobs,
  getSignedUploadUrl,
  notifyUploadComplete,
} from "~/lib/api";
import type {
  VideoJobSchema,
  SignedUploadUrlRequest,
  SignedUploadUrlResponse,
  UploadCompleteRequest,
} from "~/types/api";
import type { Step } from "~/components/ui/progress-steps";
import { VideoProgressCard } from "./video-progress-card";
import { useJobStatusManager } from "~/hooks/useJobStatusManager";
import { toast } from "sonner";

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
function getCurrentStepIndex(
  jobStatus: VideoJobSchema["status"],
  stages?: VideoJobSchema["processing_stages"],
): number {
  if (jobStatus === "COMPLETED") return 8; // Max steps
  if (jobStatus === "FAILED") return 0; // Or a specific error step
  if (typeof stages === "object" && stages !== null && !Array.isArray(stages)) {
    return Object.keys(stages).length;
  }
  if (Array.isArray(stages)) {
    return stages.length;
  }
  return 0;
}

function getProgressCardStatus(
  jobStatus: VideoJobSchema["status"],
): "processing" | "completed" | "error" | "paused" {
  switch (jobStatus) {
    case "COMPLETED":
      return "completed";
    case "FAILED":
      return "error";
    case "PENDING":
      return "processing"; // Or a specific "pending" visual state if desired
    case "PROCESSING":
      return "processing";
    default:
      return "processing"; // Fallback
  }
}

type ProcessingDashboardProps = {
  className?: string;
};

export function ProcessingDashboard({ className }: ProcessingDashboardProps) {
  useJobStatusManager();
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  const {
    data: processingJobs,
    isLoading,
    error: fetchError,
  } = useQuery<VideoJobSchema[], Error>({
    queryKey: ["processingJobs"],
    queryFn: () => getProcessingJobs(),
  });

  const handleUploadButtonClick = () => {
    if (isUploading) return;
    inputRef.current?.click();
  };

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      if (inputRef.current) {
        inputRef.current.value = "";
      }

      setIsUploading(true);
      const uploadPromise = async () => {
        let signedUrlResponse: SignedUploadUrlResponse;
        try {
          const requestData: SignedUploadUrlRequest = {
            filename: file.name,
            content_type: file.type,
          };
          signedUrlResponse = await getSignedUploadUrl(requestData);
          if (!signedUrlResponse.upload_url || !signedUrlResponse.video_id) {
            throw new Error("Invalid response from signed URL endpoint");
          }
        } catch (err: any) {
          console.error("Failed to get upload URL:", err);
          throw new Error(err.message || "Failed to get upload URL");
        }

        const { upload_url: uploadUrl, video_id: videoId } = signedUrlResponse;

        try {
          await new Promise<void>((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open("PUT", uploadUrl);
            xhr.setRequestHeader("Content-Type", file.type);
            xhr.onload = () => {
              if (xhr.status >= 200 && xhr.status < 300) {
                resolve();
              } else {
                reject(
                  new Error(
                    `Upload failed with status ${xhr.status}: ${xhr.statusText}`,
                  ),
                );
              }
            };
            xhr.onerror = () =>
              reject(new Error("Upload failed due to network error"));
            xhr.send(file);
          });
        } catch (err: any) {
          console.error("Upload failed:", err);
          throw new Error(err.message || "Upload to storage failed");
        }

        try {
          const completeRequestData: UploadCompleteRequest = {
            video_id: String(videoId),
            original_filename: file.name,
            content_type: file.type,
            size_bytes: file.size,
          };
          await notifyUploadComplete(completeRequestData);
        } catch (err: any) {
          console.error("Failed to finalize upload:", err);
          throw new Error(
            err.message || "Failed to finalize upload with backend",
          );
        }
        return videoId;
      };

      toast.promise(uploadPromise(), {
        loading: "Uploading video...",
        success: (videoId) => {
          queryClient.invalidateQueries({ queryKey: ["processingJobs"] });
          queryClient.invalidateQueries({ queryKey: ["myVideos"] });
          return `Video "${file.name}" uploaded successfully! (ID: ${videoId})`;
        },
        error: (err) => `Upload failed: ${err.message}`,
        finally: () => {
          setIsUploading(false);
        },
      });
    }
  };

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
        <Button onClick={handleUploadButtonClick} disabled={isUploading}>
          <PlusIcon className="h-4 w-4 mr-2" />
          {isUploading ? "Uploading..." : "Upload New Video"}
        </Button>
      </div>

      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        style={{ display: "none" }}
        accept="video/*"
        disabled={isUploading}
      />

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
          <Button
            variant="outline"
            onClick={handleUploadButtonClick}
            disabled={isUploading}
          >
            {isUploading ? "Uploading..." : "Upload a new video"}
          </Button>
        </div>
      ) : !fetchError && processingJobs ? (
        <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
          {processingJobs.map((job) => {
            const cardStatus = getProgressCardStatus(job.status);

            const simplifiedSteps: Step[] = [];
            let currentDisplayStepId: string | undefined = undefined;

            if (cardStatus === "processing" && job.processing_stages) {
              if (Array.isArray(job.processing_stages)) {
              } else if (
                typeof job.processing_stages === "object" &&
                job.processing_stages !== null
              ) {
              }
            } else if (cardStatus === "completed") {
            }

            return (
              <VideoProgressCard
                key={job.id}
                videoId={String(job.id)}
                videoTitle={
                  job.metadata?.title ||
                  job.video?.original_filename ||
                  "Untitled Video"
                }
                thumbnailUrl={job.metadata?.thumbnail_file_url || undefined}
                uploadedAt={
                  job.created_at ? new Date(job.created_at) : new Date()
                }
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
