import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, createFileRoute, useParams } from "@tanstack/react-router";
import { useEffect } from "react";
import { type ControllerRenderProps, FieldValues, useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "~/components/ui/form";
import { Input } from "~/components/ui/input";
import { Skeleton } from "~/components/ui/skeleton";
import { Textarea } from "~/components/ui/textarea";
import type {
  VideoDetailsResponse,
  VideoMetadataUpdateRequest,
} from "@echo/types";
import { getVideoDetails, updateVideoMetadata } from "../lib/api";

// Placeholder for MediaPlayer component - to be created later
const MediaPlayer = ({
  src,
  title,
  subtitleFilesUrls,
}: {
  src: string;
  title?: string;
  subtitleFilesUrls?: { [key: string]: string } | null;
}) => {
  return (
    <div className="aspect-video bg-slate-900 flex items-center justify-center text-slate-100 rounded-lg overflow-hidden">
      {src ? (
        <video
          controls
          src={src}
          title={title || "Video player"}
          className="w-full h-full"
          crossOrigin="anonymous"
        >
          Your browser does not support the video tag.
          {subtitleFilesUrls &&
            Object.entries(subtitleFilesUrls).map(
              ([lang, subtitleSrc], index) => (
                <track
                  key={lang}
                  kind="subtitles"
                  srcLang={lang}
                  src={subtitleSrc}
                  label={lang.toUpperCase()} // Simple label, could be more descriptive
                  default={index === 0} // Set the first subtitle track as default
                />
              ),
            )}
        </video>
      ) : (
        <p>
          Video playback URL not available. Please ensure backend provides it.
        </p>
      )}
    </div>
  );
};

const metadataFormSchema = z.object({
  title: z.string().min(1, "Title is required.").max(255),
  description: z.string().max(5000).optional(),
  tags: z.string().optional(), // Represent tags as a comma-separated string for simplicity in form
});
type MetadataFormValues = z.infer<typeof metadataFormSchema>;

export const Route = createFileRoute("/$videoId")({
  component: VideoDetailPage,
});

function VideoDetailPage() {
  const { videoId } = useParams({ from: Route.id });
  const {
    data: videoDetails,
    isLoading,
    error,
    isError,
    refetch,
  } = useQuery<VideoDetailsResponse, Error>({
    queryKey: ["videoDetails", videoId],
    queryFn: () => getVideoDetails(videoId),
  });

  const form = useForm<MetadataFormValues>({
    resolver: zodResolver(metadataFormSchema),
    // Default values will be set in useEffect when videoDetails load
  });

  useEffect(() => {
    if (videoDetails?.metadata) {
      form.reset({
        title: videoDetails.metadata.title || "",
        description: videoDetails.metadata.description || "",
        tags: videoDetails.metadata.tags?.join(", ") || "",
      });
    }
  }, [videoDetails, form.reset]);

  const { mutate: submitMetadata, isPending: isUpdatingMetadata } = useMutation(
    {
      mutationFn: async (data: VideoMetadataUpdateRequest) =>
        updateVideoMetadata(videoId, data),
      onSuccess: () => {
        toast.success("Metadata updated successfully!");
        refetch(); // Refetch video details to show updated data
      },
      onError: (err: Error) => {
        toast.error(`Failed to update metadata: ${err.message}`);
      },
    },
  );

  const onSubmitMetadata = (values: MetadataFormValues) => {
    const updateRequest: VideoMetadataUpdateRequest = {
      title: values.title,
      description: values.description || undefined,
      tags: values.tags
        ? values.tags
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag)
        : [],
    };
    submitMetadata(updateRequest);
  };

  if (isLoading) {
    return <VideoDetailSkeleton />;
  }

  if (isError || !videoDetails) {
    return (
      <div className="container mx-auto p-4">
        <Alert variant="destructive">
          <AlertTitle>Error Loading Video</AlertTitle>
          <AlertDescription>
            {error?.message ||
              "Failed to load video details. The video may not exist or an error occurred."}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Playback URL needs to be provided by the backend in VideoDetailsResponse, ideally as a direct field
  // like `video.playback_url` (e.g., a GCS signed URL).
  // The `storage_path` (e.g., gs://bucket/path) is generally not directly playable.
  // Waiting for backend to add a dedicated playback URL field to VideoSchema or VideoDetailsResponse.
  const playbackUrl =
    (videoDetails.video as any)?.playback_url ||
    videoDetails.video?.storage_path ||
    "";
  const videoTitle =
    videoDetails.metadata?.title ||
    videoDetails.video?.original_filename ||
    "Video";
  const subtitles = videoDetails.metadata?.subtitle_files_urls as
    | { [key: string]: string }
    | undefined;

  return (
    <div className="container mx-auto p-4 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{videoTitle}</CardTitle>
          {videoDetails.video?.original_filename && (
            <CardDescription>
              Original file: {videoDetails.video.original_filename}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          <MediaPlayer
            src={playbackUrl}
            title={videoTitle}
            subtitleFilesUrls={subtitles}
          />
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Details & Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p>
                <strong>Status:</strong> {videoDetails.status}
              </p>
              <p>
                <strong>Uploaded:</strong>{" "}
                {videoDetails.video?.created_at
                  ? new Date(videoDetails.video.created_at).toLocaleString()
                  : "N/A"}
              </p>
              <p>
                <strong>Last Updated:</strong>{" "}
                {videoDetails.updated_at
                  ? new Date(videoDetails.updated_at).toLocaleString()
                  : "N/A"}
              </p>
              {videoDetails.metadata?.description && (
                <p>
                  <strong>Description:</strong>{" "}
                  {videoDetails.metadata.description}
                </p>
              )}
              {videoDetails.metadata?.tags &&
                videoDetails.metadata.tags.length > 0 && (
                  <p>
                    <strong>Tags:</strong>{" "}
                    {videoDetails.metadata.tags.join(", ")}
                  </p>
                )}
            </CardContent>
          </Card>

          {videoDetails.metadata?.transcript_text && (
            <Card>
              <CardHeader>
                <CardTitle>Transcript</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  readOnly
                  value={videoDetails.metadata.transcript_text}
                  rows={10}
                  className="font-mono text-sm"
                />
              </CardContent>
            </Card>
          )}
        </div>

        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Edit Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmitMetadata)}
                  className="space-y-4"
                >
                  <FormField
                    control={form.control}
                    name="title"
                    render={({
                      field,
                    }: {
                      field: ControllerRenderProps<MetadataFormValues, "title">;
                    }) => (
                      <FormItem>
                        <FormLabel>Title</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="description"
                    render={({
                      field,
                    }: {
                      field: ControllerRenderProps<
                        MetadataFormValues,
                        "description"
                      >;
                    }) => (
                      <FormItem>
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Textarea {...field} rows={4} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="tags"
                    render={({
                      field,
                    }: {
                      field: ControllerRenderProps<MetadataFormValues, "tags">;
                    }) => (
                      <FormItem>
                        <FormLabel>Tags (comma-separated)</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button
                    type="submit"
                    disabled={isUpdatingMetadata}
                    className="w-full"
                  >
                    {isUpdatingMetadata ? "Updating..." : "Save Metadata"}
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

const VideoDetailSkeleton = () => (
  <div className="container mx-auto p-4 space-y-6">
    <Card>
      <CardHeader>
        <Skeleton className="h-8 w-3/4 mb-2" />
        <Skeleton className="h-4 w-1/2" />
      </CardHeader>
      <CardContent>
        <Skeleton className="aspect-video w-full" />
      </CardContent>
    </Card>
    <div className="grid md:grid-cols-3 gap-6">
      <div className="md:col-span-2 space-y-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-7 w-1/3" />
          </CardHeader>
          <CardContent className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-7 w-1/3" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-24 w-full" />
          </CardContent>
        </Card>
      </div>
      <div className="md:col-span-1">
        <Card>
          <CardHeader>
            <Skeleton className="h-7 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
);
