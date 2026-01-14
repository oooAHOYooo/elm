import { Stack } from 'expo-router'
import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { Providers } from './providers'

export default function RootLayout() {
  const { syncAuth } = useAuthStore()

  useEffect(() => {
    syncAuth()
  }, [])

  return (
    <Providers>
      <Stack>
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="login" options={{ title: 'Login' }} />
      <Stack.Screen name="register" options={{ title: 'Sign Up' }} />
      <Stack.Screen name="dashboard" options={{ title: 'Roadie' }} />
      <Stack.Screen name="drive/[id]" options={{ title: 'Drive Details' }} />
      <Stack.Screen name="record" options={{ title: 'Record Drive' }} />
      </Stack>
    </Providers>
  )
}

