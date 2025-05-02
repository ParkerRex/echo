import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ProgressSteps, Step } from "@/components/ui/progress-steps";
import { ExternalLink, PauseIcon, PlayIcon } from "lucide-react";
import { useState } from "react";

type VideoProgressCardProps = {
  videoId: string;
  videoTitle: string;
  thumbnailUrl?: string;
  uploadedAt: Date;
  status: "processing" | "completed" | "error" | "paused";
  processingSteps: Step[];
  currentStepId?: string;
  youtubeUrl?: string;
  onPauseResume?: () => void;
  className?: string;
};

export function VideoProgressCard({
  videoId,
  videoTitle,
  thumbnailUrl,
  uploadedAt,
  status,
  processingSteps,
  currentStepId,
  youtubeUrl,
  onPauseResume,
  className,
}: VideoProgressCardProps) {
  const [isPaused, setIsPaused] = useState(status === "paused");

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
    onPauseResume?.();
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
    }).format(date);
  };

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="line-clamp-1 text-base">{videoTitle}</CardTitle>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>Uploaded {formatDate(uploadedAt)}</span>
              <span>•</span>
              <span>ID: {videoId.slice(0, 8)}</span>
            </div>
          </div>
          
          {thumbnailUrl && (
            <div className="relative h-14 w-24 overflow-hidden rounded-md shrink-0">
              <img 
                src={thumbnailUrl} 
                alt={videoTitle}
                className="h-full w-full object-cover"
              />
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        <ProgressSteps 
          steps={processingSteps}
          currentStepId={currentStepId}
        />
      </CardContent>
      
      <CardFooter className="flex justify-between pt-0">
        {(status === "processing" || status === "paused") && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handlePauseResume}
          >
            {isPaused ? (
              <>
                <PlayIcon className="mr-1.5 h-3.5 w-3.5" />
                Resume
              </>
            ) : (
              <>
                <PauseIcon className="mr-1.5 h-3.5 w-3.5" />
                Pause
              </>
            )}
          </Button>
        )}
        
        {status === "completed" && youtubeUrl && (
          <Button 
            variant="outline" 
            size="sm" 
            asChild
          >
            <a href={youtubeUrl} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="mr-1.5 h-3.5 w-3.5" />
              View on YouTube
            </a>
          </Button>
        )}
        
        <Button 
          variant="ghost" 
          size="sm" 
          asChild
        >
          <a href={`/video/${videoId}`}>
            View Details
          </a>
        </Button>
      </CardFooter>
    </Card>
  );
}