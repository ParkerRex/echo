import { useAuth } from '../hooks/useAuth'; // Adjusted path assuming hooks are in ../hooks
import { Button } from '@/components/ui/button'; // Assuming shadcn/ui Button is available

export function GoogleLoginButton() {
  const { signInWithGoogle, isLoading, error } = useAuth();

  const handleLogin = async () => {
    const result = await signInWithGoogle();
    // signInWithGoogle from useAuth already handles redirection or returns error.
    // Error will be in the `error` state from useAuth if it occurs before redirect.
    if (result.error) {
      // Optionally, display a specific toast or alert here if not handled globally
      console.error("Google Sign-In error:", result.error.message);
    }
    // If successful, navigation to Google occurs, then to callback.
  };

  return (
    <Button
      type="button"
      onClick={handleLogin}
      className="w-full bg-red-600 hover:bg-red-700 text-white font-bold uppercase flex items-center justify-center gap-2"
      aria-label="Sign in with Google"
      disabled={isLoading}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Signing in...
        </>
      ) : (
        <>
          <svg
            width="20"
            height="20"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="mr-2"
          >
            <g>
              <path
                d="M44.5 20H24V28.5H36.9C35.5 33.1 31.2 36 24 36C16.3 36 10 29.7 10 22C10 14.3 16.3 8 24 8C27.3 8 30.1 9.1 32.3 11L38.1 5.2C34.5 2.1 29.6 0 24 0C10.7 0 0 10.7 0 24C0 37.3 10.7 48 24 48C37.3 48 48 37.3 48 24C48 22.3 47.8 20.7 47.5 19.1L44.5 20Z"
                fill="#FFC107"
              />
              <path
                d="M6.3 14.7L13.7 20.1C15.7 15.7 19.5 12.5 24 12.5C26.5 12.5 28.7 13.4 30.4 14.8L36.2 9C33.1 6.3 28.8 4.5 24 4.5C15.9 4.5 8.8 10.1 6.3 14.7Z"
                fill="#FF3D00"
              />
              <path
                d="M24 43.5C31.1 43.5 37.1 39.1 39.6 33.1L32.7 27.7C31.1 30.7 27.8 32.5 24 32.5C19.5 32.5 15.7 29.3 13.7 24.9L6.3 30.3C8.8 34.9 15.9 43.5 24 43.5Z"
                fill="#4CAF50"
              />
              <path
                d="M47.5 19.1H44.5V20H24V28.5H36.9C36.2 31 34.5 33.1 32.7 34.7L39.6 40.1C43.1 36.9 45.5 31.9 45.5 24C45.5 22.3 45.3 20.7 44.5 19.1Z"
                fill="#1976D2"
              />
            </g>
          </svg>
          Sign in with Google
        </>
      )}
      {/* Display error from useAuth if needed, though might be better handled by a global toast */}
      {/* {error && <p className="text-xs text-red-500 mt-1">Error: {error.message}</p>} */}
    </Button>
  );
}
