import { createFileRoute, redirect } from "@tanstack/react-router";
import { Login } from "~/components/login";
import { supabase } from "@echo/db/clients/client"; // Import supabase client

export const Route = createFileRoute("/login")({
  beforeLoad: async ({ cause }) => {
    // Redirect to dashboard if user is already logged in and tries to enter the login page.
    if (cause === "enter") {
      const {
        data: { session },
      } = await supabase.auth.getSession();
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
  return <Login />;
}
