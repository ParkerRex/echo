import { google } from 'googleapis'
import { OAuth2Client } from 'google-auth-library'
import { getEnv } from '../types/env'
import { db } from '../db/client'
import { videoMetadata, videos, users, youtubeCredentials } from '../db/schema'
import { eq, and } from 'drizzle-orm'
import { StorageService } from './storage.service'

const env = getEnv()

export interface YouTubeUploadOptions {
  videoId: string
  userId: string
  title: string
  description: string
  tags: string[]
  categoryId?: string
  privacyStatus?: 'private' | 'unlisted' | 'public'
  thumbnailUrl?: string
  publishAt?: Date
}

export interface YouTubeCredentials {
  accessToken: string
  refreshToken: string
  expiresAt: Date
}

export class YouTubeService {
  private oauth2Client: OAuth2Client
  private storageService: StorageService

  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      env.GOOGLE_CLIENT_ID,
      env.GOOGLE_CLIENT_SECRET,
      `${env.PUBLIC_URL || 'http://localhost:3000'}/api/youtube/callback`
    )
    this.storageService = new StorageService()
  }

  /**
   * Get OAuth URL for YouTube authorization
   */
  getAuthUrl(userId: string, videoId?: string): string {
    const scopes = [
      'https://www.googleapis.com/auth/youtube.upload',
      'https://www.googleapis.com/auth/youtube',
      'https://www.googleapis.com/auth/youtubepartner',
    ]

    const state = Buffer.from(
      JSON.stringify({ userId, videoId, timestamp: Date.now() })
    ).toString('base64')

    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes,
      state,
      prompt: 'consent', // Force consent to get refresh token
    })
  }

  /**
   * Handle OAuth callback and store credentials
   */
  async handleCallback(code: string, state: string): Promise<{ userId: string; videoId?: string }> {
    // Decode state
    const stateData = JSON.parse(Buffer.from(state, 'base64').toString())

    // Exchange code for tokens
    const { tokens } = await this.oauth2Client.getToken(code)
    this.oauth2Client.setCredentials(tokens)

    // Get channel info
    const youtube = google.youtube({ version: 'v3', auth: this.oauth2Client })
    const channelResponse = await youtube.channels.list({
      part: ['snippet'],
      mine: true,
    })

    const channel = channelResponse.data.items?.[0]

    // Store credentials in database
    await db
      .insert(youtubeCredentials)
      .values({
        userId: stateData.userId,
        channelId: channel?.id || '',
        channelName: channel?.snippet?.title || '',
        accessToken: tokens.access_token!,
        refreshToken: tokens.refresh_token!,
        expiresAt: new Date(tokens.expiry_date!),
        scope: tokens.scope?.split(' ') || [],
      })
      .onConflictDoUpdate({
        target: youtubeCredentials.userId,
        set: {
          accessToken: tokens.access_token!,
          refreshToken: tokens.refresh_token!,
          expiresAt: new Date(tokens.expiry_date!),
          updatedAt: new Date(),
        },
      })

    return stateData
  }

  /**
   * Upload video to YouTube
   */
  async uploadVideo(options: YouTubeUploadOptions): Promise<string> {
    // Get user's YouTube credentials
    const credentials = await this.getCredentials(options.userId)
    if (!credentials) {
      throw new Error('YouTube account not connected')
    }

    // Set credentials
    this.oauth2Client.setCredentials({
      access_token: credentials.accessToken,
      refresh_token: credentials.refreshToken,
    })

    // Check if token needs refresh
    if (new Date() >= credentials.expiresAt) {
      await this.refreshToken((credentials as any).userId)
    }

    const youtube = google.youtube({ version: 'v3', auth: this.oauth2Client })

    // Get video file info
    const video = await db.query.videos.findFirst({
      where: eq(videos.id, options.videoId),
    })

    if (!video) {
      throw new Error('Video not found')
    }

    // Download video file
    const videoStream = await this.storageService.getFileStream(video.fileUrl)

    // Upload video
    const uploadResponse = await youtube.videos.insert({
      part: ['snippet', 'status'],
      requestBody: {
        snippet: {
          title: options.title,
          description: options.description,
          tags: options.tags,
          categoryId: options.categoryId || '22', // People & Blogs default
        },
        status: {
          privacyStatus: options.privacyStatus || 'private',
          publishAt: options.publishAt?.toISOString(),
        },
      },
      media: {
        body: videoStream,
      },
    })

    const youtubeVideoId = uploadResponse.data.id!

    // Upload thumbnail if provided
    if (options.thumbnailUrl) {
      try {
        const thumbnailStream = await this.storageService.getFileStream(options.thumbnailUrl)
        await youtube.thumbnails.set({
          videoId: youtubeVideoId,
          media: {
            body: thumbnailStream,
          },
        })
      } catch (error) {
        console.error('Failed to upload thumbnail:', error)
      }
    }

    // TODO: Store YouTube video ID in a related table or video metadata
    console.log(`Video uploaded to YouTube: ${youtubeVideoId}`)

    return youtubeVideoId
  }

  /**
   * Update video metadata on YouTube
   */
  async updateVideo(
    videoId: string,
    userId: string,
    updates: {
      title?: string
      description?: string
      tags?: string[]
      categoryId?: string
      privacyStatus?: 'private' | 'unlisted' | 'public'
    }
  ): Promise<void> {
    const credentials = await this.getCredentials(userId)
    if (!credentials) {
      throw new Error('YouTube account not connected')
    }

    this.oauth2Client.setCredentials({
      access_token: credentials.accessToken,
      refresh_token: credentials.refreshToken,
    })

    const youtube = google.youtube({ version: 'v3', auth: this.oauth2Client })

    // Get current video data
    const currentVideo = await youtube.videos.list({
      part: ['snippet', 'status'],
      id: [videoId],
    })

    const videoData = currentVideo.data.items?.[0]
    if (!videoData) {
      throw new Error('Video not found on YouTube')
    }

    // Update video
    await youtube.videos.update({
      part: ['snippet', 'status'],
      requestBody: {
        id: videoId,
        snippet: {
          ...videoData.snippet,
          title: updates.title || videoData.snippet?.title,
          description: updates.description || videoData.snippet?.description,
          tags: updates.tags || videoData.snippet?.tags,
          categoryId: updates.categoryId || videoData.snippet?.categoryId,
        },
        status: {
          ...videoData.status,
          privacyStatus: updates.privacyStatus || videoData.status?.privacyStatus,
        },
      },
    })
  }

  /**
   * Get video analytics
   */
  async getVideoAnalytics(videoId: string, userId: string): Promise<any> {
    const credentials = await this.getCredentials(userId)
    if (!credentials) {
      throw new Error('YouTube account not connected')
    }

    this.oauth2Client.setCredentials({
      access_token: credentials.accessToken,
      refresh_token: credentials.refreshToken,
    })

    const youtube = google.youtube({ version: 'v3', auth: this.oauth2Client })
    const youtubeAnalytics = google.youtubeAnalytics({ version: 'v2', auth: this.oauth2Client })

    // Get video details
    const videoResponse = await youtube.videos.list({
      part: ['statistics', 'snippet'],
      id: [videoId],
    })

    const video = videoResponse.data.items?.[0]

    // Get analytics data (last 30 days)
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)

    const analyticsResponse = await youtubeAnalytics.reports.query({
      ids: 'channel==MINE',
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
      metrics: 'views,estimatedMinutesWatched,averageViewDuration,subscribersGained',
      dimensions: 'video',
      filters: `video==${videoId}`,
    })

    return {
      statistics: video?.statistics,
      snippet: video?.snippet,
      analytics: analyticsResponse.data,
    }
  }

  /**
   * Get user's YouTube credentials from database
   */
  private async getCredentials(userId: string): Promise<YouTubeCredentials | null> {
    const creds = await db.query.youtubeCredentials.findFirst({
      where: eq(youtubeCredentials.userId, userId),
    })

    if (!creds) return null

    return {
      accessToken: creds.accessToken,
      refreshToken: creds.refreshToken,
      expiresAt: creds.expiresAt,
    }
  }

  /**
   * Refresh access token
   */
  private async refreshToken(userId: string): Promise<void> {
    const credentials = await this.getCredentials(userId)
    if (!credentials?.refreshToken) {
      throw new Error('No refresh token available')
    }

    this.oauth2Client.setCredentials({
      refresh_token: credentials.refreshToken,
    })

    const { credentials: newTokens } = await this.oauth2Client.refreshAccessToken()

    // Update stored credentials
    await db
      .update(youtubeCredentials)
      .set({
        accessToken: newTokens.access_token!,
        expiresAt: new Date(newTokens.expiry_date!),
        updatedAt: new Date(),
      })
      .where(eq(youtubeCredentials.userId, userId))
  }

  /**
   * Disconnect YouTube account
   */
  async disconnect(userId: string): Promise<void> {
    await db.delete(youtubeCredentials).where(eq(youtubeCredentials.userId, userId))
  }

  /**
   * Check if user has connected YouTube
   */
  async isConnected(userId: string): Promise<boolean> {
    const creds = await this.getCredentials(userId)
    return !!creds
  }
}

