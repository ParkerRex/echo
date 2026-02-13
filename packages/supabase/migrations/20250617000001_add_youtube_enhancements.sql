-- Migration: Add YouTube publishing history and analytics tracking
-- Description: Creates tables for YouTube publishing history, analytics snapshots, trending topics, and user niches
-- Affected: New tables for enhanced YouTube integration and AI content strategy
-- Rollback: DROP TABLE youtube_analytics_snapshots; DROP TABLE youtube_publications; DROP TABLE user_niches; DROP TABLE trending_topics; DROP TABLE content_variants; DROP TABLE ab_test_experiments;

BEGIN;

-- Add enum for publication status
CREATE TYPE publication_status AS ENUM ('scheduled', 'published', 'failed', 'processing');

-- Add enum for A/B test status  
CREATE TYPE ab_test_status AS ENUM ('draft', 'running', 'completed', 'cancelled');

-- Add enum for competition level
CREATE TYPE competition_level AS ENUM ('low', 'medium', 'high');

-- YouTube publications table - tracks all published videos
CREATE TABLE public.youtube_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    youtube_video_id TEXT NOT NULL,
    youtube_url TEXT NOT NULL,
    published_title TEXT NOT NULL,
    published_description TEXT,
    published_tags TEXT[],
    privacy_status TEXT NOT NULL,
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    subscriber_count INTEGER DEFAULT 0,
    last_analytics_sync TIMESTAMPTZ,
    status publication_status DEFAULT 'published',
    metadata JSONB, -- Additional YouTube metadata
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- YouTube analytics snapshots - daily analytics data
CREATE TABLE public.youtube_analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES public.youtube_publications(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0,
    watch_time_minutes INTEGER DEFAULT 0,
    average_view_duration DECIMAL(10,2) DEFAULT 0,
    click_through_rate DECIMAL(5,4) DEFAULT 0, -- CTR as percentage
    retention_data JSONB, -- Audience retention graph data
    traffic_sources JSONB, -- Where views came from
    demographics JSONB, -- Age, gender, geography data
    revenue_data JSONB, -- Monetization data if available
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Trending topics for content strategy
CREATE TABLE public.trending_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    category TEXT NOT NULL,
    region TEXT DEFAULT 'US',
    trend_score INTEGER NOT NULL CHECK (trend_score >= 1 AND trend_score <= 100),
    search_volume INTEGER,
    competition_level competition_level DEFAULT 'medium',
    related_keywords TEXT[],
    sample_titles TEXT[],
    sample_channels TEXT[], -- Channels covering this topic
    discovered_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- User niches for personalized recommendations
CREATE TABLE public.user_niches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    niche TEXT NOT NULL,
    keywords TEXT[],
    competitor_channels TEXT[],
    target_audience JSONB, -- Demographics, interests
    content_themes TEXT[], -- Common themes in user's content
    optimal_posting_times JSONB, -- Best times to post for this niche
    performance_metrics JSONB, -- Average performance in this niche
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Content variants for A/B testing
CREATE TABLE public.content_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    variant_type TEXT NOT NULL CHECK (variant_type IN ('title', 'thumbnail', 'description', 'tags')),
    original_content TEXT NOT NULL,
    variant_content TEXT NOT NULL,
    ai_confidence_score DECIMAL(3,2) CHECK (ai_confidence_score >= 0.00 AND ai_confidence_score <= 1.00),
    predicted_performance JSONB, -- CTR, retention, engagement predictions
    generation_prompt TEXT, -- AI prompt used to generate this variant
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- A/B test experiments
CREATE TABLE public.ab_test_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    experiment_name TEXT NOT NULL,
    variants JSONB NOT NULL, -- Array of variant IDs and their configurations
    traffic_split JSONB NOT NULL, -- Percentage split between variants
    success_metric TEXT NOT NULL CHECK (success_metric IN ('ctr', 'retention', 'engagement', 'views')),
    target_sample_size INTEGER DEFAULT 1000,
    confidence_level DECIMAL(3,2) DEFAULT 0.95,
    status ab_test_status DEFAULT 'draft',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    results JSONB, -- Test results and statistical significance
    winner_variant_id UUID,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Add indexes for performance
CREATE INDEX idx_youtube_publications_user_id ON public.youtube_publications(user_id);
CREATE INDEX idx_youtube_publications_video_id ON public.youtube_publications(video_id);
CREATE INDEX idx_youtube_publications_youtube_video_id ON public.youtube_publications(youtube_video_id);
CREATE INDEX idx_youtube_publications_status ON public.youtube_publications(status);
CREATE INDEX idx_youtube_publications_scheduled_for ON public.youtube_publications(scheduled_for) WHERE scheduled_for IS NOT NULL;

CREATE INDEX idx_youtube_analytics_publication_id ON public.youtube_analytics_snapshots(publication_id);
CREATE INDEX idx_youtube_analytics_snapshot_date ON public.youtube_analytics_snapshots(snapshot_date);

CREATE INDEX idx_trending_topics_category ON public.trending_topics(category);
CREATE INDEX idx_trending_topics_region ON public.trending_topics(region);
CREATE INDEX idx_trending_topics_trend_score ON public.trending_topics(trend_score);
CREATE INDEX idx_trending_topics_expires_at ON public.trending_topics(expires_at);

CREATE INDEX idx_user_niches_user_id ON public.user_niches(user_id);
CREATE INDEX idx_user_niches_niche ON public.user_niches(niche);

CREATE INDEX idx_content_variants_video_id ON public.content_variants(video_id);
CREATE INDEX idx_content_variants_variant_type ON public.content_variants(variant_type);

CREATE INDEX idx_ab_test_experiments_user_id ON public.ab_test_experiments(user_id);
CREATE INDEX idx_ab_test_experiments_video_id ON public.ab_test_experiments(video_id);
CREATE INDEX idx_ab_test_experiments_status ON public.ab_test_experiments(status);

-- Enable RLS on all new tables
ALTER TABLE public.youtube_publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.youtube_analytics_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trending_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_niches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ab_test_experiments ENABLE ROW LEVEL SECURITY;

-- RLS policies for youtube_publications
CREATE POLICY "Users can view their own YouTube publications" ON public.youtube_publications
FOR SELECT TO authenticated
USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can create their own YouTube publications" ON public.youtube_publications
FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update their own YouTube publications" ON public.youtube_publications
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete their own YouTube publications" ON public.youtube_publications
FOR DELETE TO authenticated
USING ((SELECT auth.uid()) = user_id);

-- RLS policies for youtube_analytics_snapshots
CREATE POLICY "Users can view analytics for their publications" ON public.youtube_analytics_snapshots
FOR SELECT TO authenticated
USING (
    publication_id IN (
        SELECT id FROM public.youtube_publications 
        WHERE user_id = (SELECT auth.uid())
    )
);

CREATE POLICY "System can create analytics snapshots" ON public.youtube_analytics_snapshots
FOR INSERT TO authenticated
WITH CHECK (
    publication_id IN (
        SELECT id FROM public.youtube_publications 
        WHERE user_id = (SELECT auth.uid())
    )
);

-- RLS policies for trending_topics (public read access)
CREATE POLICY "Trending topics are viewable by everyone" ON public.trending_topics
FOR SELECT TO authenticated, anon
USING (true);

CREATE POLICY "Trending topics can be created by authenticated users" ON public.trending_topics
FOR INSERT TO authenticated
WITH CHECK (true);

-- RLS policies for user_niches
CREATE POLICY "Users can view their own niches" ON public.user_niches
FOR SELECT TO authenticated
USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can create their own niches" ON public.user_niches
FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update their own niches" ON public.user_niches
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete their own niches" ON public.user_niches
FOR DELETE TO authenticated
USING ((SELECT auth.uid()) = user_id);

-- RLS policies for content_variants
CREATE POLICY "Users can view variants for their videos" ON public.content_variants
FOR SELECT TO authenticated
USING (
    video_id IN (
        SELECT id FROM public.videos 
        WHERE userId = (SELECT auth.uid())
    )
);

CREATE POLICY "Users can create variants for their videos" ON public.content_variants
FOR INSERT TO authenticated
WITH CHECK (
    video_id IN (
        SELECT id FROM public.videos 
        WHERE userId = (SELECT auth.uid())
    )
);

-- RLS policies for ab_test_experiments
CREATE POLICY "Users can view their own A/B test experiments" ON public.ab_test_experiments
FOR SELECT TO authenticated
USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can create their own A/B test experiments" ON public.ab_test_experiments
FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update their own A/B test experiments" ON public.ab_test_experiments
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete their own A/B test experiments" ON public.ab_test_experiments
FOR DELETE TO authenticated
USING ((SELECT auth.uid()) = user_id);

-- Add trigger to update updated_at columns
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER youtube_publications_updated_at
    BEFORE UPDATE ON public.youtube_publications
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER user_niches_updated_at
    BEFORE UPDATE ON public.user_niches
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER ab_test_experiments_updated_at
    BEFORE UPDATE ON public.ab_test_experiments
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

COMMIT;