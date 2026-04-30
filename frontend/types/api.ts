export type JobStatus = 'uploaded' | 'processing' | 'complete' | 'failed'

export interface ProcessingStats {
  total_frames: number
  processed_frames: number
  unique_tracks: number
  duration_seconds: number
}

export interface JobResponse {
  id: string
  status: JobStatus
  original_filename: string
  thumbnail_url: string | null
  result_url: string | null
  progress: number
  stats: ProcessingStats | null
  created_at: string
  error: string | null
}
