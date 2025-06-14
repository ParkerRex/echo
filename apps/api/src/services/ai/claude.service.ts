import Anthropic from '@anthropic-ai/sdk'
import { getEnv } from '../../types/env'
import type { Idea } from '../../db/schema-mvp'

const env = getEnv()
const anthropic = new Anthropic({
  apiKey: env.ANTHROPIC_API_KEY || 'your-api-key-here',
})

interface GeneratedContent {
  titles: string[]
  outline?: string
  script?: string
  description?: string
  tags?: string[]
  thumbnailPrompts?: string[]
  model: string
  promptVersion: string
  generationCost?: number
}

export async function generateWithClaude(
  idea: Idea,
  regenerate?: 'titles' | 'script' | 'description' | 'thumbnail'
): Promise<GeneratedContent> {
  const promptVersion = '1.0'
  let totalCost = 0

  // Base content for all generations
  const baseContent: GeneratedContent = {
    titles: [],
    model: 'claude-3-opus-20240229',
    promptVersion,
  }

  // Generate titles
  if (!regenerate || regenerate === 'titles') {
    const titlesPrompt = buildTitlesPrompt(idea)
    const titlesResponse = await anthropic.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: 1000,
      messages: [{ role: 'user', content: titlesPrompt }],
    })

    const titlesContent = titlesResponse.content[0]
    if (titlesContent && 'text' in titlesContent) {
      baseContent.titles = parseTitles(titlesContent.text)
    }
    totalCost += calculateCost(titlesResponse.usage)
  }

  // Generate script and outline
  if (!regenerate || regenerate === 'script') {
    const scriptPrompt = buildScriptPrompt(idea)
    const scriptResponse = await anthropic.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: 4000,
      messages: [{ role: 'user', content: scriptPrompt }],
    })

    const scriptContent = scriptResponse.content[0]
    if (scriptContent && 'text' in scriptContent) {
      const { outline, script } = parseScriptResponse(scriptContent.text)
      baseContent.outline = outline
      baseContent.script = script
    }
    totalCost += calculateCost(scriptResponse.usage)
  }

  // Generate description and tags
  if (!regenerate || regenerate === 'description') {
    const descPrompt = buildDescriptionPrompt(idea, baseContent.titles[0] || '')
    const descResponse = await anthropic.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: 1500,
      messages: [{ role: 'user', content: descPrompt }],
    })

    const descContent = descResponse.content[0]
    if (descContent && 'text' in descContent) {
      const { description, tags } = parseDescriptionResponse(descContent.text)
      baseContent.description = description
      baseContent.tags = tags
    }
    totalCost += calculateCost(descResponse.usage)
  }

  // Generate thumbnail prompts
  if (!regenerate || regenerate === 'thumbnail') {
    const thumbnailPrompt = buildThumbnailPrompt(idea, baseContent.titles[0] || '')
    const thumbnailResponse = await anthropic.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: 1000,
      messages: [{ role: 'user', content: thumbnailPrompt }],
    })

    const thumbnailContent = thumbnailResponse.content[0]
    if (thumbnailContent && 'text' in thumbnailContent) {
      baseContent.thumbnailPrompts = parseThumbnailPrompts(thumbnailContent.text)
    }
    totalCost += calculateCost(thumbnailResponse.usage)
  }

  baseContent.generationCost = totalCost
  return baseContent
}

// Prompt builders
function buildTitlesPrompt(idea: Idea): string {
  const videoTypeContext = idea.videoType ? `This is a ${idea.videoType} video.` : ''

  return `Generate 10 compelling YouTube video titles based on this idea:

${idea.content}

${videoTypeContext}

Requirements:
- Each title should be 50-60 characters (optimal for YouTube)
- Use power words and emotional triggers
- Include numbers where appropriate
- Make them clickable but not clickbait
- Optimize for YouTube search

Format your response as a numbered list (1-10), with each title on a new line.`
}

function buildScriptPrompt(idea: Idea): string {
  const videoTypeContext = idea.videoType ? `This is a ${idea.videoType} video.` : ''

  return `Create a video script based on this idea:

${idea.content}

${videoTypeContext}

First, provide a brief outline (3-5 main points).
Then, write a full script that:
- Has a strong hook in the first 5 seconds
- Maintains engagement throughout
- Includes clear transitions between sections
- Ends with a call-to-action
- Is conversational and authentic
- Is approximately 500-800 words (3-5 minute video)

Format your response with:
OUTLINE:
[outline here]

SCRIPT:
[full script here]`
}

function buildDescriptionPrompt(idea: Idea, title: string): string {
  return `Write a YouTube video description for a video titled: "${title}"

Based on this concept: ${idea.content}

Include:
1. A compelling first paragraph (visible in search results)
2. Key timestamps (use placeholder times like 00:00, 01:30, etc.)
3. Relevant links section
4. Social media links
5. SEO-optimized text
6. Relevant hashtags

Also provide 10-15 relevant tags for this video.

Format your response as:
DESCRIPTION:
[description here]

TAGS:
[comma-separated tags]`
}

function buildThumbnailPrompt(idea: Idea, title: string): string {
  return `Generate 4 detailed thumbnail image prompts for a YouTube video titled: "${title}"

Based on: ${idea.content}

Each prompt should describe:
- Main visual elements
- Text overlay (if any)
- Color scheme
- Composition/layout
- Style (photorealistic, illustrated, etc.)
- Emotional tone

Make them eye-catching and click-worthy while staying authentic.

Format as numbered list (1-4).`
}

// Response parsers
function parseTitles(response: string): string[] {
  const lines = response.split('\n')
  const titles: string[] = []

  for (const line of lines) {
    const match = line.match(/^\d+\.\s*(.+)$/)
    if (match) {
      titles.push(match[1]!.trim())
    }
  }

  return titles.slice(0, 10)
}

function parseScriptResponse(response: string): { outline?: string; script?: string } {
  const outlineMatch = response.match(/OUTLINE:\s*([\s\S]*?)(?=SCRIPT:|$)/i)
  const scriptMatch = response.match(/SCRIPT:\s*([\s\S]*?)$/i)

  return {
    outline: outlineMatch ? outlineMatch[1]!.trim() : undefined,
    script: scriptMatch ? scriptMatch[1]!.trim() : undefined,
  }
}

function parseDescriptionResponse(response: string): { description?: string; tags?: string[] } {
  const descMatch = response.match(/DESCRIPTION:\s*([\s\S]*?)(?=TAGS:|$)/i)
  const tagsMatch = response.match(/TAGS:\s*([\s\S]*?)$/i)

  const tags = tagsMatch
    ? tagsMatch[1]!
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
    : []

  return {
    description: descMatch ? descMatch[1]!.trim() : undefined,
    tags,
  }
}

function parseThumbnailPrompts(response: string): string[] {
  const lines = response.split('\n')
  const prompts: string[] = []
  let currentPrompt = ''

  for (const line of lines) {
    if (line.match(/^\d+\.\s*/)) {
      if (currentPrompt) {
        prompts.push(currentPrompt.trim())
      }
      currentPrompt = line.replace(/^\d+\.\s*/, '')
    } else if (currentPrompt && line.trim()) {
      currentPrompt += ' ' + line.trim()
    }
  }

  if (currentPrompt) {
    prompts.push(currentPrompt.trim())
  }

  return prompts.slice(0, 4)
}

// Cost calculation (based on Claude pricing)
function calculateCost(usage?: { input_tokens: number; output_tokens: number }): number {
  if (!usage) return 0

  // Claude 3 Opus pricing (as of 2024)
  const inputCostPer1k = 0.015
  const outputCostPer1k = 0.075

  const inputCost = (usage.input_tokens / 1000) * inputCostPer1k
  const outputCost = (usage.output_tokens / 1000) * outputCostPer1k

  return inputCost + outputCost
}
