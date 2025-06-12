'use client'

import { useState, useEffect } from 'react'
import { trpc } from '@/lib/trpc'
import { Copy, Download, RefreshCw, ArrowLeft, CheckCircle } from 'lucide-react'
import Image from 'next/image'

interface VideoResultsProps {
  videoId: string
  onReset: () => void
}

export function VideoResults({ videoId, onReset }: VideoResultsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [selectedThumbnail, setSelectedThumbnail] = useState(0)

  // Poll for job status
  const { data: video, isLoading } = trpc.video.get.useQuery(
    { id: videoId },
    {
      refetchInterval: (data) => {
        // Poll every 2 seconds if processing
        if (data?.status === 'processing') return 2000
        return false
      },
    }
  )

  const { data: job } = trpc.jobs.get.useQuery(
    { videoId },
    {
      enabled: !!video && video.status === 'processing',
      refetchInterval: 2000,
    }
  )

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto text-center py-12">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-64 mx-auto mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (!video) {
    return (
      <div className="max-w-6xl mx-auto text-center py-12">
        <p className="text-red-600 dark:text-red-400 mb-4">Video not found</p>
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Upload another video
        </button>
      </div>
    )
  }

  const isProcessing = video.status === 'processing'
  const metadata = video.metadata?.[0] // Get the latest metadata

  return (
    <div className="max-w-6xl mx-auto">
      <button
        onClick={onReset}
        className="mb-6 inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Upload another video
      </button>

      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">
            {video.fileName}
          </h2>
          <div className="flex items-center gap-2">
            {isProcessing ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin text-purple-600" />
                <span className="text-purple-600 font-medium">Processing...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-green-600 font-medium">Completed</span>
              </>
            )}
          </div>
        </div>

        {isProcessing && job && (
          <div className="mb-8 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <p className="text-sm text-purple-700 dark:text-purple-300 mb-2">
              Current step: {job.currentStep || 'Initializing...'}
            </p>
            {job.progress !== undefined && (
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-purple-600 h-full transition-all duration-500 ease-out"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            )}
          </div>
        )}

        {metadata && (
          <div className="space-y-8">
            {/* Generated Titles */}
            <section>
              <h3 className="text-xl font-semibold mb-4">Generated YouTube Titles</h3>
              <div className="space-y-3">
                {metadata.generatedTitles?.map((title, index) => (
                  <div 
                    key={index}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <p className="flex-1 pr-4">{title}</p>
                    <button
                      onClick={() => copyToClipboard(title, index)}
                      className="p-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
                      title="Copy to clipboard"
                    >
                      {copiedIndex === index ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <Copy className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </section>

            {/* Thumbnails */}
            {metadata.thumbnailUrls && metadata.thumbnailUrls.length > 0 && (
              <section>
                <h3 className="text-xl font-semibold mb-4">AI-Generated Thumbnails</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  {metadata.thumbnailUrls.map((url, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedThumbnail(index)}
                      className={`relative aspect-video rounded-lg overflow-hidden border-2 transition-all ${
                        selectedThumbnail === index 
                          ? 'border-purple-600 shadow-lg' 
                          : 'border-gray-200 dark:border-gray-700 hover:border-purple-400'
                      }`}
                    >
                      <Image
                        src={url}
                        alt={`Thumbnail ${index + 1}`}
                        fill
                        className="object-cover"
                      />
                    </button>
                  ))}
                </div>
                
                {/* Selected Thumbnail Preview */}
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                  <div className="relative aspect-video rounded-lg overflow-hidden mb-4">
                    <Image
                      src={metadata.thumbnailUrls[selectedThumbnail]}
                      alt="Selected thumbnail"
                      fill
                      className="object-cover"
                    />
                  </div>
                  <button
                    className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Download className="w-5 h-5" />
                    Download Thumbnail
                  </button>
                </div>
              </section>
            )}

            {/* Video Description */}
            {metadata.description && (
              <section>
                <h3 className="text-xl font-semibold mb-4">Generated Description</h3>
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="whitespace-pre-wrap">{metadata.description}</p>
                </div>
              </section>
            )}

            {/* Tags */}
            {metadata.tags && metadata.tags.length > 0 && (
              <section>
                <h3 className="text-xl font-semibold mb-4">Suggested Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {metadata.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-sm"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {!isProcessing && !metadata && (
          <div className="text-center py-12">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No results generated yet. Please try uploading again.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}