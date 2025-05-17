import { createFileRoute, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { getJobDetails } from "@/lib/api"; // Corrected: Import specific function
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from 'date-fns';

export const Route = createFileRoute("/_authed/jobs/$jobId")({
  component: JobDetailsPage,
});

function JobDetailsPage() {
  const { jobId } = useParams({ from: Route.id });

  const { data: jobDetails, isLoading, error, isError } = useQuery({
    queryKey: ["jobDetails", jobId], 
    queryFn: () => getJobDetails(jobId), // Corrected: Use imported function directly
    // ... (rest of useQuery options)
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
            {/* Skeleton for progress bar area removed */}
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
  
  const {
    id, 
    video_id,
    status,
    processing_stages,
    created_at,
    updated_at,
    error_message,
    video // Assuming 'video' object is part of VideoJobSchema and contains original_filename
  } = jobDetails;

  const getStatusVariant = (currentStatus: string) => {
    switch (currentStatus.toUpperCase()) {
      case 'COMPLETED': return 'default'; // Corrected: Use 'default' for success, can be styled green via CSS
      case 'FAILED': return 'destructive';
      case 'PROCESSING': return 'default'; // Or 'secondary' if 'default' is used for COMPLETED with specific styling
      case 'PENDING': return 'secondary';
      default: return 'outline';
    }
  };
  
  const videoFilename = video?.original_filename || 'N/A';
  const lastUpdatedText = updated_at ? formatDistanceToNow(new Date(updated_at), { addSuffix: true }) : 'N/A';
  const createdAtText = created_at ? new Date(created_at).toLocaleString() : 'N/A';

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>Job ID: {id}</span>
            <Badge variant={getStatusVariant(status)}>{status}</Badge>
          </CardTitle>
          <CardDescription>
            Details for video processing job. Last updated: {lastUpdatedText}.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-1">Video Information</h3>
            <p><strong>Video ID:</strong> {video_id || 'N/A'}</p>
            <p><strong>Original Filename:</strong> {videoFilename}</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-1">Job Progress/Stages</h3>
            {/* Display processing_stages if available and meaningful */}
            {processing_stages && (
              <pre className="text-xs bg-muted p-2 rounded-md overflow-x-auto">
                {JSON.stringify(processing_stages, null, 2)}
              </pre>
            )}
            {status === 'PENDING' && !processing_stages && <p>Waiting to be processed...</p>}
            {status === 'PROCESSING' && !processing_stages && <p>Processing...</p>}
            {status === 'COMPLETED' && <p>Processing complete.</p>}
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-1">Timestamps</h3>
            <p><strong>Created:</strong> {createdAtText}</p>
            <p><strong>Last Updated:</strong> {updated_at ? new Date(updated_at).toLocaleString() : 'N/A'}</p>
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