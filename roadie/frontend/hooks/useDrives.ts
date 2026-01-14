import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useDrives() {
  return useQuery({
    queryKey: ['drives'],
    queryFn: async () => {
      const response = await api.get('/drives')
      return response.data
    },
  })
}

