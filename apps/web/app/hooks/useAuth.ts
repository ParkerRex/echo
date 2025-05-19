import { useState, useEffect, useCallback } from 'react';
import { supabase } from '@echo/db/clients/client';
import type { AuthError, Session, User, SignInWithPasswordCredentials, SignUpWithPasswordCredentials, AuthChangeEvent, OAuthResponse, UserResponse } from '@supabase/supabase-js';

interface UseAuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  error: AuthError | null;
  isInitialized: boolean; // To track if the initial auth state has been loaded
}

interface UseAuthActions {
  loginWithPassword: (credentials: SignInWithPasswordCredentials) => Promise<{ error: AuthError | null }>;
  signUpWithEmailPassword: (credentials: SignUpWithPasswordCredentials) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<{ error: AuthError | null }>;
  signInWithGoogle: () => Promise<OAuthResponse>;
}

export function useAuth(): UseAuthState & UseAuthActions {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false); // For active operations like login/signup
  const [error, setError] = useState<AuthError | null>(null);
  const [isInitialized, setIsInitialized] = useState<boolean>(false); // Tracks initial auth state check

  useEffect(() => {
    setIsLoading(true);
    supabase.auth.getSession().then(({ data, error }: { data: { session: Session | null }, error: AuthError | null }) => {
      if (error) {
        console.error('Error getting initial session:', error);
        setError(error);
      }
      setSession(data.session);
      setUser(data.session?.user ?? null);
      setIsInitialized(true);
      setIsLoading(false);
    });

    const { data: authListenerData } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, newSession: Session | null) => {
        setSession(newSession);
        setUser(newSession?.user ?? null);
        setError(null);
        setIsInitialized(true);
        setIsLoading(false);
      }
    );

    return () => {
      authListenerData.subscription.unsubscribe();
    };
  }, []);

  const handleAuthOperation = useCallback(
    async (authPromiseFactory: () => Promise<{ data?: any; error: AuthError | null }>) => {
      setIsLoading(true);
      setError(null);
      try {
        const { error: opError } = await authPromiseFactory();
        if (opError) {
          setError(opError);
          return { error: opError };
        }
        // Session and user state will be updated by onAuthStateChange listener
        return { error: null };
      } catch (e: any) {
        const err = { name: 'AuthOperationError', message: e.message || 'An unknown error occurred' } as AuthError;
        setError(err);
        return { error: err };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const loginWithPassword = useCallback(
    async (credentials: SignInWithPasswordCredentials) => {
      return handleAuthOperation(() => supabase.auth.signInWithPassword(credentials));
    },
    [handleAuthOperation]
  );

  const signUpWithEmailPassword = useCallback(
    async (credentials: SignUpWithPasswordCredentials) => {
      return handleAuthOperation(() => supabase.auth.signUp(credentials));
    },
    [handleAuthOperation]
  );

  const signOut = useCallback(async () => {
    return handleAuthOperation(() => supabase.auth.signOut());
  }, [handleAuthOperation]);

  const signInWithGoogle = useCallback(async (): Promise<OAuthResponse> => {
    setIsLoading(true);
    setError(null);
    const result = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: `${window.location.origin}/auth/callback`,
        },
    });
    
    if (result.error) {
        setError(result.error);
        setIsLoading(false);
    }
    return result; 
  }, []);


  return { user, session, isLoading, error, isInitialized, loginWithPassword, signUpWithEmailPassword, signOut, signInWithGoogle };
} 