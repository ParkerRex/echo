import { createFileRoute, Link, useRouter, redirect } from "@tanstack/react-router";
import { useAuth } from "../hooks/useAuth";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { supabase } from "@echo/db/clients/client"; // Import supabase client

// Define the schema for signup form validation
const signupSchema = z.object({
	email: z.string().email({ message: "Invalid email address." }),
	password: z.string().min(8, { message: "Password must be at least 8 characters." }),
	confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
	message: "Passwords do not match.",
	path: ["confirmPassword"], // Path to field where the error message should be shown
});

type SignupFormValues = z.infer<typeof signupSchema>;

export const Route = createFileRoute("/signup")({
	beforeLoad: async ({ cause }) => {
		// Redirect to dashboard if user is already logged in and tries to enter the signup page.
		if (cause === 'enter') { 
			const { data: { session } } = await supabase.auth.getSession();
			if (session) {
				throw redirect({
					to: "/dashboard",
					replace: true,
				});
			}
		}
	},
	component: SignupComponent,
});

function SignupComponent() {
	const router = useRouter();
	const { signUpWithEmailPassword, isLoading, error: authError, isInitialized } = useAuth();

	const form = useForm<SignupFormValues>({
		resolver: zodResolver(signupSchema),
		defaultValues: {
			email: "",
			password: "",
			confirmPassword: "",
		},
	});

	const onSubmit = async (values: SignupFormValues) => {
		const { error } = await signUpWithEmailPassword({
			email: values.email,
			password: values.password,
		});

		if (error) {
			toast.error(error.message || "Signup failed. Please try again.");
		} else {
			// Supabase typically sends a confirmation email.
			toast.success("Signup successful! Please check your email to confirm your account.");
			// Optionally, clear form or redirect to a page indicating to check email
			form.reset();
			// router.navigate({ to: "/check-email" }); // Example: if you have such a page
			// For now, we can redirect to login or home after a delay, or let user click away.
			// router.navigate({ to: "/login" }); 
		}
	};

	return (
		<div className="max-w-md mx-auto mt-8 p-6 border rounded-lg shadow-md">
			<h2 className="text-2xl font-semibold text-center mb-6">Create Account</h2>
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
					<FormField
						control={form.control}
						name="confirmPassword"
						render={({ field }) => (
							<FormItem>
								<FormLabel>Confirm Password</FormLabel>
								<FormControl>
									<Input type="password" placeholder="••••••••" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>

					{authError && (
						<p className="text-sm text-red-500 text-center">{authError.message}</p>
					)}

					<Button type="submit" className="w-full" disabled={isLoading}>
						{isLoading ? (
							<>
								<svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
									<path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Creating account...
							</>
						) : "Create Account"}
					</Button>
				</form>
			</Form>
			<p className="mt-6 text-center text-sm">
				Already have an account?{" "}
				<Link to="/login" className="font-medium text-primary hover:underline">
					Log in
				</Link>
			</p>
		</div>
	);
}
