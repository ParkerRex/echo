// @ts-nocheck
import { httpBatchLink } from '@trpc/client'
import { createTRPCReact } from '@trpc/react-query'
import { createClient } from '@/lib/supabase/client'

// Use any for now to bypass type compatibility issues
export const trpc = createTRPCReact<any>()

export const getTRPCUrl = () => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  return `${baseUrl}/trpc`
}

export const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: getTRPCUrl(),
      async headers() {
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()
        
        return {
          authorization: session?.access_token ? `Bearer ${session.access_token}` : '',
        }
      },
    }),
  ],
})
