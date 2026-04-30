export type JobStatus = 'uploaded' | 'processing' | 'complete' | 'failed'

export interface JobResponse {
  id: string
  status: JobStatus
  original_filename: string
  thumbnail_url: string | null
  created_at: string
}
