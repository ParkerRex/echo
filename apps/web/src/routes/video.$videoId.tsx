import { Link, createFileRoute, useParams } from "@tanstack/react-router";
import { AlignLeft, FileText, FileVideo, Image, Loader2 } from "lucide-react";
import React, { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import type { Step } from "../components/ui/progress-steps";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "../components/ui/tabs";
import { Textarea } from "../components/ui/textarea";
import {
	ProcessingStepId,
	createMockProcessingSteps,
} from "../components/video/processing-steps";
import {
	type Thumbnail,
	ThumbnailGallery,
} from "../components/video/thumbnail-gallery";
import {
	type TitleOption,
	TitleSelector,
} from "../components/video/title-selector";
import { VideoDetail } from "../components/video/video-detail";
import { cn } from "../lib/utils";

interface VideoData {
	title: string;
	description: string;
	tags: string;
	scheduledTime: string;
	thumbnails: Thumbnail[];
	titleOptions?: TitleOption[];
	current_stage?: string;
	output_files?: {
		transcript?: string;
		subtitles?: string;
		chapters?: string;
		shownotes?: string;
		title?: string;
		[key: string]: string | undefined;
	};
	bucket_name?: string;
	processed_path?: string;
	youtube_video_id?: string;
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

// Map backend processing stages to frontend processing steps
const stageToStepMap: Record<string, number> = {
	uploaded: 0,
	audio_extraction: 1,
	transcript_generation: 2,
	subtitle_generation: 3,
	shownote_generation: 4,
	chapter_generation: 5,
	title_generation: 6,
	youtube_upload: 7,
	completed: 8,
};

// Helper to determine the current step index based on backend stage
function getCurrentStepIndex(stage?: string): number {
	if (!stage) return 0;
	return stageToStepMap[stage] || 0;
}

function getVideoStatus(
	stage?: string,
): "processing" | "completed" | "error" | "paused" {
	if (!stage) return "processing";
	if (stage === "completed") return "completed";
	if (stage === "error") return "error";
	if (stage === "paused") return "paused";
	return "processing";
}

function VideoDetailComponent() {
	const { videoId } = useParams({ from: "/video/$videoId" });
	const [videoData, setVideoData] = useState<VideoData | null>(null);
	const [loading, setLoading] = useState(true);
	const [form, setForm] = useState<VideoFormData | null>(null);
	const [saving, setSaving] = useState(false);
	const [activeTab, setActiveTab] = useState("overview");
	const [isGeneratingThumbnails, setIsGeneratingThumbnails] = useState(false);

	// Mock title options for demo
	const [titleOptions, setTitleOptions] = useState<TitleOption[]>([]);
	const [thumbnails, setThumbnails] = useState<Thumbnail[]>([]);

	useEffect(() => {
		if (!videoId) return;
		setLoading(true);
		// const docRef = doc(db, "videos", videoId);
		// const unsubscribe = onSnapshot(
		// 	docRef,
		// 	(docSnap: DocumentSnapshot<DocumentData>) => {
		// 		if (docSnap.exists()) {
		// 			const data = docSnap.data() as VideoData;
		// 			setVideoData(data);
		// 			setForm(data);
		//
		// 			// Generate mock title options if not present
		// 			if (!data.titleOptions || data.titleOptions.length === 0) {
		// 				const mockTitles = generateMockTitles(data.title || "Video Title");
		// 				setTitleOptions(mockTitles);
		// 			} else {
		// 				setTitleOptions(data.titleOptions);
		// 			}
		//
		// 			// Format thumbnails for our component
		// 			if (data.thumbnails && data.thumbnails.length > 0) {
		// 				const formattedThumbnails = data.thumbnails.map((thumb, index) => ({
		// 					id: `thumb-${index}`,
		// 					url: thumb.url,
		// 					prompt: thumb.prompt,
		// 					status: thumb.status as "ready" | "generating" | "failed",
		// 					isSelected: index === 0, // Default first one selected
		// 				}));
		//
		// 				// If we don't have at least 4, add placeholders
		// 				while (formattedThumbnails.length < 4) {
		// 					formattedThumbnails.push({
		// 						id: `thumb-placeholder-${formattedThumbnails.length}`,
		// 						url: `https://picsum.photos/id/${formattedThumbnails.length + 10}/640/360`,
		// 						prompt: "Example thumbnail prompt with style settings",
		// 						status: "ready",
		// 						isSelected: false,
		// 					});
		// 				}
		//
		// 				setThumbnails(formattedThumbnails);
		// 			} else {
		// 				// Create 4 mock thumbnails
		// 				const mockThumbnails = [
		// 					{
		// 						id: "thumb-1",
		// 						url: "https://picsum.photos/id/10/640/360",
		// 						prompt:
		// 							"Professional headshot with blurred background, high contrast",
		// 						status: "ready" as const,
		// 						isSelected: true,
		// 					},
		// 					{
		// 						id: "thumb-2",
		// 						url: "https://picsum.photos/id/11/640/360",
		// 						prompt: "Product featured prominently with clean background",
		// 						status: "ready" as const,
		// 					},
		// 					{
		// 						id: "thumb-3",
		// 						url: "https://picsum.photos/id/12/640/360",
		// 						prompt:
		// 							"Action shot with dynamic composition and vibrant colors",
		// 						status: "ready" as const,
		// 					},
		// 					{
		// 						id: "thumb-4",
		// 						url: "https://picsum.photos/id/13/640/360",
		// 						prompt:
		// 							"Infographic style with text overlay and minimal design",
		// 						status: "ready" as const,
		// 					},
		// 				];
		// 				setThumbnails(mockThumbnails);
		// 			}
		// 		} else {
		// 			setVideoData(null);
		// 			setForm(null);
		// 		}
		// 		setLoading(false);
		// 	},
		// 	(error) => {
		// 		console.error("Error fetching video data:", error);
		// 		setVideoData(null);
		// 		setForm(null);
		// 		setLoading(false);
		// 	},
		// );
		// return () => unsubscribe();
		// NOTE: The above Firebase listener logic needs to be replaced
		// with a TanStack Query hook using api.getVideoDetails(videoId)
		// For now, we'll leave it to expose the missing data load.
		// Actual data loading logic using api.getVideoDetails should be implemented
		// as part of the VideoDetail component or a TanStack Query hook.
		setLoading(false); // Placeholder
	}, [videoId]);

	const handleSave = async (updates: Partial<VideoData>) => {
		setSaving(true);
		// const docRef = doc(db, "videos", videoId);
		try {
			// await updateDoc(docRef, updates);
			// NOTE: This needs to be replaced with a call to api.updateVideoMetadata(videoId, updates)
			// For now, logging the intent.
			console.log("Attempting to save updates (Firebase logic removed):", updates);
		} catch (error) {
			console.error("Error updating video data:", error);
		} finally {
			setSaving(false);
		}
	};

	// Mock title generation
	const generateMockTitles = (baseTitle: string): TitleOption[] => {
		const titles = [
			{
				id: "title-1",
				text: baseTitle,
				votes: 2,
				isSelected: true,
			},
			{
				id: "title-2",
				text: `How to ${baseTitle} in 5 Simple Steps`,
				votes: 1,
			},
			{
				id: "title-3",
				text: `The Ultimate Guide to ${baseTitle}`,
				votes: 3,
			},
			{
				id: "title-4",
				text: `${baseTitle}: Expert Tips and Tricks`,
				votes: 0,
			},
			{
				id: "title-5",
				text: `Why ${baseTitle} Is Changing Everything`,
				votes: 1,
			},
		];

		return titles;
	};

	// Title selector handlers
	const handleTitleSelect = (titleId: string) => {
		setTitleOptions((prev) =>
			prev.map((title) => ({
				...title,
				isSelected: title.id === titleId,
			})),
		);
	};

	const handleTitleEdit = (titleId: string, newText: string) => {
		setTitleOptions((prev) =>
			prev.map((title) =>
				title.id === titleId ? { ...title, text: newText } : title,
			),
		);
	};

	const handleTitleVote = (titleId: string) => {
		setTitleOptions((prev) =>
			prev.map((title) =>
				title.id === titleId
					? { ...title, votes: (title.votes || 0) + 1 }
					: title,
			),
		);
	};

	const handleGenerateMoreTitles = () => {
		setSaving(true);
		// Simulate API call delay
		setTimeout(() => {
			const currentTitle = videoData?.title || "Video Title";
			const newTitles = [
				{
					id: `title-${titleOptions.length + 1}`,
					text: `NEW: ${currentTitle} For Beginners`,
					votes: 0,
				},
				{
					id: `title-${titleOptions.length + 2}`,
					text: `NEW: Top 10 ${currentTitle} Strategies`,
					votes: 0,
				},
				{
					id: `title-${titleOptions.length + 3}`,
					text: `NEW: ${currentTitle} That Actually Work`,
					votes: 0,
				},
			];

			setTitleOptions((prev) => [...prev, ...newTitles]);
			setSaving(false);
		}, 1500);
	};

	const handleApplyTitle = async (titleId: string) => {
		const selectedTitle = titleOptions.find((title) => title.id === titleId);
		if (!selectedTitle) return;

		await handleSave({
			title: selectedTitle.text,
			titleOptions: titleOptions,
		});
	};

	// Thumbnail handlers
	const handleThumbnailSelect = (thumbnailId: string) => {
		setThumbnails((prev) =>
			prev.map((thumb) => ({
				...thumb,
				isSelected: thumb.id === thumbnailId,
			})),
		);
	};

	const handleRegenerateAllThumbnails = () => {
		setIsGeneratingThumbnails(true);

		// Mark all thumbnails as generating
		setThumbnails((prev) =>
			prev.map((thumb) => ({
				...thumb,
				status: "generating",
			})),
		);

		// Simulate API call delay
		setTimeout(() => {
			// Replace with new thumbnails
			const newThumbnails = thumbnails.map((thumb, index) => ({
				...thumb,
				url: `https://picsum.photos/id/${20 + index}/640/360?random=${Date.now()}`,
				status: "ready" as const,
			}));

			setThumbnails(newThumbnails);
			setIsGeneratingThumbnails(false);
		}, 3000);
	};

	const handleRegenerateSingleThumbnail = (
		thumbnailId: string,
		newPrompt: string,
	) => {
		// Mark this thumbnail as generating
		setThumbnails((prev) =>
			prev.map((thumb) =>
				thumb.id === thumbnailId
					? { ...thumb, status: "generating", prompt: newPrompt }
					: thumb,
			),
		);

		// Simulate API call delay
		setTimeout(() => {
			// Replace with new thumbnail
			setThumbnails((prev) =>
				prev.map((thumb) =>
					thumb.id === thumbnailId
						? {
								...thumb,
								url: `https://picsum.photos/id/${30}/640/360?random=${Date.now()}`,
								status: "ready",
							}
						: thumb,
				),
			);
		}, 2000);
	};

	const handleApplyThumbnail = async (thumbnailId: string) => {
		const selectedThumb = thumbnails.find((thumb) => thumb.id === thumbnailId);
		if (!selectedThumb) return;

		// In a real implementation, this would update the backend
		// For demo, we'll just update our local state
		console.log("Applied thumbnail:", selectedThumb);
	};

	const handleCustomThumbnailUpload = (file: File) => {
		// In a real implementation, this would upload the file
		// For demo, we'll just log it
		console.log("Uploaded custom thumbnail:", file);
	};

	if (loading) {
		return (
			<div className="container py-10">
				<div className="flex justify-center py-20">
					<div className="animate-pulse flex items-center">
						<Loader2 className="h-5 w-5 animate-spin mr-2" />
						Loading video details...
					</div>
				</div>
			</div>
		);
	}

	if (!videoData) {
		return (
			<div className="container py-10">
				<div className="flex flex-col items-center justify-center py-20 text-center">
					<p className="text-muted-foreground mb-4">Video not found</p>
					<Link to="/dashboard" className="text-primary hover:underline">
						Back to dashboard
					</Link>
				</div>
			</div>
		);
	}

	// Prepare data for the VideoDetail component
	const processingSteps: Step[] = createMockProcessingSteps(
		getCurrentStepIndex(videoData.current_stage),
	);

	// Generate video assets for download with real URLs if available
	const videoAssets = [
		{
			type: "transcript",
			label: "Transcript (TXT)",
			url: videoData.output_files?.transcript
				? `https://storage.googleapis.com/${videoData.bucket_name}/${videoData.output_files.transcript}`
				: "#",
			icon: FileText,
			sizeKB: 120,
		},
		{
			type: "subtitles",
			label: "Subtitles (VTT)",
			url: videoData.output_files?.subtitles
				? `https://storage.googleapis.com/${videoData.bucket_name}/${videoData.output_files.subtitles}`
				: "#",
			icon: AlignLeft,
			sizeKB: 45,
		},
		{
			type: "video",
			label: "Original Video (MP4)",
			url: "#", // The full video URL would require a signed URL for larger files
			icon: FileVideo,
			sizeKB: 24500,
		},
		{
			type: "thumbnail",
			label: "Thumbnail (JPG)",
			url: videoData.thumbnails?.[0]?.url || "#",
			icon: Image,
			sizeKB: 320,
		},
	];

	// Use the first thumbnail as preview if available
	const thumbnailUrl =
		videoData.thumbnails?.[0]?.url || thumbnails.find((t) => t.isSelected)?.url;

	// Get the current step ID
	const currentStepIndex = getCurrentStepIndex(videoData.current_stage);
	const stepIds = Object.values(ProcessingStepId);
	const currentStepId = stepIds[currentStepIndex];

	return (
		<div className="container py-10">
			<div className="mb-8">
				<Link
					to="/dashboard"
					className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
				>
					← Back to dashboard
				</Link>
				<h1 className="text-2xl font-bold tracking-tight mt-4">
					{videoData.title || "Untitled Video"}
				</h1>
				<div className="flex items-center text-sm text-muted-foreground mt-1">
					<span className="text-primary">#{videoId.slice(0, 6)}</span>
					{videoData.current_stage && (
						<>
							<span className="mx-2">•</span>
							<span className="capitalize">
								{videoData.current_stage.replace("_", " ")}
							</span>
						</>
					)}
				</div>
			</div>

			<Tabs
				value={activeTab}
				onValueChange={setActiveTab}
				className="space-y-4"
			>
				<TabsList className="w-full max-w-md">
					<TabsTrigger value="overview" className="flex-1">
						Overview
					</TabsTrigger>
					<TabsTrigger value="title" className="flex-1">
						Title
					</TabsTrigger>
					<TabsTrigger value="thumbnail" className="flex-1">
						Thumbnail
					</TabsTrigger>
					<TabsTrigger value="metadata" className="flex-1">
						Metadata
					</TabsTrigger>
				</TabsList>

				<TabsContent value="overview" className="animate-in space-y-6">
					<VideoDetail
						videoId={videoId}
						videoTitle={videoData.title || "Untitled Video"}
						videoUrl="#" // Mock video URL for demo
						thumbnailUrl={thumbnailUrl}
						processingSteps={processingSteps}
						currentStepId={currentStepId}
						youtubeUrl={videoData.youtube_url}
						status={getVideoStatus(videoData.current_stage)}
						assets={videoAssets}
						output_files={videoData.output_files}
						bucket_name={videoData.bucket_name}
						onSaveContent={async (contentType, content) => {
							// In a real implementation, this would send to the backend API
							console.log(
								`Saving ${contentType} content:`,
								`${content.substring(0, 100)}...`,
							);
							// For demo, we'll just simulate a delay
							setSaving(true);
							await new Promise((resolve) => setTimeout(resolve, 1000));
							setSaving(false);
							// In a real implementation, you would update the output_files in Firestore
							return;
						}}
					/>
				</TabsContent>

				<TabsContent value="title" className="animate-in">
					<TitleSelector
						videoId={videoId}
						titleOptions={titleOptions}
						onSelect={handleTitleSelect}
						onEdit={handleTitleEdit}
						onVote={handleTitleVote}
						onGenerateMore={handleGenerateMoreTitles}
						onApply={handleApplyTitle}
					/>
				</TabsContent>

				<TabsContent value="thumbnail" className="animate-in">
					<ThumbnailGallery
						videoId={videoId}
						thumbnails={thumbnails}
						onSelect={handleThumbnailSelect}
						onRegenerateAll={handleRegenerateAllThumbnails}
						onRegenerateSingle={handleRegenerateSingleThumbnail}
						onApply={handleApplyThumbnail}
						onCustomUpload={handleCustomThumbnailUpload}
						isGenerating={isGeneratingThumbnails}
					/>
				</TabsContent>

				<TabsContent value="metadata" className="animate-in space-y-6">
					<Card>
						<CardHeader>
							<CardTitle>Video Metadata</CardTitle>
							<CardDescription>
								Edit details and metadata for your video
							</CardDescription>
						</CardHeader>
						<CardContent>
							<form className="space-y-6">
								<div className="space-y-2">
									<Label htmlFor="title">Title</Label>
									<Input
										id="title"
										value={form?.title || ""}
										onChange={(e) =>
											setForm((prev) => ({ ...prev!, title: e.target.value }))
										}
									/>
								</div>

								<div className="space-y-2">
									<Label htmlFor="description">Description</Label>
									<Textarea
										id="description"
										value={form?.description || ""}
										onChange={(e) =>
											setForm((prev) => ({
												...prev!,
												description: e.target.value,
											}))
										}
										className="min-h-[150px]"
									/>
								</div>

								<div className="space-y-2">
									<Label htmlFor="tags">Tags (comma separated)</Label>
									<Input
										id="tags"
										value={form?.tags || ""}
										onChange={(e) =>
											setForm((prev) => ({ ...prev!, tags: e.target.value }))
										}
									/>
								</div>

								<div className="space-y-2">
									<Label htmlFor="scheduledTime">Scheduled Publish Time</Label>
									<Input
										id="scheduledTime"
										type="datetime-local"
										value={form?.scheduledTime || ""}
										onChange={(e) =>
											setForm((prev) => ({
												...prev!,
												scheduledTime: e.target.value,
											}))
										}
									/>
								</div>

								<Button
									className="w-full"
									onClick={(e) => {
										e.preventDefault();
										if (!form) return;
										handleSave({
											title: form.title,
											description: form.description,
											tags: form.tags,
											scheduledTime: form.scheduledTime,
										});
									}}
									disabled={saving}
								>
									{saving ? (
										<>
											<Loader2 className="mr-2 h-4 w-4 animate-spin" />
											Saving...
										</>
									) : (
										"Save Changes"
									)}
								</Button>
							</form>
						</CardContent>
					</Card>

					<Card>
						<CardHeader>
							<CardTitle>Raw Data</CardTitle>
							<CardDescription>
								Debug information for developers
							</CardDescription>
						</CardHeader>
						<CardContent>
							<pre className="overflow-auto text-xs bg-muted p-4 rounded-md max-h-[300px]">
								{JSON.stringify(videoData, null, 2)}
							</pre>
						</CardContent>
					</Card>
				</TabsContent>
			</Tabs>
		</div>
	);
}

export const Route = createFileRoute("/video/$videoId")({
	component: VideoDetailComponent,
});
