import Container from '@/components/shared/container';
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger,
} from '@/components/ui/tabs';

// Props interface currently empty, update if needed for future enhancements.
type Props = {};

export default function Hero({ }: Props) {
    return (
        <Container spacer={true}>
            {/* Main container using flexbox for vertical stacking */}
            <div className="flex flex-col items-center text-center py-16">

                {/* Title Section */}
                <div className="flex items-center justify-center bg-[var(--accent-blue)] text-white h-24 w-24 rounded-full mb-6">
                    <span className="text-2xl font-bold">VIDEO</span>
                </div>

                {/* Main Heading */}
                <h1 className="text-7xl text-[var(--accent-blue)] lg:text-6xl md:text-5xl sm:text-4xl">
                    VIDEO AI PIPELINE
                </h1>

                {/* Tagline */}
                <p className="text-xl text-[var(--foreground)] mt-4 md:text-lg sm:text-base max-w-2xl">
                    Automate your video publishing workflow with AI-powered metadata generation and YouTube integration
                </p>

                {/* Feature Icons as Text */}
                <div className="my-8 flex items-center justify-center gap-8">
                    <div className="flex flex-col items-center">
                        <div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center">
                            <span className="font-bold">AI</span>
                        </div>
                        <span className="text-sm mt-1">Gemini</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <div className="bg-red-600 text-white h-12 w-12 rounded-full flex items-center justify-center">
                            <span className="font-bold">YT</span>
                        </div>
                        <span className="text-sm mt-1">YouTube</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <div className="bg-gray-700 text-white h-12 w-12 rounded-full flex items-center justify-center">
                            <span className="font-bold">GCP</span>
                        </div>
                        <span className="text-sm mt-1">Cloud</span>
                    </div>
                </div>

                {/* Separator */}
                <hr className="my-6 w-1/5 border-[var(--accent-blue)] border-t-2" />

                {/* Feature Tabs Section */}
                <div className="w-full max-w-2xl mt-8">
                    <Tabs defaultValue="upload" className="w-full">
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="upload">Upload</TabsTrigger>
                            <TabsTrigger value="process">Process</TabsTrigger>
                            <TabsTrigger value="metadata">Metadata</TabsTrigger>
                            <TabsTrigger value="publish">Publish</TabsTrigger>
                        </TabsList>
                        <TabsContent value="upload" className="mt-4 text-left space-y-2">
                            <p><strong>Drag & Drop:</strong> Simple video upload interface</p>
                            <p><strong>Multi-Channel:</strong> Support for both daily and main channels</p>
                            <p><strong>Cloud Storage:</strong> Videos stored securely in Google Cloud Storage</p>
                            <p><strong>Real-time:</strong> Live status updates as your video moves through the pipeline</p>
                        </TabsContent>
                        <TabsContent value="process" className="mt-4 text-left space-y-2">
                            <p><strong>Automatic:</strong> Hands-off video processing workflow</p>
                            <p><strong>AI-Powered:</strong> Gemini 2.5 Pro generates high-quality metadata</p>
                            <p><strong>Transcription:</strong> Accurate speech-to-text for your entire video</p>
                            <p><strong>Chapters:</strong> Smart chapter markers generated from video content</p>
                        </TabsContent>
                        <TabsContent value="metadata" className="mt-4 text-left space-y-2">
                            <p><strong>Title Generation:</strong> AI creates engaging, SEO-friendly titles</p>
                            <p><strong>Description:</strong> Comprehensive video descriptions with keywords</p>
                            <p><strong>Thumbnails:</strong> Generate 10 thumbnails with Imagen3 + Pillow</p>
                            <p><strong>Editable:</strong> Review and customize all metadata before publishing</p>
                        </TabsContent>
                        <TabsContent value="publish" className="mt-4 text-left space-y-2">
                            <p><strong>YouTube Integration:</strong> Direct upload to your YouTube channel</p>
                            <p><strong>Scheduling:</strong> Set publication dates and times</p>
                            <p><strong>Status Tracking:</strong> Monitor progress from processing to published</p>
                            <p><strong>Error Handling:</strong> Robust error recovery and notification</p>
                        </TabsContent>
                    </Tabs>
                </div>

                {/* Key Benefits Section */}
                <div className="w-full max-w-2xl mt-16">
                    <h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-6">
                        KEY BENEFITS
                    </h2>
                    <ul className="grid grid-cols-2 gap-4 text-base text-[var(--foreground)]">
                        <li className="flex items-center gap-2">
                            <span className="text-[var(--accent-blue)]">✓</span> Save hours on video publishing
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-[var(--accent-blue)]">✓</span> Consistent, high-quality metadata
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-[var(--accent-blue)]">✓</span> AI-generated thumbnails
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-[var(--accent-blue)]">✓</span> Real-time status tracking
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-[var(--accent-blue)]">✓</span> Full editing control
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-[var(--accent-blue)]">✓</span> Cloud-native architecture
                        </li>
                    </ul>
                </div>

                {/* CTA Button */}
                <div className="mt-12">
                    <a href="/upload" className="bg-[var(--accent-blue)] text-white px-8 py-3 rounded-md text-lg hover:bg-opacity-90 transition-all">
                        Get Started
                    </a>
                </div>
            </div>
        </Container>
    );
}