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

// Users table (managed by Supabase Auth, but we reference it)
export const users = pgTable('users', {
  id: uuid('id').primaryKey(),
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

// Define relations
export const usersRelations = relations(users, ({ many }) => ({
  videos: many(videos),
  videoJobs: many(videoJobs),
  chats: many(chats),
}))

export const videosRelations = relations(videos, ({ one, many }) => ({
  user: one(users, {
    fields: [videos.userId],
    references: [users.id],
  }),
  jobs: many(videoJobs),
  metadata: one(videoMetadata),
  chats: many(chats),
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
