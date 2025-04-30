import { createFileRoute, useParams } from "@tanstack/react-router";
import React, { useEffect, useState } from "react";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { db } from "../../firebase";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";

function VideoDetailComponent() {
  const { videoId } = useParams({ from: "/video/$videoId" });
  const [videoData, setVideoData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function fetchVideo() {
      setLoading(true);
      const docRef = doc(db, "videos", videoId);
      const docSnap = await getDoc(docRef);
      if (docSnap.exists()) {
        setVideoData(docSnap.data());
        setForm(docSnap.data());
      } else {
        setVideoData(null);
        setForm(null);
      }
      setLoading(false);
    }
    if (videoId) fetchVideo();
  }, [videoId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!form) return;
    setSaving(true);
    const docRef = doc(db, "videos", videoId);
    await updateDoc(docRef, {
      title: form.title,
      description: form.description,
      tags: form.tags,
      scheduledTime: form.scheduledTime,
    });
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
