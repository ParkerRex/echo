import { Button } from "src/components/ui/button";
import { VideoUploadDropzone } from "src/components/video/VideoUploadDropzone";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "src/components/ui/tabs";
import { ProcessingDashboard } from "src/components/video/processing-dashboard";
import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import { fetchMyVideos, type PaginationParams } from "src/lib/api";
import type { VideoSummary } from "@echo/types";
import {
  useInfiniteQuery,
  type InfiniteData,
  type QueryKey,
} from "@tanstack/react-query";
import { ExternalLink, UploadIcon } from "lucide-react";
import { useEffect, useState, Fragment } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "src/components/ui/dialog";
import { VideoList } from "src/components/video/VideoList";

function DashboardComponent() {
  const [activeTab, setActiveTab] = useState("library");
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  const navigate = useNavigate();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: videosLoading,
    error: videosError,
  } = useInfiniteQuery<
    VideoSummary[],
    Error,
    InfiniteData<VideoSummary[], PaginationParams | undefined>,
    QueryKey,
    PaginationParams | undefined
  >({
    queryKey: ["myVideos"],
    queryFn: ({ pageParam = { offset: 0, limit: 10 } }) =>
      fetchMyVideos(pageParam),
    initialPageParam: { offset: 0, limit: 10 } as PaginationParams | undefined,
    getNextPageParam: (
      lastPage: VideoSummary[],
      allPages: VideoSummary[][],
      lastPageParam: PaginationParams | undefined,
    ) => {
      if (!lastPageParam || lastPage.length < (lastPageParam.limit ?? 10)) {
        return undefined;
      }
      const currentTotal = allPages.reduce((acc, page) => acc + page.length, 0);
      return { offset: currentTotal, limit: lastPageParam.limit ?? 10 };
    },
  });

  const videos: VideoSummary[] =
    data?.pages.flatMap((page: VideoSummary[]) => page) ?? [];

  return (
    <div className="container py-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
            Video Dashboard
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage and monitor your video processing status
          </p>
        </div>
        <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <UploadIcon className="h-4 w-4 md:mr-2" />
              <span className="hidden md:inline">Upload New Video</span>
              <span className="sr-only md:hidden">Upload New Video</span>
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Upload Video</DialogTitle>
            </DialogHeader>
            <div className="py-4">
              <VideoUploadDropzone
                onUploadComplete={() => setUploadDialogOpen(false)}
              />
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full grid grid-cols-2 max-w-md mb-6">
          <TabsTrigger value="processing" className="flex-1">
            Processing Status
          </TabsTrigger>
          <TabsTrigger value="library" className="flex-1">
            Video Library
          </TabsTrigger>
        </TabsList>

        <TabsContent value="processing" className="space-y-4 animate-in">
          <ProcessingDashboard />
        </TabsContent>

        <TabsContent value="library" className="space-y-4 animate-in">
          <VideoList
            videos={videos}
            isLoading={videosLoading && !data}
            error={videosError}
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
            showUploadButton={true}
            onTriggerUpload={() => setUploadDialogOpen(true)}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export const Route = createFileRoute("/dashboard")({
  component: DashboardComponent,
});
