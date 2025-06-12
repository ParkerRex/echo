'use client'

import { useState } from 'react'
import { VideoUploader } from '@/components/video-uploader'
import { VideoResults } from '@/components/video-results'

export default function Home() {
  const [videoId, setVideoId] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Echo
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Upload your YouTube video and get 10 optimized titles and AI-generated thumbnail backgrounds
          </p>
        </header>

        {!videoId ? (
          <VideoUploader onVideoUploaded={setVideoId} />
        ) : (
          <VideoResults videoId={videoId} onReset={() => setVideoId(null)} />
        )}
      </div>
    </div>
  )
}