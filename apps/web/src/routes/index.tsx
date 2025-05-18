import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { useAuth } from "../hooks/useAuth";
import { GoogleLoginButton } from "@/components/GoogleLoginButton"; // Assuming this is the correct path

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  const { session, user, isLoading } = useAuth();

  return (
    <div className="container mx-auto p-4 sm:p-6 md:p-8 max-w-3xl text-center">
      <header className="mb-12">
        <h1 className="text-4xl sm:text-5xl font-bold mb-4 text-gray-800">
          Welcome to EchoStream
        </h1>
        <p className="text-lg sm:text-xl text-gray-600">
          Transform your raw video content into polished, engaging material with automated transcripts, summaries, chapters, and more. Perfect for creators and businesses looking to maximize their video impact.
        </p>
      </header>

      <section className="mb-12">
        <h2 className="text-2xl sm:text-3xl font-semibold mb-6 text-gray-700">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6 text-left">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2 text-blue-600">1. Upload</h3>
            <p className="text-gray-600">Simply upload your video file. We handle the rest, kicking off our powerful AI processing pipeline.</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2 text-blue-600">2. Process</h3>
            <p className="text-gray-600">Our AI gets to work generating accurate transcripts, insightful summaries, logical chapters, and even potential titles for your content.</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2 text-blue-600">3. Publish</h3>
            <p className="text-gray-600">Review the generated content, make any tweaks, and get ready to share your enhanced video with the world or use the assets in your workflow.</p>
          </div>
        </div>
      </section>

      {isLoading ? (
        <div className="my-8">
          <p className="text-gray-500">Loading authentication status...</p>
          {/* You can add a spinner here if you like */}
        </div>
      ) : session ? (
        <div className="my-8 p-6 bg-green-50 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-3 text-green-700">
            Welcome back, {user?.email || "Creator"}!
          </h2>
          <p className="text-gray-700 mb-4">
            You are logged in. Head to your dashboard to manage your videos.
          </p>
          <Button asChild size="lg">
            <Link to="/dashboard" className="font-semibold">
              Go to Dashboard
            </Link>
          </Button>
        </div>
      ) : (
        <div className="my-8 p-6 bg-blue-50 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-4 text-blue-700">
            Ready to Get Started?
          </h2>
          <p className="text-gray-700 mb-6">
            Sign in with Google to start processing your videos and unlock powerful AI features.
          </p>
          <div className="max-w-xs mx-auto">
            <GoogleLoginButton />
          </div>
        </div>
      )}

      <footer className="mt-16 pt-8 border-t border-gray-200">
        <p className="text-sm text-gray-500">
          &copy; {new Date().getFullYear()} EchoStream. All rights reserved.
        </p>
      </footer>
    </div>
  );
}