import { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native'
import { useRouter } from 'expo-router'
import * as Location from 'expo-location'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { formatDistance, formatDuration } from '@/lib/utils'
import MapView, { Polyline } from 'react-native-maps'

interface RoutePoint {
  latitude: number
  longitude: number
  altitude: number | null
  speed: number | null
  timestamp: Date
  sequence: number
}

export default function RecordScreen() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [isRecording, setIsRecording] = useState(false)
  const [routePoints, setRoutePoints] = useState<RoutePoint[]>([])
  const [distance, setDistance] = useState(0)
  const [duration, setDuration] = useState(0)
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [locationSubscription, setLocationSubscription] = useState<Location.LocationSubscription | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace('/login')
    }
  }, [isAuthenticated, router])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRecording && startTime) {
      interval = setInterval(() => {
        setDuration(Math.floor((new Date().getTime() - startTime.getTime()) / 1000))
      }, 1000)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isRecording, startTime])

  const requestPermissions = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync()
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Location permission is required to record drives')
      return false
    }
    return true
  }

  const startRecording = async () => {
    const hasPermission = await requestPermissions()
    if (!hasPermission) return

    const now = new Date()
    setStartTime(now)
    setIsRecording(true)
    setRoutePoints([])
    setDistance(0)
    setDuration(0)

    const subscription = await Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.BestForNavigation,
        timeInterval: 5000, // Update every 5 seconds
        distanceInterval: 10, // Update every 10 meters
      },
      (location) => {
        const point: RoutePoint = {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          altitude: location.coords.altitude || null,
          speed: location.coords.speed ? location.coords.speed * 3.6 : null, // Convert to km/h
          timestamp: new Date(),
          sequence: routePoints.length,
        }

        setRoutePoints((prev) => {
          const newPoints = [...prev, point]
          // Calculate distance
          if (newPoints.length > 1) {
            let totalDistance = 0
            for (let i = 1; i < newPoints.length; i++) {
              const prev = newPoints[i - 1]
              const curr = newPoints[i]
              // Simple distance calculation (Haversine would be better)
              const latDiff = curr.latitude - prev.latitude
              const lonDiff = curr.longitude - prev.longitude
              const dist = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff) * 111000 // Rough conversion
              totalDistance += dist
            }
            setDistance(totalDistance)
          }
          return newPoints
        })
      }
    )

    setLocationSubscription(subscription)
  }

  const stopRecording = () => {
    if (locationSubscription) {
      locationSubscription.remove()
      setLocationSubscription(null)
    }
    setIsRecording(false)
  }

  const saveDrive = async () => {
    if (routePoints.length === 0) {
      Alert.alert('Error', 'No route data to save')
      return
    }

    try {
      const driveData = {
        name: `Drive ${new Date().toLocaleDateString()}`,
        start_time: startTime?.toISOString(),
        route_points: routePoints.map((point, index) => ({
          latitude: point.latitude,
          longitude: point.longitude,
          altitude: point.altitude,
          speed: point.speed,
          timestamp: point.timestamp.toISOString(),
          sequence: index,
        })),
      }

      await api.post('/drives', driveData)
      Alert.alert('Success', 'Drive saved!', [
        { text: 'OK', onPress: () => router.replace('/dashboard') },
      ])
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to save drive')
    }
  }

  const cancelRecording = () => {
    Alert.alert('Cancel Drive', 'Are you sure you want to cancel? All data will be lost.', [
      { text: 'No', style: 'cancel' },
      {
        text: 'Yes',
        style: 'destructive',
        onPress: () => {
          stopRecording()
          router.back()
        },
      },
    ])
  }

  const coordinates = routePoints.map((point) => ({
    latitude: point.latitude,
    longitude: point.longitude,
  }))

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: routePoints[0]?.latitude || 37.7749,
          longitude: routePoints[0]?.longitude || -122.4194,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
        region={
          routePoints.length > 0
            ? {
                latitude: routePoints[routePoints.length - 1].latitude,
                longitude: routePoints[routePoints.length - 1].longitude,
                latitudeDelta: 0.01,
                longitudeDelta: 0.01,
              }
            : undefined
        }
      >
        {coordinates.length > 1 && (
          <Polyline coordinates={coordinates} strokeColor="#0ea5e9" strokeWidth={4} />
        )}
      </MapView>

      <View style={styles.overlay}>
        <View style={styles.statsContainer}>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{formatDistance(distance)}</Text>
            <Text style={styles.statLabel}>Distance</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{formatDuration(duration)}</Text>
            <Text style={styles.statLabel}>Time</Text>
          </View>
        </View>

        <View style={styles.buttonContainer}>
          {!isRecording ? (
            <TouchableOpacity style={styles.startButton} onPress={startRecording}>
              <Text style={styles.buttonText}>Start Recording</Text>
            </TouchableOpacity>
          ) : (
            <>
              <TouchableOpacity style={styles.stopButton} onPress={stopRecording}>
                <Text style={styles.buttonText}>Pause</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveButton} onPress={saveDrive}>
                <Text style={styles.buttonText}>Save Drive</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.cancelButton} onPress={cancelRecording}>
                <Text style={styles.buttonText}>Cancel</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  map: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#38bdf8',
  },
  statLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  buttonContainer: {
    gap: 8,
  },
  startButton: {
    backgroundColor: '#0ea5e9',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#0ea5e9',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  stopButton: {
    backgroundColor: '#f59e0b',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#f59e0b',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  saveButton: {
    backgroundColor: '#10b981',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  cancelButton: {
    backgroundColor: '#ef4444',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#ef4444',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
})

