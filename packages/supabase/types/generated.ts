export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          operationName?: string
          query?: string
          variables?: Json
          extensions?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      video_jobs: {
        Row: {
          created_at: string
          error_message: string | null
          id: number
          processing_stages: Json | null
          status: Database["public"]["Enums"]["processing_status_enum"]
          updated_at: string
          video_id: number
        }
        Insert: {
          created_at?: string
          error_message?: string | null
          id?: number
          processing_stages?: Json | null
          status?: Database["public"]["Enums"]["processing_status_enum"]
          updated_at?: string
          video_id: number
        }
        Update: {
          created_at?: string
          error_message?: string | null
          id?: number
          processing_stages?: Json | null
          status?: Database["public"]["Enums"]["processing_status_enum"]
          updated_at?: string
          video_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "video_jobs_video_id_fkey"
            columns: ["video_id"]
            isOneToOne: false
            referencedRelation: "videos"
            referencedColumns: ["id"]
          },
        ]
      }
      video_metadata: {
        Row: {
          created_at: string
          description: string | null
          extracted_video_duration_seconds: number | null
          extracted_video_format: string | null
          extracted_video_resolution: string | null
          id: number
          job_id: number
          show_notes_text: string | null
          subtitle_files_urls: Json | null
          tags: string[] | null
          thumbnail_file_url: string | null
          title: string | null
          transcript_file_url: string | null
          transcript_text: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          extracted_video_duration_seconds?: number | null
          extracted_video_format?: string | null
          extracted_video_resolution?: string | null
          id?: number
          job_id: number
          show_notes_text?: string | null
          subtitle_files_urls?: Json | null
          tags?: string[] | null
          thumbnail_file_url?: string | null
          title?: string | null
          transcript_file_url?: string | null
          transcript_text?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string | null
          extracted_video_duration_seconds?: number | null
          extracted_video_format?: string | null
          extracted_video_resolution?: string | null
          id?: number
          job_id?: number
          show_notes_text?: string | null
          subtitle_files_urls?: Json | null
          tags?: string[] | null
          thumbnail_file_url?: string | null
          title?: string | null
          transcript_file_url?: string | null
          transcript_text?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "video_metadata_job_id_fkey"
            columns: ["job_id"]
            isOneToOne: true
            referencedRelation: "video_jobs"
            referencedColumns: ["id"]
          },
        ]
      }
      videos: {
        Row: {
          content_type: string
          created_at: string
          id: number
          original_filename: string
          size_bytes: number
          storage_path: string
          updated_at: string
          uploader_user_id: string
        }
        Insert: {
          content_type: string
          created_at?: string
          id?: number
          original_filename: string
          size_bytes: number
          storage_path: string
          updated_at?: string
          uploader_user_id: string
        }
        Update: {
          content_type?: string
          created_at?: string
          id?: number
          original_filename?: string
          size_bytes?: number
          storage_path?: string
          updated_at?: string
          uploader_user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      processing_status_enum: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {
      processing_status_enum: ["PENDING", "PROCESSING", "COMPLETED", "FAILED"],
    },
  },
} as const

