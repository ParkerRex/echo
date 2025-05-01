import { createFileRoute, useParams } from "@tanstack/react-router";
import React, { useEffect, useState } from "react";
import { doc, getDoc, updateDoc, onSnapshot, DocumentSnapshot } from "firebase/firestore";
import type { DocumentData } from "firebase/firestore";
import { db } from "../../firebase/index";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";

interface Thumbnail {
  url: string;
  prompt: string;
  status: string;
}

interface VideoData {
  title: string;
  description: string;
  tags: string;
  scheduledTime: string;
  thumbnails: Thumbnail[];
  [key: string]: any; // For other properties that might be in the data
}

interface VideoFormData {
  title?: string;
  description?: string;
  tags?: string;
  scheduledTime?: string;
  thumbnails?: Thumbnail[];
  [key: string]: any;
}

function VideoDetailComponent() {
  const { videoId } = useParams({ from: "/video/$videoId" });
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<VideoFormData | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!videoId) return;
    setLoading(true);
    const docRef = doc(db, "videos", videoId);
    const unsubscribe = onSnapshot(
      docRef,
      (docSnap: DocumentSnapshot<DocumentData>) => {
        if (docSnap.exists()) {
          const data = docSnap.data() as VideoData;
          setVideoData(data);
          setForm(data);
        } else {
          setVideoData(null);
          setForm(null);
        }
        setLoading(false);
      },
      (error) => {
        console.error("Error fetching video data:", error);
        setVideoData(null);
        setForm(null);
        setLoading(false);
      }
    );
    return () => unsubscribe();
  }, [videoId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (!form) return;
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!form) return;
    setSaving(true);
    const docRef = doc(db, "videos", videoId);

    // Only include fields that are present in the form
    const updates: Partial<VideoData> = {};
    if (form.title !== undefined) updates.title = form.title;
    if (form.description !== undefined) updates.description = form.description;
    if (form.tags !== undefined) updates.tags = form.tags;
    if (form.scheduledTime !== undefined) updates.scheduledTime = form.scheduledTime;

    await updateDoc(docRef, updates);
    setSaving(false);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!videoData) {
    return <div>Video not found.</div>;
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Video Detail</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={e => {
              e.preventDefault();
              handleSave();
            }}
            className="space-y-4"
          >
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                name="title"
                value={form?.title || ""}
                onChange={handleChange}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                name="description"
                value={form?.description || ""}
                onChange={handleChange}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="tags">Tags (comma separated)</Label>
              <Input
                id="tags"
                name="tags"
                value={form?.tags || ""}
                onChange={handleChange}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="scheduledTime">Scheduled Time</Label>
              <Input
                id="scheduledTime"
                name="scheduledTime"
                type="datetime-local"
                value={form?.scheduledTime || ""}
                onChange={handleChange}
                className="mt-1"
              />
            </div>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </form>
        </CardContent>
      </Card>
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Thumbnails</CardTitle>
          </CardHeader>
          <CardContent>
            {Array.isArray(videoData.thumbnails) && videoData.thumbnails.length > 0 ? (
              <div className="space-y-6">
                {videoData.thumbnails.map((thumb: Thumbnail, idx: number) => (
                  <div key={idx} className="flex items-center space-x-4">
                    <img
                      src={thumb.url}
                      alt={`Thumbnail ${idx + 1}`}
                      className="w-32 h-20 object-cover rounded border"
                    />
                    <div className="flex-1">
                      <Label htmlFor={`thumb-prompt-${idx}`}>Prompt</Label>
                      <Input
                        id={`thumb-prompt-${idx}`}
                        name={`thumb-prompt-${idx}`}
                        value={form?.thumbnails?.[idx]?.prompt || thumb.prompt || ""}
                        onChange={e => {
                          if (!form) return;
                          const newThumbs = [...(form.thumbnails || videoData.thumbnails)];
                          newThumbs[idx] = {
                            ...newThumbs[idx],
                            prompt: e.target.value,
                          };
                          setForm({ ...form, thumbnails: newThumbs });
                        }}
                        className="mt-1"
                      />
                    </div>
                    <Button
                      type="button"
                      onClick={async () => {
                        // Save the new prompt and trigger backend regeneration
                        if (!form || !form.thumbnails) return;
                        setSaving(true);
                        const docRef = doc(db, "videos", videoId);
                        await updateDoc(docRef, {
                          [`thumbnails.${idx}.prompt`]: form.thumbnails[idx].prompt,
                          [`thumbnails.${idx}.status`]: "pending", // Mark as pending for backend to pick up
                        });
                        setSaving(false);
                      }}
                      disabled={saving}
                    >
                      {saving ? "Regenerating..." : "Regenerate"}
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div>No thumbnails found for this video.</div>
            )}
          </CardContent>
        </Card>
      </div>
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Raw Video Data</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted p-4 rounded text-xs overflow-x-auto">
              {JSON.stringify(videoData, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/video/$videoId")({
  component: VideoDetailComponent,
});
