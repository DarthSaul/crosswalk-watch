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

  function thumbnailUrl(id: string): string {
    return `${apiBase}/api/jobs/${id}/thumbnail`
  }

  return { uploadVideo, getJob, thumbnailUrl, apiBase }
}
