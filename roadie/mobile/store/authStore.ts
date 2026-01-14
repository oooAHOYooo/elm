import { create } from 'zustand'
import AsyncStorage from '@react-native-async-storage/async-storage'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (accessToken: string, refreshToken: string) => Promise<void>
  logout: () => Promise<void>
  syncAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  login: async (accessToken, refreshToken) => {
    await AsyncStorage.setItem('access_token', accessToken)
    await AsyncStorage.setItem('refresh_token', refreshToken)
    set({
      accessToken,
      refreshToken,
      isAuthenticated: true,
    })
  },
  logout: async () => {
    await AsyncStorage.removeItem('access_token')
    await AsyncStorage.removeItem('refresh_token')
    set({
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })
  },
  syncAuth: async () => {
    const accessToken = await AsyncStorage.getItem('access_token')
    const refreshToken = await AsyncStorage.getItem('refresh_token')
    if (accessToken && refreshToken) {
      set({
        accessToken,
        refreshToken,
        isAuthenticated: true,
      })
    }
  },
}))

