import type { JobResponse } from '~/types/api'

export function useJobApi() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  async function uploadVideo(file: File): Promise<JobResponse> {
    const form = new FormData()
    form.append('file', file)
    return await $fetch<JobResponse>(`${apiBase}/api/videos`, {
      method: 'POST',
      body: form,
    })
  }

  async function getJob(id: string): Promise<JobResponse> {
    return await $fetch<JobResponse>(`${apiBase}/api/jobs/${id}`)
  }

  async function analyzeJob(id: string): Promise<JobResponse> {
    return await $fetch<JobResponse>(`${apiBase}/api/jobs/${id}/analyze`, {
      method: 'POST',
    })
  }

  function thumbnailUrl(id: string): string {
    return `${apiBase}/api/jobs/${id}/thumbnail`
  }

  function resultUrl(id: string): string {
    return `${apiBase}/api/jobs/${id}/result`
  }

  return { uploadVideo, getJob, analyzeJob, thumbnailUrl, resultUrl, apiBase }
}
