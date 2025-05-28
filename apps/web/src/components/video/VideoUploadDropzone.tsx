import React, { useRef, useState } from "react";
import {
  getSignedUploadUrl,
  notifyUploadComplete,
} from "../../lib/api"; // Import new API functions
import type {
  SignedUploadUrlRequest,
  SignedUploadUrlResponse,
  UploadCompleteRequest,
} from "@echo/types";
import { toast } from "sonner"; // Import toast

type UploadStatus = "idle" | "requesting" | "uploading" | "finalizing" | "done" | "error";

export function VideoUploadDropzone({
  onUploadComplete: onUploadSuccess, // Renamed prop for clarity
}: {
  onUploadComplete?: (videoId: string) => void; // Pass videoId back
}) {
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setError(null);
    setStatus("requesting");
    setProgress(0);

    let signedUrlResponse: SignedUploadUrlResponse;
    try {
      const requestData: SignedUploadUrlRequest = {
        filename: file.name,
        content_type: file.type,
        size_bytes: file.size,
      };
      signedUrlResponse = await getSignedUploadUrl(requestData);
      if (!signedUrlResponse.upload_url || !signedUrlResponse.video_id) {
        throw new Error("Invalid response from signed URL endpoint");
      }
    } catch (err: any) {
      const errorMsg = err.message || "Failed to get upload URL";
      setError(errorMsg);
      toast.error(errorMsg);
      setStatus("error");
      return;
    }

    const { upload_url: uploadUrl, video_id: videoId } = signedUrlResponse;

    // 2. Upload file to signed URL
    setStatus("uploading");
    try {
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("PUT", uploadUrl);
        xhr.setRequestHeader("Content-Type", file.type);
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            setProgress(Math.round((e.loaded / e.total) * 100));
          }
        };
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve();
          } else {
            reject(new Error(`Upload failed with status ${xhr.status}: ${xhr.statusText}`));
          }
        };
        xhr.onerror = () => reject(new Error("Upload failed due to network error"));
        xhr.send(file);
      });
    } catch (err: any) {
      const errorMsg = err.message || "Upload failed";
      setError(errorMsg);
      toast.error(errorMsg);
      setStatus("error");
      return;
    }

    // 3. Notify backend upload is complete
    setStatus("finalizing");
    try {
      const completeRequestData: UploadCompleteRequest = {
        video_id: Number(videoId),
        upload_key: "upload_key", // This should come from the upload response
        original_filename: file.name,
      };
      await notifyUploadComplete(completeRequestData);
    } catch (err: any) {
      const errorMsg = err.message || "Failed to finalize upload";
      setError(errorMsg);
      toast.error(errorMsg);
      setStatus("error");
      return;
    }

    setStatus("done");
    setProgress(100);
    if (onUploadSuccess) onUploadSuccess(String(videoId)); // Pass videoId on success
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (status === "uploading" || status === "finalizing" || status === "requesting") return;
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (status === "uploading" || status === "finalizing" || status === "requesting") return;
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
      // Reset file input to allow uploading the same file again
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  const isUploading = status === "requesting" || status === "uploading" || status === "finalizing";

  return (
    <div
      onDrop={onDrop}
      onDragOver={(e) => e.preventDefault()}
      style={{
        border: "2px dashed #888",
        borderRadius: 8,
        padding: 32,
        textAlign: "center",
        background: isUploading ? "#f0f0f0" : "#fafbfc",
        cursor: isUploading ? "default" : "pointer",
        opacity: isUploading ? 0.7 : 1,
        margin: "16px 0",
      }}
      onClick={() => !isUploading && inputRef.current?.click()}
      tabIndex={0}
      role="button"
      aria-label="Upload video"
      aria-disabled={isUploading}
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        style={{ display: "none" }}
        onChange={onFileChange}
        disabled={isUploading}
      />
      {status === "idle" && <span>Drag & drop a video file here, or click to select</span>}
      {status === "requesting" && <span>Requesting upload permissions…</span>}
      {status === "uploading" && (
        <div>
          <span>Uploading… {progress}%</span>
          <progress
            value={progress}
            max={100}
            style={{ width: "100%", marginTop: "8px" }}
          />
        </div>
      )}
      {status === "finalizing" && <span>Finalizing upload…</span>}
      {status === "done" && <span style={{ color: "green" }}>Upload complete! Ready for processing.</span>}
      {status === "error" && (
        <span style={{ color: "red" }}>
          Error: {error}
        </span>
      )}
    </div>
  );
}

export default VideoUploadDropzone;
