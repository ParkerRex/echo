'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Film, AlertCircle } from 'lucide-react'
import { trpc } from '@/lib/trpc'

interface VideoUploaderProps {
  onVideoUploaded: (videoId: string) => void
}

export function VideoUploader({ onVideoUploaded }: VideoUploaderProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)

  const uploadMutation = trpc.video.upload.useMutation({
    onSuccess: (data) => {
      onVideoUploaded(data.id)
    },
    onError: (error) => {
      setError(error.message)
      setIsUploading(false)
    },
  })

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    if (!file.type.startsWith('video/')) {
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
    if (file.size < 10 * 1024 * 1024) { // Less than 10MB
      const reader = new FileReader()
      reader.onload = async (e) => {
        const base64 = e.target?.result as string
        const base64Data = base64.split(',')[1]
        
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
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    },
    maxFiles: 1,
    disabled: isUploading,
  })

  return (
    <div className="max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative rounded-2xl border-2 border-dashed p-12 text-center transition-all
          ${isDragActive 
            ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' 
            : 'border-gray-300 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-600'
          }
          ${isUploading ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4">
          {isUploading ? (
            <>
              <div className="w-16 h-16 relative">
                <div className="absolute inset-0 rounded-full border-4 border-gray-200 dark:border-gray-700"></div>
                <div 
                  className="absolute inset-0 rounded-full border-4 border-purple-600 border-t-transparent animate-spin"
                  style={{
                    transform: `rotate(${uploadProgress * 3.6}deg)`,
                    transition: 'transform 0.3s ease-out'
                  }}
                ></div>
              </div>
              <p className="text-lg font-medium">Uploading... {Math.round(uploadProgress)}%</p>
            </>
          ) : (
            <>
              <Film className="w-16 h-16 text-purple-600" />
              <div>
                <p className="text-lg font-medium mb-2">
                  {isDragActive ? 'Drop your video here' : 'Drag & drop your video here'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  or click to browse (max 500MB)
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center mt-2">
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">MP4</span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">MOV</span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">AVI</span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">MKV</span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">WEBM</span>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}
    </div>
  )
}