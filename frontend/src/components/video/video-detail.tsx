import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { ProgressSteps, type Step } from "@/components/ui/progress-steps";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { tryFetchContent } from "@/services/gcs-content";
import { Link } from "@tanstack/react-router";
import {
	ArrowLeft,
	CheckCircle,
	Download,
	ExternalLink,
	Loader2,
	type LucideIcon,
} from "lucide-react";
import { useEffect, useState } from "react";
import { ContentEditor } from "./content-editor";
import { calculateOverallProgress } from "./processing-steps";

type VideoAsset = {
	type: string;
	label: string;
	url: string;
	icon: LucideIcon;
	sizeKB?: number;
};

type VideoDetailProps = {
	videoId: string;
	videoTitle: string;
	videoUrl: string;
	thumbnailUrl?: string;
	processingSteps: Step[];
	currentStepId?: string;
	youtubeUrl?: string;
	status: "processing" | "completed" | "error" | "paused";
	assets?: VideoAsset[];
	className?: string;
	// Content related props
	output_files?: Record<string, string>;
	bucket_name?: string;
	onSaveContent?: (contentType: string, content: string) => Promise<void>;
};

export function VideoDetail({
	videoId,
	videoTitle,
	videoUrl,
	thumbnailUrl,
	processingSteps,
	currentStepId,
	youtubeUrl,
	status,
	assets = [],
	className,
	output_files = {},
	bucket_name,
	onSaveContent,
}: VideoDetailProps) {
	const overallProgress = calculateOverallProgress(processingSteps);
	const isCompleted = status === "completed";

	// State for content
	const [transcript, setTranscript] = useState<string>("");
	const [subtitles, setSubtitles] = useState<string>("");
	const [chapters, setChapters] = useState<string>("");
	const [shownotes, setShownotes] = useState<string>("");

	// Loading states
	const [loadingTranscript, setLoadingTranscript] = useState<boolean>(false);
	const [loadingSubtitles, setLoadingSubtitles] = useState<boolean>(false);
	const [loadingChapters, setLoadingChapters] = useState<boolean>(false);
	const [loadingShownotes, setLoadingShownotes] = useState<boolean>(false);

	// Error states
	const [transcriptError, setTranscriptError] = useState<string | null>(null);
	const [subtitlesError, setSubtitlesError] = useState<string | null>(null);
	const [chaptersError, setChaptersError] = useState<string | null>(null);
	const [shownotesError, setShownotesError] = useState<string | null>(null);

	// Active tab
	const [activeContentTab, setActiveContentTab] =
		useState<string>("transcript");

	// Effect to load content based on active tab
	useEffect(() => {
		if (!bucket_name || status !== "completed") return;

		const fetchContent = async () => {
			// Only fetch content for the active tab to save bandwidth
			switch (activeContentTab) {
				case "transcript":
					if (transcript || loadingTranscript) return;
					setLoadingTranscript(true);
					setTranscriptError(null);
					try {
						const content = await tryFetchContent(
							bucket_name,
							output_files,
							"transcript",
						);
						setTranscript(content || "");
					} catch (error) {
						setTranscriptError(
							error instanceof Error
								? error.message
								: "Failed to load transcript",
						);
					} finally {
						setLoadingTranscript(false);
					}
					break;

				case "subtitles":
					if (subtitles || loadingSubtitles) return;
					setLoadingSubtitles(true);
					setSubtitlesError(null);
					try {
						const content = await tryFetchContent(
							bucket_name,
							output_files,
							"subtitles",
						);
						setSubtitles(content || "");
					} catch (error) {
						setSubtitlesError(
							error instanceof Error
								? error.message
								: "Failed to load subtitles",
						);
					} finally {
						setLoadingSubtitles(false);
					}
					break;

				case "chapters":
					if (chapters || loadingChapters) return;
					setLoadingChapters(true);
					setChaptersError(null);
					try {
						const content = await tryFetchContent(
							bucket_name,
							output_files,
							"chapters",
						);
						setChapters(content || "");
					} catch (error) {
						setChaptersError(
							error instanceof Error
								? error.message
								: "Failed to load chapters",
						);
					} finally {
						setLoadingChapters(false);
					}
					break;

				case "shownotes":
					if (shownotes || loadingShownotes) return;
					setLoadingShownotes(true);
					setShownotesError(null);
					try {
						const content = await tryFetchContent(
							bucket_name,
							output_files,
							"shownotes",
						);
						setShownotes(content || "");
					} catch (error) {
						setShownotesError(
							error instanceof Error
								? error.message
								: "Failed to load shownotes",
						);
					} finally {
						setLoadingShownotes(false);
					}
					break;
			}
		};

		fetchContent();
	}, [
		activeContentTab,
		bucket_name,
		output_files,
		status,
		transcript,
		subtitles,
		chapters,
		shownotes,
		loadingTranscript,
		loadingSubtitles,
		loadingChapters,
		loadingShownotes,
	]);

	// Handle save operations for different content types
	const handleSaveTranscript = async (content: string) => {
		if (!onSaveContent) throw new Error("Save function not provided");
		await onSaveContent("transcript", content);
		setTranscript(content);
	};

	const handleSaveSubtitles = async (content: string) => {
		if (!onSaveContent) throw new Error("Save function not provided");
		await onSaveContent("subtitles", content);
		setSubtitles(content);
	};

	const handleSaveChapters = async (content: string) => {
		if (!onSaveContent) throw new Error("Save function not provided");
		await onSaveContent("chapters", content);
		setChapters(content);
	};

	const handleSaveShownotes = async (content: string) => {
		if (!onSaveContent) throw new Error("Save function not provided");
		await onSaveContent("shownotes", content);
		setShownotes(content);
	};

	return (
		<div className={className}>
			<div className="mb-6">
				<Link
					to="/dashboard"
					className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
				>
					<ArrowLeft className="mr-2 h-4 w-4" />
					Back to dashboard
				</Link>

				<div className="flex items-center justify-between">
					<h1 className="text-2xl font-bold tracking-tight line-clamp-1">
						{videoTitle}
					</h1>
					{youtubeUrl && (
						<Button variant="outline" size="sm" asChild>
							<a href={youtubeUrl} target="_blank" rel="noopener noreferrer">
								<ExternalLink className="mr-2 h-4 w-4" />
								View on YouTube
							</a>
						</Button>
					)}
				</div>

				<div className="text-sm text-muted-foreground mt-1">ID: {videoId}</div>
			</div>

			<div className="grid gap-6 md:grid-cols-2">
				<div className="md:col-span-1 space-y-6">
					{/* Video Preview */}
					<Card>
						<CardHeader className="pb-2">
							<CardTitle className="text-base">Video Preview</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="aspect-video bg-muted rounded-md overflow-hidden">
								{status === "completed" ? (
									<video
										src={videoUrl}
										poster={thumbnailUrl}
										controls
										className="w-full h-full object-cover"
									/>
								) : thumbnailUrl ? (
									<img
										src={thumbnailUrl}
										alt={videoTitle}
										className="w-full h-full object-cover"
									/>
								) : (
									<div className="w-full h-full flex items-center justify-center text-muted-foreground">
										Processing video...
									</div>
								)}
							</div>
						</CardContent>
					</Card>

					{/* Status Card */}
					<Card>
						<CardHeader className="pb-2">
							<div className="flex items-center justify-between">
								<CardTitle className="text-base">Processing Status</CardTitle>
								{isCompleted && (
									<div className="flex items-center text-xs font-medium text-primary">
										<CheckCircle className="mr-1 h-3 w-3" />
										Complete
									</div>
								)}
								{!isCompleted && (
									<div className="text-xs font-medium text-muted-foreground">
										{overallProgress}% complete
									</div>
								)}
							</div>
						</CardHeader>
						<CardContent>
							<ProgressSteps
								steps={processingSteps}
								currentStepId={currentStepId}
							/>
						</CardContent>
					</Card>
				</div>

				<div className="md:col-span-1 space-y-6">
					{/* Generated Content */}
					<Card>
						<CardHeader>
							<CardTitle className="text-base">Generated Content</CardTitle>
							<CardDescription>
								Assets created during video processing
							</CardDescription>
						</CardHeader>
						<CardContent>
							<Tabs
								value={activeContentTab}
								onValueChange={setActiveContentTab}
							>
								<TabsList className="grid grid-cols-4 mb-4">
									<TabsTrigger value="transcript">Transcript</TabsTrigger>
									<TabsTrigger value="subtitles">Subtitles</TabsTrigger>
									<TabsTrigger value="chapters">Chapters</TabsTrigger>
									<TabsTrigger value="shownotes">Shownotes</TabsTrigger>
								</TabsList>

								<TabsContent value="transcript" className="space-y-4">
									{isCompleted ? (
										<ContentEditor
											content={transcript}
											isLoading={loadingTranscript}
											errorMessage={transcriptError || undefined}
											onSave={onSaveContent ? handleSaveTranscript : undefined}
											readOnly={!onSaveContent}
											placeholder="Transcript not available"
											maxHeight="400px"
										/>
									) : (
										<div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
											<p>Transcript not yet generated</p>
											<p className="text-xs mt-1">
												This will be available once processing is complete
											</p>
										</div>
									)}
								</TabsContent>

								<TabsContent value="subtitles" className="space-y-4">
									{isCompleted ? (
										<ContentEditor
											content={subtitles}
											isLoading={loadingSubtitles}
											errorMessage={subtitlesError || undefined}
											onSave={onSaveContent ? handleSaveSubtitles : undefined}
											readOnly={!onSaveContent}
											placeholder="Subtitles not available"
											maxHeight="400px"
										/>
									) : (
										<div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
											<p>Subtitles not yet generated</p>
											<p className="text-xs mt-1">
												This will be available once processing is complete
											</p>
										</div>
									)}
								</TabsContent>

								<TabsContent value="chapters" className="space-y-4">
									{isCompleted ? (
										<ContentEditor
											content={chapters}
											isLoading={loadingChapters}
											errorMessage={chaptersError || undefined}
											onSave={onSaveContent ? handleSaveChapters : undefined}
											readOnly={!onSaveContent}
											placeholder="Chapters not available"
											maxHeight="400px"
										/>
									) : (
										<div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
											<p>Chapters not yet generated</p>
											<p className="text-xs mt-1">
												This will be available once processing is complete
											</p>
										</div>
									)}
								</TabsContent>

								<TabsContent value="shownotes" className="space-y-4">
									{isCompleted ? (
										<ContentEditor
											content={shownotes}
											isLoading={loadingShownotes}
											errorMessage={shownotesError || undefined}
											onSave={onSaveContent ? handleSaveShownotes : undefined}
											readOnly={!onSaveContent}
											placeholder="Show notes not available"
											maxHeight="400px"
										/>
									) : (
										<div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
											<p>Show notes not yet generated</p>
											<p className="text-xs mt-1">
												This will be available once processing is complete
											</p>
										</div>
									)}
								</TabsContent>
							</Tabs>
						</CardContent>
					</Card>

					{/* Download Assets */}
					{isCompleted && assets.length > 0 && (
						<Card>
							<CardHeader className="pb-2">
								<CardTitle className="text-base">Download Assets</CardTitle>
							</CardHeader>
							<CardContent>
								<ul className="divide-y">
									{assets.map((asset, index) => (
										<li key={index} className="py-2 first:pt-0 last:pb-0">
											<div className="flex items-center justify-between">
												<div className="flex items-center">
													<asset.icon className="h-4 w-4 text-muted-foreground mr-2" />
													<span className="text-sm">{asset.label}</span>
													{asset.sizeKB && (
														<span className="text-xs text-muted-foreground ml-2">
															({asset.sizeKB} KB)
														</span>
													)}
												</div>
												<Button variant="ghost" size="sm" asChild>
													<a href={asset.url} download>
														<Download className="h-4 w-4" />
													</a>
												</Button>
											</div>
										</li>
									))}
								</ul>
							</CardContent>
						</Card>
					)}
				</div>
			</div>
		</div>
	);
}
