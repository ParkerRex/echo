import { exec } from 'child_process'
import { promisify } from 'util'
import { writeFile, unlink, readFile } from 'fs/promises'
import { tmpdir } from 'os'
import { join } from 'path'
import { randomUUID } from 'crypto'

const execAsync = promisify(exec)

export interface VideoMetadata {
  duration: number // seconds
  width?: number
  height?: number
  fps?: number
  codec?: string
  bitrate?: number
}

export class FFmpegService {
  /**
   * Extract metadata from video
   */
  async extractMetadata(videoUrl: string): Promise<VideoMetadata> {
    const tempFile = await this.downloadToTemp(videoUrl)

    try {
      const { stdout } = await execAsync(
        `ffprobe -v quiet -print_format json -show_format -show_streams "${tempFile}"`
      )

      const data = JSON.parse(stdout)
      const videoStream = data.streams?.find((s: any) => s.codec_type === 'video')

      return {
        duration: parseFloat(data.format?.duration || '0'),
        width: videoStream?.width,
        height: videoStream?.height,
        fps: videoStream?.r_frame_rate ? eval(videoStream.r_frame_rate) : undefined,
        codec: videoStream?.codec_name,
        bitrate: parseInt(data.format?.bit_rate || '0'),
      }
    } finally {
      await this.cleanup(tempFile)
    }
  }

  /**
   * Extract audio from video and upload to storage
   */
  async extractAudio(videoUrl: string, userId?: string): Promise<string> {
    const tempVideoFile = await this.downloadToTemp(videoUrl)
    const tempAudioFile = join(tmpdir(), `${randomUUID()}.mp3`)

    try {
      // Extract audio using FFmpeg
      await execAsync(`ffmpeg -i "${tempVideoFile}" -vn -acodec mp3 -ab 128k "${tempAudioFile}"`)

      // Upload to storage if userId provided
      if (userId) {
        const { StorageService } = await import('../../services/storage.service')
        const storageService = new StorageService()
        
        const audioBuffer = await readFile(tempAudioFile)
        const audioUrl = await storageService.uploadFile({
          fileName: `audio-${Date.now()}.mp3`,
          data: audioBuffer,
          mimeType: 'audio/mpeg',
          userId,
        })
        
        await this.cleanup(tempAudioFile)
        return audioUrl
      }

      // Return local path if no userId
      return tempAudioFile
    } catch (error) {
      await this.cleanup(tempAudioFile)
      throw error
    } finally {
      await this.cleanup(tempVideoFile)
    }
  }

  /**
   * Generate thumbnail from video
   */
  async generateThumbnail(videoUrl: string, timestamp: number = 5, userId?: string): Promise<string> {
    const tempVideoFile = await this.downloadToTemp(videoUrl)
    const tempThumbFile = join(tmpdir(), `${randomUUID()}.jpg`)

    try {
      await execAsync(
        `ffmpeg -i "${tempVideoFile}" -ss ${timestamp} -vframes 1 -q:v 2 "${tempThumbFile}"`
      )

      // Upload to storage if userId provided
      if (userId) {
        const { StorageService } = await import('../../services/storage.service')
        const storageService = new StorageService()
        
        const thumbBuffer = await readFile(tempThumbFile)
        const thumbUrl = await storageService.uploadFile({
          fileName: `thumbnail-${Date.now()}.jpg`,
          data: thumbBuffer,
          mimeType: 'image/jpeg',
          userId,
        })
        
        await this.cleanup(tempThumbFile)
        return thumbUrl
      }

      return tempThumbFile
    } catch (error) {
      await this.cleanup(tempThumbFile)
      throw error
    } finally {
      await this.cleanup(tempVideoFile)
    }
  }

  /**
   * Generate multiple thumbnails
   */
  async generateThumbnails(videoUrl: string, count: number = 4): Promise<string[]> {
    const metadata = await this.extractMetadata(videoUrl)
    const interval = metadata.duration / (count + 1)
    const thumbnails: string[] = []

    for (let i = 1; i <= count; i++) {
      const timestamp = interval * i
      const thumbnail = await this.generateThumbnail(videoUrl, timestamp)
      thumbnails.push(thumbnail)
    }

    return thumbnails
  }

  /**
   * Convert video format
   */
  async convertVideo(
    videoUrl: string,
    outputFormat: string,
    options?: {
      resolution?: string // e.g., "1280x720"
      bitrate?: string // e.g., "1M"
      fps?: number
    }
  ): Promise<string> {
    const tempInputFile = await this.downloadToTemp(videoUrl)
    const tempOutputFile = join(tmpdir(), `${randomUUID()}.${outputFormat}`)

    let command = `ffmpeg -i "${tempInputFile}"`

    if (options?.resolution) {
      command += ` -s ${options.resolution}`
    }
    if (options?.bitrate) {
      command += ` -b:v ${options.bitrate}`
    }
    if (options?.fps) {
      command += ` -r ${options.fps}`
    }

    command += ` "${tempOutputFile}"`

    try {
      await execAsync(command)
      return tempOutputFile
    } catch (error) {
      await this.cleanup(tempOutputFile)
      throw error
    } finally {
      await this.cleanup(tempInputFile)
    }
  }

  /**
   * Extract video segment
   */
  async extractSegment(videoUrl: string, startTime: number, duration: number): Promise<string> {
    const tempInputFile = await this.downloadToTemp(videoUrl)
    const tempOutputFile = join(tmpdir(), `${randomUUID()}.mp4`)

    try {
      await execAsync(
        `ffmpeg -i "${tempInputFile}" -ss ${startTime} -t ${duration} -c copy "${tempOutputFile}"`
      )

      return tempOutputFile
    } catch (error) {
      await this.cleanup(tempOutputFile)
      throw error
    } finally {
      await this.cleanup(tempInputFile)
    }
  }

  /**
   * Add subtitles to video
   */
  async addSubtitles(videoUrl: string, subtitlesPath: string): Promise<string> {
    const tempVideoFile = await this.downloadToTemp(videoUrl)
    const tempOutputFile = join(tmpdir(), `${randomUUID()}.mp4`)

    try {
      await execAsync(
        `ffmpeg -i "${tempVideoFile}" -vf subtitles="${subtitlesPath}" "${tempOutputFile}"`
      )

      return tempOutputFile
    } catch (error) {
      await this.cleanup(tempOutputFile)
      throw error
    } finally {
      await this.cleanup(tempVideoFile)
    }
  }

  /**
   * Download file to temp directory
   */
  private async downloadToTemp(url: string): Promise<string> {
    // In production, this would download from URL
    // For now, assume it's a local path or implement download logic

    if (url.startsWith('http')) {
      const response = await fetch(url)
      const buffer = await response.arrayBuffer()
      const tempFile = join(tmpdir(), `${randomUUID()}.tmp`)
      await writeFile(tempFile, Buffer.from(buffer))
      return tempFile
    }

    return url // Assume local path
  }

  /**
   * Clean up temporary file
   */
  private async cleanup(filePath: string): Promise<void> {
    try {
      await unlink(filePath)
    } catch (error) {
      // Ignore cleanup errors
    }
  }

  /**
   * Check if FFmpeg is available
   */
  async checkFFmpeg(): Promise<boolean> {
    try {
      await execAsync('ffmpeg -version')
      return true
    } catch {
      return false
    }
  }
}
