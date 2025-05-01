import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import DropZone from "../components/ui/dropzone";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { db } from "../../firebase";

function UploadComponent() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFilesAccepted = async (files: FileList | File[]) => {
    setUploadError(null);

    if (!files || (files instanceof FileList && files.length === 0) || (Array.isArray(files) && files.length === 0)) {
      return;
    }
    const file = Array.isArray(files) ? files[0] : files[0];

    if (!file.name.toLowerCase().endsWith(".mp4") && file.type !== "video/mp4") {
      setUploadError("Invalid file type. Please upload a .mp4 video file.");
      return;
    }

    setUploadStatus("Starting upload...");
    setUploadProgress(0);

    try {
      // Step 1: Request signed URL from backend
      const res = await fetch("/api/gcs-upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: file.name,
          content_type: file.type || "video/mp4",
        }),
      });

      if (!res.ok) {
        setUploadError("Failed to get upload URL from backend.");
        setUploadProgress(0);
        setUploadStatus(null);
        return;
      }

      const { url, gcs_url } = await res.json();
      if (!url) {
        setUploadError("Backend did not return a valid upload URL.");
        setUploadProgress(0);
        setUploadStatus(null);
        return;
      }

      // Step 2: Upload file directly to GCS using the signed URL
      setUploadStatus("Uploading to Google Cloud Storage...");
      const xhr = new XMLHttpRequest();
      xhr.open("PUT", url, true);
      xhr.setRequestHeader("Content-Type", file.type || "video/mp4");

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          setUploadProgress(progress);
          setUploadStatus(`Uploading... ${Math.floor(progress)}%`);
        }
      };

      xhr.onerror = () => {
        setUploadError("An error occurred during upload to GCS.");
        setUploadProgress(0);
        setUploadStatus(null);
      };

      xhr.onload = async () => {
        if (xhr.status === 200) {
          setUploadProgress(100);
          setUploadStatus("Upload complete!");

          // Use the gcs_url returned by the backend
          const gcsUrl = gcs_url;

          // Create Firestore document for the uploaded video
          try {
            await addDoc(collection(db, "videos"), {
              filename: file.name,
              url: gcsUrl,
              uploadTime: serverTimestamp(),
              current_stage: "Uploaded",
              stages_completed: [],
              error: null,
              metadata: {},
              thumbnails: [],
              editable_fields: {},
            });
          } catch (firestoreError) {
            setUploadError("Upload succeeded but failed to create video record.");
          }
        } else {
          setUploadError("Upload to GCS failed.");
          setUploadProgress(0);
          setUploadStatus(null);
        }
      };

      xhr.send(file);
    } catch (error: any) {
      setUploadError("An error occurred during upload.");
      setUploadProgress(0);
      setUploadStatus(null);
    }
  };

  const isUploading = uploadStatus !== null && uploadStatus.startsWith("Uploading");

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Upload Video</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-6">
            Drag and drop your .mp4 file below or click to select from your computer.
          </p>
          <div className="w-full max-w-lg">
            <DropZone onFilesAccepted={handleFilesAccepted} accept=".mp4" multiple={false} disabled={isUploading} />
          </div>
          {uploadStatus && (
            <div className="mt-4 w-full max-w-lg">
              <p className="mb-2">{uploadStatus}</p>
              <progress className="w-full" value={uploadProgress} max="100"></progress>
            </div>
          )}
          {uploadError && (
            <div className="mt-4 w-full max-w-lg">
              <p className="mb-2 text-red-500">{uploadError}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export const Route = createFileRoute("/upload")({
  component: UploadComponent,
});
