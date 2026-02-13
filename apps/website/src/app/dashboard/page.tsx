'use client'

import { useAuth } from '@/components/providers/auth-provider'
import { VideoUploader } from '@/components/video-uploader'
import { VideoResults } from '@/components/video-results'
import { VideoHistory } from '@/components/video-history'
import { Button } from '@echo/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { Video, Upload, History, Settings, LogOut } from 'lucide-react'
import { useState } from 'react'

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const [videoId, setVideoId] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Video className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="text-xl font-semibold">Echo</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">{user?.email}</span>
              <Button variant="ghost" size="sm" onClick={signOut}>
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Upload and optimize your YouTube videos with AI-powered tools
          </p>
        </div>

        {videoId ? (
          <VideoResults videoId={videoId} onReset={() => setVideoId(null)} />
        ) : (
          <Tabs defaultValue="upload" className="space-y-4">
            <TabsList>
              <TabsTrigger value="upload">
                <Upload className="w-4 h-4 mr-2" />
                Upload
              </TabsTrigger>
              <TabsTrigger value="history">
                <History className="w-4 h-4 mr-2" />
                History
              </TabsTrigger>
              <TabsTrigger value="settings">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Upload Video</CardTitle>
                  <CardDescription>
                    Upload your video to generate optimized titles and thumbnails
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <VideoUploader onVideoUploaded={setVideoId} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Video History</CardTitle>
                  <CardDescription>
                    View and manage your previously uploaded videos
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <VideoHistory onSelectVideo={setVideoId} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Account Settings</CardTitle>
                  <CardDescription>
                    Manage your account and preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Email</label>
                    <p className="text-sm text-muted-foreground">{user?.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">User ID</label>
                    <p className="text-sm text-muted-foreground font-mono">{user?.id}</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  )
}