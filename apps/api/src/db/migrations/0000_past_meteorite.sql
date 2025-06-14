CREATE TYPE "public"."job_status" AS ENUM('pending', 'processing', 'completed', 'failed', 'cancelled');--> statement-breakpoint
CREATE TYPE "public"."video_status" AS ENUM('draft', 'processing', 'published', 'failed');--> statement-breakpoint
CREATE TYPE "public"."competitor_status" AS ENUM('active', 'paused', 'archived');--> statement-breakpoint
CREATE TYPE "public"."content_source" AS ENUM('youtube_channel', 'blog', 'podcast', 'twitter_user', 'reddit');--> statement-breakpoint
CREATE TYPE "public"."idea_status" AS ENUM('draft', 'outlining', 'scripting', 'ready', 'published', 'archived');--> statement-breakpoint
CREATE TYPE "public"."video_type" AS ENUM('tutorial', 'review', 'vlog', 'shorts', 'podcast', 'other');--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "chat_messages" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"chat_id" uuid NOT NULL,
	"role" text NOT NULL,
	"content" text NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "chats" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"title" text NOT NULL,
	"video_id" uuid,
	"is_active" boolean DEFAULT true NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "users" (
	"id" uuid PRIMARY KEY NOT NULL,
	"email" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "video_jobs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"video_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"status" "job_status" DEFAULT 'pending' NOT NULL,
	"progress" integer DEFAULT 0 NOT NULL,
	"config" jsonb,
	"result" jsonb,
	"error" text,
	"started_at" timestamp,
	"completed_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "video_metadata" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"video_id" uuid NOT NULL,
	"title" text,
	"description" text,
	"transcript" text,
	"subtitles" jsonb,
	"tags" text[],
	"thumbnail" text,
	"generated_titles" text[],
	"thumbnail_urls" text[],
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "videos" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"file_name" text NOT NULL,
	"file_url" text NOT NULL,
	"file_size" integer,
	"mime_type" text,
	"duration" integer,
	"status" "video_status" DEFAULT 'draft' NOT NULL,
	"uploaded_at" timestamp DEFAULT now() NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "competitor_videos" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"competitor_id" uuid NOT NULL,
	"youtube_video_id" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"views" integer,
	"likes" integer,
	"comments" integer,
	"duration" integer,
	"published_at" timestamp NOT NULL,
	"transcript" text,
	"tags" text[],
	"performance_score" numeric(5, 2),
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "competitors" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"channel_name" text NOT NULL,
	"youtube_channel_id" text NOT NULL,
	"channel_url" text,
	"tracking_keywords" text[],
	"status" "competitor_status" DEFAULT 'active' NOT NULL,
	"metadata" jsonb,
	"last_scraped_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "content_sources" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"type" "content_source" NOT NULL,
	"name" text NOT NULL,
	"identifier" text NOT NULL,
	"rss_feed" text,
	"check_frequency" text DEFAULT 'daily' NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"last_checked_at" timestamp,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "generated_content" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"idea_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"titles" text[] NOT NULL,
	"selected_title" text,
	"outline" text,
	"script" text,
	"description" text,
	"tags" text[],
	"thumbnail_prompts" text[],
	"thumbnail_urls" text[],
	"selected_thumbnail" text,
	"model" text DEFAULT 'claude-3-opus' NOT NULL,
	"prompt_version" text,
	"generation_cost" numeric(10, 4),
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "idea_embeddings" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"idea_id" uuid NOT NULL,
	"embedding" vector(1536),
	"model_version" text DEFAULT 'text-embedding-3-small' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "ideas" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"content" text NOT NULL,
	"type" text DEFAULT 'idea' NOT NULL,
	"status" "idea_status" DEFAULT 'draft' NOT NULL,
	"video_type" "video_type",
	"source" text,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "published_videos" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"idea_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"youtube_video_id" text NOT NULL,
	"youtube_url" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"tags" text[],
	"thumbnail_url" text,
	"published_at" timestamp NOT NULL,
	"views" integer DEFAULT 0,
	"likes" integer DEFAULT 0,
	"comments" integer DEFAULT 0,
	"watch_time" integer,
	"ctr" numeric(5, 2),
	"avg_view_duration" integer,
	"last_metrics_update" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "youtube_credentials" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"channel_id" text NOT NULL,
	"channel_name" text,
	"access_token" text NOT NULL,
	"refresh_token" text NOT NULL,
	"expires_at" timestamp NOT NULL,
	"scope" text[],
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chat_messages" ADD CONSTRAINT "chat_messages_chat_id_chats_id_fk" FOREIGN KEY ("chat_id") REFERENCES "public"."chats"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chats" ADD CONSTRAINT "chats_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chats" ADD CONSTRAINT "chats_video_id_videos_id_fk" FOREIGN KEY ("video_id") REFERENCES "public"."videos"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "video_jobs" ADD CONSTRAINT "video_jobs_video_id_videos_id_fk" FOREIGN KEY ("video_id") REFERENCES "public"."videos"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "video_jobs" ADD CONSTRAINT "video_jobs_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "video_metadata" ADD CONSTRAINT "video_metadata_video_id_videos_id_fk" FOREIGN KEY ("video_id") REFERENCES "public"."videos"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "videos" ADD CONSTRAINT "videos_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "competitor_videos" ADD CONSTRAINT "competitor_videos_competitor_id_competitors_id_fk" FOREIGN KEY ("competitor_id") REFERENCES "public"."competitors"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "competitors" ADD CONSTRAINT "competitors_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "content_sources" ADD CONSTRAINT "content_sources_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "generated_content" ADD CONSTRAINT "generated_content_idea_id_ideas_id_fk" FOREIGN KEY ("idea_id") REFERENCES "public"."ideas"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "generated_content" ADD CONSTRAINT "generated_content_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "idea_embeddings" ADD CONSTRAINT "idea_embeddings_idea_id_ideas_id_fk" FOREIGN KEY ("idea_id") REFERENCES "public"."ideas"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "ideas" ADD CONSTRAINT "ideas_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "published_videos" ADD CONSTRAINT "published_videos_idea_id_ideas_id_fk" FOREIGN KEY ("idea_id") REFERENCES "public"."ideas"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "published_videos" ADD CONSTRAINT "published_videos_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "youtube_credentials" ADD CONSTRAINT "youtube_credentials_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "chat_messages_chat_id_idx" ON "chat_messages" USING btree ("chat_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "chats_user_id_idx" ON "chats" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "chats_video_id_idx" ON "chats" USING btree ("video_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "video_jobs_video_id_idx" ON "video_jobs" USING btree ("video_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "video_jobs_user_id_idx" ON "video_jobs" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "video_jobs_status_idx" ON "video_jobs" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "video_metadata_video_id_idx" ON "video_metadata" USING btree ("video_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "videos_user_id_idx" ON "videos" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "videos_status_idx" ON "videos" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "competitor_videos_competitor_id_idx" ON "competitor_videos" USING btree ("competitor_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "competitor_videos_video_id_idx" ON "competitor_videos" USING btree ("youtube_video_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "competitor_videos_performance_idx" ON "competitor_videos" USING btree ("performance_score");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "competitors_user_id_idx" ON "competitors" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "competitors_channel_id_idx" ON "competitors" USING btree ("youtube_channel_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "content_sources_user_id_idx" ON "content_sources" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "content_sources_type_idx" ON "content_sources" USING btree ("type");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "generated_content_idea_id_idx" ON "generated_content" USING btree ("idea_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "generated_content_user_id_idx" ON "generated_content" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idea_embeddings_idea_id_idx" ON "idea_embeddings" USING btree ("idea_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "ideas_user_id_idx" ON "ideas" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "ideas_status_idx" ON "ideas" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "ideas_created_at_idx" ON "ideas" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "published_videos_idea_id_idx" ON "published_videos" USING btree ("idea_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "published_videos_user_id_idx" ON "published_videos" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "published_videos_youtube_id_idx" ON "published_videos" USING btree ("youtube_video_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "youtube_credentials_user_id_idx" ON "youtube_credentials" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "youtube_credentials_channel_id_idx" ON "youtube_credentials" USING btree ("channel_id");