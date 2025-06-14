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
  vector,
} from 'drizzle-orm/pg-core'
import { relations } from 'drizzle-orm'

// Import existing tables we'll relate to
import { users } from './schema'

// Enums
export const ideaStatusEnum = pgEnum('idea_status', [
  'draft',
  'outlining',
  'scripting',
  'ready',
  'published',
  'archived',
])

export const videoTypeEnum = pgEnum('video_type', [
  'tutorial',
  'review',
  'vlog',
  'shorts',
  'podcast',
  'other',
])

export const competitorStatusEnum = pgEnum('competitor_status', ['active', 'paused', 'archived'])

export const contentSourceEnum = pgEnum('content_source', [
  'youtube_channel',
  'blog',
  'podcast',
  'twitter_user',
  'reddit',
])

// Ideas table - quick capture
export const ideas = pgTable(
  'ideas',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    content: text('content').notNull(), // The raw idea text
    type: text('type', { enum: ['idea', 'transcript', 'url'] })
      .default('idea')
      .notNull(),
    status: ideaStatusEnum('status').default('draft').notNull(),
    videoType: videoTypeEnum('video_type'),
    source: text('source'), // Where the idea came from (e.g., "voice", "paste", "manual")
    metadata: jsonb('metadata'), // Any additional data (e.g., voice recording URL)
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('ideas_user_id_idx').on(table.userId),
      statusIdx: index('ideas_status_idx').on(table.status),
      createdAtIdx: index('ideas_created_at_idx').on(table.createdAt),
    }
  }
)

// Generated content for ideas
export const generatedContent = pgTable(
  'generated_content',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    ideaId: uuid('idea_id')
      .notNull()
      .references(() => ideas.id),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),

    // Multiple title options
    titles: text('titles').array().notNull(), // Array of generated titles
    selectedTitle: text('selected_title'), // User's chosen title

    // Content sections
    outline: text('outline'),
    script: text('script'),
    description: text('description'),
    tags: text('tags').array(),

    // Thumbnail data
    thumbnailPrompts: text('thumbnail_prompts').array(),
    thumbnailUrls: text('thumbnail_urls').array(),
    selectedThumbnail: text('selected_thumbnail'),

    // Generation metadata
    model: text('model').default('claude-3-opus').notNull(),
    promptVersion: text('prompt_version'),
    generationCost: decimal('generation_cost', { precision: 10, scale: 4 }), // in USD

    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      ideaIdIdx: index('generated_content_idea_id_idx').on(table.ideaId),
      userIdIdx: index('generated_content_user_id_idx').on(table.userId),
    }
  }
)

// Competitors to track
export const competitors = pgTable(
  'competitors',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    channelName: text('channel_name').notNull(),
    youtubeChannelId: text('youtube_channel_id').notNull(),
    channelUrl: text('channel_url'),
    trackingKeywords: text('tracking_keywords').array(),
    status: competitorStatusEnum('status').default('active').notNull(),
    metadata: jsonb('metadata'), // subscriber count, etc.
    lastScrapedAt: timestamp('last_scraped_at'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('competitors_user_id_idx').on(table.userId),
      channelIdIdx: index('competitors_channel_id_idx').on(table.youtubeChannelId),
    }
  }
)

// Competitor videos we're tracking
export const competitorVideos = pgTable(
  'competitor_videos',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    competitorId: uuid('competitor_id')
      .notNull()
      .references(() => competitors.id),
    youtubeVideoId: text('youtube_video_id').notNull(),
    title: text('title').notNull(),
    description: text('description'),
    views: integer('views'),
    likes: integer('likes'),
    comments: integer('comments'),
    duration: integer('duration'), // in seconds
    publishedAt: timestamp('published_at').notNull(),
    transcript: text('transcript'),
    tags: text('tags').array(),
    performanceScore: decimal('performance_score', { precision: 5, scale: 2 }), // 0-100
    metadata: jsonb('metadata'), // additional YouTube data
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      competitorIdIdx: index('competitor_videos_competitor_id_idx').on(table.competitorId),
      videoIdIdx: index('competitor_videos_video_id_idx').on(table.youtubeVideoId),
      performanceIdx: index('competitor_videos_performance_idx').on(table.performanceScore),
    }
  }
)

// YouTube credentials for users
export const youtubeCredentials = pgTable(
  'youtube_credentials',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    channelId: text('channel_id').notNull(),
    channelName: text('channel_name'),
    accessToken: text('access_token').notNull(),
    refreshToken: text('refresh_token').notNull(),
    expiresAt: timestamp('expires_at').notNull(),
    scope: text('scope').array(),
    metadata: jsonb('metadata'), // channel stats, etc.
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

// Published videos (linked to ideas)
export const publishedVideos = pgTable(
  'published_videos',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    ideaId: uuid('idea_id')
      .notNull()
      .references(() => ideas.id),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    youtubeVideoId: text('youtube_video_id').notNull(),
    youtubeUrl: text('youtube_url').notNull(),
    title: text('title').notNull(),
    description: text('description'),
    tags: text('tags').array(),
    thumbnailUrl: text('thumbnail_url'),
    publishedAt: timestamp('published_at').notNull(),

    // Performance metrics (updated periodically)
    views: integer('views').default(0),
    likes: integer('likes').default(0),
    comments: integer('comments').default(0),
    watchTime: integer('watch_time'), // in minutes
    ctr: decimal('ctr', { precision: 5, scale: 2 }), // click-through rate %
    avgViewDuration: integer('avg_view_duration'), // in seconds

    lastMetricsUpdate: timestamp('last_metrics_update'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      ideaIdIdx: index('published_videos_idea_id_idx').on(table.ideaId),
      userIdIdx: index('published_videos_user_id_idx').on(table.userId),
      youtubeIdIdx: index('published_videos_youtube_id_idx').on(table.youtubeVideoId),
    }
  }
)

// Content sources for trend discovery
export const contentSources = pgTable(
  'content_sources',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id),
    type: contentSourceEnum('type').notNull(),
    name: text('name').notNull(),
    identifier: text('identifier').notNull(), // URL, username, channel ID, etc.
    rssFeed: text('rss_feed'),
    checkFrequency: text('check_frequency', { enum: ['hourly', 'daily', 'weekly'] })
      .default('daily')
      .notNull(),
    isActive: boolean('is_active').default(true).notNull(),
    lastCheckedAt: timestamp('last_checked_at'),
    metadata: jsonb('metadata'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      userIdIdx: index('content_sources_user_id_idx').on(table.userId),
      typeIdx: index('content_sources_type_idx').on(table.type),
    }
  }
)

// Vector embeddings for semantic search
export const ideaEmbeddings = pgTable(
  'idea_embeddings',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    ideaId: uuid('idea_id')
      .notNull()
      .references(() => ideas.id),
    embedding: vector('embedding', { dimensions: 1536 }), // OpenAI embedding size
    modelVersion: text('model_version').default('text-embedding-3-small').notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => {
    return {
      ideaIdIdx: index('idea_embeddings_idea_id_idx').on(table.ideaId),
    }
  }
)

// Define relations
export const ideasRelations = relations(ideas, ({ one, many }) => ({
  user: one(users, {
    fields: [ideas.userId],
    references: [users.id],
  }),
  generatedContent: one(generatedContent),
  publishedVideo: one(publishedVideos),
  embedding: one(ideaEmbeddings),
}))

export const generatedContentRelations = relations(generatedContent, ({ one }) => ({
  idea: one(ideas, {
    fields: [generatedContent.ideaId],
    references: [ideas.id],
  }),
  user: one(users, {
    fields: [generatedContent.userId],
    references: [users.id],
  }),
}))

export const competitorsRelations = relations(competitors, ({ one, many }) => ({
  user: one(users, {
    fields: [competitors.userId],
    references: [users.id],
  }),
  videos: many(competitorVideos),
}))

export const competitorVideosRelations = relations(competitorVideos, ({ one }) => ({
  competitor: one(competitors, {
    fields: [competitorVideos.competitorId],
    references: [competitors.id],
  }),
}))

export const youtubeCredentialsRelations = relations(youtubeCredentials, ({ one }) => ({
  user: one(users, {
    fields: [youtubeCredentials.userId],
    references: [users.id],
  }),
}))

export const publishedVideosRelations = relations(publishedVideos, ({ one }) => ({
  idea: one(ideas, {
    fields: [publishedVideos.ideaId],
    references: [ideas.id],
  }),
  user: one(users, {
    fields: [publishedVideos.userId],
    references: [users.id],
  }),
}))

export const contentSourcesRelations = relations(contentSources, ({ one }) => ({
  user: one(users, {
    fields: [contentSources.userId],
    references: [users.id],
  }),
}))

export const ideaEmbeddingsRelations = relations(ideaEmbeddings, ({ one }) => ({
  idea: one(ideas, {
    fields: [ideaEmbeddings.ideaId],
    references: [ideas.id],
  }),
}))

// Type exports
export type Idea = typeof ideas.$inferSelect
export type NewIdea = typeof ideas.$inferInsert
export type GeneratedContent = typeof generatedContent.$inferSelect
export type NewGeneratedContent = typeof generatedContent.$inferInsert
export type Competitor = typeof competitors.$inferSelect
export type NewCompetitor = typeof competitors.$inferInsert
export type CompetitorVideo = typeof competitorVideos.$inferSelect
export type NewCompetitorVideo = typeof competitorVideos.$inferInsert
export type YouTubeCredentials = typeof youtubeCredentials.$inferSelect
export type NewYouTubeCredentials = typeof youtubeCredentials.$inferInsert
export type PublishedVideo = typeof publishedVideos.$inferSelect
export type NewPublishedVideo = typeof publishedVideos.$inferInsert
export type ContentSource = typeof contentSources.$inferSelect
export type NewContentSource = typeof contentSources.$inferInsert
export type IdeaEmbedding = typeof ideaEmbeddings.$inferSelect
export type NewIdeaEmbedding = typeof ideaEmbeddings.$inferInsert
