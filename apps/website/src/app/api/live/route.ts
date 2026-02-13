import { NextResponse } from 'next/server'

export async function GET() {
  // Simple liveness check - just confirm the app is running
  return NextResponse.json({
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '2.0.0',
    environment: process.env.NODE_ENV
  })
}

export async function HEAD() {
  return new NextResponse(null, { status: 200 })
}