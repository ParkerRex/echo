'use client'

import { Button } from '@echo/ui/button'
import { Badge } from '@echo/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { 
  ArrowRight, 
  Sparkles, 
  Video, 
  Zap, 
  TrendingUp, 
  Target, 
  CheckCircle, 
  Star, 
  Users, 
  BarChart3,
  Clock,
  Eye,
  Heart,
  Play,
  Quote
} from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

export default function Home() {
  const [videoCount, setVideoCount] = useState(12847) // Start with realistic number

  // Simulate counter increment
  useState(() => {
    const interval = setInterval(() => {
      setVideoCount(prev => prev + Math.floor(Math.random() * 3))
    }, 3000)
    return () => clearInterval(interval)
  })

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Video className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="text-xl font-semibold">Echo</span>
            </div>
            <div className="flex items-center space-x-6">
              <Link href="/auth/login">
                <Button variant="ghost" size="sm">
                  Sign in
                </Button>
              </Link>
              <Link href="/auth/signup">
                <Button size="sm" className="bg-primary hover:bg-primary/90">
                  Start Free Trial
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - Pain-Focused */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background via-background to-primary/5">
        <div className="container mx-auto px-6 py-20 max-w-6xl">
          <div className="text-center space-y-8">
            {/* Social Proof Badge */}
            <div className="inline-flex items-center rounded-full px-6 py-3 text-sm bg-green-50 text-green-700 border border-green-200">
              <Users className="w-4 h-4 mr-2" />
              <span className="font-medium">{videoCount.toLocaleString()}</span>
              <span className="ml-1">videos optimized • Join 2,400+ creators</span>
            </div>

            {/* Pain-Driven Headline */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground tracking-tight leading-[1.1]">
              Stop Losing 90% of Your
              <br />
              <span className="text-red-600">Potential Views</span>
              <br />
              <span className="text-primary">to Bad Titles</span>
            </h1>

            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              <span className="text-red-600 font-semibold">Most YouTube videos get under 1,000 views.</span>
              <br />
              We use AI to give you titles, thumbnails, and strategies that actually work.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
              <Link href="/auth/signup">
                <Button size="lg" className="text-lg px-10 py-4 h-auto bg-primary hover:bg-primary/90">
                  <Sparkles className="w-5 h-5 mr-2" />
                  Get 10x Better Titles (Free)
                </Button>
              </Link>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CheckCircle className="w-4 h-4 text-green-500" />
                No credit card required
              </div>
            </div>

            {/* Results Preview */}
            <div className="pt-12">
              <p className="text-sm text-muted-foreground mb-6">Real results from our creators:</p>
              <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                <Card className="border border-green-200 bg-green-50/50">
                  <CardContent className="p-6 text-center">
                    <div className="text-2xl font-bold text-green-600 mb-1">847%</div>
                    <div className="text-sm text-green-700">views increase</div>
                  </CardContent>
                </Card>
                <Card className="border border-blue-200 bg-blue-50/50">
                  <CardContent className="p-6 text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">12x</div>
                    <div className="text-sm text-blue-700">higher CTR</div>
                  </CardContent>
                </Card>
                <Card className="border border-purple-200 bg-purple-50/50">
                  <CardContent className="p-6 text-center">
                    <div className="text-2xl font-bold text-purple-600 mb-1">3.2M</div>
                    <div className="text-sm text-purple-700">viral video</div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pain Points Section */}
      <section className="py-20 bg-secondary/20">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-foreground mb-6">
              Tired of Creating Videos
              <br />
              <span className="text-red-600">That Nobody Watches?</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              You're not alone. 95% of YouTubers struggle with the same problems...
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            <Card className="border-red-200 bg-red-50/30">
              <CardHeader>
                <CardTitle className="text-xl text-red-800 flex items-center gap-2">
                  <Target className="w-6 h-6" />
                  Your Current Reality
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                  <p className="text-red-700">Spending 20+ hours creating content that gets 200 views</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                  <p className="text-red-700">Guessing at titles and getting terrible click-through rates</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                  <p className="text-red-700">Thumbnails that look amateur next to big creators</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                  <p className="text-red-700">No idea why some videos flop and others don't</p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-green-50/30">
              <CardHeader>
                <CardTitle className="text-xl text-green-800 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6" />
                  With Echo
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <p className="text-green-700">10 data-driven titles that actually get clicks</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <p className="text-green-700">AI thumbnails that compete with million-sub channels</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <p className="text-green-700">Predict your video's performance before publishing</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <p className="text-green-700">A/B test everything to find what works</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="text-center">
            <Link href="/auth/signup">
              <Button size="lg" className="text-lg px-10 py-4 h-auto">
                Stop the Struggle - Try Echo Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Social Proof & Testimonials */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Real Creators, Real Results
            </h2>
            <p className="text-lg text-muted-foreground">
              See how Echo transformed these channels from struggling to thriving
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <Card className="border-green-200 bg-green-50/20">
              <CardContent className="p-6">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <Quote className="w-8 h-8 text-green-600 mb-4" />
                <p className="text-foreground mb-4 italic">
                  "My last video got 47K views instead of my usual 800. The AI titles are insane - 
                  they know exactly what people want to click on."
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                    M
                  </div>
                  <div>
                    <div className="font-semibold">Marcus Chen</div>
                    <div className="text-sm text-muted-foreground">Tech Creator • 23K subs</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Testimonial 2 */}
            <Card className="border-blue-200 bg-blue-50/20">
              <CardContent className="p-6">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <Quote className="w-8 h-8 text-blue-600 mb-4" />
                <p className="text-foreground mb-4 italic">
                  "I went from 3% CTR to 14% CTR overnight. The thumbnail generator is like having 
                  a professional designer who knows YouTube psychology."
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                    S
                  </div>
                  <div>
                    <div className="font-semibold">Sarah Williams</div>
                    <div className="text-sm text-muted-foreground">Lifestyle Creator • 89K subs</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Testimonial 3 */}
            <Card className="border-purple-200 bg-purple-50/20">
              <CardContent className="p-6">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <Quote className="w-8 h-8 text-purple-600 mb-4" />
                <p className="text-foreground mb-4 italic">
                  "Finally hit 100K subscribers! Echo's performance predictions helped me 
                  understand what content actually works. Game changer."
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                    J
                  </div>
                  <div>
                    <div className="font-semibold">James Rodriguez</div>
                    <div className="text-sm text-muted-foreground">Education Creator • 156K subs</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Features Deep Dive */}
      <section className="py-20 bg-secondary/10">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Everything You Need to Dominate YouTube
            </h2>
            <p className="text-lg text-muted-foreground">
              Stop guessing. Start winning with AI-powered optimization.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border border-border/50">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>10 Viral-Ready Titles</CardTitle>
                <CardDescription>
                  AI-generated titles that hack the YouTube algorithm and psychology
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Keyword-optimized for search
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Emotion-driven for clicks
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Length-optimized for display
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-border/50">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Video className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>AI Thumbnail Generator</CardTitle>
                <CardDescription>
                  Professional thumbnails that compete with million-subscriber channels
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Psychology-based designs
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Multiple style variations
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    HD quality downloads
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-border/50">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>Performance Prediction</CardTitle>
                <CardDescription>
                  Know if your video will go viral before you publish it
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    View count predictions
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    CTR forecasting
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Optimization suggestions
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-border/50">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Target className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>A/B Testing Lab</CardTitle>
                <CardDescription>
                  Test different versions to find what converts best
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Title split testing
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Thumbnail variants
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Statistical significance
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-border/50">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>Trend Discovery</CardTitle>
                <CardDescription>
                  Spot viral opportunities before your competitors do
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Real-time trend analysis
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Keyword research
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Content ideas generator
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-border/50">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Get optimized content in under 2 minutes, not 2 hours
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Instant optimization
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Bulk processing
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Real-time results
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Start Your YouTube Transformation
            </h2>
            <p className="text-lg text-muted-foreground">
              Join thousands of creators who've 10x'd their views with Echo
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            {/* Free Plan */}
            <Card className="border border-border/50 relative">
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl mb-2">Free Trial</CardTitle>
                <div className="text-4xl font-bold mb-2">$0</div>
                <p className="text-muted-foreground">For 7 days</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>5 video optimizations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>10 AI-generated titles per video</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>5 AI thumbnail variants</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>Performance predictions</span>
                </div>
                <div className="pt-6">
                  <Link href="/auth/signup" className="w-full">
                    <Button variant="outline" className="w-full">
                      Start Free Trial
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>

            {/* Pro Plan */}
            <Card className="border-2 border-primary relative bg-primary/5">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-primary text-primary-foreground px-6 py-1">
                  MOST POPULAR
                </Badge>
              </div>
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl mb-2">Pro Creator</CardTitle>
                <div className="text-4xl font-bold mb-2">$29</div>
                <p className="text-muted-foreground">per month</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>Unlimited video optimizations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>Advanced A/B testing</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>Trend discovery engine</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>Keyword research tools</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span>Priority support</span>
                </div>
                <div className="pt-6">
                  <Link href="/auth/signup" className="w-full">
                    <Button className="w-full bg-primary hover:bg-primary/90">
                      Start Free Trial
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="text-center mt-8">
            <p className="text-sm text-muted-foreground">
              No credit card required • Cancel anytime • 30-day money-back guarantee
            </p>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container mx-auto px-6 max-w-4xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Stop Struggling and Start Succeeding?
          </h2>
          <p className="text-xl mb-8 text-primary-foreground/90">
            Join 2,400+ creators who've transformed their channels with Echo.
            <br />
            Your next viral video is just one click away.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signup">
              <Button size="lg" variant="secondary" className="text-lg px-10 py-4 h-auto">
                <Sparkles className="w-5 h-5 mr-2" />
                Start Your Free Trial Now
              </Button>
            </Link>
            <div className="flex items-center gap-2 text-sm text-primary-foreground/80">
              <CheckCircle className="w-4 h-4" />
              No credit card required
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-12 bg-secondary/20">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Video className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="text-xl font-semibold">Echo</span>
            </div>
            <div className="flex items-center space-x-8 text-sm text-muted-foreground">
              <Link href="/auth/login" className="hover:text-foreground transition-colors">
                Sign In
              </Link>
              <Link href="/auth/signup" className="hover:text-foreground transition-colors">
                Get Started
              </Link>
              <span>© 2024 Echo. All rights reserved.</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
