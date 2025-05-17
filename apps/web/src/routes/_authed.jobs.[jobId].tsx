import { createFileRoute, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api"; // Assuming api client is here
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from 'date-fns';

export const Route = createFileRoute("/_authed/jobs/$jobId")({
  component: JobDetailsPage,
});

function JobDetailsPage() {
  const { jobId } = useParams({ from: Route.id });
  // Convert jobId to number if your API expects that, or ensure it's a string if not.
  // For now, assuming API client handles string/number conversion or API accepts string.
  const numericJobId = parseInt(jobId, 10);

  const { data: jobDetails, isLoading, error, isError } = useQuery({
    queryKey: ["jobDetails", jobId], // Use string jobId for queryKey consistency if API takes string
                                     // or numericJobId if API needs number and key should reflect that.
                                     // useJobStatusManager updates cache for ['jobDetails', String(job_id)]
    queryFn: () => api.getJobDetails(jobId), // Or numericJobId if needed by API
    // Real-time updates will come from useJobStatusManager updating this query's cache
    // Optional: Add polling as a fallback if WS is not connected or for robustness
    // refetchInterval: (query) => {
    //   const job = query.state.data;
    //   if (job && (job.status === 'PENDING' || job.status === 'PROCESSING')) {
    //     return 5000; // Poll every 5 seconds if job is active
    //   }
    //   return false; // Don't poll if job is completed or failed
    // },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto p-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-1/2 mt-2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-6 w-1/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isError || !jobDetails) {
    return (
      <div className="container mx-auto p-4">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error?.message || "Failed to load job details. The job may not exist or an error occurred."}
          </AlertDescription>
        </Alert>
      </div>
    );
  }
  
  // Assuming VideoJobSchema structure from apps/core/api/schemas/video_processing_schemas.py
  // (e.g., job_id, video_id, status, progress, created_at, updated_at, error_message)
  const {
    id, // Assuming jobDetails has an 'id' field for the job ID
    video_id,
    status,
    progress,
    created_at,
    updated_at,
    error_message,
    // video_filename, // This might come from video details, not job details itself.
  } = jobDetails;

  const getStatusVariant = (status: string) => {
    switch (status.toUpperCase()) {
      case 'COMPLETED': return 'success';
      case 'FAILED': return 'destructive';
      case 'PROCESSING': return 'default';
      case 'PENDING': return 'secondary';
      default: return 'outline';
    }
  };
  
  const videoFilename = jobDetails.video?.original_filename || 'N/A'; // Example: access related video info

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>Job ID: {id}</span>
            <Badge variant={getStatusVariant(status)}>{status}</Badge>
          </CardTitle>
          <CardDescription>
            Details for video processing job. Last updated: {formatDistanceToNow(new Date(updated_at), { addSuffix: true })}.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-1">Video Information</h3>
            <p><strong>Video ID:</strong> {video_id || 'N/A'}</p>
            <p><strong>Original Filename:</strong> {videoFilename}</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-1">Job Progress</h3>
            {(status === 'PROCESSING' || status === 'COMPLETED') && progress !== null && progress !== undefined && (
              <div className="space-y-1">
                <Progress value={progress} className="w-full" />
                <p className="text-sm text-muted-foreground">{progress}% complete</p>
              </div>
            )}
            {status === 'PENDING' && <p>Waiting to be processed...</p>}
            {status === 'COMPLETED' && !progress && <p>Processing complete.</p>}
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-1">Timestamps</h3>
            <p><strong>Created:</strong> {new Date(created_at).toLocaleString()}</p>
            <p><strong>Last Updated:</strong> {new Date(updated_at).toLocaleString()}</p>
          </div>

          {error_message && (
            <div>
              <h3 className="text-lg font-semibold mb-1 text-destructive">Error Details</h3>
              <Alert variant="destructive">
                <AlertDescription>{error_message}</AlertDescription>
              </Alert>
            </div>
          )}
          
          {/* TODO: Add link to the video page if processing is complete */}
          {/* {status === 'COMPLETED' && video_id && (
            <Button asChild>
              <Link to={`/video/${video_id}`}>View Video</Link>
            </Button>
          )} */}
        </CardContent>
      </Card>
    </div>
  );
} 