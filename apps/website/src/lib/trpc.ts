// @ts-nocheck
import { httpBatchLink } from '@trpc/client'
import { createTRPCReact } from '@trpc/react-query'

// Use any for now to bypass type compatibility issues
export const trpc = createTRPCReact<any>()

export const getTRPCUrl = () => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3003'
  return `${baseUrl}/trpc`
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
