import { useEffect, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

interface Hospital {
  id: string
  name: string
  latitude: number
  longitude: number
}

interface MapProps {
  hospitals: Hospital[]
}

export default function Map({ hospitals }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)

  useEffect(() => {
    if (!mapContainer.current) return

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-122.4194, 37.7749], // San Francisco default
      zoom: 12,
      accessToken: process.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
    })

    // Add markers for hospitals
    hospitals.forEach((hospital) => {
      new mapboxgl.Marker()
        .setLngLat([hospital.longitude, hospital.latitude])
        .setPopup(new mapboxgl.Popup().setHTML(`<strong>${hospital.name}</strong>`))
        .addTo(map.current!)
    })

    return () => {
      map.current?.remove()
    }
  }, [hospitals])

  return <div ref={mapContainer} className="h-96 w-full rounded-lg" />
}


