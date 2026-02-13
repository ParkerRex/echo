import { supabase } from '../lib/auth/supabase'
import { getEnv } from '../types/env'
import { randomUUID } from 'crypto'

const env = getEnv()

export interface UploadFileOptions {
  fileName: string
  data: Buffer | Blob | File
  mimeType: string
  userId: string
}

export interface PresignedUrlOptions {
  fileName: string
  mimeType: string
  userId: string
  expiresIn?: number // seconds
}

export class StorageService {
  private bucket: string

  constructor() {
    this.bucket = env.STORAGE_BUCKET || 'uploads'
  }

  /**
   * Upload a file to storage
   */
  async uploadFile(options: UploadFileOptions): Promise<string> {
    const { fileName, data, mimeType, userId } = options
    const fileKey = this.generateFileKey(userId, fileName)

    const { error } = await supabase.storage.from(this.bucket).upload(fileKey, data, {
      contentType: mimeType,
      upsert: false,
    })

    if (error) {
      throw new Error(`Failed to upload file: ${error.message}`)
    }

    return this.getPublicUrl(fileKey)
  }

  /**
   * Delete a file from storage
   */
  async deleteFile(fileUrl: string): Promise<void> {
    const fileKey = this.extractFileKey(fileUrl)

    const { error } = await supabase.storage.from(this.bucket).remove([fileKey])

    if (error) {
      console.error('Failed to delete file:', error)
      // Don't throw - file might already be deleted
    }
  }

  /**
   * Get a presigned upload URL for direct client uploads
   */
  async getPresignedUploadUrl(options: PresignedUrlOptions): Promise<string> {
    const { fileName, userId, expiresIn = 3600 } = options
    const fileKey = this.generateFileKey(userId, fileName)

    const { data, error } = await supabase.storage.from(this.bucket).createSignedUploadUrl(fileKey)

    if (error || !data) {
      throw new Error(`Failed to create upload URL: ${error?.message}`)
    }

    return data.signedUrl
  }

  /**
   * Get a presigned URL for file access
   */
  async getPresignedUrl(fileKey: string, expiresIn = 3600): Promise<string> {
    const { data, error } = await supabase.storage
      .from(this.bucket)
      .createSignedUrl(fileKey, expiresIn)

    if (error || !data) {
      throw new Error(`Failed to create signed URL: ${error?.message}`)
    }

    return data.signedUrl
  }

  /**
   * Generate a unique file key
   */
  generateFileKey(userId: string, fileName: string): string {
    const timestamp = Date.now()
    const uuid = randomUUID()
    const extension = fileName.split('.').pop() || 'bin'
    return `${userId}/${timestamp}-${uuid}.${extension}`
  }

  /**
   * Get the public URL for a file
   */
  getPublicUrl(fileKey: string): string {
    const { data } = supabase.storage.from(this.bucket).getPublicUrl(fileKey)

    return data.publicUrl
  }

  /**
   * Extract file key from URL
   */
  private extractFileKey(fileUrl: string): string {
    // Extract the file key from the full URL
    const url = new URL(fileUrl)
    const pathParts = url.pathname.split('/')
    const bucketIndex = pathParts.indexOf(this.bucket)

    if (bucketIndex === -1) {
      throw new Error('Invalid file URL')
    }

    return pathParts.slice(bucketIndex + 1).join('/')
  }

  /**
   * Check if file exists
   */
  async fileExists(fileKey: string): Promise<boolean> {
    const { data, error } = await supabase.storage
      .from(this.bucket)
      .list(fileKey.split('/').slice(0, -1).join('/'), {
        search: fileKey.split('/').pop(),
      })

    return !error && data.length > 0
  }

  /**
   * Get file metadata
   */
  async getFileMetadata(fileKey: string): Promise<any> {
    const { data, error } = await supabase.storage
      .from(this.bucket)
      .list(fileKey.split('/').slice(0, -1).join('/'), {
        search: fileKey.split('/').pop(),
      })

    if (error || !data.length) {
      throw new Error('File not found')
    }

    return data[0]
  }

  /**
   * Get file as a readable stream
   */
  async getFileStream(fileUrl: string): Promise<NodeJS.ReadableStream> {
    // If it's a Supabase URL, download it
    if (fileUrl.includes('supabase')) {
      const fileKey = this.extractFileKey(fileUrl)
      const { data, error } = await supabase.storage.from(this.bucket).download(fileKey)

      if (error || !data) {
        throw new Error(`Failed to download file: ${error?.message}`)
      }

      // Convert Blob to Node.js stream
      const stream = data.stream()
      return stream as unknown as NodeJS.ReadableStream
    }

    // For other URLs, fetch and return stream
    const response = await fetch(fileUrl)
    if (!response.ok) {
      throw new Error(`Failed to fetch file: ${response.statusText}`)
    }

    return response.body as unknown as NodeJS.ReadableStream
  }
}
