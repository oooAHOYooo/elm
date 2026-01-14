'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import Link from 'next/link'

export default function NewDrivePage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djJoNHYtMmgtNHptMCA0djJoNHYtMmgtNHptMCA0djJoNHYtMmgtNHptLTItMmgydjJoLTJ2LTJ6bTAgNGgyNHYtMmgtMjR2MnptMCA0aDI0di0yaC0yNHYyem0tMi0yaDJ2MmgtMnYtMnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>
      </div>
      
      <div className="max-w-md w-full relative z-10">
        <div className="glass glass-strong rounded-2xl p-8">
          <h2 className="text-2xl font-bold mb-4 text-white">Start Recording</h2>
          <p className="text-gray-400 mb-6">
            To record a drive, please use the mobile app. The web app is for viewing your drives.
          </p>
          <Link
            href="/dashboard"
            className="block w-full text-center px-4 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:from-primary-600 hover:to-primary-700 transition-all shadow-lg shadow-primary-500/50"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

