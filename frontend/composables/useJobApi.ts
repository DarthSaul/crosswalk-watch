import type { JobResponse, SampleInfo, ZoneDefinition } from '~/types/api'

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

  async function analyzeJob(
    id: string,
    zones: ZoneDefinition[] = [],
  ): Promise<JobResponse> {
    return await $fetch<JobResponse>(`${apiBase}/api/jobs/${id}/analyze`, {
      method: 'POST',
      body: { zones },
    })
  }

  async function listSamples(): Promise<SampleInfo[]> {
    return await $fetch<SampleInfo[]>(`${apiBase}/api/samples`)
  }

  async function createJobFromSample(filename: string): Promise<JobResponse> {
    return await $fetch<JobResponse>(`${apiBase}/api/videos/from-sample`, {
      method: 'POST',
      body: { filename },
    })
  }

  function thumbnailUrl(id: string): string {
    return `${apiBase}/api/jobs/${id}/thumbnail`
  }

  function resultUrl(id: string): string {
    return `${apiBase}/api/jobs/${id}/result`
  }

  function sampleThumbnailUrl(filename: string): string {
    return `${apiBase}/api/samples/${encodeURIComponent(filename)}/thumbnail`
  }

  return {
    uploadVideo,
    getJob,
    analyzeJob,
    listSamples,
    createJobFromSample,
    thumbnailUrl,
    resultUrl,
    sampleThumbnailUrl,
    apiBase,
  }
}
