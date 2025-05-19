import type { Step } from "~/components/ui/progress-steps";

// Define the IDs for our processing steps
export enum ProcessingStepId {
  UPLOAD = "upload",
  AUDIO_EXTRACTION = "audio_extraction",
  TRANSCRIPT = "transcript",
  SUBTITLES = "subtitles",
  SHOWNOTES = "shownotes",
  CHAPTERS = "chapters",
  TITLE = "title",
  YOUTUBE_UPLOAD = "youtube_upload",
}

// Define static step metadata
export const PROCESSING_STEPS_META = {
  [ProcessingStepId.UPLOAD]: {
    label: "Video Upload",
    description: "Uploading video file to secure storage",
    progressPercentage: 10,
  },
  [ProcessingStepId.AUDIO_EXTRACTION]: {
    label: "Audio Extraction",
    description: "Extracting audio track for transcription",
    progressPercentage: 15,
  },
  [ProcessingStepId.TRANSCRIPT]: {
    label: "Transcript Generation",
    description: "Creating full text transcript from audio",
    progressPercentage: 15,
  },
  [ProcessingStepId.SUBTITLES]: {
    label: "Subtitles Generation",
    description: "Creating timestamped VTT subtitles",
    progressPercentage: 15,
  },
  [ProcessingStepId.SHOWNOTES]: {
    label: "Shownotes Generation",
    description: "Creating detailed show notes and summary",
    progressPercentage: 15,
  },
  [ProcessingStepId.CHAPTERS]: {
    label: "Chapters Generation",
    description: "Creating timestamped chapters",
    progressPercentage: 15,
  },
  [ProcessingStepId.TITLE]: {
    label: "Title & Keywords",
    description: "Creating optimized title and keywords",
    progressPercentage: 5,
  },
  [ProcessingStepId.YOUTUBE_UPLOAD]: {
    label: "YouTube Upload",
    description: "Uploading to YouTube with metadata",
    progressPercentage: 10,
  },
};

// Create the processing steps in the proper order
export const ORDERED_PROCESSING_STEPS = Object.keys(PROCESSING_STEPS_META).map(
  (id) => ({
    id,
    ...PROCESSING_STEPS_META[id as ProcessingStepId],
  }),
);

// Initialize all steps to pending
export function initializeProcessingSteps(): Step[] {
  return Object.entries(PROCESSING_STEPS_META).map(([id, meta]) => ({
    id,
    label: meta.label,
    description: meta.description,
    status: "pending" as const,
  }));
}

// Update step status in the array
export function updateStepStatus(
  steps: Step[],
  stepId: ProcessingStepId,
  status: Step["status"],
  options?: { progress?: number; errorMessage?: string },
): Step[] {
  return steps.map((step) => {
    if (step.id === stepId) {
      return {
        ...step,
        status,
        progress: options?.progress,
        errorMessage: options?.errorMessage,
      };
    }
    return step;
  });
}

// Calculate the overall progress percentage
export function calculateOverallProgress(steps: Step[]): number {
  // If all steps are completed, return 100%
  if (steps.every((step) => step.status === "completed")) {
    return 100;
  }

  let totalProgress = 0;
  let completedProgress = 0;

  steps.forEach((step) => {
    const stepMeta = PROCESSING_STEPS_META[step.id as ProcessingStepId];
    const weight = stepMeta.progressPercentage;

    totalProgress += weight;

    if (step.status === "completed") {
      completedProgress += weight;
    } else if (step.status === "in_progress" && step.progress !== undefined) {
      // For in-progress steps, add a portion based on its progress
      completedProgress += (weight * step.progress) / 100;
    }
  });

  return Math.round((completedProgress / totalProgress) * 100);
}

// Mock step progress for UI development/testing
export function createMockProcessingSteps(currentStepIndex: number): Step[] {
  const orderedStepIds = Object.keys(PROCESSING_STEPS_META);

  return orderedStepIds.map((id, index) => {
    const meta = PROCESSING_STEPS_META[id as ProcessingStepId];

    let status: Step["status"] = "pending";
    let progress: number | undefined = undefined;

    if (index < currentStepIndex) {
      status = "completed";
    } else if (index === currentStepIndex) {
      status = "in_progress";
      progress = Math.floor(Math.random() * 100);
    }

    return {
      id,
      label: meta.label,
      description: meta.description,
      status,
      progress,
    };
  });
}
