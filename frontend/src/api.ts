import { httpBaseToWsUrl } from './httpToWs'

const DEFAULT_BASE = 'http://localhost:8001'
const DEFAULT_TIMEOUT_MS = 8000

export function getApiBase(): string {
  const fromEnv = import.meta.env.VITE_API_BASE as string | undefined
  const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('agro_api_base') : null
  const base = (stored || fromEnv || DEFAULT_BASE).replace(/\/$/, '')
  return base
}

export function getWsUrl(): string {
  return httpBaseToWsUrl(getApiBase())
}

export function getActuatorApiKey(): string | null {
  const fromEnv = import.meta.env.VITE_ACTUATOR_API_KEY as string | undefined
  const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('agro_actuator_api_key') : null
  return (stored || fromEnv || '').trim() || null
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

async function apiRequest(path: string, init?: RequestInit, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(`${getApiBase()}${path}`, { ...init, signal: controller.signal })
    if (!response.ok) {
      throw new Error(await response.text())
    }
    return response
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeoutMs}ms`)
    }
    throw error
  } finally {
    window.clearTimeout(timer)
  }
}

export async function fetchSensors(): Promise<SensorReading[]> {
  const r = await apiRequest('/sensors')
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
  const r = await apiRequest(`/history?${q.toString()}`)
  return r.json()
}

export async function postActuator(deviceId: string, valve: 'ON' | 'OFF'): Promise<void> {
  const apiKey = getActuatorApiKey()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (apiKey) headers['x-api-key'] = apiKey
  await apiRequest('/actuator', {
    method: 'POST',
    headers,
    body: JSON.stringify({ device_id: deviceId, valve }),
  })
}
