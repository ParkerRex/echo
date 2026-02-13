'use client'

import { useState } from 'react'
import { trpc } from '@/lib/trpc'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Label } from '@echo/ui/label'
import { Textarea } from '@echo/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@echo/ui/select'
import { Badge } from '@echo/ui/badge'
import { Switch } from '@echo/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@echo/ui/tabs'
import { FlaskConical, Target, Zap, Loader2, Plus, X, Copy } from 'lucide-react'

interface TestCreatorProps {
  videoId?: string
  initialTitle?: string
  initialDescription?: string
  initialThumbnail?: string
}

export function TestCreator({ 
  videoId, 
  initialTitle = '', 
  initialDescription = '', 
  initialThumbnail = '' 
}: TestCreatorProps) {
  const [testType, setTestType] = useState<'title' | 'thumbnail' | 'description' | 'tags'>('title')
  const [testName, setTestName] = useState('')
  const [testDuration, setTestDuration] = useState(7) // days
  const [splitRatio, setSplitRatio] = useState(50) // percentage for variant A
  const [autoOptimize, setAutoOptimize] = useState(true)
  
  // Variants state
  const [variants, setVariants] = useState<Array<{
    id: string
    name: string
    content: string
    isControl: boolean
  }>>([
    { id: 'control', name: 'Control (Original)', content: '', isControl: true },
    { id: 'variant-1', name: 'Variant 1', content: '', isControl: false }
  ])

  // Generate content variants mutation
  const generateVariants = trpc.contentStrategy.generateContentVariants.useMutation()
  
  // Create A/B test mutation
  const createABTest = trpc.contentStrategy.createABTest.useMutation()

  const handleGenerateVariants = async () => {
    const baseContent = getBaseContent()
    if (!baseContent.trim()) return

    const generated = await generateVariants.mutateAsync({
      content: baseContent,
      type: testType,
      userId: '', // Will be set by tRPC context
      count: 5
    })

    // Update variants with generated content
    const newVariants = [
      { id: 'control', name: 'Control (Original)', content: baseContent, isControl: true },
      ...generated.map((variant, index) => ({
        id: `variant-${index + 1}`,
        name: `Variant ${index + 1}`,
        content: variant.content,
        isControl: false
      }))
    ]
    
    setVariants(newVariants)
  }

  const getBaseContent = () => {
    switch (testType) {
      case 'title': return initialTitle
      case 'description': return initialDescription
      case 'thumbnail': return initialThumbnail
      case 'tags': return ''
      default: return ''
    }
  }

  const handleAddVariant = () => {
    const newId = `variant-${variants.length}`
    setVariants([
      ...variants,
      { id: newId, name: `Variant ${variants.length}`, content: '', isControl: false }
    ])
  }

  const handleRemoveVariant = (id: string) => {
    if (variants.length <= 2) return // Keep at least control + 1 variant
    setVariants(variants.filter(v => v.id !== id))
  }

  const handleVariantChange = (id: string, field: string, value: string) => {
    setVariants(variants.map(v => 
      v.id === id ? { ...v, [field]: value } : v
    ))
  }

  const handleCreateTest = async () => {
    if (!testName.trim() || !videoId) return

    const testVariants = variants.filter(v => v.content.trim()).map(v => ({
      name: v.name,
      content: v.content,
      isControl: v.isControl
    }))

    await createABTest.mutateAsync({
      videoId,
      testName,
      testType,
      variants: testVariants,
      duration: testDuration,
      splitRatio,
      autoOptimize
    })
  }

  const getTestTypeDescription = () => {
    switch (testType) {
      case 'title': return 'Test different video titles to maximize click-through rates'
      case 'thumbnail': return 'Compare thumbnail designs to improve video visibility'
      case 'description': return 'Optimize descriptions for better search rankings'
      case 'tags': return 'Test tag combinations for improved discoverability'
      default: return ''
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <FlaskConical className="w-5 h-5 text-primary" />
          Create A/B Test
        </h3>
        <p className="text-sm text-muted-foreground">
          Set up experiments to optimize your content performance
        </p>
      </div>

      <Tabs defaultValue="setup" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="setup">Test Setup</TabsTrigger>
          <TabsTrigger value="variants">Variants</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="setup" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Test Configuration</CardTitle>
              <CardDescription>
                Define what you want to test and how
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="testName">Test Name *</Label>
                <Input
                  id="testName"
                  value={testName}
                  onChange={(e) => setTestName(e.target.value)}
                  placeholder="e.g., Title Optimization Test #1"
                />
              </div>

              <div>
                <Label htmlFor="testType">What to Test *</Label>
                <Select value={testType} onValueChange={(value: any) => setTestType(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="title">Video Title</SelectItem>
                    <SelectItem value="thumbnail">Thumbnail</SelectItem>
                    <SelectItem value="description">Description</SelectItem>
                    <SelectItem value="tags">Tags</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground mt-1">
                  {getTestTypeDescription()}
                </p>
              </div>

              <div className="flex gap-4">
                <Button
                  onClick={handleGenerateVariants}
                  disabled={generateVariants.isPending}
                  variant="outline"
                >
                  {generateVariants.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  Generate AI Variants
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="variants" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium">Test Variants ({variants.length})</h4>
              <p className="text-sm text-muted-foreground">
                Create different versions to test against each other
              </p>
            </div>
            <Button onClick={handleAddVariant} size="sm" variant="outline">
              <Plus className="w-4 h-4" />
              Add Variant
            </Button>
          </div>

          <div className="space-y-4">
            {variants.map((variant, index) => (
              <Card key={variant.id} className={variant.isControl ? 'border-primary/50' : ''}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Input
                        value={variant.name}
                        onChange={(e) => handleVariantChange(variant.id, 'name', e.target.value)}
                        className="w-48"
                      />
                      {variant.isControl && (
                        <Badge variant="outline" className="border-primary text-primary">
                          Control
                        </Badge>
                      )}
                    </div>
                    {!variant.isControl && variants.length > 2 && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemoveVariant(variant.id)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {testType === 'description' ? (
                    <Textarea
                      value={variant.content}
                      onChange={(e) => handleVariantChange(variant.id, 'content', e.target.value)}
                      placeholder={`Enter ${testType} content for ${variant.name}...`}
                      rows={3}
                    />
                  ) : (
                    <Input
                      value={variant.content}
                      onChange={(e) => handleVariantChange(variant.id, 'content', e.target.value)}
                      placeholder={`Enter ${testType} content for ${variant.name}...`}
                    />
                  )}
                  {variant.content && (
                    <div className="flex justify-end mt-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => navigator.clipboard.writeText(variant.content)}
                      >
                        <Copy className="w-4 h-4" />
                        Copy
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Test Settings</CardTitle>
              <CardDescription>
                Configure how your test will run
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="duration">Test Duration</Label>
                <Select value={testDuration.toString()} onValueChange={(value) => setTestDuration(parseInt(value))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="3">3 days</SelectItem>
                    <SelectItem value="7">1 week</SelectItem>
                    <SelectItem value="14">2 weeks</SelectItem>
                    <SelectItem value="30">1 month</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground mt-1">
                  How long the test should run before declaring a winner
                </p>
              </div>

              <div>
                <Label htmlFor="splitRatio">Traffic Split</Label>
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Control: {splitRatio}%</span>
                      <span>Variants: {100 - splitRatio}%</span>
                    </div>
                    <input
                      type="range"
                      min="20"
                      max="80"
                      value={splitRatio}
                      onChange={(e) => setSplitRatio(parseInt(e.target.value))}
                      className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  How to split traffic between control and variant versions
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="autoOptimize">Auto-optimize</Label>
                  <p className="text-xs text-muted-foreground">
                    Automatically switch to the winning variant when test concludes
                  </p>
                </div>
                <Switch
                  id="autoOptimize"
                  checked={autoOptimize}
                  onCheckedChange={setAutoOptimize}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Success Metrics</CardTitle>
              <CardDescription>
                What metrics will determine the winner
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  <span className="text-sm">Click-through Rate</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  <span className="text-sm">Watch Time</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  <span className="text-sm">Engagement Rate</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  <span className="text-sm">Conversion Rate</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Button
            onClick={handleCreateTest}
            disabled={createABTest.isPending || !testName.trim() || variants.filter(v => v.content.trim()).length < 2}
            className="w-full"
          >
            {createABTest.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FlaskConical className="w-4 h-4" />
            )}
            Create A/B Test
          </Button>
        </TabsContent>
      </Tabs>
    </div>
  )
}