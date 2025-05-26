// Re-export the official Supabase-generated types
// This file maintains backward compatibility while using the official Supabase CLI generated types
export * from './generated'
export type { Database } from './generated'

// Legacy aliases for backward compatibility
export type { Tables, TablesInsert, TablesUpdate, Enums } from './generated'
