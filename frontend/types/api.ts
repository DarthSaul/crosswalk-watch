export type JobStatus = 'uploaded' | 'processing' | 'complete' | 'failed'

export type Point = readonly [number, number]

export interface ZoneDefinition {
  name: string
  color: string
  points: Point[]
}

export interface ZoneStats {
  name: string
  color: string
  entries: number
  avg_dwell_seconds: number
  max_concurrent: number
  occupancy_series: number[]
}

export interface ProcessingStats {
  total_frames: number
  processed_frames: number
  unique_tracks: number
  duration_seconds: number
  fps: number
  zones: ZoneStats[]
}

export interface SampleInfo {
  filename: string
  size_bytes: number
  duration_seconds: number | null
  width: number | null
  height: number | null
  fps: number | null
  thumbnail_url: string
}

export interface JobResponse {
  id: string
  status: JobStatus
  original_filename: string
  thumbnail_url: string | null
  result_url: string | null
  progress: number
  stats: ProcessingStats | null
  zones: ZoneDefinition[]
  created_at: string
  error: string | null
}
