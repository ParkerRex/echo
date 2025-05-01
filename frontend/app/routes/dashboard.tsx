import { createFileRoute, Link } from "@tanstack/react-router";
import React, { useEffect, useState } from "react";
import { collection, onSnapshot } from "firebase/firestore";
import type { QuerySnapshot, DocumentData } from "firebase/firestore";
import { db } from "../../firebase/index";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";

interface VideoData extends DocumentData {
    id: string;
    title?: string;
    current_stage?: string;
    filename?: string;
    channel?: string;
}

function DashboardComponent() {
    const [videos, setVideos] = useState<VideoData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const unsubscribe = onSnapshot(
            collection(db, "videos"),
            (snapshot: QuerySnapshot<DocumentData>) => {
                const vids = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })) as VideoData[];
                setVideos(vids);
                setLoading(false);
            },
            (error) => {
                console.error("Error fetching videos:", error);
                setLoading(false);
            }
        );
        return () => unsubscribe();
    }, []);

    return (
        <div className="max-w-3xl mx-auto py-8">
            <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
            {loading ? (
                <div>Loading videos...</div>
            ) : videos.length === 0 ? (
                <div>No videos found.</div>
            ) : (
                <div className="space-y-4">
                    {videos.map(video => (
                        <Card key={video.id}>
                            <CardHeader>
                                <CardTitle>
                                    <Link
                                        to="/video/$videoId"
                                        params={{ videoId: video.id }}
                                        className="text-blue-600 hover:underline"
                                    >
                                        {video.title || "Untitled Video"}
                                    </Link>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div>Status: {video.current_stage || "Unknown"}</div>
                                <div>Filename: {video.filename || "N/A"}</div>
                                <div>Channel: {video.channel || "N/A"}</div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}

export const Route = createFileRoute("/dashboard")({
    component: DashboardComponent,
});
