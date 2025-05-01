import { createFileRoute, Link } from "@tanstack/react-router";
import React, { useEffect, useState } from "react";
import { collection, onSnapshot, query, where } from "firebase/firestore";
import type { QuerySnapshot, DocumentData } from "firebase/firestore";
import { db } from "../../firebase/index";
import { ProcessingDashboard } from "@/components/video/processing-dashboard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { PlusIcon, ExternalLink } from "lucide-react";

interface VideoData extends DocumentData {
    id: string;
    title?: string;
    current_stage?: string;
    filename?: string;
    channel?: string;
}

function DashboardComponent() {
    const [processingVideos, setProcessingVideos] = useState<VideoData[]>([]);
    const [completedVideos, setCompletedVideos] = useState<VideoData[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("processing");

    useEffect(() => {
        // Fetch videos that are still processing (not completed)
        const processingQuery = query(
            collection(db, "videos"),
            where("current_stage", "!=", "completed")
        );
        
        const unsubscribeProcessing = onSnapshot(
            processingQuery,
            (snapshot: QuerySnapshot<DocumentData>) => {
                const vids = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })) as VideoData[];
                setProcessingVideos(vids);
                setLoading(false);
            },
            (error) => {
                console.error("Error fetching processing videos:", error);
                setLoading(false);
            }
        );
        
        // Fetch completed videos separately
        const completedQuery = query(
            collection(db, "videos"),
            where("current_stage", "==", "completed")
        );
        
        const unsubscribeCompleted = onSnapshot(
            completedQuery,
            (snapshot: QuerySnapshot<DocumentData>) => {
                const vids = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })) as VideoData[];
                setCompletedVideos(vids);
            },
            (error) => {
                console.error("Error fetching completed videos:", error);
            }
        );
        
        return () => {
            unsubscribeProcessing();
            unsubscribeCompleted();
        };
    }, []);

    return (
        <div className="container py-10">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Video Dashboard</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Manage and monitor your video processing status
                    </p>
                </div>
                <Button asChild>
                    <Link to="/upload">
                        <PlusIcon className="h-4 w-4 mr-2" />
                        Upload New Video
                    </Link>
                </Button>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="w-full max-w-md mb-6">
                    <TabsTrigger value="processing" className="flex-1">Processing Status</TabsTrigger>
                    <TabsTrigger value="library" className="flex-1">Video Library</TabsTrigger>
                </TabsList>
                
                <TabsContent value="processing" className="space-y-4 animate-in">
                    <ProcessingDashboard />
                </TabsContent>
                
                <TabsContent value="library" className="space-y-4 animate-in">
                    {loading ? (
                        <div className="flex justify-center py-20">
                            <div className="animate-pulse">Loading videos...</div>
                        </div>
                    ) : completedVideos.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                            <p className="text-muted-foreground mb-4">No completed videos found in your library</p>
                            <Button asChild variant="outline">
                                <Link to="/upload">Upload your first video</Link>
                            </Button>
                        </div>
                    ) : (
                        <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
                            {completedVideos.map(video => (
                                <div key={video.id} className="group relative rounded-lg border border-border p-4 hover:border-primary transition-colors">
                                    <div className="flex justify-between items-start mb-3">
                                        <h3 className="font-semibold line-clamp-1 group-hover:text-primary transition-colors">
                                            {video.title || "Untitled Video"}
                                        </h3>
                                        {video.youtube_video_id && (
                                            <a 
                                                href={`https://studio.youtube.com/video/${video.youtube_video_id}/edit`} 
                                                target="_blank" 
                                                rel="noopener noreferrer"
                                                className="text-muted-foreground hover:text-primary transition-colors"
                                            >
                                                <ExternalLink className="h-4 w-4" />
                                            </a>
                                        )}
                                    </div>
                                    <div className="mt-2 space-y-1 text-sm text-muted-foreground">
                                        <p className="line-clamp-1">Filename: {video.filename || "N/A"}</p>
                                        <p>Channel: {video.channel || "N/A"}</p>
                                        {video.youtube_video_id && (
                                            <div className="mt-3 flex space-x-2">
                                                <Button 
                                                    variant="outline" 
                                                    size="sm" 
                                                    asChild
                                                >
                                                    <Link
                                                        to="/video/$videoId"
                                                        params={{ videoId: video.id }}
                                                    >
                                                        View Details
                                                    </Link>
                                                </Button>
                                                <Button 
                                                    variant="outline" 
                                                    size="sm" 
                                                    asChild
                                                >
                                                    <a 
                                                        href={`https://youtube.com/watch?v=${video.youtube_video_id}`} 
                                                        target="_blank" 
                                                        rel="noopener noreferrer"
                                                    >
                                                        Watch on YouTube
                                                    </a>
                                                </Button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}

export const Route = createFileRoute("/dashboard")({
    component: DashboardComponent,
});
