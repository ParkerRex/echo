// Re-export the official Supabase-generated types
// This file maintains backward compatibility while using the official Supabase CLI generated types
export * from './database'
export type { Database } from './database'

// Legacy aliases for backward compatibility
export type { Tables, TablesInsert, TablesUpdate, Enums } from './database'
