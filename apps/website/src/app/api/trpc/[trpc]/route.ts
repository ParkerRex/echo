import { type NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3003'

export async function GET(req: NextRequest, { params }: { params: { trpc: string } }) {
  const url = new URL(req.url)
  const targetUrl = `${API_URL}/trpc/${params.trpc}${url.search}`

  const response = await fetch(targetUrl, {
    headers: req.headers,
  })

  const data = await response.text()

  return new NextResponse(data, {
    status: response.status,
    headers: {
      'Content-Type': response.headers.get('Content-Type') || 'application/json',
    },
  })
}

export async function POST(req: NextRequest, { params }: { params: { trpc: string } }) {
  const url = new URL(req.url)
  const targetUrl = `${API_URL}/trpc/${params.trpc}${url.search}`
  const body = await req.text()

  const response = await fetch(targetUrl, {
    method: 'POST',
    headers: req.headers,
    body,
  })

  const data = await response.text()

  return new NextResponse(data, {
    status: response.status,
    headers: {
      'Content-Type': response.headers.get('Content-Type') || 'application/json',
    },
  })
}
