import { create } from 'zustand'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (accessToken: string, refreshToken: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  login: (accessToken, refreshToken) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken)
      localStorage.setItem('refresh_token', refreshToken)
    }
    set({
      accessToken,
      refreshToken,
      isAuthenticated: true,
    })
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
    set({
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })
  },
}))

// Initialize from localStorage on mount
if (typeof window !== 'undefined') {
  const initAuth = () => {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    if (accessToken && refreshToken) {
      useAuthStore.setState({
        accessToken,
        refreshToken,
        isAuthenticated: true,
      })
    }
  }
  // Run on next tick to avoid hydration issues
  setTimeout(initAuth, 0)
}

