import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines multiple class names into a single string, merging Tailwind CSS classes properly.
 * Uses clsx for conditional classes and tailwind-merge to handle Tailwind class conflicts.
 * 
 * @param inputs - Class values to be combined
 * @returns A string of combined class names
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
