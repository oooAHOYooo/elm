'use client'

import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface MapProps {
  routePoints: Array<{
    latitude: number
    longitude: number
    sequence: number
  }>
}

function MapBounds({ routePoints }: MapProps) {
  const map = useMap()

  useEffect(() => {
    if (routePoints.length > 0) {
      const bounds = L.latLngBounds(
        routePoints.map((point) => [point.latitude, point.longitude])
      )
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [routePoints, map])

  return null
}

export default function Map({ routePoints }: MapProps) {
  const mapRef = useRef<L.Map>(null)

  const positions = routePoints
    .sort((a, b) => a.sequence - b.sequence)
    .map((point) => [point.latitude, point.longitude] as [number, number])

  if (positions.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        No route data available
      </div>
    )
  }

  const center: [number, number] = positions[Math.floor(positions.length / 2)]

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
      ref={mapRef}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapBounds routePoints={routePoints} />
      <Polyline positions={positions} color="#0ea5e9" weight={4} />
    </MapContainer>
  )
}

