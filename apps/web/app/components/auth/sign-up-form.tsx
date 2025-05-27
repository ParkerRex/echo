import { useRouter } from "@tanstack/react-router"
import { useServerFn } from "@tanstack/react-start"
import { useMutation } from "~/lib/useMutation"
import { signUp } from "~/services/auth.api"
import { Auth } from "../auth"

export function SignUpForm() {
  const router = useRouter()

  const signUpMutation = useMutation({
    fn: useServerFn(signUp),
    onSuccess: async (ctx) => {
      if (ctx.data && ctx.data.success) {
        await router.invalidate()
        router.navigate({ to: "/dashboard" })
        return
      }
    },
  })

  return (
    <Auth
      actionText="Sign Up"
      status={signUpMutation.status}
      onSubmit={(e) => {
        const formData = new FormData(e.target as HTMLFormElement)

        signUpMutation.mutate({
          email: formData.get('email') as string,
          password: formData.get('password') as string,
        })
      }}
      afterSubmit={
        signUpMutation.data?.error ? (
          <div className="text-red-400">{signUpMutation.data.error}</div>
        ) : null
      }
    />
  )
} 