import { useRouter } from "@tanstack/react-router"
import { useServerFn } from "@tanstack/react-start"
import { useMutation } from "src/lib/useMutation"
import { signIn } from "src/services/auth.api"
import { Auth } from "../auth"

export function SignInForm() {
  const router = useRouter()

  const signInMutation = useMutation({
    fn: useServerFn(signIn),
    onSuccess: async (ctx) => {
      if (!ctx.data?.error) {
        await router.invalidate()
        router.navigate({ to: "/dashboard" })
        return
      }
    },
  })

  return (
    <Auth
      actionText="Sign In"
      status={signInMutation.status}
      onSubmit={(e) => {
        const formData = new FormData(e.target as HTMLFormElement)

        signInMutation.mutate({
          email: formData.get('email') as string,
          password: formData.get('password') as string,
        })
      }}
      afterSubmit={
        signInMutation.data?.error ? (
          <div className="text-red-400">{signInMutation.data.error}</div>
        ) : null
      }
    />
  )
} 