import { createFileRoute, useRouter, useSearch, redirect } from "@tanstack/react-router"
import { GoogleLoginButton } from "src/components/GoogleLoginButton"
import { Layout } from "src/components/layout"

type LoginSearch = {
  redirect?: string
}

export const Route = createFileRoute("/login")({
  validateSearch: (search: Record<string, unknown>): LoginSearch => {
    return {
      redirect: typeof search.redirect === 'string' ? search.redirect : undefined,
    }
  },
  beforeLoad: ({ context, search }) => {
    // If user is already authenticated, redirect to intended destination
    if (context.user) {
      const redirectTo = search.redirect || "/dashboard"
      throw redirect({
        to: redirectTo,
        replace: true,
      })
    }
  },
  component: LoginComp,
})

function LoginComp() {
  const search = useSearch({ from: "/login" })

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
