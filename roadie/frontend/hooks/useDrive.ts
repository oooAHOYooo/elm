import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useDrive(driveId: string) {
  return useQuery({
    queryKey: ['drive', driveId],
    queryFn: async () => {
      const response = await api.get(`/drives/${driveId}`)
      return response.data
    },
    enabled: !!driveId,
  })
}

