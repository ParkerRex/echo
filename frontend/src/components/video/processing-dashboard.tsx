import { useEffect, useState } from "react";
import { ProcessingStepId, createMockProcessingSteps } from "./processing-steps";
import { VideoProgressCard } from "./video-progress-card";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { collection, onSnapshot, query, where } from "firebase/firestore";
import type { QuerySnapshot, DocumentData } from "firebase/firestore";
import { db } from "../../../firebase/index";

// Map backend processing stages to frontend steps
const stageToStepMap: Record<string, number> = {
  "uploaded": 0,
  "audio_extraction": 1,
  "transcript_generation": 2,
  "subtitle_generation": 3,
  "shownote_generation": 4,
  "chapter_generation": 5,
  "title_generation": 6,
  "youtube_upload": 7,
  "completed": 8
};

// Helper to determine the current step index based on backend stage
function getCurrentStepIndex(stage?: string): number {
  if (!stage) return 0;
  return stageToStepMap[stage] || 0;
}

function getVideoStatus(stage?: string): "processing" | "completed" | "error" | "paused" {
  if (!stage) return "processing";
  if (stage === "completed") return "completed";
  if (stage === "error") return "error";
  if (stage === "paused") return "paused";
  return "processing";
}

interface VideoData extends DocumentData {
  id: string;
  title?: string;
  current_stage?: string;
  filename?: string;
  channel?: string;
  created_at?: any; // Timestamp from Firestore
  youtube_video_id?: string;
  thumbnails?: Array<{url: string, prompt: string, status: string}>;
  error_message?: string;
}

type ProcessingDashboardProps = {
  className?: string;
};

export function ProcessingDashboard({ className }: ProcessingDashboardProps) {
  const [videos, setVideos] = useState<VideoData[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch videos in processing status
  useEffect(() => {
    const processingVideosQuery = query(
      collection(db, "videos"),
      where("current_stage", "!=", "completed")
    );

    const unsubscribe = onSnapshot(
      processingVideosQuery,
      (snapshot: QuerySnapshot<DocumentData>) => {
        const vids = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })) as VideoData[];
        setVideos(vids);
        setLoading(false);
      },
      (error) => {
        console.error("Error fetching processing videos:", error);
        setLoading(false);
      }
    );
    
    return () => unsubscribe();
  }, []);

  // Pause/resume functionality would require backend support
  const handlePauseResume = (videoId: string) => {
    console.log("Pause/resume functionality would require backend support", videoId);
    // In a real implementation, this would update the Firestore document
  };

  // Get the current step ID based on current_stage
  const getCurrentStepId = (video: VideoData) => {
    const stepIndex = getCurrentStepIndex(video.current_stage);
    const steps = Object.keys(ProcessingStepId);
    return steps[stepIndex];
  };

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Video Processing</h1>
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

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-pulse">Loading videos...</div>
        </div>
      ) : videos.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <p className="text-muted-foreground mb-4">No videos currently processing</p>
          <Button asChild variant="outline">
            <Link to="/upload">Upload a new video</Link>
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
          {videos.map((video) => {
            // Get current step index and ID
            const stepIndex = getCurrentStepIndex(video.current_stage);
            const currentStepId = getCurrentStepId(video);
            
            // Create processing steps with appropriate status
            const processingSteps = createMockProcessingSteps(stepIndex);
            
            // If there's an error, update the error step
            if (video.error_message) {
              // Find the step that corresponds to the current stage
              const currentStep = processingSteps.find(step => step.id === currentStepId);
              if (currentStep) {
                currentStep.status = "error";
                currentStep.errorMessage = video.error_message;
              }
            }
            
            // Create YouTube URL if available
            const youtubeUrl = video.youtube_video_id 
              ? `https://youtube.com/watch?v=${video.youtube_video_id}` 
              : undefined;
            
            // Get thumbnail if available
            const thumbnailUrl = video.thumbnails && video.thumbnails.length > 0
              ? video.thumbnails[0].url
              : undefined;
            
            // Create upload date from timestamp
            const uploadedAt = video.created_at 
              ? new Date(video.created_at.seconds * 1000) 
              : new Date();
            
            return (
              <VideoProgressCard
                key={video.id}
                videoId={video.id}
                videoTitle={video.title || "Untitled Video"}
                thumbnailUrl={thumbnailUrl}
                uploadedAt={uploadedAt}
                status={getVideoStatus(video.current_stage)}
                processingSteps={processingSteps}
                currentStepId={currentStepId}
                youtubeUrl={youtubeUrl}
                onPauseResume={() => handlePauseResume(video.id)}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}