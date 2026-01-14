'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { useDrives } from '@/hooks/useDrives'
import { useStats } from '@/hooks/useStats'
import Link from 'next/link'
import { formatDistance, formatDuration } from '@/lib/utils'

export default function DashboardPage() {
  const router = useRouter()
  const { isAuthenticated, logout } = useAuthStore()
  const { data: drives, isLoading: drivesLoading } = useDrives()
  const { data: stats, isLoading: statsLoading } = useStats()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djJoNHYtMmgtNHptMCA0djJoNHYtMmgtNHptMCA0djJoNHYtMmgtNHptLTItMmgydjJoLTJ2LTJ6bTAgNGgyNHYtMmgtMjR2MnptMCA0aDI0di0yaC0yNHYyem0tMi0yaDJ2MmgtMnYtMnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>
      </div>

      <nav className="glass glass-strong sticky top-0 z-50 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                Roadie
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/drives/new"
                className="px-4 py-2 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:from-primary-600 hover:to-primary-700 transition-all shadow-lg shadow-primary-500/50"
              >
                New Drive
              </Link>
              <button
                onClick={logout}
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 relative z-10">
        {/* Stats */}
        {statsLoading ? (
          <div className="animate-pulse text-gray-400">Loading stats...</div>
        ) : stats ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="glass glass-hover rounded-xl p-6">
              <div className="text-sm text-gray-400">Total Drives</div>
              <div className="text-2xl font-bold text-white mt-2">{stats.total_drives}</div>
            </div>
            <div className="glass glass-hover rounded-xl p-6">
              <div className="text-sm text-gray-400">Total Distance</div>
              <div className="text-2xl font-bold text-primary-400 mt-2">
                {formatDistance(stats.total_distance)}
              </div>
            </div>
            <div className="glass glass-hover rounded-xl p-6">
              <div className="text-sm text-gray-400">Total Time</div>
              <div className="text-2xl font-bold text-primary-400 mt-2">
                {formatDuration(stats.total_duration)}
              </div>
            </div>
            <div className="glass glass-hover rounded-xl p-6">
              <div className="text-sm text-gray-400">Avg Distance</div>
              <div className="text-2xl font-bold text-primary-400 mt-2">
                {formatDistance(stats.average_distance)}
              </div>
            </div>
          </div>
        ) : null}

        {/* Recent Drives */}
        <div className="glass glass-strong rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/10">
            <h2 className="text-lg font-semibold text-white">Recent Drives</h2>
          </div>
          {drivesLoading ? (
            <div className="p-6 text-center text-gray-400">Loading drives...</div>
          ) : drives && drives.length > 0 ? (
            <div className="divide-y divide-white/10">
              {drives.map((drive) => (
                <Link
                  key={drive.id}
                  href={`/drives/${drive.id}`}
                  className="block px-6 py-4 hover:bg-white/5 transition-colors glass-hover"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-white">
                        {drive.name || 'Unnamed Drive'}
                      </div>
                      <div className="text-sm text-gray-400">
                        {new Date(drive.start_time).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-primary-400">
                        {formatDistance(drive.distance)}
                      </div>
                      <div className="text-sm text-gray-400">
                        {formatDuration(drive.duration)}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center text-gray-400">
              No drives yet. Start your first drive!
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

