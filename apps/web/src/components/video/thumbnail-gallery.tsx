import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
	Check,
	Edit2,
	Image,
	Loader2,
	RefreshCw,
	Sparkles,
} from "lucide-react";
import { useState } from "react";

export type Thumbnail = {
	id: string;
	url: string;
	prompt: string;
	isSelected?: boolean;
	status: "ready" | "generating" | "failed";
	error?: string;
};

type ThumbnailGalleryProps = {
	videoId: string;
	thumbnails: Thumbnail[];
	onSelect: (thumbnailId: string) => void;
	onRegenerateAll: () => void;
	onRegenerateSingle: (thumbnailId: string, newPrompt: string) => void;
	onApply: (thumbnailId: string) => void;
	onCustomUpload?: (file: File) => void;
	className?: string;
	isGenerating?: boolean;
};

export function ThumbnailGallery({
	videoId,
	thumbnails,
	onSelect,
	onRegenerateAll,
	onRegenerateSingle,
	onApply,
	onCustomUpload,
	className,
	isGenerating = false,
}: ThumbnailGalleryProps) {
	const [editingThumbnailId, setEditingThumbnailId] = useState<string | null>(
		null,
	);
	const [editPrompt, setEditPrompt] = useState("");
	const [customUploadFile, setCustomUploadFile] = useState<File | null>(null);

	const selectedThumbnail = thumbnails.find((thumb) => thumb.isSelected);

	const handleEditStart = (thumbnail: Thumbnail) => {
		setEditingThumbnailId(thumbnail.id);
		setEditPrompt(thumbnail.prompt);
	};

	const handleEditSave = (thumbnailId: string) => {
		if (editPrompt.trim()) {
			onRegenerateSingle(thumbnailId, editPrompt.trim());
			setEditingThumbnailId(null);
		}
	};

	const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		if (e.target.files && e.target.files.length > 0) {
			setCustomUploadFile(e.target.files[0]);
		}
	};

	const handleCustomUpload = () => {
		if (customUploadFile && onCustomUpload) {
			onCustomUpload(customUploadFile);
			setCustomUploadFile(null);
		}
	};

	return (
		<Card className={className}>
			<CardHeader>
				<CardTitle className="flex justify-between items-center">
					<span>Thumbnail Options</span>
					<Button
						size="sm"
						variant="outline"
						onClick={onRegenerateAll}
						disabled={isGenerating}
						className="gap-1"
					>
						{isGenerating ? (
							<>
								<Loader2 className="h-3.5 w-3.5 animate-spin" />
								Generating...
							</>
						) : (
							<>
								<Sparkles className="h-3.5 w-3.5" />
								Generate New Set
							</>
						)}
					</Button>
				</CardTitle>
				<CardDescription>
					Select or customize the thumbnail for your video
				</CardDescription>
			</CardHeader>

			<CardContent>
				<Tabs defaultValue="gallery">
					<TabsList className="grid w-full grid-cols-2 mb-4">
						<TabsTrigger value="gallery">AI Generated</TabsTrigger>
						<TabsTrigger value="custom">Custom Upload</TabsTrigger>
					</TabsList>

					<TabsContent value="gallery" className="space-y-4">
						{/* Selected Thumbnail Preview */}
						{selectedThumbnail && (
							<div className="space-y-2">
								<Label className="text-xs text-muted-foreground">
									Selected Thumbnail
								</Label>
								<div className="aspect-video bg-muted rounded-md overflow-hidden relative">
									<img
										src={selectedThumbnail.url}
										alt="Selected thumbnail"
										className="w-full h-full object-cover"
									/>
									<div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
										<Button
											variant="secondary"
											size="sm"
											onClick={() => handleEditStart(selectedThumbnail)}
										>
											Edit Prompt
										</Button>
									</div>
								</div>
							</div>
						)}

						{/* Thumbnail Grid */}
						<div className="grid grid-cols-2 gap-3">
							{thumbnails.map((thumbnail) => (
								<div
									key={thumbnail.id}
									className={cn(
										"relative group rounded-md overflow-hidden border-2 aspect-video",
										thumbnail.isSelected
											? "border-primary"
											: "border-transparent",
									)}
								>
									{/* Thumbnail Image */}
									{thumbnail.status === "generating" ? (
										<div className="w-full h-full bg-muted flex items-center justify-center">
											<Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
										</div>
									) : thumbnail.status === "failed" ? (
										<div className="w-full h-full bg-destructive/10 flex flex-col items-center justify-center p-2">
											<span className="text-xs text-destructive font-medium">
												Generation Failed
											</span>
											{thumbnail.error && (
												<span className="text-[10px] text-muted-foreground text-center mt-1">
													{thumbnail.error}
												</span>
											)}
										</div>
									) : (
										<img
											src={thumbnail.url}
											alt={`Thumbnail option ${thumbnail.id}`}
											className="w-full h-full object-cover"
										/>
									)}

									{/* Overlay with Actions */}
									{thumbnail.status === "ready" && (
										<div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2">
											<div className="flex gap-1">
												<Button
													size="sm"
													variant="secondary"
													className="h-8"
													onClick={() => handleEditStart(thumbnail)}
												>
													<Edit2 className="h-3.5 w-3.5 mr-1" />
													Edit
												</Button>
												<Button
													size="sm"
													variant={thumbnail.isSelected ? "default" : "outline"}
													className="h-8"
													onClick={() => onSelect(thumbnail.id)}
												>
													<Check className="h-3.5 w-3.5 mr-1" />
													{thumbnail.isSelected ? "Selected" : "Select"}
												</Button>
											</div>
											<p className="text-[10px] text-white/70 px-2 text-center line-clamp-2 mt-1">
												{thumbnail.prompt}
											</p>
										</div>
									)}
								</div>
							))}
						</div>

						{/* Edit Prompt Dialog */}
						{editingThumbnailId && (
							<div className="mt-4 border rounded-md p-3 space-y-3">
								<Label htmlFor="thumbnail-prompt">Edit Thumbnail Prompt</Label>
								<Textarea
									id="thumbnail-prompt"
									value={editPrompt}
									onChange={(e) => setEditPrompt(e.target.value)}
									placeholder="Describe what you want in this thumbnail..."
									className="resize-none min-h-[100px]"
								/>
								<div className="flex justify-end gap-2">
									<Button
										variant="outline"
										size="sm"
										onClick={() => setEditingThumbnailId(null)}
									>
										Cancel
									</Button>
									<Button
										size="sm"
										onClick={() => handleEditSave(editingThumbnailId)}
										disabled={!editPrompt.trim()}
									>
										Regenerate
									</Button>
								</div>
							</div>
						)}
					</TabsContent>

					<TabsContent value="custom" className="space-y-4">
						<div className="border-2 border-dashed rounded-md p-4 text-center">
							<div className="flex flex-col items-center justify-center gap-2">
								<Image className="h-8 w-8 text-muted-foreground" />
								<div className="space-y-1">
									<p className="text-sm font-medium">Upload Custom Thumbnail</p>
									<p className="text-xs text-muted-foreground">
										PNG, JPG, or WEBP up to 2MB
									</p>
								</div>

								<Input
									type="file"
									accept="image/png,image/jpeg,image/webp"
									className="max-w-xs mt-2"
									onChange={handleFileChange}
								/>

								{customUploadFile && (
									<div className="mt-2 w-full max-w-xs">
										<p className="text-xs text-muted-foreground truncate">
											{customUploadFile.name} (
											{Math.round(customUploadFile.size / 1024)} KB)
										</p>
										<Button
											className="w-full mt-2"
											size="sm"
											onClick={handleCustomUpload}
										>
											Upload & Use This Thumbnail
										</Button>
									</div>
								)}
							</div>
						</div>

						<div className="text-xs text-muted-foreground">
							<p>Image requirements:</p>
							<ul className="list-disc pl-5 space-y-1 mt-1">
								<li>1280x720 pixels (16:9 aspect ratio)</li>
								<li>Less than 2MB in size</li>
								<li>PNG, JPG, or WEBP format</li>
								<li>High-contrast images work best</li>
							</ul>
						</div>
					</TabsContent>
				</Tabs>
			</CardContent>

			<CardFooter>
				<Button
					className="w-full"
					disabled={!selectedThumbnail}
					onClick={() => selectedThumbnail && onApply(selectedThumbnail.id)}
				>
					Apply Selected Thumbnail
				</Button>
			</CardFooter>
		</Card>
	);
}
