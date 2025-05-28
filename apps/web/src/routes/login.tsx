import { createFileRoute, redirect } from "@tanstack/react-router";
import { supabase } from "@echo/db/clients";
import { GoogleLoginButton } from "src/components/GoogleLoginButton";
import { Layout } from "src/components/layout";

export const Route = createFileRoute("/login")({
  beforeLoad: async ({ cause }) => {
    // Redirect to dashboard if user is already logged in and tries to enter the login page.
    if (cause === "enter") {
      const {
        data: { session },
      } = await supabase().auth.getSession();
      if (session) {
        throw redirect({
          to: "/dashboard",
          replace: true,
        });
      }
    }
  },
  component: LoginComp,
});

function LoginComp() {
  return (
    <Layout className="items-center gap-6 max-w-md">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Welcome to Echo</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Sign in with your Google account to continue
        </p>
      </div>

      <div className="w-full">
        <GoogleLoginButton />
      </div>

      <div className="text-center text-sm text-gray-500">
        <p>
          By signing in, you agree to our{" "}
          <a href="/terms" className="underline hover:no-underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="underline hover:no-underline">
            Privacy Policy
          </a>
        </p>
      </div>
    </Layout>
  );
}
