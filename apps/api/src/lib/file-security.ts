/**
 * File Upload Security and Validation
 * 
 * Provides comprehensive file validation, virus scanning,
 * and security checks for uploaded files.
 */

import crypto from 'crypto'
import { createReadStream } from 'fs'
import { pipeline } from 'stream/promises'

export interface FileValidationOptions {
  maxSizeBytes: number
  allowedMimeTypes: string[]
  allowedExtensions: string[]
  scanForViruses?: boolean
  checkMagicNumbers?: boolean
}

export interface FileValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
  metadata: {
    size: number
    mimeType: string
    extension: string
    hash: string
    isExecutable: boolean
    hasSuspiciousContent: boolean
  }
}

export interface VirusScanResult {
  isClean: boolean
  threats: string[]
  scanEngine: string
  scanTime: number
}

// File type magic numbers for validation
const MAGIC_NUMBERS: Record<string, Buffer> = {
  // Images
  'image/jpeg': Buffer.from([0xFF, 0xD8, 0xFF]),
  'image/png': Buffer.from([0x89, 0x50, 0x4E, 0x47]),
  'image/gif': Buffer.from([0x47, 0x49, 0x46]),
  'image/webp': Buffer.from([0x52, 0x49, 0x46, 0x46]),
  
  // Videos
  'video/mp4': Buffer.from([0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70]), // ftyp
  'video/webm': Buffer.from([0x1A, 0x45, 0xDF, 0xA3]),
  'video/avi': Buffer.from([0x52, 0x49, 0x46, 0x46]),
  'video/quicktime': Buffer.from([0x00, 0x00, 0x00, 0x14, 0x66, 0x74, 0x79, 0x70]),
  
  // Documents
  'application/pdf': Buffer.from([0x25, 0x50, 0x44, 0x46]),
  'application/zip': Buffer.from([0x50, 0x4B, 0x03, 0x04]),
}

// Suspicious file extensions and patterns
const SUSPICIOUS_EXTENSIONS = [
  '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
  '.app', '.dmg', '.pkg', '.deb', '.rpm', '.msi', '.ps1', '.sh'
]

const SUSPICIOUS_PATTERNS = [
  /eval\s*\(/i,
  /exec\s*\(/i,
  /system\s*\(/i,
  /shell_exec/i,
  /passthru/i,
  /file_get_contents/i,
  /base64_decode/i,
  /gzinflate/i,
  /str_rot13/i,
  /<script[^>]*>/i,
  /<iframe[^>]*>/i,
  /javascript:/i,
  /vbscript:/i,
  /onload\s*=/i,
  /onerror\s*=/i,
]

export class FileSecurityValidator {
  private options: FileValidationOptions

  constructor(options: FileValidationOptions) {
    this.options = options
  }

  async validateFile(filePath: string, originalName: string): Promise<FileValidationResult> {
    const errors: string[] = []
    const warnings: string[] = []
    const metadata = await this.extractMetadata(filePath, originalName)

    // Size validation
    if (metadata.size > this.options.maxSizeBytes) {
      errors.push(`File size ${metadata.size} bytes exceeds maximum allowed size ${this.options.maxSizeBytes} bytes`)
    }

    // MIME type validation
    if (!this.options.allowedMimeTypes.includes(metadata.mimeType)) {
      errors.push(`MIME type ${metadata.mimeType} is not allowed`)
    }

    // Extension validation
    if (!this.options.allowedExtensions.includes(metadata.extension)) {
      errors.push(`File extension ${metadata.extension} is not allowed`)
    }

    // Magic number validation
    if (this.options.checkMagicNumbers) {
      const magicNumberValid = await this.validateMagicNumber(filePath, metadata.mimeType)
      if (!magicNumberValid) {
        errors.push('File content does not match declared MIME type (possible file type spoofing)')
      }
    }

    // Executable check
    if (metadata.isExecutable) {
      errors.push('Executable files are not allowed')
    }

    // Suspicious content check
    if (metadata.hasSuspiciousContent) {
      warnings.push('File contains potentially suspicious content patterns')
    }

    // Virus scan
    if (this.options.scanForViruses) {
      try {
        const virusScanResult = await this.scanForViruses(filePath)
        if (!virusScanResult.isClean) {
          errors.push(`Virus detected: ${virusScanResult.threats.join(', ')}`)
        }
      } catch (error) {
        warnings.push('Virus scan failed - file may be unsafe')
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      metadata
    }
  }

  private async extractMetadata(filePath: string, originalName: string) {
    const fs = await import('fs')
    const stats = await fs.promises.stat(filePath)
    const extension = this.getFileExtension(originalName)
    
    // Calculate file hash
    const hash = await this.calculateFileHash(filePath)
    
    // Detect MIME type
    const mimeType = await this.detectMimeType(filePath, extension)
    
    // Check if file is executable
    const isExecutable = this.isExecutableFile(extension, originalName)
    
    // Check for suspicious content
    const hasSuspiciousContent = await this.checkSuspiciousContent(filePath)

    return {
      size: stats.size,
      mimeType,
      extension,
      hash,
      isExecutable,
      hasSuspiciousContent
    }
  }

  private getFileExtension(filename: string): string {
    const match = filename.match(/\.[^.]*$/)
    return match ? match[0].toLowerCase() : ''
  }

  private async calculateFileHash(filePath: string): Promise<string> {
    const hash = crypto.createHash('sha256')
    const stream = createReadStream(filePath)
    
    await pipeline(stream, hash)
    return hash.digest('hex')
  }

  private async detectMimeType(filePath: string, extension: string): Promise<string> {
    // For now, use extension-based detection
    // TODO: Add file-type library for magic number detection

    // Extension-based MIME type detection
    const mimeTypes: Record<string, string> = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.mp4': 'video/mp4',
      '.webm': 'video/webm',
      '.avi': 'video/avi',
      '.mov': 'video/quicktime',
      '.pdf': 'application/pdf',
      '.txt': 'text/plain',
      '.json': 'application/json',
      '.xml': 'application/xml',
    }

    return mimeTypes[extension] || 'application/octet-stream'
  }

  private async validateMagicNumber(filePath: string, mimeType: string): Promise<boolean> {
    const expectedMagic = MAGIC_NUMBERS[mimeType]
    if (!expectedMagic) {
      return true // No magic number to validate
    }

    try {
      const fs = await import('fs')
      const fd = await fs.promises.open(filePath, 'r')
      const buffer = Buffer.alloc(expectedMagic.length)
      await fd.read(buffer, 0, expectedMagic.length, 0)
      await fd.close()

      return buffer.equals(expectedMagic)
    } catch (error) {
      return false
    }
  }

  private isExecutableFile(extension: string, filename: string): boolean {
    return SUSPICIOUS_EXTENSIONS.includes(extension) ||
           /\.(exe|app|dmg|pkg|deb|rpm|msi)$/i.test(filename)
  }

  private async checkSuspiciousContent(filePath: string): Promise<boolean> {
    try {
      const fs = await import('fs')
      const content = await fs.promises.readFile(filePath, 'utf8')
      
      return SUSPICIOUS_PATTERNS.some(pattern => pattern.test(content))
    } catch (error) {
      // If we can't read as text, assume it's binary and safe
      return false
    }
  }

  private async scanForViruses(filePath: string): Promise<VirusScanResult> {
    const startTime = performance.now()
    
    // Simple virus scan implementation
    // In production, you would integrate with ClamAV, VirusTotal, or similar
    const result: VirusScanResult = {
      isClean: true,
      threats: [],
      scanEngine: 'simple-scanner',
      scanTime: Math.round(performance.now() - startTime)
    }

    try {
      // Check for known malicious signatures (basic implementation)
      const fs = await import('fs')
      const buffer = await fs.promises.readFile(filePath)
      
      // Known malicious signatures (simplified)
      const maliciousSignatures = [
        Buffer.from('EICAR-STANDARD-ANTIVIRUS-TEST-FILE'), // EICAR test file
        Buffer.from('X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR'), // EICAR variant
      ]

      for (const signature of maliciousSignatures) {
        if (buffer.includes(signature)) {
          result.isClean = false
          result.threats.push('EICAR-Test-File')
          break
        }
      }

      // Check file size patterns that might indicate packed malware
      if (buffer.length > 0 && buffer.length < 100) {
        // Very small files with executable patterns might be suspicious
        const executableMarkers = [0x4D, 0x5A] // MZ header
        if (buffer[0] === executableMarkers[0] && buffer[1] === executableMarkers[1]) {
          result.threats.push('Suspicious-Executable-Pattern')
          result.isClean = false
        }
      }

    } catch (error) {
      // If scan fails, err on the side of caution
      result.isClean = false
      result.threats.push('Scan-Failed')
    }

    result.scanTime = Math.round(performance.now() - startTime)
    return result
  }
}

// Pre-configured validators for common use cases
export const fileValidators = {
  // Video uploads
  video: new FileSecurityValidator({
    maxSizeBytes: 500 * 1024 * 1024, // 500MB
    allowedMimeTypes: ['video/mp4', 'video/webm', 'video/avi', 'video/quicktime'],
    allowedExtensions: ['.mp4', '.webm', '.avi', '.mov'],
    scanForViruses: true,
    checkMagicNumbers: true,
  }),

  // Image uploads
  image: new FileSecurityValidator({
    maxSizeBytes: 10 * 1024 * 1024, // 10MB
    allowedMimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    scanForViruses: true,
    checkMagicNumbers: true,
  }),

  // Document uploads
  document: new FileSecurityValidator({
    maxSizeBytes: 25 * 1024 * 1024, // 25MB
    allowedMimeTypes: ['application/pdf', 'text/plain', 'application/json'],
    allowedExtensions: ['.pdf', '.txt', '.json'],
    scanForViruses: true,
    checkMagicNumbers: true,
  }),

  // Avatar uploads
  avatar: new FileSecurityValidator({
    maxSizeBytes: 2 * 1024 * 1024, // 2MB
    allowedMimeTypes: ['image/jpeg', 'image/png', 'image/webp'],
    allowedExtensions: ['.jpg', '.jpeg', '.png', '.webp'],
    scanForViruses: true,
    checkMagicNumbers: true,
  }),
}

/**
 * Utility function to validate a file upload
 */
export async function validateUpload(
  filePath: string,
  originalName: string,
  validatorType: keyof typeof fileValidators = 'video'
): Promise<FileValidationResult> {
  const validator = fileValidators[validatorType]
  return await validator.validateFile(filePath, originalName)
}

/**
 * Sanitize filename to prevent directory traversal and other attacks
 */
export function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[^a-zA-Z0-9._-]/g, '_') // Replace unsafe characters
    .replace(/^\.+/, '') // Remove leading dots
    .replace(/\.{2,}/g, '.') // Replace multiple dots with single dot
    .substring(0, 255) // Limit length
}

/**
 * Generate a secure random filename while preserving extension
 */
export function generateSecureFilename(originalName: string): string {
  const extension = originalName.match(/\.[^.]*$/)?.[0] || ''
  const randomName = crypto.randomBytes(16).toString('hex')
  return `${randomName}${extension}`
}