import { Link } from "@tanstack/react-router";
import type { VideoSummary } from "@echo/types";
import { Button } from "../ui/button";

interface VideoListItemProps {
  video: VideoSummary;
}

export function VideoListItem({ video }: VideoListItemProps) {
  return (
    <div
      key={video.id} // Key should be on the top-level element returned by map in VideoList
      className="group relative rounded-lg border border-border p-4 hover:border-primary transition-colors"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold line-clamp-1 group-hover:text-primary transition-colors">
          {video.title || "Untitled Video"}
        </h3>
        {/* TODO: Add status badge or icon here based on video.status */}
      </div>
      {video.thumbnail_file_url && (
        <Link
          to="/$videoId"
          params={{ videoId: String(video.id) }}
          className="block aspect-video w-full overflow-hidden rounded-md mb-3"
        >
          <img
            src={video.thumbnail_file_url}
            alt={video.title || "Video thumbnail"}
            className="w-full h-full object-cover transition-transform group-hover:scale-105"
          />
        </Link>
      )}
      <div className="mt-2 space-y-1 text-sm text-muted-foreground">
        <p>Status: {video.status || "N/A"}</p>
        {/* Can add more details like created_at, duration etc. if needed */}
      </div>
      <div className="mt-3 flex space-x-2">
        <Button variant="outline" size="sm" asChild>
          <Link to="/$videoId" params={{ videoId: String(video.id) }}>
            View Details
          </Link>
        </Button>
        {/* TODO: Add other actions like Edit, Delete if applicable */}
      </div>
    </div>
  );
}
