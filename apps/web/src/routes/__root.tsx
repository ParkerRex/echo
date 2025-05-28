import type { QueryClient } from "@tanstack/react-query"
import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router"
import { createServerFn } from "@tanstack/react-start"
import * as React from "react"
import { Header } from "src/components/header"
import { Toaster } from "src/components/ui/sonner"
// @ts-expect-error
import css from "~/globals.css?url"
import { seo } from "src/lib/seo"
import { getSupabaseServerClient } from "src/lib/supabase"
import type { User } from "@supabase/supabase-js"

/**
 * Server function to fetch current user session
 * This ensures auth state is fetched on server and serialized to client
 * Prevents SSR/CSR hydration mismatches
 */
export const fetchSessionUser = createServerFn({ method: 'GET' }).handler<{
  user: User | null
  error: string | null
}>(async () => {
  try {
    const supabase = getSupabaseServerClient()

    const { data: { session }, error: sessionError } = await supabase.auth.getSession()

    if (sessionError) {
      console.error('Session error:', sessionError)
      return { user: null, error: sessionError.message }
    }

    if (!session) {
      return { user: null, error: null }
    }

    const { data: { user }, error: userError } = await supabase.auth.getUser()

    if (userError) {
      console.error('User error:', userError)
      return { user: null, error: userError.message }
    }

    return { user, error: null }
  } catch (error) {
    console.error('Unexpected auth error:', error)
    return { user: null, error: 'Unexpected authentication error' }
  }
})

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient
}>()({
  head: () => ({
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      ...seo({
        title: "Echo - AI YouTube Video Metadata Generator",
        description: "Automatically generate titles, descriptions, chapters, and transcripts for YouTube videos using Google Gemini AI",
        keywords: "YouTube metadata, AI video processing, content creation, video automation",
      }),
    ],
    links: [
      {
        rel: "stylesheet",
        href: css,
      },
      {
        rel: "icon",
        type: "image/png",
        href: "/favicon.png",
      },
    ],
  }),
  beforeLoad: async () => {
    // Fetch user session using server function
    // This ensures consistent auth state between server and client
    const authResult = await fetchSessionUser()

    return {
      user: authResult.user,
      authError: authResult.error,
    }
  },
  component: RootComponent,
})

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  )
}

const TanStackRouterDevtools =
  process.env.NODE_ENV === "production"
    ? () => null
    : React.lazy(() =>
      import("@tanstack/router-devtools").then((res) => ({
        default: res.TanStackRouterDevtools,
      })),
    )

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <head>
        <HeadContent />
      </head>
      <body>
        <Header />
        <hr />
        {children}
        <Scripts />
        <Toaster />
        <React.Suspense>
          <TanStackRouterDevtools />
        </React.Suspense>
      </body>
    </html>
  )
}
