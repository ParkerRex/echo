import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useRouter } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { toast } from "sonner"; // Assuming sonner is used for toasts as per Phase 5
import * as z from "zod";
import { Button } from "src/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "src/components/ui/form";
import { Input } from "src/components/ui/input";
import { useAuth } from "../lib/useAuth";
import { GoogleLoginButton } from "./GoogleLoginButton";

const loginSchema = z.object({
  email: z.string().email({ message: "Invalid email address." }),
  password: z.string().min(1, { message: "Password is required." }),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function Login() {
  const router = useRouter();
  const {
    loginWithPassword,
    isLoading,
    error: authError,
    isInitialized,
  } = useAuth(); // `error` from useAuth renamed to `authError` to avoid conflict

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    const { error } = await loginWithPassword({
      email: values.email,
      password: values.password,
    });

    if (error) {
      // Error is already set in `authError` state by `useAuth`
      // Optionally, show a toast for more immediate feedback if authError isn't displayed directly
      toast.error(
        error.message || "Login failed. Please check your credentials.",
      );
    } else {
      toast.success("Login successful!");
      // router.invalidate() might be needed if loader data depends on auth state
      await router.invalidate();
      router.navigate({ to: "/dashboard" }); // Navigate to dashboard as per task
    }
  };

  // Redirect if already logged in and initialized
  // This logic might be better placed in the route component or a layout
  // useEffect(() => {
  //   if (isInitialized && session) {
  //     router.navigate({ to: '/dashboard' });
  //   }
  // }, [isInitialized, session, router]);

  return (
    <div className="max-w-md mx-auto mt-8 p-6 border rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold text-center mb-6">Login</h2>

      <GoogleLoginButton />

      <div className="my-4 flex items-center">
        <hr className="flex-grow border-gray-300" />
        <span className="mx-2 text-gray-500 text-xs uppercase">or</span>
        <hr className="flex-grow border-gray-300" />
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input placeholder="your@email.com" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="••••••••" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {authError && (
            <p className="text-sm text-red-500 text-center">
              {authError.message}
            </p>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                Logging in...
              </>
            ) : (
              "Login"
            )}
          </Button>
        </form>
      </Form>
      <p className="mt-6 text-center text-sm">
        Don't have an account?{" "}
        <Link to="/signup" className="font-medium text-primary hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
