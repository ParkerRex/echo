import { useState, useEffect } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Dropzone } from "../components/ui/dropzone";
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ProcessingStepId, createMockProcessingSteps, initializeProcessingSteps, updateStepStatus } from "../components/video/processing-steps";
import { VideoProgressCard } from "../components/video/video-progress-card";
import { Step } from "../components/ui/progress-steps";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { db } from "../../firebase";
import { ArrowRight, CheckCircle, Info, Loader2 } from "lucide-react";

function UploadComponent() {
  const [uploadState, setUploadState] = useState<"idle" | "uploading" | "processing" | "complete" | "error">("idle");
  const [selectedChannel, setSelectedChannel] = useState<string>("daily");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [processingSteps, setProcessingSteps] = useState<Step[]>(initializeProcessingSteps());
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  // Reset demo processing after component mounts
  useEffect(() => {
    return () => {
      setProcessingSteps(initializeProcessingSteps());
      setUploadState("idle");
      setUploadProgress(0);
    };
  }, []);

  const handleFilesAccepted = async (files: File[]) => {
    if (files.length === 0) return;
    
    setVideoFile(files[0]);
    setUploadError(null);
    
    // Validate file type
    const file = files[0];
    if (!file.name.toLowerCase().endsWith(".mp4") && file.type !== "video/mp4") {
      setUploadError("Invalid file type. Please upload a .mp4 video file.");
      return;
    }
  }

  const handleUpload = async () => {
    if (!videoFile) return;
    
    // Start upload
    setUploadState("uploading");
    setUploadProgress(0);
    
    try {
      // Step 1: Request signed URL from backend
      const res = await fetch("/api/gcs-upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: videoFile.name,
          content_type: videoFile.type || "video/mp4",
          channel: selectedChannel,
        }),
      });

      if (!res.ok) {
        setUploadError("Failed to get upload URL from backend.");
        setUploadState("error");
        return;
      }

      const { url, gcs_url } = await res.json();
      if (!url) {
        setUploadError("Backend did not return a valid upload URL.");
        setUploadState("error");
        return;
      }

      // Step 2: Upload file directly to GCS using the signed URL
      const xhr = new XMLHttpRequest();
      xhr.open("PUT", url, true);
      xhr.setRequestHeader("Content-Type", videoFile.type || "video/mp4");

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          setUploadProgress(Math.floor(progress));
        }
      };

      xhr.onerror = () => {
        setUploadError("An error occurred during upload to GCS.");
        setUploadState("error");
      };

      xhr.onload = async () => {
        if (xhr.status === 200) {
          setUploadProgress(100);
          
          // Mark upload step as completed
          setProcessingSteps(prev => 
            updateStepStatus(prev, ProcessingStepId.UPLOAD, "completed")
          );
          
          // Use the gcs_url returned by the backend
          const gcsUrl = gcs_url;

          // Create Firestore document for the uploaded video
          try {
            await addDoc(collection(db, "videos"), {
              filename: videoFile.name,
              url: gcsUrl,
              uploadTime: serverTimestamp(),
              current_stage: "uploaded",
              channel: selectedChannel,
              stages_completed: ["upload"],
              error: null,
              metadata: {},
              thumbnails: [],
              title: videoFile.name.replace(/\.[^/.]+$/, ""), // Remove extension
            });
            
            // Change to processing state
            setUploadState("processing");
            
            // Start simulating processing steps for demo
            simulateProcessing();
            
          } catch (firestoreError) {
            setUploadError("Upload succeeded but failed to create video record.");
            setUploadState("error");
          }
        } else {
          setUploadError("Upload to GCS failed.");
          setUploadState("error");
        }
      };

      xhr.send(videoFile);
    } catch (error: any) {
      setUploadError("An error occurred during upload.");
      setUploadState("error");
    }
  };
  
  // Simulate the processing steps for demo purposes
  const simulateProcessing = () => {
    const steps = Object.values(ProcessingStepId);
    let currentStepIndex = 1; // Start from the second step (first is upload)
    
    const processStep = () => {
      if (currentStepIndex >= steps.length) {
        setUploadState("complete");
        return;
      }
      
      const currentStep = steps[currentStepIndex] as ProcessingStepId;
      
      // Set step to in progress
      setProcessingSteps(prev => 
        updateStepStatus(prev, currentStep, "in_progress")
      );
      
      // Simulate step progress
      let stepProgress = 0;
      const stepInterval = setInterval(() => {
        stepProgress += 10;
        
        setProcessingSteps(prev => 
          updateStepStatus(prev, currentStep, "in_progress", { progress: stepProgress })
        );
        
        if (stepProgress >= 100) {
          clearInterval(stepInterval);
          
          // Mark current step as completed
          setProcessingSteps(prev => 
            updateStepStatus(prev, currentStep, "completed")
          );
          
          // Move to next step
          currentStepIndex++;
          setTimeout(processStep, 500);
        }
      }, 250);
    };
    
    processStep();
  };
  
  // Create a video object for the progress card
  const getVideoPreview = () => {
    if (!videoFile) return null;
    
    const currentStepId = processingSteps.find(step => step.status === "in_progress")?.id;
    
    return {
      videoId: "preview-" + Date.now(),
      videoTitle: videoFile.name.replace(/\.[^/.]+$/, ""), // Remove extension
      uploadedAt: new Date(),
      status: uploadState as "processing" | "completed" | "error" | "paused",
      processingSteps,
      currentStepId,
    };
  };
  
  return (
    <div className="container py-10">
      <h1 className="text-2xl font-bold tracking-tight mb-6">Upload Video</h1>
      
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Select Video</CardTitle>
              <CardDescription>
                Upload a video file to process
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {uploadState === "idle" && (
                <>
                  <Tabs defaultValue="upload">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="upload">Upload File</TabsTrigger>
                      <TabsTrigger value="url">Video URL</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="upload" className="space-y-4">
                      <Dropzone 
                        onFilesAccepted={handleFilesAccepted}
                        maxFiles={1}
                        maxSize={1024 * 1024 * 500} // 500MB
                        accept={{
                          'video/*': ['.mp4', '.mov', '.avi', '.webm']
                        }}
                      />
                      
                      {uploadError && (
                        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
                          {uploadError}
                        </div>
                      )}
                    </TabsContent>
                    
                    <TabsContent value="url" className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <input 
                          type="text" 
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                          placeholder="Enter YouTube or video URL"
                        />
                        <Button disabled>Import</Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        <Info className="inline-block h-3 w-3 mr-1" />
                        URL import coming soon
                      </p>
                    </TabsContent>
                  </Tabs>
                  
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="channel">Processing Channel</Label>
                      <Select 
                        value={selectedChannel} 
                        onValueChange={setSelectedChannel}
                      >
                        <SelectTrigger id="channel" className="mt-1.5">
                          <SelectValue placeholder="Select channel" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="daily">Daily</SelectItem>
                          <SelectItem value="main">Main Channel</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </>
              )}
              
              {uploadState === "uploading" && (
                <div className="space-y-6">
                  <div className="flex items-center space-x-3">
                    <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                    <span>Uploading {videoFile?.name}</span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground flex justify-between">
                      <span>Upload progress</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                      <div
                        className="h-full bg-primary transition-all duration-300 ease-in-out"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
              
              {(uploadState === "processing" || uploadState === "complete") && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    {uploadState === "processing" ? (
                      <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    ) : (
                      <CheckCircle className="h-5 w-5 text-primary" />
                    )}
                    <span className="font-medium">
                      {uploadState === "processing" ? "Processing video..." : "Processing complete!"}
                    </span>
                  </div>
                  
                  {videoFile && getVideoPreview() && (
                    <VideoProgressCard 
                      {...getVideoPreview()!}
                    />
                  )}
                </div>
              )}
              
              {uploadState === "error" && (
                <div className="space-y-4">
                  <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-md">
                    <h3 className="text-destructive font-medium mb-2">Upload Error</h3>
                    <p className="text-sm text-muted-foreground">{uploadError}</p>
                  </div>
                  
                  <Button onClick={() => setUploadState("idle")} variant="outline">
                    Try Again
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Upload Details</CardTitle>
              <CardDescription>
                Information about your video
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {videoFile ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-sm font-medium">Filename</span>
                    <p className="text-sm text-muted-foreground truncate">{videoFile.name}</p>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium">Size</span>
                    <p className="text-sm text-muted-foreground">
                      {(videoFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium">Type</span>
                    <p className="text-sm text-muted-foreground">{videoFile.type || "video/mp4"}</p>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium">Channel</span>
                    <p className="text-sm text-muted-foreground capitalize">{selectedChannel}</p>
                  </div>
                  
                  {uploadState === "idle" && (
                    <Button 
                      className="w-full mt-4" 
                      onClick={handleUpload}
                    >
                      Start Processing
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  )}
                  
                  {uploadState === "complete" && (
                    <div className="space-y-4 mt-6">
                      <Button 
                        className="w-full" 
                        asChild
                      >
                        <Link to="/dashboard">
                          Go to Dashboard
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                      </Button>
                      <Button 
                        className="w-full" 
                        variant="outline"
                        onClick={() => {
                          setVideoFile(null);
                          setUploadState("idle");
                          setProcessingSteps(initializeProcessingSteps());
                        }}
                      >
                        Upload Another Video
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-8 text-center text-muted-foreground">
                  <p>No file selected</p>
                  <p className="text-xs mt-1">Select a video file to upload</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/upload")({
  component: UploadComponent,
});
