// @ts-nocheck
'use client'

import { trpc } from '@/lib/trpc'
import { Button } from '@echo/ui/components/button'
import { AlertCircle, Upload, VideoIcon, Check } from 'lucide-react'
import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

interface VideoUploaderProps {
  onVideoUploaded: (videoId: string) => void
}

export function VideoUploader({ onVideoUploaded }: VideoUploaderProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)

  const uploadMutation = trpc.video.upload.useMutation({
    onSuccess: (data: any) => {
      onVideoUploaded(data.video.id)
    },
    onError: (error: any) => {
      setError(error.message)
      setIsUploading(false)
    },
  })

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return

      const file = acceptedFiles[0]
      if (!file || !file.type.startsWith('video/')) {
        setError('Please upload a valid video file')
        return
      }

      // Max file size: 500MB
      if (file.size > 500 * 1024 * 1024) {
        setError('File size must be less than 500MB')
        return
      }

      setError(null)
      setIsUploading(true)
      setUploadProgress(0)

      // Convert file to base64 for small files, or use presigned URL for large files
      if (file.size < 10 * 1024 * 1024) {
        // Less than 10MB
        const reader = new FileReader()
        reader.onload = async (e) => {
          const base64 = e.target?.result as string
          const base64Data = base64?.split(',')[1]

          uploadMutation.mutate({
            fileName: file.name,
            fileSize: file.size,
            mimeType: file.type,
            base64Data,
          })
        }
        reader.onprogress = (e) => {
          if (e.lengthComputable) {
            setUploadProgress((e.loaded / e.total) * 100)
          }
        }
        reader.readAsDataURL(file)
      } else {
        // For large files, implement presigned URL upload
        setError('Large file uploads coming soon!')
        setIsUploading(false)
      }
    },
    [uploadMutation]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
    },
    maxFiles: 1,
    disabled: isUploading,
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-200
          ${
            isDragActive
              ? 'border-primary bg-primary/5 scale-[1.02]'
              : 'border-border/50 hover:border-border bg-card'
          }
          ${isUploading ? 'cursor-not-allowed' : 'cursor-pointer hover:shadow-lg'}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-6">
          {isUploading ? (
            <>
              <div className="relative">
                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                  <VideoIcon className="w-8 h-8 text-primary" />
                </div>
                <div className="absolute inset-0 rounded-full">
                  <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-primary/20"
                      stroke="currentColor"
                      strokeWidth="3"
                      fill="transparent"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="text-primary"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeDasharray={`${uploadProgress}, 100`}
                      strokeLinecap="round"
                      fill="transparent"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-lg font-medium text-foreground">Processing your video...</p>
                <p className="text-sm text-muted-foreground">
                  {Math.round(uploadProgress)}% complete
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-foreground">
                  {isDragActive ? 'Drop your video here' : 'Upload your video'}
                </h3>
                <p className="text-muted-foreground">
                  Drag and drop your video file here, or click to browse
                </p>
                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <span>Maximum file size: 500MB</span>
                  <span>•</span>
                  <span>Supported formats: MP4, MOV, AVI, MKV, WEBM</span>
                </div>
              </div>

              <Button variant="outline" className="mt-4">
                Choose file
              </Button>

              <div className="grid grid-cols-3 gap-4 mt-8 w-full max-w-md">
                <div className="text-center p-4 rounded-lg bg-secondary/50">
                  <div className="w-8 h-8 mx-auto mb-2 rounded-full bg-primary/10 flex items-center justify-center">
                    <Check className="w-4 h-4 text-primary" />
                  </div>
                  <p className="text-xs font-medium">10 AI Titles</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-secondary/50">
                  <div className="w-8 h-8 mx-auto mb-2 rounded-full bg-primary/10 flex items-center justify-center">
                    <Check className="w-4 h-4 text-primary" />
                  </div>
                  <p className="text-xs font-medium">AI Thumbnails</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-secondary/50">
                  <div className="w-8 h-8 mx-auto mb-2 rounded-full bg-primary/10 flex items-center justify-center">
                    <Check className="w-4 h-4 text-primary" />
                  </div>
                  <p className="text-xs font-medium">Full Analysis</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-6 p-4 bg-destructive/10 border border-destructive/20 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-destructive">Upload failed</p>
            <p className="text-sm text-destructive/80 mt-1">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}
