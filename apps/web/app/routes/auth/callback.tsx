import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { toast } from "sonner";
import { useAuth } from "~/lib/useAuth"; // Assuming path to useAuth hook

export const Route = createFileRoute("/auth/callback")({
  component: AuthCallbackComponent,
});

function AuthCallbackComponent() {
  const navigate = useNavigate();
  const { session, error: authError, isLoading, isInitialized } = useAuth();

  useEffect(() => {
    if (!isInitialized) {
      // Still waiting for useAuth to initialize and process the auth state
      return;
    }

    if (authError) {
      toast.error(
        authError.message || "Authentication failed. Please try again.",
      );
      navigate({ to: "/login", replace: true });
    } else if (session) {
      toast.success("Successfully signed in!");
      navigate({ to: "/dashboard", replace: true });
    } else {
      // This case might occur if the callback was invalid or already processed,
      // and no session was established, and no explicit error was thrown by useAuth from the callback processing.
      toast.error("Could not establish a session. Please log in.");
      navigate({ to: "/login", replace: true });
    }
  }, [session, authError, isLoading, isInitialized, navigate]);

  // Display a user-friendly loading message
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
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
        Processing Authentication...
      </h2>
      <p className="text-gray-600">
        Please wait while we securely sign you in. You will be redirected
        shortly.
      </p>
    </div>
  );
}
