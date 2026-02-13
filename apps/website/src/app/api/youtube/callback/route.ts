import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const url = new URL(request.url)
  const code = url.searchParams.get('code')
  const state = url.searchParams.get('state')
  const error = url.searchParams.get('error')

  // Handle OAuth errors
  if (error) {
    console.error('YouTube OAuth error:', error)
    return NextResponse.redirect(new URL('/dashboard?youtube=error', request.url))
  }

  if (!code || !state) {
    return NextResponse.redirect(new URL('/dashboard?youtube=error', request.url))
  }

  try {
    // Call our API endpoint to handle the callback
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'
    const response = await fetch(`${apiUrl}/trpc/youtube.callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        json: { code, state },
      }),
    })

    if (!response.ok) {
      throw new Error('API call failed')
    }

    const result = await response.json()

    if (result.result?.data?.success) {
      const redirectUrl = result.result.data.redirectUrl
      return NextResponse.redirect(new URL(redirectUrl, request.url))
    } else {
      throw new Error('Callback failed')
    }
  } catch (error) {
    console.error('YouTube callback error:', error)
    return NextResponse.redirect(new URL('/dashboard?youtube=error', request.url))
  }
}