import { createTRPCReact } from '@trpc/react-query'
import { httpBatchLink } from '@trpc/client'
import type { AppRouter } from '@echo/core/src/routers'

export const trpc = createTRPCReact<AppRouter>()

export const getTRPCUrl = () => {
  if (typeof window !== 'undefined') {
    // Browser should use relative url
    return '/api/trpc'
  }
  
  // SSR should use absolute url
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/trpc'
}

export const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: getTRPCUrl(),
      async headers() {
        return {
          // Add auth headers here if needed
        }
      },
    }),
  ],
})