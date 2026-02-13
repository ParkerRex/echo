import {
  pgTable,
  uuid,
  text,
  timestamp,
  jsonb,
  integer,
  boolean,
  pgEnum,
  index,
  decimal,
  date,
} from 'drizzle-orm/pg-core'
import { relations } from 'drizzle-orm'

// Enums
export const jobStatusEnum = pgEnum('job_status', [
  'pending',
  'processing',
  'completed',
  'failed',
  'cancelled',
])

export const videoStatusEnum = pgEnum('video_status', [
  'draft',
  'processing',
  'published',
  'failed',
])

export const publicationStatusEnum = pgEnum('publication_status', [
  'scheduled',
  'published',
  'failed',
  'processing',
])

export const abTestStatusEnum = pgEnum('ab_test_status', [
  'draft',
  'running',
  'completed',
  'cancelled',
])

export const competitionLevelEnum = pgEnum('competition_level', [
  'low',
  'medium',
  'high',
])

// Users table (syncs with Supabase Auth via trigger)
export const users = pgTable('users', {
  id: uuid('id').primaryKey(), // References auth.users.id
  email: text('email').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// Videos table
export const videos = pgTable(
  'videos',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    fileName: text('file_name').notNull(),
    fileUrl: text('file_url').notNull(),
    fileSize: integer('file_size'),
    mimeType: text('mime_type'),
    duration: integer('duration'), // in seconds
    status: videoStatusEnum('status').default('draft').notNull(),
    uploadedAt: timestamp('uploaded_at').defaultNow().notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('videos_user_id_idx').on(table.userId),
      statusIdx: index('videos_status_idx').on(table.status),
    }
  }
)

// Video processing jobs
export const videoJobs = pgTable(
  'video_jobs',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    videoId: uuid('video_id')
      .notNull()
      .references(() => videos.id),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    status: jobStatusEnum('status').default('pending').notNull(),
    progress: integer('progress').default(0).notNull(), // 0-100
    config: jsonb('config'), // Processing configuration
    result: jsonb('result'), // Processing result/output
    error: text('error'), // Error message if failed
    startedAt: timestamp('started_at'),
    completedAt: timestamp('completed_at'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      videoIdIdx: index('video_jobs_video_id_idx').on(table.videoId),
      userIdIdx: index('video_jobs_user_id_idx').on(table.userId),
      statusIdx: index('video_jobs_status_idx').on(table.status),
    }
  }
)

// Video metadata (extracted data)
export const videoMetadata = pgTable(
  'video_metadata',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    videoId: uuid('video_id')
      .notNull()
      .references(() => videos.id),
    title: text('title'),
    description: text('description'),
    transcript: text('transcript'),
    subtitles: jsonb('subtitles'), // SRT/VTT data
    tags: text('tags').array(),
    thumbnail: text('thumbnail'), // URL
    generatedTitles: text('generated_titles').array(), // Array of 10 generated titles
    thumbnailUrls: text('thumbnail_urls').array(), // Array of AI-generated thumbnail URLs
    metadata: jsonb('metadata'), // Additional extracted metadata
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      videoIdIdx: index('video_metadata_video_id_idx').on(table.videoId),
    }
  }
)

// Chat/Conversations
export const chats = pgTable(
  'chats',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    title: text('title').notNull(),
    videoId: uuid('video_id').references(() => videos.id), // Optional video context
    isActive: boolean('is_active').default(true).notNull(),
    metadata: jsonb('metadata'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('chats_user_id_idx').on(table.userId),
      videoIdIdx: index('chats_video_id_idx').on(table.videoId),
    }
  }
)

// Chat messages
export const chatMessages = pgTable(
  'chat_messages',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    chatId: uuid('chat_id')
      .notNull()
      .references(() => chats.id),
    role: text('role', { enum: ['user', 'assistant', 'system'] }).notNull(),
    content: text('content').notNull(),
    metadata: jsonb('metadata'), // Token counts, model used, etc.
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      chatIdIdx: index('chat_messages_chat_id_idx').on(table.chatId),
    }
  }
)

// YouTube credentials table for OAuth tokens
export const youtubeCredentials = pgTable(
  'youtube_credentials',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id)
      .unique(), // One YouTube account per user
    channelId: text('channel_id').notNull(),
    channelName: text('channel_name'),
    accessToken: text('access_token').notNull(),
    refreshToken: text('refresh_token').notNull(),
    expiresAt: timestamp('expires_at').notNull(),
    scope: text('scope').array(),
    metadata: jsonb('metadata'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('youtube_credentials_user_id_idx').on(table.userId),
      channelIdIdx: index('youtube_credentials_channel_id_idx').on(table.channelId),
    }
  }
)

// YouTube publications table - tracks all published videos
export const youtubePublications = pgTable(
  'youtube_publications',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    videoId: uuid('video_id')
      .notNull()
      .references(() => videos.id),
    youtubeVideoId: text('youtube_video_id').notNull(),
    youtubeUrl: text('youtube_url').notNull(),
    publishedTitle: text('published_title').notNull(),
    publishedDescription: text('published_description'),
    publishedTags: text('published_tags').array(),
    privacyStatus: text('privacy_status').notNull(),
    scheduledFor: timestamp('scheduled_for'),
    publishedAt: timestamp('published_at'),
    viewCount: integer('view_count').default(0),
    likeCount: integer('like_count').default(0),
    commentCount: integer('comment_count').default(0),
    subscriberCount: integer('subscriber_count').default(0),
    lastAnalyticsSync: timestamp('last_analytics_sync'),
    status: publicationStatusEnum('status').default('published').notNull(),
    metadata: jsonb('metadata'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('youtube_publications_user_id_idx').on(table.userId),
      videoIdIdx: index('youtube_publications_video_id_idx').on(table.videoId),
      youtubeVideoIdIdx: index('youtube_publications_youtube_video_id_idx').on(table.youtubeVideoId),
      statusIdx: index('youtube_publications_status_idx').on(table.status),
      scheduledForIdx: index('youtube_publications_scheduled_for_idx').on(table.scheduledFor),
    }
  }
)

// YouTube analytics snapshots - daily analytics data
export const youtubeAnalyticsSnapshots = pgTable(
  'youtube_analytics_snapshots',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    publicationId: uuid('publication_id')
      .notNull()
      .references(() => youtubePublications.id),
    snapshotDate: date('snapshot_date').notNull(),
    views: integer('views').default(0),
    likes: integer('likes').default(0),
    comments: integer('comments').default(0),
    shares: integer('shares').default(0),
    dislikes: integer('dislikes').default(0),
    watchTimeMinutes: integer('watch_time_minutes').default(0),
    averageViewDuration: decimal('average_view_duration', { precision: 10, scale: 2 }).default('0'),
    clickThroughRate: decimal('click_through_rate', { precision: 5, scale: 4 }).default('0'),
    retentionData: jsonb('retention_data'),
    trafficSources: jsonb('traffic_sources'),
    demographics: jsonb('demographics'),
    revenueData: jsonb('revenue_data'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      publicationIdIdx: index('youtube_analytics_publication_id_idx').on(table.publicationId),
      snapshotDateIdx: index('youtube_analytics_snapshot_date_idx').on(table.snapshotDate),
    }
  }
)

// Trending topics for content strategy
export const trendingTopics = pgTable(
  'trending_topics',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    topic: text('topic').notNull(),
    category: text('category').notNull(),
    region: text('region').default('US'),
    trendScore: integer('trend_score').notNull(),
    searchVolume: integer('search_volume'),
    competitionLevel: competitionLevelEnum('competition_level').default('medium'),
    relatedKeywords: text('related_keywords').array(),
    sampleTitles: text('sample_titles').array(),
    sampleChannels: text('sample_channels').array(),
    discoveredAt: timestamp('discovered_at').defaultNow().notNull(),
    expiresAt: timestamp('expires_at'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      categoryIdx: index('trending_topics_category_idx').on(table.category),
      regionIdx: index('trending_topics_region_idx').on(table.region),
      trendScoreIdx: index('trending_topics_trend_score_idx').on(table.trendScore),
      expiresAtIdx: index('trending_topics_expires_at_idx').on(table.expiresAt),
    }
  }
)

// User niches for personalized recommendations
export const userNiches = pgTable(
  'user_niches',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    niche: text('niche').notNull(),
    keywords: text('keywords').array(),
    competitorChannels: text('competitor_channels').array(),
    targetAudience: jsonb('target_audience'),
    contentThemes: text('content_themes').array(),
    optimalPostingTimes: jsonb('optimal_posting_times'),
    performanceMetrics: jsonb('performance_metrics'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('user_niches_user_id_idx').on(table.userId),
      nicheIdx: index('user_niches_niche_idx').on(table.niche),
    }
  }
)

// Content variants for A/B testing
export const contentVariants = pgTable(
  'content_variants',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    videoId: uuid('video_id')
      .notNull()
      .references(() => videos.id),
    variantType: text('variant_type').notNull(),
    originalContent: text('original_content').notNull(),
    variantContent: text('variant_content').notNull(),
    aiConfidenceScore: decimal('ai_confidence_score', { precision: 3, scale: 2 }),
    predictedPerformance: jsonb('predicted_performance'),
    generationPrompt: text('generation_prompt'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      videoIdIdx: index('content_variants_video_id_idx').on(table.videoId),
      variantTypeIdx: index('content_variants_variant_type_idx').on(table.variantType),
    }
  }
)

// A/B test experiments
export const abTestExperiments = pgTable(
  'ab_test_experiments',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    videoId: uuid('video_id')
      .notNull()
      .references(() => videos.id),
    experimentName: text('experiment_name').notNull(),
    variants: jsonb('variants').notNull(),
    trafficSplit: jsonb('traffic_split').notNull(),
    successMetric: text('success_metric').notNull(),
    targetSampleSize: integer('target_sample_size').default(1000),
    confidenceLevel: decimal('confidence_level', { precision: 3, scale: 2 }).default('0.95'),
    status: abTestStatusEnum('status').default('draft').notNull(),
    startedAt: timestamp('started_at'),
    endedAt: timestamp('ended_at'),
    results: jsonb('results'),
    winnerVariantId: uuid('winner_variant_id'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('ab_test_experiments_user_id_idx').on(table.userId),
      videoIdIdx: index('ab_test_experiments_video_id_idx').on(table.videoId),
      statusIdx: index('ab_test_experiments_status_idx').on(table.status),
    }
  }
)

// Define relations
export const usersRelations = relations(users, ({ many, one }) => ({
  videos: many(videos),
  videoJobs: many(videoJobs),
  chats: many(chats),
  youtubeCredentials: one(youtubeCredentials),
  youtubePublications: many(youtubePublications),
  userNiches: many(userNiches),
  abTestExperiments: many(abTestExperiments),
}))

export const videosRelations = relations(videos, ({ one, many }) => ({
  user: one(users, {
    fields: [videos.userId],
    references: [users.id],
  }),
  jobs: many(videoJobs),
  metadata: one(videoMetadata),
  chats: many(chats),
  youtubePublications: many(youtubePublications),
  contentVariants: many(contentVariants),
  abTestExperiments: many(abTestExperiments),
}))

export const videoJobsRelations = relations(videoJobs, ({ one }) => ({
  video: one(videos, {
    fields: [videoJobs.videoId],
    references: [videos.id],
  }),
  user: one(users, {
    fields: [videoJobs.userId],
    references: [users.id],
  }),
}))

export const videoMetadataRelations = relations(videoMetadata, ({ one }) => ({
  video: one(videos, {
    fields: [videoMetadata.videoId],
    references: [videos.id],
  }),
}))

export const chatsRelations = relations(chats, ({ one, many }) => ({
  user: one(users, {
    fields: [chats.userId],
    references: [users.id],
  }),
  video: one(videos, {
    fields: [chats.videoId],
    references: [videos.id],
  }),
  messages: many(chatMessages),
}))

export const chatMessagesRelations = relations(chatMessages, ({ one }) => ({
  chat: one(chats, {
    fields: [chatMessages.chatId],
    references: [chats.id],
  }),
}))

export const youtubeCredentialsRelations = relations(youtubeCredentials, ({ one }) => ({
  user: one(users, {
    fields: [youtubeCredentials.userId],
    references: [users.id],
  }),
}))

export const youtubePublicationsRelations = relations(youtubePublications, ({ one, many }) => ({
  user: one(users, {
    fields: [youtubePublications.userId],
    references: [users.id],
  }),
  video: one(videos, {
    fields: [youtubePublications.videoId],
    references: [videos.id],
  }),
  analyticsSnapshots: many(youtubeAnalyticsSnapshots),
}))

export const youtubeAnalyticsSnapshotsRelations = relations(youtubeAnalyticsSnapshots, ({ one }) => ({
  publication: one(youtubePublications, {
    fields: [youtubeAnalyticsSnapshots.publicationId],
    references: [youtubePublications.id],
  }),
}))

export const userNichesRelations = relations(userNiches, ({ one }) => ({
  user: one(users, {
    fields: [userNiches.userId],
    references: [users.id],
  }),
}))

export const contentVariantsRelations = relations(contentVariants, ({ one }) => ({
  video: one(videos, {
    fields: [contentVariants.videoId],
    references: [videos.id],
  }),
}))

export const abTestExperimentsRelations = relations(abTestExperiments, ({ one }) => ({
  user: one(users, {
    fields: [abTestExperiments.userId],
    references: [users.id],
  }),
  video: one(videos, {
    fields: [abTestExperiments.videoId],
    references: [videos.id],
  }),
}))

// Type exports
export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
export type Video = typeof videos.$inferSelect
export type NewVideo = typeof videos.$inferInsert
export type VideoJob = typeof videoJobs.$inferSelect
export type NewVideoJob = typeof videoJobs.$inferInsert
export type VideoMetadata = typeof videoMetadata.$inferSelect
export type NewVideoMetadata = typeof videoMetadata.$inferInsert
export type Chat = typeof chats.$inferSelect
export type NewChat = typeof chats.$inferInsert
export type ChatMessage = typeof chatMessages.$inferSelect
export type NewChatMessage = typeof chatMessages.$inferInsert
export type YouTubeCredentials = typeof youtubeCredentials.$inferSelect
export type NewYouTubeCredentials = typeof youtubeCredentials.$inferInsert
export type YouTubePublication = typeof youtubePublications.$inferSelect
export type NewYouTubePublication = typeof youtubePublications.$inferInsert
export type YouTubeAnalyticsSnapshot = typeof youtubeAnalyticsSnapshots.$inferSelect
export type NewYouTubeAnalyticsSnapshot = typeof youtubeAnalyticsSnapshots.$inferInsert
export type TrendingTopic = typeof trendingTopics.$inferSelect
export type NewTrendingTopic = typeof trendingTopics.$inferInsert
export type UserNiche = typeof userNiches.$inferSelect
export type NewUserNiche = typeof userNiches.$inferInsert
export type ContentVariant = typeof contentVariants.$inferSelect
export type NewContentVariant = typeof contentVariants.$inferInsert
export type AbTestExperiment = typeof abTestExperiments.$inferSelect
export type NewAbTestExperiment = typeof abTestExperiments.$inferInsert
