import { cn } from "src/lib/utils";

// Props interface for the pricing component
type PricingProps = {
	className?: string;
	showHeader?: boolean;
	headerText?: string;
	ctaPrimary?: string;
	ctaSecondary?: string;
	showFeatures?: boolean;
	compact?: boolean;
};

export default function EchoPricing({
	className,
	showHeader = true,
	headerText = "SIMPLE PRICING FOR UNLIMITED CREATIVITY",
	ctaPrimary = "Try Echo Free - Save Hours Today",
	ctaSecondary = "No credit card required • Cancel anytime • Start saving time in minutes",
	showFeatures = true,
	compact = false,
}: PricingProps) {
	return (
		<div className={cn("w-full", compact ? "max-w-lg" : "max-w-2xl", className)}>
			{showHeader && (
				<h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-6 text-center">
					{headerText}
				</h2>
			)}
			
			<div className="bg-white border-2 border-[var(--accent-blue)] rounded-lg p-8 shadow-lg">
				<div className="text-center">
					<h3 className="text-2xl font-bold text-[var(--accent-blue)] mb-2">
						Echo Pro
					</h3>
					<div className="text-5xl font-bold text-[var(--foreground)] mb-4">
						$99<span className="text-xl text-gray-500">/month</span>
					</div>
					<p className="text-lg text-gray-600 mb-6">
						Everything you need to automate your YouTube workflow
					</p>
					
					{showFeatures && (
						<ul className="text-left space-y-3 mb-8">
							<li className="flex items-center gap-3">
								<span className="text-[var(--accent-blue)] text-xl">✓</span>
								<span>Unlimited video processing</span>
							</li>
							<li className="flex items-center gap-3">
								<span className="text-[var(--accent-blue)] text-xl">✓</span>
								<span>AI metadata generation with Google Gemini</span>
							</li>
							<li className="flex items-center gap-3">
								<span className="text-[var(--accent-blue)] text-xl">✓</span>
								<span>10 AI-generated thumbnails per video</span>
							</li>
							<li className="flex items-center gap-3">
								<span className="text-[var(--accent-blue)] text-xl">✓</span>
								<span>Cloud storage for all your videos</span>
							</li>
							<li className="flex items-center gap-3">
								<span className="text-[var(--accent-blue)] text-xl">✓</span>
								<span>Priority processing & support</span>
							</li>
							<li className="flex items-center gap-3">
								<span className="text-[var(--accent-blue)] text-xl">✓</span>
								<span>Save 10+ hours per week</span>
							</li>
						</ul>
					)}
					
					<div className="text-center">
						<a
							href="/dashboard"
							className="bg-[var(--accent-blue)] text-white px-8 py-4 rounded-md text-lg font-semibold hover:bg-opacity-90 transition-all inline-block mb-3"
						>
							{ctaPrimary}
						</a>
						{ctaSecondary && (
							<p className="text-sm text-gray-500">
								{ctaSecondary}
							</p>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}

// Alternative pricing component with multiple plans (for future use)
export function EchoPricingComparison() {
	return (
		<div className="w-full max-w-4xl">
			<h2 className="font-bold text-3xl text-[var(--accent-blue)] md:text-2xl sm:text-xl mb-8 text-center">
				CHOOSE YOUR ECHO PLAN
			</h2>
			
			<div className="grid grid-cols-1 md:grid-cols-2 gap-8">
				{/* Free Trial */}
				<div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
					<div className="text-center">
						<h3 className="text-xl font-bold text-gray-700 mb-2">
							Echo Free Trial
						</h3>
						<div className="text-3xl font-bold text-gray-700 mb-4">
							$0<span className="text-lg text-gray-500">/7 days</span>
						</div>
						<p className="text-gray-600 mb-6">
							Try Echo risk-free for 7 days
						</p>
						<ul className="text-left space-y-2 mb-6 text-sm">
							<li className="flex items-center gap-2">
								<span className="text-green-500">✓</span>
								<span>Process up to 3 videos</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-green-500">✓</span>
								<span>Full AI metadata generation</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-green-500">✓</span>
								<span>10 thumbnails per video</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-green-500">✓</span>
								<span>No credit card required</span>
							</li>
						</ul>
						<a
							href="/dashboard"
							className="bg-gray-600 text-white px-6 py-3 rounded-md font-semibold hover:bg-gray-700 transition-all inline-block"
						>
							Start Free Trial
						</a>
					</div>
				</div>

				{/* Echo Pro */}
				<div className="bg-white border-2 border-[var(--accent-blue)] rounded-lg p-6 shadow-lg relative">
					<div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
						<span className="bg-[var(--accent-blue)] text-white px-4 py-1 rounded-full text-sm font-semibold">
							MOST POPULAR
						</span>
					</div>
					<div className="text-center">
						<h3 className="text-xl font-bold text-[var(--accent-blue)] mb-2">
							Echo Pro
						</h3>
						<div className="text-3xl font-bold text-[var(--accent-blue)] mb-4">
							$99<span className="text-lg text-gray-500">/month</span>
						</div>
						<p className="text-gray-600 mb-6">
							Unlimited video processing for creators
						</p>
						<ul className="text-left space-y-2 mb-6 text-sm">
							<li className="flex items-center gap-2">
								<span className="text-[var(--accent-blue)]">✓</span>
								<span>Unlimited video processing</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-[var(--accent-blue)]">✓</span>
								<span>Google Gemini AI metadata</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-[var(--accent-blue)]">✓</span>
								<span>10 thumbnails per video</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-[var(--accent-blue)]">✓</span>
								<span>Priority processing</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-[var(--accent-blue)]">✓</span>
								<span>Cloud storage included</span>
							</li>
							<li className="flex items-center gap-2">
								<span className="text-[var(--accent-blue)]">✓</span>
								<span>Premium support</span>
							</li>
						</ul>
						<a
							href="/dashboard"
							className="bg-[var(--accent-blue)] text-white px-6 py-3 rounded-md font-semibold hover:bg-opacity-90 transition-all inline-block"
						>
							Get Echo Pro
						</a>
					</div>
				</div>
			</div>
		</div>
	);
}
