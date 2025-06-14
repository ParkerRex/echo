import { z } from 'zod'

/**
 * Common validation schemas
 */
export const commonSchemas = {
  uuid: z.string().uuid(),
  email: z.string().email(),
  url: z.string().url(),
  pagination: z.object({
    limit: z.number().min(1).max(100).default(20),
    offset: z.number().min(0).default(0),
  }),
  sorting: z.object({
    sortBy: z.string().optional(),
    sortOrder: z.enum(['asc', 'desc']).default('desc'),
  }),
  dateRange: z.object({
    startDate: z.date().optional(),
    endDate: z.date().optional(),
  }),
}

/**
 * File validation schemas
 */
export const fileSchemas = {
  videoUpload: z.object({
    fileName: z.string().min(1).max(255),
    fileSize: z
      .number()
      .min(1)
      .max(5 * 1024 * 1024 * 1024), // 5GB max
    mimeType: z.enum([
      'video/mp4',
      'video/quicktime',
      'video/x-msvideo',
      'video/x-matroska',
      'video/webm',
      'video/mpeg',
    ]),
  }),
  imageUpload: z.object({
    fileName: z.string().min(1).max(255),
    fileSize: z
      .number()
      .min(1)
      .max(10 * 1024 * 1024), // 10MB max
    mimeType: z.enum(['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']),
  }),
}

/**
 * Video processing configuration schema
 */
export const videoConfigSchema = z.object({
  generateTranscript: z.boolean().default(true),
  generateSubtitles: z.boolean().default(true),
  extractMetadata: z.boolean().default(true),
  generateThumbnail: z.boolean().default(true),
  targetResolutions: z
    .array(z.enum(['360p', '480p', '720p', '1080p', '1440p', '2160p']))
    .optional(),
  outputFormat: z.enum(['mp4', 'webm']).default('mp4'),
  watermark: z
    .object({
      enabled: z.boolean(),
      position: z.enum(['top-left', 'top-right', 'bottom-left', 'bottom-right']),
      opacity: z.number().min(0).max(1),
    })
    .optional(),
})

/**
 * Batch operation schemas
 */
export const batchSchemas = {
  batchIds: z.object({
    ids: z.array(commonSchemas.uuid).min(1).max(100),
  }),
  batchOperation: z.object({
    operation: z.enum(['delete', 'publish', 'unpublish', 'reprocess']),
    ids: z.array(commonSchemas.uuid).min(1).max(100),
  }),
}

/**
 * Filter schemas
 */
export const filterSchemas = {
  videoFilter: z.object({
    status: z.enum(['draft', 'processing', 'published', 'failed']).optional(),
    mimeType: z.string().optional(),
    minDuration: z.number().positive().optional(),
    maxDuration: z.number().positive().optional(),
    minSize: z.number().positive().optional(),
    maxSize: z.number().positive().optional(),
    hasTranscript: z.boolean().optional(),
    hasSubtitles: z.boolean().optional(),
    search: z.string().optional(),
    tags: z.array(z.string()).optional(),
  }),
}

/**
 * Validate and sanitize file name
 */
export function sanitizeFileName(fileName: string): string {
  // Remove any path components
  const baseName = fileName.split(/[/\\]/).pop() || fileName

  // Replace problematic characters
  return baseName
    .replace(/[^a-zA-Z0-9.-]/g, '_')
    .replace(/_{2,}/g, '_')
    .replace(/^_|_$/g, '')
    .substring(0, 255)
}

/**
 * Validate file extension
 */
export function validateFileExtension(fileName: string, allowedExtensions: string[]): boolean {
  const ext = fileName.split('.').pop()?.toLowerCase()
  return ext ? allowedExtensions.includes(ext) : false
}

/**
 * Create a paginated response schema
 */
export function paginatedResponse<T extends z.ZodType>(itemSchema: T) {
  return z.object({
    items: z.array(itemSchema),
    totalCount: z.number(),
    hasMore: z.boolean(),
    nextOffset: z.number().optional(),
  })
}

/**
 * Safe parse with detailed error messages
 */
export function safeParse<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: string[] } {
  const result = schema.safeParse(data)

  if (result.success) {
    return { success: true, data: result.data }
  }

  const errors = result.error.issues.map((issue) => {
    const path = issue.path.join('.')
    return path ? `${path}: ${issue.message}` : issue.message
  })

  return { success: false, errors }
}
