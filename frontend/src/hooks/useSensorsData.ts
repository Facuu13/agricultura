import { useCallback, useEffect, useMemo, useState } from 'react'

import { fetchHistory, fetchSensors, type SensorReading, type WsReadingPayload } from '../api'

function formatTime(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch {
    return iso
  }
}

export type HistoryPoint = {
  received_at: string
  soil_moisture: number
  rain_mm: number
  wind_speed: number
  radiation: number
  t: string
}

export function useSensorsData(deviceId: string) {
  const [sensors, setSensors] = useState<SensorReading[]>([])
  const [history, setHistory] = useState<HistoryPoint[]>([])
  const [live, setLive] = useState<WsReadingPayload | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshSensors = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setSensors(await fetchSensors())
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  const refreshHistory = useCallback(async () => {
    if (!deviceId.trim()) return
    setError(null)
    try {
      const rows = await fetchHistory(deviceId.trim())
      setHistory(rows.map((row) => ({ ...row, t: formatTime(row.received_at) })))
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }, [deviceId])

  useEffect(() => {
    void refreshSensors()
  }, [refreshSensors])

  useEffect(() => {
    void refreshHistory()
  }, [refreshHistory])

  const latestForDevice = useMemo(() => {
    if (live && live.device_id === deviceId) return live
    return sensors.find((s) => s.device_id === deviceId) ?? null
  }, [live, sensors, deviceId])

  return {
    sensors,
    history,
    live,
    loading,
    error,
    latestForDevice,
    setLive,
    setError,
    refreshSensors,
    refreshHistory,
  }
}
