import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { supabase } from "@echo/db/clients/client";

export default function AuthCallback() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Supabase handles the OAuth callback automatically on page load.
    // We just need to check if the user is authenticated.
    async function handleAuth() {
      const { data, error } = await supabase.auth.getSession();
      if (error) {
        setError("Authentication failed. Please try again.");
        return;
      }
      if (data.session) {
        // Authenticated, redirect to dashboard or protected route
        navigate({ to: "/dashboard" });
      } else {
        setError("No session found. Please log in again.");
      }
    }
    handleAuth();
  }, [navigate]);

  if (error) {
    return (
      <div>
        <h2>Authentication Error</h2>
        <p>{error}</p>
        <a href="/login">Back to Login</a>
      </div>
    );
  }

  return (
    <div>
      <h2>Signing you in...</h2>
      <p>Please wait while we complete authentication.</p>
    </div>
  );
}
