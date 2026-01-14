import { useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl } from 'react-native'
import { useRouter } from 'expo-router'
import { useAuthStore } from '@/store/authStore'
import { useDrives } from '@/hooks/useDrives'
import { useStats } from '@/hooks/useStats'
import { formatDistance, formatDuration } from '@/lib/utils'

export default function DashboardScreen() {
  const router = useRouter()
  const { isAuthenticated, logout } = useAuthStore()
  const { data: drives, isLoading, refetch } = useDrives()
  const { data: stats } = useStats()

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace('/login')
    }
  }, [isAuthenticated, router])

  if (!isAuthenticated) {
    return null
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Roadie</Text>
        <TouchableOpacity onPress={logout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {stats && (
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{stats.total_drives}</Text>
            <Text style={styles.statLabel}>Drives</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{formatDistance(stats.total_distance)}</Text>
            <Text style={styles.statLabel}>Distance</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{formatDuration(stats.total_duration)}</Text>
            <Text style={styles.statLabel}>Time</Text>
          </View>
        </View>
      )}

      <TouchableOpacity
        style={styles.recordButton}
        onPress={() => router.push('/record')}
      >
        <Text style={styles.recordButtonText}>Start Recording</Text>
      </TouchableOpacity>

      <FlatList
        data={drives}
        keyExtractor={(item) => item.id}
        refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} />}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.driveItem}
            onPress={() => router.push(`/drive/${item.id}`)}
          >
            <View>
              <Text style={styles.driveName}>
                {item.name || 'Unnamed Drive'}
              </Text>
              <Text style={styles.driveDate}>
                {new Date(item.start_time).toLocaleDateString()}
              </Text>
            </View>
            <View style={styles.driveStats}>
              <Text style={styles.driveDistance}>
                {formatDistance(item.distance)}
              </Text>
              <Text style={styles.driveDuration}>
                {formatDuration(item.duration)}
              </Text>
            </View>
          </TouchableOpacity>
        )}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No drives yet</Text>
            <Text style={styles.emptySubtext}>Start your first drive!</Text>
          </View>
        }
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#38bdf8',
  },
  logoutText: {
    color: '#cbd5e1',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#38bdf8',
  },
  statLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  recordButton: {
    backgroundColor: '#0ea5e9',
    padding: 16,
    margin: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#0ea5e9',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  recordButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  driveItem: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  driveName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    color: '#fff',
  },
  driveDate: {
    fontSize: 12,
    color: '#94a3b8',
  },
  driveStats: {
    alignItems: 'flex-end',
  },
  driveDistance: {
    fontSize: 16,
    fontWeight: '600',
    color: '#38bdf8',
    marginBottom: 4,
  },
  driveDuration: {
    fontSize: 12,
    color: '#94a3b8',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    color: '#94a3b8',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#64748b',
  },
})

