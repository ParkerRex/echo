import { cn } from "@/lib/utils";
import { CheckIcon, Loader2 } from "lucide-react";

export type Step = {
	id: string;
	label: string;
	description?: string;
	status: "pending" | "in_progress" | "completed" | "error";
	progress?: number; // 0-100
	errorMessage?: string;
};

type ProgressStepsProps = {
	steps: Step[];
	currentStepId?: string;
	className?: string;
};

export function ProgressSteps({
	steps,
	currentStepId,
	className,
}: ProgressStepsProps) {
	return (
		<div className={cn("w-full space-y-2", className)}>
			<div className="flex items-center justify-between">
				<div className="text-sm font-medium">Processing Status</div>
				<div className="text-xs text-muted-foreground">
					{steps.filter((step) => step.status === "completed").length} of{" "}
					{steps.length} completed
				</div>
			</div>
			<ul className="space-y-3">
				{steps.map((step, i) => {
					const isCurrent = step.id === currentStepId;
					const isCompleted = step.status === "completed";
					const isInProgress = step.status === "in_progress";
					const isError = step.status === "error";

					return (
						<li key={step.id} className="relative">
							<div
								className={cn(
									"group relative flex items-start",
									isCurrent && "animate-in fade-in duration-300",
								)}
							>
								<div
									className={cn(
										"flex h-9 w-9 shrink-0 items-center justify-center rounded-full border",
										isCompleted &&
											"bg-primary border-primary text-primary-foreground",
										isInProgress && "border-primary/70 bg-primary/10",
										isError &&
											"bg-destructive border-destructive text-destructive-foreground",
										!isCompleted &&
											!isInProgress &&
											!isError &&
											"border-muted-foreground/30",
									)}
								>
									{isCompleted && <CheckIcon className="h-4 w-4" />}
									{isInProgress && (
										<Loader2 className="h-4 w-4 animate-spin text-primary" />
									)}
									{isError && <span className="text-xs font-bold">!</span>}
									{!isCompleted && !isInProgress && !isError && (
										<span className="text-xs text-muted-foreground">
											{i + 1}
										</span>
									)}
								</div>

								<div className="ml-4 min-w-0 flex-1">
									<div className="flex items-center justify-between">
										<div
											className={cn(
												"text-sm font-medium",
												isCompleted && "text-foreground",
												isInProgress && "text-primary",
												isError && "text-destructive",
												!isCompleted &&
													!isInProgress &&
													!isError &&
													"text-muted-foreground",
											)}
										>
											{step.label}
										</div>
										{step.status === "in_progress" &&
											step.progress !== undefined && (
												<div className="text-xs text-muted-foreground">
													{step.progress}%
												</div>
											)}
									</div>

									{step.description && (
										<p className="text-xs text-muted-foreground mt-0.5">
											{step.description}
										</p>
									)}

									{isError && step.errorMessage && (
										<p className="text-xs text-destructive mt-1">
											{step.errorMessage}
										</p>
									)}

									{isInProgress && step.progress !== undefined && (
										<div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
											<div
												className="h-full bg-primary transition-all duration-300 ease-in-out"
												style={{ width: `${step.progress}%` }}
											/>
										</div>
									)}
								</div>
							</div>

							{i < steps.length - 1 && (
								<div
									className={cn(
										"absolute left-4 top-9 h-full w-px -translate-x-1/2 bg-border",
										isCompleted && "bg-primary",
									)}
									aria-hidden="true"
								/>
							)}
						</li>
					);
				})}
			</ul>
		</div>
	);
}
