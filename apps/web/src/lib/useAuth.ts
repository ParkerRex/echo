/**
 * @deprecated This hook is deprecated in favor of server-side authentication.
 * Use the server functions from src/services/auth.api.ts instead:
 * - getUser() for checking auth state
 * - signInWithGoogle() for OAuth login
 * - signOut() for logout
 *
 * This file is kept for backward compatibility during migration.
 * It will be removed in a future version.
 */

import { useState, useEffect, useCallback } from 'react'
import { supabase } from '@echo/db/clients'
import type { AuthError, Session, User } from '@supabase/supabase-js'

interface UseAuthState {
  user: User | null
  session: Session | null
  isLoading: boolean
  error: AuthError | null
  isInitialized: boolean
}

/**
 * @deprecated Legacy auth hook - use server-side auth functions instead
 */
export function useAuth(): UseAuthState {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<AuthError | null>(null)
  const [isInitialized, setIsInitialized] = useState<boolean>(false)

  useEffect(() => {
    console.warn(
      'useAuth() is deprecated. Use server functions from src/services/auth.api.ts instead. ' +
      'This hook will be removed in a future version.'
    )

    const client = supabase()

    // Get initial session
    client.auth.getSession().then(({ data, error }) => {
      if (error) {
        console.error('Error getting initial session:', error)
        setError(error)
      }
      setSession(data.session)
      setUser(data.session?.user ?? null)
      setIsInitialized(true)
      setIsLoading(false)
    })

    // Listen for auth changes
    const { data: authListenerData } = client.auth.onAuthStateChange(
      async (event, newSession) => {
        console.log('Auth state change (legacy hook):', event)
        setSession(newSession)
        setUser(newSession?.user ?? null)
        setError(null)
        setIsInitialized(true)
        setIsLoading(false)
      }
    )

    return () => {
      authListenerData.subscription.unsubscribe()
    }
  }, [])

  return {
    user,
    session,
    isLoading,
    error,
    isInitialized,
  }
}