import { createFileRoute, useNavigate, useSearch } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import { supabase } from "@echo/db/clients"

type CallbackSearch = {
  redirect?: string
}

export const Route = createFileRoute("/auth/callback")({
  validateSearch: (search: Record<string, unknown>): CallbackSearch => {
    return {
      redirect: typeof search.redirect === 'string' ? search.redirect : undefined,
    }
  },
  component: AuthCallbackComponent,
})

function AuthCallbackComponent() {
  const navigate = useNavigate()
  const search = useSearch({ from: "/auth/callback" })
  const [isProcessing, setIsProcessing] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    console.log('OAuth callback page loaded, URL:', window.location.href)

    const processCallback = async () => {
      try {
        // Check for OAuth error first
        const searchParams = new URLSearchParams(window.location.search)
        const urlError = searchParams.get('error')
        const error_description = searchParams.get('error_description')

        if (urlError) {
          console.error('OAuth error from provider:', urlError, error_description)
          const errorMsg = error_description || urlError || 'OAuth authentication failed'
          setError(errorMsg)
          setIsProcessing(false)
          toast.error(errorMsg)
          setTimeout(() => {
            navigate({ to: "/login", replace: true })
          }, 3000)
          return
        }

        console.log('Processing OAuth callback...')

        // Let Supabase handle the OAuth callback
        const client = supabase()

        // Simple timeout to prevent infinite waiting
        const timeoutId = setTimeout(() => {
          console.error('OAuth callback timeout')
          setError('Authentication timeout. Please try again.')
          setIsProcessing(false)
          toast.error('Authentication timeout. Please try again.')
          setTimeout(() => {
            navigate({ to: "/login", replace: true })
          }, 3000)
        }, 8000) // 8 second timeout

        // Listen for auth state changes
        const { data: { subscription } } = client.auth.onAuthStateChange(async (event, session) => {
          console.log('Auth state change during callback:', { event, hasSession: !!session })

          if (event === 'SIGNED_IN' && session) {
            clearTimeout(timeoutId)
            console.log('OAuth authentication successful')

            // Show success message
            const userName = session.user?.user_metadata?.full_name ||
                           session.user?.email?.split('@')[0] || 'User'
            toast.success(`Welcome, ${userName}!`)

            // Clean up subscription
            subscription.unsubscribe()

            // Redirect to intended destination
            // The root route will handle fetching the user context
            const redirectTo = search.redirect || "/dashboard"
            navigate({ to: redirectTo, replace: true })

          } else if (event === 'SIGNED_OUT') {
            clearTimeout(timeoutId)
            console.log('OAuth authentication failed - user signed out')
            setError('Authentication failed')
            setIsProcessing(false)
            subscription.unsubscribe()
            toast.error('Authentication failed. Please try again.')
            setTimeout(() => {
              navigate({ to: "/login", replace: true })
            }, 3000)
          }
        })

        // Also check if there's already a session (fallback)
        setTimeout(async () => {
          try {
            const { data, error: sessionError } = await client.auth.getSession()

            if (sessionError) {
              console.error('Error getting session during callback check:', sessionError)
              clearTimeout(timeoutId)
              setError(sessionError.message)
              setIsProcessing(false)
              subscription.unsubscribe()
              toast.error(sessionError.message)
              setTimeout(() => {
                navigate({ to: "/login", replace: true })
              }, 3000)
              return
            }

            if (data.session) {
              clearTimeout(timeoutId)
              console.log('OAuth authentication successful via session check')

              // Show success message
              const userName = data.session.user?.user_metadata?.full_name ||
                             data.session.user?.email?.split('@')[0] || 'User'
              toast.success(`Welcome, ${userName}!`)

              // Clean up subscription
              subscription.unsubscribe()

              // Redirect to intended destination
              const redirectTo = search.redirect || "/dashboard"
              navigate({ to: redirectTo, replace: true })
            }
          } catch (err) {
            console.error('Error during session check:', err)
          }
        }, 1000)

        // Return cleanup function
        return () => {
          clearTimeout(timeoutId)
          subscription.unsubscribe()
        }

      } catch (err) {
        console.error('Error processing OAuth callback:', err)
        const errorMessage = 'An unexpected error occurred during authentication'
        setError(errorMessage)
        setIsProcessing(false)
        toast.error(errorMessage)
        setTimeout(() => {
          navigate({ to: "/login", replace: true })
        }, 3000)
      }
    }

    const cleanup = processCallback()

    // Return cleanup function
    return () => {
      if (cleanup && typeof cleanup.then === 'function') {
        cleanup.then(cleanupFn => {
          if (typeof cleanupFn === 'function') {
            cleanupFn()
          }
        })
      }
    }
  }, [navigate, search.redirect])

  // Display a user-friendly loading message or error
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
      {isProcessing ? (
        <>
          <svg
            className="animate-spin h-12 w-12 text-primary mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <h2 className="text-2xl font-semibold mb-2">
            Completing Sign In...
          </h2>
          <p className="text-gray-600">
            We're setting up your account with Google. You'll be redirected to your dashboard in just a moment.
          </p>
        </>
      ) : error ? (
        <>
          <div className="text-red-500 mb-4">
            <svg
              className="h-12 w-12 mx-auto mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold mb-2 text-red-600">
            Authentication Failed
          </h2>
          <p className="text-gray-600 mb-4">
            {error}
          </p>
          <p className="text-sm text-gray-500">
            You'll be redirected to the login page shortly...
          </p>
        </>
      ) : (
        <>
          <div className="text-green-500 mb-4">
            <svg
              className="h-12 w-12 mx-auto mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold mb-2 text-green-600">
            Sign In Successful!
          </h2>
          <p className="text-gray-600">
            Redirecting to your dashboard...
          </p>
        </>
      )}
    </div>
  );
}
