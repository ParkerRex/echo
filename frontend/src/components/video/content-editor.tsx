import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Save, Pencil, X } from "lucide-react";

type ContentEditorProps = {
  content: string;
  isLoading?: boolean;
  errorMessage?: string;
  onSave?: (content: string) => Promise<void>;
  className?: string;
  readOnly?: boolean;
  placeholder?: string;
  maxHeight?: string;
};

export function ContentEditor({
  content,
  isLoading = false,
  errorMessage,
  onSave,
  className = "",
  readOnly = false,
  placeholder = "Content not available yet",
  maxHeight = "400px"
}: ContentEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Update edited content when the source content changes
  useEffect(() => {
    setEditedContent(content);
  }, [content]);

  const handleEdit = () => {
    setIsEditing(true);
    setSaveError(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedContent(content);
    setSaveError(null);
  };

  const handleSave = async () => {
    if (!onSave) return;
    setIsSaving(true);
    setSaveError(null);

    try {
      await onSave(editedContent);
      setIsEditing(false);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : "Error saving content");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        <span>Loading content...</span>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="p-4 border border-red-200 rounded-md bg-red-50 text-red-600">
        <p className="font-medium">Error loading content</p>
        <p className="text-sm mt-1">{errorMessage}</p>
      </div>
    );
  }

  if (!content.trim() && !isEditing) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
        <p>{placeholder}</p>
        {!readOnly && onSave && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleEdit}
            className="mt-4"
          >
            <Pencil className="h-4 w-4 mr-2" />
            Create Content
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {isEditing ? (
        <>
          <Textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className={`min-h-[200px] font-mono text-sm p-4 ${saveError ? 'border-red-300' : ''}`}
            placeholder="Enter content here..."
            disabled={isSaving}
          />
          
          {saveError && (
            <div className="mt-2 p-2 text-sm text-red-600 bg-red-50 rounded-md">
              {saveError}
            </div>
          )}
          
          <div className="flex justify-end gap-2 mt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCancel}
              disabled={isSaving}
            >
              <X className="h-4 w-4 mr-1" />
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-1" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </>
      ) : (
        <>
          <div 
            className={`overflow-y-auto p-4 font-mono text-sm whitespace-pre-wrap border rounded-md ${
              !readOnly ? "hover:border-primary hover:bg-accent/10 transition-colors" : ""
            }`}
            style={{ maxHeight }}
          >
            {content}
          </div>
          
          {!readOnly && onSave && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEdit}
              className="absolute top-2 right-2"
            >
              <Pencil className="h-4 w-4" />
            </Button>
          )}
        </>
      )}
    </div>
  );
}