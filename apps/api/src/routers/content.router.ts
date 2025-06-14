import { z } from 'zod'
import { router, publicProcedure, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { db, generatedContent, ideas } from '../db/client'
import { eq, and } from 'drizzle-orm'
import { generateWithClaude } from '../services/ai/claude.service'

export const contentRouter = router({
  // Generate content for an idea
  generate: protectedProcedure
    .input(
      z.object({
        ideaId: z.string().uuid(),
        regenerate: z.enum(['titles', 'script', 'description', 'thumbnail']).optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const userId = ctx.user.id

      // Get the idea
      const idea = await db.query.ideas.findFirst({
        where: and(eq(ideas.id, input.ideaId), eq(ideas.userId, userId)),
        with: {
          generatedContent: true,
        },
      })

      if (!idea) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Idea not found',
        })
      }

      // Check if content exists
      let content = idea.generatedContent

      // Generate or regenerate content
      const generated = await generateWithClaude(idea, input.regenerate)

      if (content) {
        // Update existing content
        const [updated] = await db
          .update(generatedContent)
          .set({
            ...generated,
            generationCost: generated.generationCost?.toString(),
            updatedAt: new Date(),
          })
          .where(eq(generatedContent.id, content.id))
          .returning()

        // Update idea status
        await db
          .update(ideas)
          .set({
            status: 'ready',
            updatedAt: new Date(),
          })
          .where(eq(ideas.id, input.ideaId))

        return updated
      } else {
        // Create new content
        const [created] = await db
          .insert(generatedContent)
          .values({
            ideaId: input.ideaId,
            userId,
            ...generated,
            generationCost: generated.generationCost?.toString(),
          })
          .returning()

        // Update idea status
        await db
          .update(ideas)
          .set({
            status: 'ready',
            updatedAt: new Date(),
          })
          .where(eq(ideas.id, input.ideaId))

        return created
      }
    }),

  // Get content for an idea
  get: protectedProcedure
    .input(z.object({ ideaId: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const content = await db.query.generatedContent.findFirst({
        where: and(eq(generatedContent.ideaId, input.ideaId), eq(generatedContent.userId, userId)),
      })

      return content
    }),

  // Update content (for edits)
  update: protectedProcedure
    .input(
      z.object({
        id: z.string().uuid(),
        selectedTitle: z.string().optional(),
        titles: z.array(z.string()).optional(),
        outline: z.string().optional(),
        script: z.string().optional(),
        description: z.string().optional(),
        tags: z.array(z.string()).optional(),
        selectedThumbnail: z.string().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const userId = ctx.user.id
      const { id, ...updates } = input

      const [updated] = await db
        .update(generatedContent)
        .set({
          ...updates,
          updatedAt: new Date(),
        })
        .where(and(eq(generatedContent.id, id), eq(generatedContent.userId, userId)))
        .returning()

      if (!updated) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Content not found',
        })
      }

      return updated
    }),

  // Export content in various formats
  export: protectedProcedure
    .input(
      z.object({
        contentId: z.string().uuid(),
        format: z.enum(['json', 'markdown', 'text']).default('json'),
      })
    )
    .query(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const content = await db.query.generatedContent.findFirst({
        where: and(eq(generatedContent.id, input.contentId), eq(generatedContent.userId, userId)),
        with: {
          idea: true,
        },
      })

      if (!content) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Content not found',
        })
      }

      switch (input.format) {
        case 'markdown':
          return {
            format: 'markdown',
            content: `# ${content.selectedTitle || content.titles?.[0] || 'Untitled'}

## Original Idea
${content.idea.content}

## Script
${content.script}

## Description
${content.description}

## Tags
${content.tags?.join(', ')}
`,
          }

        case 'text':
          return {
            format: 'text',
            content: `Title: ${content.selectedTitle || content.titles?.[0] || 'Untitled'}

Script:
${content.script}

Description:
${content.description}

Tags: ${content.tags?.join(', ')}`,
          }

        default:
          return {
            format: 'json',
            content: {
              title: content.selectedTitle || content.titles?.[0],
              allTitles: content.titles,
              script: content.script,
              description: content.description,
              tags: content.tags,
              idea: content.idea.content,
              generatedAt: content.createdAt,
            },
          }
      }
    }),
})
