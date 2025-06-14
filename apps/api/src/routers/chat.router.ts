import { z } from 'zod'
import { router, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { eq, and, desc } from 'drizzle-orm'
import { chats, chatMessages, type NewChat, type NewChatMessage } from '../db/schema'
import { AIService } from '../services/ai.service'

const aiService = new AIService()

export const chatRouter = router({
  /**
   * Create a new chat
   */
  create: protectedProcedure
    .input(
      z.object({
        title: z.string().min(1).max(255),
        videoId: z.string().uuid().optional(),
        initialMessage: z.string().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Create chat
      const [chat] = await db
        .insert(chats)
        .values({
          userId: user.id,
          title: input.title,
          videoId: input.videoId,
          metadata: {},
        } satisfies NewChat)
        .returning()

      // Add initial message if provided
      if (input.initialMessage && chat) {
        await db.insert(chatMessages).values([
          {
            chatId: chat.id,
            role: 'user',
            content: input.initialMessage,
          },
        ] satisfies NewChatMessage[])
      }

      return chat
    }),

  /**
   * Get a specific chat with messages
   */
  getById: protectedProcedure
    .input(
      z.object({
        chatId: z.string().uuid(),
        includeMessages: z.boolean().default(true),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const chat = await db.query.chats.findFirst({
        where: and(eq(chats.id, input.chatId), eq(chats.userId, user.id)),
        with: {
          messages: input.includeMessages
            ? {
                orderBy: [desc(chatMessages.createdAt)],
              }
            : undefined,
          video: {
            with: {
              metadata: true,
            },
          },
        },
      })

      if (!chat) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Chat not found',
        })
      }

      return chat
    }),

  /**
   * List user's chats
   */
  list: protectedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0),
        videoId: z.string().uuid().optional(),
        isActive: z.boolean().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const where = and(
        eq(chats.userId, user.id),
        input.videoId ? eq(chats.videoId, input.videoId) : undefined,
        input.isActive !== undefined ? eq(chats.isActive, input.isActive) : undefined
      )

      const [items, totalCount] = await Promise.all([
        db.query.chats.findMany({
          where,
          limit: input.limit,
          offset: input.offset,
          orderBy: [desc(chats.updatedAt)],
          with: {
            messages: {
              orderBy: [desc(chatMessages.createdAt)],
              limit: 1, // Just get the last message
            },
            video: true,
          },
        }),
        db.$count(chats, where),
      ])

      return {
        items,
        totalCount,
        hasMore: input.offset + items.length < totalCount,
      }
    }),

  /**
   * Send a message to a chat
   */
  sendMessage: protectedProcedure
    .input(
      z.object({
        chatId: z.string().uuid(),
        content: z.string().min(1),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Verify chat ownership
      const chat = await db.query.chats.findFirst({
        where: and(eq(chats.id, input.chatId), eq(chats.userId, user.id)),
        with: {
          messages: {
            orderBy: [desc(chatMessages.createdAt)],
            limit: 10, // Get recent context
          },
          video: {
            with: {
              metadata: true,
            },
          },
        },
      })

      if (!chat) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Chat not found',
        })
      }

      // Add user message
      const [userMessage] = await db
        .insert(chatMessages)
        .values({
          chatId: chat.id,
          role: 'user',
          content: input.content,
        } satisfies NewChatMessage)
        .returning()

      // Generate AI response
      const context = {
        videoTitle: chat.video?.metadata?.title,
        videoDescription: chat.video?.metadata?.description,
        transcript: chat.video?.metadata?.transcript,
        recentMessages: chat.messages.reverse(),
      }

      const aiResponse = await aiService.generateChatResponse(input.content, context)

      // Add AI message
      const [assistantMessage] = await db
        .insert(chatMessages)
        .values({
          chatId: chat.id,
          role: 'assistant',
          content: aiResponse.content,
          metadata: {
            model: aiResponse.model,
            tokens: aiResponse.tokens,
          },
        } satisfies NewChatMessage)
        .returning()

      // Update chat timestamp
      await db.update(chats).set({ updatedAt: new Date() }).where(eq(chats.id, chat.id))

      return {
        userMessage,
        assistantMessage,
      }
    }),

  /**
   * Stream a message response
   */
  streamMessage: protectedProcedure
    .input(
      z.object({
        chatId: z.string().uuid(),
        content: z.string().min(1),
      })
    )
    .subscription(async function* ({ ctx, input }) {
      const { db, user } = ctx

      // Verify chat ownership
      const chat = await db.query.chats.findFirst({
        where: and(eq(chats.id, input.chatId), eq(chats.userId, user.id)),
        with: {
          messages: {
            orderBy: [desc(chatMessages.createdAt)],
            limit: 10,
          },
          video: {
            with: {
              metadata: true,
            },
          },
        },
      })

      if (!chat) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Chat not found',
        })
      }

      // Add user message
      const [userMessage] = await db
        .insert(chatMessages)
        .values({
          chatId: chat.id,
          role: 'user',
          content: input.content,
        } satisfies NewChatMessage)
        .returning()

      yield { type: 'user_message', data: userMessage }

      // Stream AI response
      const context = {
        videoTitle: chat.video?.metadata?.title,
        videoDescription: chat.video?.metadata?.description,
        transcript: chat.video?.metadata?.transcript,
        recentMessages: chat.messages.reverse(),
      }

      let fullContent = ''
      const messageId = crypto.randomUUID()

      for await (const chunk of aiService.streamChatResponse(input.content, context)) {
        fullContent += chunk.content
        yield {
          type: 'assistant_chunk',
          data: {
            id: messageId,
            content: chunk.content,
            isComplete: chunk.isComplete,
          },
        }
      }

      // Save the complete message
      const [assistantMessage] = await db
        .insert(chatMessages)
        .values({
          chatId: chat.id,
          role: 'assistant',
          content: fullContent,
          metadata: {
            model: 'gemini-pro',
            streamedAt: new Date(),
          },
        } satisfies NewChatMessage)
        .returning()

      // Update chat timestamp
      await db.update(chats).set({ updatedAt: new Date() }).where(eq(chats.id, chat.id))

      yield { type: 'complete', data: assistantMessage }
    }),

  /**
   * Update chat title
   */
  updateTitle: protectedProcedure
    .input(
      z.object({
        chatId: z.string().uuid(),
        title: z.string().min(1).max(255),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      const result = await db
        .update(chats)
        .set({
          title: input.title,
          updatedAt: new Date(),
        })
        .where(and(eq(chats.id, input.chatId), eq(chats.userId, user.id)))
        .returning()

      if (!result.length) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Chat not found',
        })
      }

      return result[0]
    }),

  /**
   * Delete a chat
   */
  delete: protectedProcedure
    .input(
      z.object({
        chatId: z.string().uuid(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      const result = await db
        .delete(chats)
        .where(and(eq(chats.id, input.chatId), eq(chats.userId, user.id)))
        .returning()

      if (!result.length) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Chat not found',
        })
      }

      return { success: true }
    }),

  /**
   * Archive/deactivate a chat
   */
  archive: protectedProcedure
    .input(
      z.object({
        chatId: z.string().uuid(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      const result = await db
        .update(chats)
        .set({
          isActive: false,
          updatedAt: new Date(),
        })
        .where(and(eq(chats.id, input.chatId), eq(chats.userId, user.id)))
        .returning()

      if (!result.length) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Chat not found',
        })
      }

      return result[0]
    }),
})
