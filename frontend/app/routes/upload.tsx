import { createFileRoute } from "@tanstack/react-router";

import { DropZone } from "../components/ui/dropzone";

function UploadComponent() {
  const handleFilesAccepted = (files: FileList | File[]) => {
    // For now, just log the files. Integration with backend/Firestore comes next.
    console.log("Files accepted:", files);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] py-8">
      <h1 className="text-3xl font-bold mb-4">Upload Video</h1>
      <p className="text-gray-600 mb-6">Drag and drop your .mp4 file below or click to select from your computer.</p>
      <div className="w-full max-w-lg">
        <DropZone onFilesAccepted={handleFilesAccepted} accept=".mp4" multiple={false} />
      </div>
    </div>
  );
}

export const Route = createFileRoute("/upload")({
  component: UploadComponent,
});
