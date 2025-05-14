import { Button } from "@/components/ui/button";
import { VideoUploadDropzone } from "@/components/video/VideoUploadDropzone";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ProcessingDashboard } from "@/components/video/processing-dashboard";
import { Link, createFileRoute } from "@tanstack/react-router";
import { ProtectedLayout } from "@/components/ProtectedLayout";
import { fetchMyVideos, type VideoSummary } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { ExternalLink, UploadIcon } from "lucide-react";
import { useEffect, useState } from "react";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";

type VideoData = VideoSummary;

function DashboardComponent() {
	const [activeTab, setActiveTab] = useState("processing");
	const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
	const [uploading, setUploading] = useState(false);

	const {
		data: videos = [],
		isLoading: loading,
		error,
	} = useQuery({
		queryKey: ["my-videos"],
		queryFn: fetchMyVideos,
		refetchInterval: 10000, // Poll every 10 seconds
	});

	// TODO: Implement handleFilesAccepted to use Supabase upload flow
	const handleFilesAccepted = async (files: FileList | File[]) => {
		// Placeholder for future upload logic
	};

	return (
		<div className="container py-10">
			<div className="flex items-center justify-between mb-8">
				<div>
					<h1 className="text-2xl font-bold tracking-tight">Video Dashboard</h1>
					<p className="text-muted-foreground text-sm mt-1">
						Manage and monitor your video processing status
					</p>
				</div>
				<Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
					<DialogTrigger asChild>
						<Button>
							<UploadIcon className="h-4 w-4 mr-2" />
							Upload New Video
						</Button>
					</DialogTrigger>
					<DialogContent className="sm:max-w-md">
						<DialogHeader>
							<DialogTitle>Upload Video</DialogTitle>
						</DialogHeader>
						<div className="py-4">
							<VideoUploadDropzone
								onUploadComplete={() => setUploadDialogOpen(false)}
							/>
						</div>
					</DialogContent>
				</Dialog>
			</div>

			<Tabs value={activeTab} onValueChange={setActiveTab}>
				<TabsList className="w-full max-w-md mb-6">
					<TabsTrigger value="processing" className="flex-1">
						Processing Status
					</TabsTrigger>
					<TabsTrigger value="library" className="flex-1">
						Video Library
					</TabsTrigger>
				</TabsList>

				<TabsContent value="processing" className="space-y-4 animate-in">
					<ProcessingDashboard />
				</TabsContent>

				<TabsContent value="library" className="space-y-4 animate-in">
					{loading ? (
						<div className="flex justify-center py-20">
							<div className="animate-pulse">Loading videos...</div>
						</div>
					) : videos.length === 0 ? (
						<div className="flex flex-col items-center justify-center py-20 text-center">
							<p className="text-muted-foreground mb-4">
								No videos found in your library
							</p>
							<Dialog
								open={uploadDialogOpen}
								onOpenChange={setUploadDialogOpen}
							>
								<DialogTrigger asChild>
									<Button variant="outline">Upload your first video</Button>
								</DialogTrigger>
							</Dialog>
						</div>
					) : (
						<div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
							{videos.map((video) => (
								<div
									key={video.id}
									className="group relative rounded-lg border border-border p-4 hover:border-primary transition-colors"
								>
									<div className="flex justify-between items-start mb-3">
										<h3 className="font-semibold line-clamp-1 group-hover:text-primary transition-colors">
											{video.title || "Untitled Video"}
										</h3>
										{/* Add more video fields as needed */}
									</div>
									<div className="mt-2 space-y-1 text-sm text-muted-foreground">
										<p>
											Status: {video.status || "N/A"}
										</p>
										{video.thumbnail_url && (
											<img
												src={video.thumbnail_url}
												alt="Thumbnail"
												className="mt-2 rounded w-full max-h-40 object-cover"
											/>
										)}
										<div className="mt-3 flex space-x-2">
											<Button variant="outline" size="sm" asChild>
												<Link
													to="/video/$videoId"
													params={{ videoId: video.id }}
												>
													View Details
												</Link>
											</Button>
										</div>
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
	component: () => (
		<ProtectedLayout>
			<DashboardComponent />
		</ProtectedLayout>
	),
});
