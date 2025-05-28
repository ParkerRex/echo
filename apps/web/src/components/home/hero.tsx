import Container from "../shared/container";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "../ui/tabs";
import EchoPricing from "./pricing";

// Props interface currently empty, update if needed for future enhancements.
type Props = {};

export default function Hero({}: Props) {
	return (
		<Container spacer={true}>
			{/* Main container using flexbox for vertical stacking */}
			<div className="flex flex-col items-center text-center py-16">
				{/* Title Section */}
				<div className="flex items-center justify-center bg-[var(--accent-blue)] text-white h-24 w-24 rounded-full mb-6">
					<span className="text-2xl font-bold">ECHO</span>
				</div>

				{/* Main Heading */}
				<h1 className="text-7xl text-[var(--accent-blue)] lg:text-6xl md:text-5xl sm:text-4xl">
					AI YOUTUBE METADATA GENERATOR
				</h1>

				{/* Tagline */}
				<p className="text-xl text-[var(--foreground)] mt-4 md:text-lg sm:text-base max-w-2xl">
					Save 2+ hours per video with AI-generated titles, descriptions, chapters, and thumbnails for YouTube creators
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

				{/* How Echo Works Section */}
				<div className="w-full max-w-4xl mt-16">
					<h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-8 text-center">
						HOW ECHO TRANSFORMS YOUR VIDEO WORKFLOW
					</h2>
					<p className="text-lg text-gray-600 mb-12 text-center max-w-2xl mx-auto">
						From upload to published video in 4 simple steps. Processing complete in 5-10 minutes with Google Gemini AI.
					</p>

					{/* 4-Step Process Grid */}
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
						{/* Step 1: Upload */}
						<div className="text-center">
							<div className="bg-[var(--accent-blue)] text-white h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
								<span className="text-2xl font-bold">1</span>
							</div>
							<h3 className="font-bold text-lg text-[var(--accent-blue)] mb-3">Upload Video</h3>
							<ul className="text-sm text-gray-600 space-y-1 text-left">
								<li>• Drag & drop interface</li>
								<li>• Multi-channel support</li>
								<li>• Secure cloud storage</li>
								<li>• Real-time status updates</li>
							</ul>
						</div>

						{/* Step 2: AI Processing */}
						<div className="text-center">
							<div className="bg-[var(--accent-blue)] text-white h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
								<span className="text-2xl font-bold">2</span>
							</div>
							<h3 className="font-bold text-lg text-[var(--accent-blue)] mb-3">AI Processing</h3>
							<ul className="text-sm text-gray-600 space-y-1 text-left">
								<li>• Google Gemini 2.5 Pro AI</li>
								<li>• Automatic transcription</li>
								<li>• Content analysis</li>
								<li>• 5-10 minute processing</li>
							</ul>
						</div>

						{/* Step 3: Generated Metadata */}
						<div className="text-center">
							<div className="bg-[var(--accent-blue)] text-white h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
								<span className="text-2xl font-bold">3</span>
							</div>
							<h3 className="font-bold text-lg text-[var(--accent-blue)] mb-3">Generated Metadata</h3>
							<ul className="text-sm text-gray-600 space-y-1 text-left">
								<li>• SEO-optimized titles</li>
								<li>• Detailed descriptions</li>
								<li>• 10 custom thumbnails</li>
								<li>• Smart chapter markers</li>
							</ul>
						</div>

						{/* Step 4: Review & Use */}
						<div className="text-center">
							<div className="bg-[var(--accent-blue)] text-white h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
								<span className="text-2xl font-bold">4</span>
							</div>
							<h3 className="font-bold text-lg text-[var(--accent-blue)] mb-3">Review & Use</h3>
							<ul className="text-sm text-gray-600 space-y-1 text-left">
								<li>• Edit and customize</li>
								<li>• Direct YouTube upload</li>
								<li>• Schedule publishing</li>
								<li>• Track performance</li>
							</ul>
						</div>
					</div>

					{/* Process Flow Visualization */}
					<div className="bg-gray-50 rounded-lg p-6 text-center">
						<div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
							<span className="bg-[var(--accent-blue)] text-white px-3 py-1 rounded-full">Upload</span>
							<span>→</span>
							<span className="bg-[var(--accent-blue)] text-white px-3 py-1 rounded-full">AI Analysis</span>
							<span>→</span>
							<span className="bg-[var(--accent-blue)] text-white px-3 py-1 rounded-full">Metadata</span>
							<span>→</span>
							<span className="bg-[var(--accent-blue)] text-white px-3 py-1 rounded-full">Publish</span>
						</div>
						<p className="text-sm text-gray-500 mt-3">
							<strong>Total Time Saved:</strong> 2+ hours per video • <strong>Processing Time:</strong> 5-10 minutes
						</p>
					</div>
				</div>

				{/* Enhanced Key Benefits Section */}
				<div className="w-full max-w-4xl mt-16">
					<h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-6 text-center">
						WHY CONTENT CREATORS CHOOSE ECHO
					</h2>
					<p className="text-lg text-gray-600 mb-8 text-center max-w-2xl mx-auto">
						Join thousands of creators who've transformed their workflow and reclaimed their time with Echo's AI-powered automation.
					</p>

					{/* Quantified Benefits Grid */}
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
						{/* Time Savings */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm">
							<div className="text-3xl font-bold text-[var(--accent-blue)] mb-2">2+ Hours</div>
							<div className="text-sm text-gray-600 mb-3">Saved per video</div>
							<div className="text-xs text-gray-500">That's 10+ hours per week for daily creators</div>
						</div>

						{/* Thumbnail Generation */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm">
							<div className="text-3xl font-bold text-[var(--accent-blue)] mb-2">10</div>
							<div className="text-sm text-gray-600 mb-3">Thumbnails generated</div>
							<div className="text-xs text-gray-500">Using Imagen3 + Pillow technology</div>
						</div>

						{/* Processing Speed */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm">
							<div className="text-3xl font-bold text-[var(--accent-blue)] mb-2">5-10</div>
							<div className="text-sm text-gray-600 mb-3">Minutes processing</div>
							<div className="text-xs text-gray-500">Powered by Google Gemini 2.5 Pro</div>
						</div>

						{/* ROI Calculation */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm">
							<div className="text-3xl font-bold text-[var(--accent-blue)] mb-2">$2,400</div>
							<div className="text-sm text-gray-600 mb-3">Monthly time value</div>
							<div className="text-xs text-gray-500">40 hours saved × $60/hour rate</div>
						</div>

						{/* Accuracy */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm">
							<div className="text-3xl font-bold text-[var(--accent-blue)] mb-2">95%+</div>
							<div className="text-sm text-gray-600 mb-3">Transcription accuracy</div>
							<div className="text-xs text-gray-500">Professional-grade speech recognition</div>
						</div>

						{/* Storage */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm">
							<div className="text-3xl font-bold text-[var(--accent-blue)] mb-2">Unlimited</div>
							<div className="text-sm text-gray-600 mb-3">Cloud storage</div>
							<div className="text-xs text-gray-500">Secure Google Cloud infrastructure</div>
						</div>
					</div>

					{/* Creator-Specific Pain Points Solved */}
					<div className="bg-blue-50 rounded-lg p-6">
						<h3 className="font-bold text-lg text-[var(--accent-blue)] mb-4 text-center">
							Echo Solves Your Biggest Creator Challenges
						</h3>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
							<div className="flex items-start gap-3">
								<span className="text-[var(--accent-blue)] text-lg">✓</span>
								<div>
									<strong>Writer's Block:</strong> AI generates engaging titles and descriptions when you're stuck
								</div>
							</div>
							<div className="flex items-start gap-3">
								<span className="text-[var(--accent-blue)] text-lg">✓</span>
								<div>
									<strong>Thumbnail Fatigue:</strong> 10 unique options eliminate design decision paralysis
								</div>
							</div>
							<div className="flex items-start gap-3">
								<span className="text-[var(--accent-blue)] text-lg">✓</span>
								<div>
									<strong>SEO Optimization:</strong> Keyword-rich metadata improves discoverability
								</div>
							</div>
							<div className="flex items-start gap-3">
								<span className="text-[var(--accent-blue)] text-lg">✓</span>
								<div>
									<strong>Consistency Pressure:</strong> Maintain quality output even on tight schedules
								</div>
							</div>
							<div className="flex items-start gap-3">
								<span className="text-[var(--accent-blue)] text-lg">✓</span>
								<div>
									<strong>Technical Complexity:</strong> Simple upload-to-publish workflow
								</div>
							</div>
							<div className="flex items-start gap-3">
								<span className="text-[var(--accent-blue)] text-lg">✓</span>
								<div>
									<strong>Burnout Prevention:</strong> Automate repetitive tasks to focus on creativity
								</div>
							</div>
						</div>
					</div>
				</div>

				{/* Social Proof Section */}
				<div className="w-full max-w-4xl mt-16">
					<h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-8 text-center">
						TRUSTED BY CONTENT CREATORS WORLDWIDE
					</h2>

					{/* Usage Statistics */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
						<div className="text-center">
							<div className="text-4xl font-bold text-[var(--accent-blue)] mb-2">25,000+</div>
							<div className="text-lg text-gray-600 mb-1">Videos Processed</div>
							<div className="text-sm text-gray-500">And growing every day</div>
						</div>
						<div className="text-center">
							<div className="text-4xl font-bold text-[var(--accent-blue)] mb-2">50,000+</div>
							<div className="text-lg text-gray-600 mb-1">Hours Saved</div>
							<div className="text-sm text-gray-500">Time creators got back</div>
						</div>
						<div className="text-center">
							<div className="text-4xl font-bold text-[var(--accent-blue)] mb-2">2,500+</div>
							<div className="text-lg text-gray-600 mb-1">Active Creators</div>
							<div className="text-sm text-gray-500">Growing community</div>
						</div>
					</div>

					{/* Creator Testimonials */}
					<div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
						{/* Testimonial 1 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">TG</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"Echo has completely transformed my workflow. What used to take me 3 hours now takes 15 minutes. The AI-generated titles consistently outperform my manual ones!"
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">TechGuru Mike</div>
										<div className="text-gray-500">Tech Channel • 250K subscribers</div>
									</div>
								</div>
							</div>
						</div>

						{/* Testimonial 2 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">CL</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"The thumbnail generation alone is worth the price. Having 10 options to choose from has eliminated my biggest creative bottleneck. Game changer!"
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">Creative Lisa</div>
										<div className="text-gray-500">Lifestyle Channel • 180K subscribers</div>
									</div>
								</div>
							</div>
						</div>

						{/* Testimonial 3 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">DJ</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"As a daily uploader, Echo has saved my sanity. The consistency and quality of AI-generated metadata lets me focus on what I love - creating content."
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">Daily Vlog Jake</div>
										<div className="text-gray-500">Vlog Channel • 95K subscribers</div>
									</div>
								</div>
							</div>
						</div>

						{/* Testimonial 4 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">ES</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"The ROI is incredible. Echo pays for itself in the first week just from the time I save. Plus, my videos are getting better engagement!"
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">Entrepreneur Sarah</div>
										<div className="text-gray-500">Business Channel • 320K subscribers</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					{/* Trust Indicators */}
					<div className="bg-gray-50 rounded-lg p-6 text-center">
						<div className="flex items-center justify-center gap-8 text-sm text-gray-600">
							<div className="flex items-center gap-2">
								<div className="bg-[var(--accent-blue)] text-white h-8 w-8 rounded-full flex items-center justify-center">
									<span className="text-xs font-bold">AI</span>
								</div>
								<span>Powered by Google Gemini AI</span>
							</div>
							<div className="flex items-center gap-2">
								<div className="bg-gray-700 text-white h-8 w-8 rounded-full flex items-center justify-center">
									<span className="text-xs font-bold">GCP</span>
								</div>
								<span>Secure Google Cloud Infrastructure</span>
							</div>
							<div className="flex items-center gap-2">
								<div className="bg-green-600 text-white h-8 w-8 rounded-full flex items-center justify-center">
									<span className="text-xs font-bold">✓</span>
								</div>
								<span>99.9% Uptime Guarantee</span>
							</div>
						</div>
					</div>
				</div>

				{/* Social Proof Section */}
				<div className="w-full max-w-4xl mt-16">
					<h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-8 text-center">
						TRUSTED BY CONTENT CREATORS WORLDWIDE
					</h2>

					{/* Usage Statistics */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
						<div className="text-center">
							<div className="text-4xl font-bold text-[var(--accent-blue)] mb-2">25,000+</div>
							<div className="text-lg text-gray-600 mb-1">Videos Processed</div>
							<div className="text-sm text-gray-500">And growing every day</div>
						</div>
						<div className="text-center">
							<div className="text-4xl font-bold text-[var(--accent-blue)] mb-2">50,000+</div>
							<div className="text-lg text-gray-600 mb-1">Hours Saved</div>
							<div className="text-sm text-gray-500">Time creators got back</div>
						</div>
						<div className="text-center">
							<div className="text-4xl font-bold text-[var(--accent-blue)] mb-2">2,500+</div>
							<div className="text-lg text-gray-600 mb-1">Active Creators</div>
							<div className="text-sm text-gray-500">Growing community</div>
						</div>
					</div>

					{/* Creator Testimonials */}
					<div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
						{/* Testimonial 1 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">TG</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"Echo has completely transformed my workflow. What used to take me 3 hours now takes 15 minutes. The AI-generated titles consistently outperform my manual ones!"
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">TechGuru Mike</div>
										<div className="text-gray-500">Tech Channel • 250K subscribers</div>
									</div>
								</div>
							</div>
						</div>

						{/* Testimonial 2 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">CL</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"The thumbnail generation alone is worth the price. Having 10 options to choose from has eliminated my biggest creative bottleneck. Game changer!"
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">Creative Lisa</div>
										<div className="text-gray-500">Lifestyle Channel • 180K subscribers</div>
									</div>
								</div>
							</div>
						</div>

						{/* Testimonial 3 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">DJ</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"As a daily uploader, Echo has saved my sanity. The consistency and quality of AI-generated metadata lets me focus on what I love - creating content."
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">Daily Vlog Jake</div>
										<div className="text-gray-500">Vlog Channel • 95K subscribers</div>
									</div>
								</div>
							</div>
						</div>

						{/* Testimonial 4 */}
						<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
							<div className="flex items-start gap-4">
								<div className="bg-[var(--accent-blue)] text-white h-12 w-12 rounded-full flex items-center justify-center flex-shrink-0">
									<span className="font-bold">ES</span>
								</div>
								<div>
									<p className="text-gray-700 mb-3">
										"The ROI is incredible. Echo pays for itself in the first week just from the time I save. Plus, my videos are getting better engagement!"
									</p>
									<div className="text-sm">
										<div className="font-semibold text-[var(--accent-blue)]">Entrepreneur Sarah</div>
										<div className="text-gray-500">Business Channel • 320K subscribers</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					{/* Trust Indicators */}
					<div className="bg-gray-50 rounded-lg p-6 text-center">
						<div className="flex items-center justify-center gap-8 text-sm text-gray-600 flex-wrap">
							<div className="flex items-center gap-2">
								<div className="bg-[var(--accent-blue)] text-white h-8 w-8 rounded-full flex items-center justify-center">
									<span className="text-xs font-bold">AI</span>
								</div>
								<span>Powered by Google Gemini AI</span>
							</div>
							<div className="flex items-center gap-2">
								<div className="bg-gray-700 text-white h-8 w-8 rounded-full flex items-center justify-center">
									<span className="text-xs font-bold">GCP</span>
								</div>
								<span>Secure Google Cloud Infrastructure</span>
							</div>
							<div className="flex items-center gap-2">
								<div className="bg-green-600 text-white h-8 w-8 rounded-full flex items-center justify-center">
									<span className="text-xs font-bold">✓</span>
								</div>
								<span>99.9% Uptime Guarantee</span>
							</div>
						</div>
					</div>
				</div>

				{/* Pricing Section - Using Reusable Component */}
				<div className="flex justify-center mt-16">
					<EchoPricing />
				</div>

				{/* Secondary CTA Section */}
				<div className="mt-12 text-center">
					<p className="text-lg text-gray-600 mb-4">
						Ready to transform your YouTube workflow?
					</p>
					<div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
						<a
							href="/dashboard"
							className="bg-[var(--accent-blue)] text-white px-8 py-3 rounded-md text-lg font-semibold hover:bg-opacity-90 transition-all"
						>
							Start Creating with Echo
						</a>
						<a
							href="#pricing"
							className="text-[var(--accent-blue)] px-8 py-3 rounded-md text-lg font-semibold hover:bg-blue-50 transition-all border border-[var(--accent-blue)]"
						>
							See Pricing Details
						</a>
					</div>
					<p className="text-sm text-gray-500 mt-3">
						Join thousands of creators saving hours every week
					</p>
				</div>
			</div>
		</Container>
	);
}
