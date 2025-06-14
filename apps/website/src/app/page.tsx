'use client'

import { VideoResults } from '@/components/video-results'
import { VideoUploader } from '@/components/video-uploader'
import { Button } from '@echo/ui/button'
import { ArrowRight, Sparkles, Video, Zap } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

export default function Home() {
  const [videoId, setVideoId] = useState<string | null>(null)

  if (videoId) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-6 py-16 max-w-7xl">
          <VideoResults videoId={videoId} onReset={() => setVideoId(null)} />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Video className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="text-xl font-semibold">Echo</span>
            </div>
            <div className="flex items-center space-x-6">
              <Link
                href="/creator"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Creator Tools
              </Link>
              <Link
                href="/pricing"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Pricing
              </Link>
              <Button variant="outline" size="sm">
                Sign in
              </Button>
              <Button size="sm">
                Get started
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="container mx-auto px-6 py-24 max-w-6xl">
          <div className="text-center space-y-8">
            <div className="inline-flex items-center rounded-full px-4 py-2 text-sm bg-secondary/50 text-secondary-foreground border border-border/50">
              <Sparkles className="w-4 h-4 mr-2" />
              AI-Powered YouTube Optimization
            </div>

            <h1 className="text-5xl md:text-7xl font-medium text-foreground tracking-tight leading-none">
              Transform your videos into
              <br />
              <span className="text-muted-foreground">viral content</span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Upload your video and get 10 optimized titles, AI-generated thumbnails, and detailed
              analytics to maximize your YouTube reach.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Button size="lg" className="text-base px-8">
                Upload your first video
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button variant="outline" size="lg" className="text-base">
                Watch demo
              </Button>
            </div>
          </div>
        </div>

        {/* Background gradient */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-background via-background to-secondary/20" />
      </section>

      {/* Features Section */}
      <section className="py-24 bg-secondary/20">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-medium text-foreground mb-4">
              Everything you need to succeed
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our AI analyzes your content and generates data-driven recommendations to boost your
              video performance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-card rounded-xl p-8 border border-border/50">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Smart Titles</h3>
              <p className="text-muted-foreground leading-relaxed">
                Generate 10 engaging, SEO-optimized titles tailored to your content and audience.
              </p>
            </div>

            <div className="bg-card rounded-xl p-8 border border-border/50">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Video className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Thumbnails</h3>
              <p className="text-muted-foreground leading-relaxed">
                Create eye-catching thumbnail backgrounds that drive clicks and engagement.
              </p>
            </div>

            <div className="bg-card rounded-xl p-8 border border-border/50">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Lightning Fast</h3>
              <p className="text-muted-foreground leading-relaxed">
                Get your optimized content in minutes, not hours. Perfect for content creators on
                the go.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section className="py-24">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-medium text-foreground mb-4">
              Ready to optimize your video?
            </h2>
            <p className="text-lg text-muted-foreground">
              Upload your video and see the magic happen in real-time.
            </p>
          </div>

          <VideoUploader onVideoUploaded={setVideoId} />
        </div>
      </section>
    </div>
  )
}
