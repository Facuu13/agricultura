import { httpBaseToWsUrl } from './httpToWs'

const DEFAULT_BASE = 'http://localhost:8001'

export function getApiBase(): string {
  const fromEnv = import.meta.env.VITE_API_BASE as string | undefined
  const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('agro_api_base') : null
  const base = (stored || fromEnv || DEFAULT_BASE).replace(/\/$/, '')
  return base
}

export function getWsUrl(): string {
  return httpBaseToWsUrl(getApiBase())
}

export type SensorReading = {
  device_id: string
  received_at: string
  soil_moisture: number
  rain_mm: number
  wind_speed: number
  radiation: number
  device_timestamp: number | null
}

export type WsReadingPayload = {
  device_id: string
  soil_moisture: number
  rain_mm: number
  wind_speed: number
  radiation: number
  received_at: string
  irrigation_recommended: boolean
  irrigation_reason: string
  valve_auto: string
}

export async function fetchSensors(): Promise<SensorReading[]> {
  const r = await fetch(`${getApiBase()}/sensors`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function fetchHistory(
  deviceId: string,
  from?: string,
  to?: string,
): Promise<
  Array<{
    received_at: string
    soil_moisture: number
    rain_mm: number
    wind_speed: number
    radiation: number
  }>
> {
  const q = new URLSearchParams({ device_id: deviceId })
  if (from) q.set('from_ts', from)
  if (to) q.set('to_ts', to)
  const r = await fetch(`${getApiBase()}/history?${q.toString()}`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function postActuator(deviceId: string, valve: 'ON' | 'OFF'): Promise<void> {
  const r = await fetch(`${getApiBase()}/actuator`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device_id: deviceId, valve }),
  })
  if (!r.ok) throw new Error(await r.text())
}
