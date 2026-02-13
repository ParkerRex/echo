import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import '../styles/globals.css'
import { TRPCProvider } from '@/components/providers/trpc-provider'
import { AuthProvider } from '@/components/providers/auth-provider'
import { ErrorBoundary } from '@/components/error-boundary'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'Echo - Stop Losing 90% of Your Potential Views to Bad Titles',
  description: 'Join 2,400+ creators using AI to get 10x better YouTube titles, thumbnails, and performance predictions. Start your free trial - no credit card required.',
  keywords: 'YouTube optimization, AI titles, YouTube thumbnails, video SEO, YouTube analytics, content creator tools',
  openGraph: {
    title: 'Echo - Stop Losing 90% of Your Potential Views to Bad Titles',
    description: 'Join 2,400+ creators using AI to get 10x better YouTube titles, thumbnails, and performance predictions.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Echo - Stop Losing 90% of Your Potential Views to Bad Titles',
    description: 'Join 2,400+ creators using AI to get 10x better YouTube titles, thumbnails, and performance predictions.',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ErrorBoundary>
          <AuthProvider>
            <TRPCProvider>{children}</TRPCProvider>
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
