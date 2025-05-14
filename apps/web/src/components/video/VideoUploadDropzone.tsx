import React, { useRef, useState } from "react";

type UploadStatus = "idle" | "requesting" | "uploading" | "finalizing" | "done" | "error";

export function VideoUploadDropzone({
  onUploadComplete,
}: {
  onUploadComplete?: () => void;
}) {
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setError(null);
    setStatus("requesting");
    setProgress(0);

    // 1. Request signed upload URL from backend
    let uploadUrl: string | null = null;
    let uploadCompleteToken: string | null = null;
    try {
      const res = await fetch("/videos/upload-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          filename: file.name,
          content_type: file.type,
        }),
      });
      if (!res.ok) throw new Error("Failed to get upload URL");
      const data = await res.json();
      uploadUrl = data.upload_url;
      uploadCompleteToken = data.upload_complete_token;
      if (!uploadUrl || !uploadCompleteToken) throw new Error("Invalid upload URL response");
    } catch (err: any) {
      setError(err.message || "Failed to get upload URL");
      setStatus("error");
      return;
    }

    // 2. Upload file to signed URL
    setStatus("uploading");
    try {
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("PUT", uploadUrl!);
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
            reject(new Error("Upload failed"));
          }
        };
        xhr.onerror = () => reject(new Error("Upload failed"));
        xhr.send(file);
      });
    } catch (err: any) {
      setError(err.message || "Upload failed");
      setStatus("error");
      return;
    }

    // 3. Notify backend upload is complete
    setStatus("finalizing");
    try {
      const res = await fetch("/videos/upload-complete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          upload_complete_token: uploadCompleteToken,
        }),
      });
      if (!res.ok) throw new Error("Failed to finalize upload");
    } catch (err: any) {
      setError(err.message || "Failed to finalize upload");
      setStatus("error");
      return;
    }

    setStatus("done");
    setProgress(100);
    if (onUploadComplete) onUploadComplete();
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  }

  return (
    <div
      onDrop={onDrop}
      onDragOver={(e) => e.preventDefault()}
      style={{
        border: "2px dashed #888",
        borderRadius: 8,
        padding: 32,
        textAlign: "center",
        background: "#fafbfc",
        cursor: "pointer",
        margin: "16px 0",
      }}
      onClick={() => inputRef.current?.click()}
      tabIndex={0}
      role="button"
      aria-label="Upload video"
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        style={{ display: "none" }}
        onChange={onFileChange}
        disabled={status === "uploading" || status === "finalizing"}
      />
      {status === "idle" && <span>Drag & drop a video file here, or click to select</span>}
      {status === "requesting" && <span>Requesting upload URL…</span>}
      {status === "uploading" && (
        <span>
          Uploading… {progress}%
          <br />
          <progress value={progress} max={100} />
        </span>
      )}
      {status === "finalizing" && <span>Finalizing upload…</span>}
      {status === "done" && <span>Upload complete!</span>}
      {status === "error" && (
        <span style={{ color: "red" }}>
          Error: {error}
        </span>
      )}
    </div>
  );
}

export default VideoUploadDropzone;
