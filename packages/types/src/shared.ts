/**
 * Shared types and utilities for the Echo monorepo.
 *
 * This module contains common types, enums, and utility types that are used
 * across both database operations and API interactions.
 */

// Processing Status Enum - Single source of truth
export enum ProcessingStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

// Common utility types
export type ID = number;
export type UUID = string;
export type Timestamp = string; // ISO 8601 string
export type JSONValue = string | number | boolean | null | JSONObject | JSONArray;
export type JSONObject = { [key: string]: JSONValue };
export type JSONArray = JSONValue[];

// API Response wrapper types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// File upload types
export interface FileUpload {
  file: File;
  progress?: number;
  status: 'pending' | 'uploading' | 'completed' | 'failed';
  error?: string;
}

// Video processing stage types
export interface ProcessingStage {
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  startedAt?: Timestamp;
  completedAt?: Timestamp;
  error?: string;
}

export type ProcessingStages = Record<string, ProcessingStage>;

// Common field types for consistency
export interface TimestampFields {
  created_at: Timestamp;
  updated_at: Timestamp;
}

export interface OptionalTimestampFields {
  created_at?: Timestamp;
  updated_at?: Timestamp;
}
