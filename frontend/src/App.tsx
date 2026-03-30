import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'
import {
  fetchHistory,
  fetchSensors,
  getApiBase,
  getWsUrl,
  postActuator,
  type SensorReading,
  type WsReadingPayload,
} from './api'

type WsMsg =
  | { type: 'reading'; payload: WsReadingPayload }
  | { type: 'actuator_manual'; payload: { device_id: string; valve: string } }

function formatTime(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch {
    return iso
  }
}

export default function App() {
  const [apiBaseInput, setApiBaseInput] = useState(getApiBase)
  const [deviceId, setDeviceId] = useState('dev1')
  const [sensors, setSensors] = useState<SensorReading[]>([])
  const [live, setLive] = useState<WsReadingPayload | null>(null)
  const [manualValve, setManualValve] = useState<string | null>(null)
  const [history, setHistory] = useState<
    Array<{
      received_at: string
      soil_moisture: number
      rain_mm: number
      wind_speed: number
      radiation: number
      t: string
    }>
  >([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [wsState, setWsState] = useState<'off' | 'connecting' | 'open'>('off')

  const applyApiBase = () => {
    localStorage.setItem('agro_api_base', apiBaseInput.trim())
    window.location.reload()
  }

  const refreshSensors = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchSensors()
      setSensors(data)
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
      const h = await fetchHistory(deviceId.trim())
      setHistory(
        h.map((row) => ({
          ...row,
          t: formatTime(row.received_at),
        })),
      )
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

  useEffect(() => {
    setWsState('connecting')
    const url = getWsUrl()
    const ws = new WebSocket(url)
    ws.onopen = () => setWsState('open')
    ws.onclose = () => setWsState('off')
    ws.onerror = () => setWsState('off')
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(String(ev.data)) as WsMsg
        if (msg.type === 'reading') {
          setLive(msg.payload)
          if (msg.payload.device_id === deviceId) {
            setManualValve(null)
          }
        }
        if (msg.type === 'actuator_manual') {
          setManualValve(msg.payload.valve)
        }
      } catch {
        /* ignore */
      }
    }
    return () => ws.close()
  }, [deviceId])

  const latestForDevice = useMemo(() => {
    if (live && live.device_id === deviceId) return live
    return sensors.find((s) => s.device_id === deviceId)
  }, [live, sensors, deviceId])

  const irrigationBadge = () => {
    if (!latestForDevice || !('irrigation_recommended' in latestForDevice)) {
      return { className: 'badge ok', text: 'Sin datos en vivo' }
    }
    const rec = (latestForDevice as WsReadingPayload).irrigation_recommended
    const reason = (latestForDevice as WsReadingPayload).irrigation_reason
    if (rec) return { className: 'badge dry', text: `Riego recomendado (${reason})` }
    return { className: 'badge ok', text: `Riego no requerido (${reason})` }
  }

  const badge = irrigationBadge()

  const sendValve = async (valve: 'ON' | 'OFF') => {
    setError(null)
    try {
      await postActuator(deviceId.trim(), valve)
      setManualValve(valve)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className="app">
      <h1>Estación agrometeorológica</h1>

      <div className="row">
        <label>
          URL API
          <input
            type="text"
            value={apiBaseInput}
            onChange={(e) => setApiBaseInput(e.target.value)}
            placeholder="http://localhost:8001"
          />
        </label>
        <button type="button" className="ghost" onClick={applyApiBase}>
          Guardar y recargar
        </button>
        <label>
          Device ID
          <input
            type="text"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
          />
        </label>
        <button type="button" className="ghost" onClick={() => void refreshSensors()} disabled={loading}>
          Actualizar sensores
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      <p className="status-bar">
        WebSocket: {wsState}
        {manualValve ? ` · Último comando manual: ${manualValve}` : ''}
      </p>

      <div style={{ marginBottom: '1rem' }}>
        <span className={badge.className}>{badge.text}</span>
      </div>

      <div className="cards">
        <div className="card">
          <h2>Humedad suelo</h2>
          <div>
            <span className="value">
              {latestForDevice != null ? latestForDevice.soil_moisture.toFixed(1) : '—'}
            </span>
            <span className="unit">%</span>
          </div>
        </div>
        <div className="card">
          <h2>Lluvia (lectura)</h2>
          <div>
            <span className="value">
              {latestForDevice != null ? latestForDevice.rain_mm.toFixed(2) : '—'}
            </span>
            <span className="unit">mm</span>
          </div>
        </div>
        <div className="card">
          <h2>Viento</h2>
          <div>
            <span className="value">
              {latestForDevice != null ? latestForDevice.wind_speed.toFixed(1) : '—'}
            </span>
            <span className="unit">m/s</span>
          </div>
        </div>
        <div className="card">
          <h2>Radiación</h2>
          <div>
            <span className="value">
              {latestForDevice != null ? latestForDevice.radiation.toFixed(0) : '—'}
            </span>
            <span className="unit">W/m²</span>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1.25rem' }}>
        <h2 style={{ fontSize: '1rem', color: '#9aba9f', margin: '0 0 0.5rem' }}>Control de válvula</h2>
        <div className="controls">
          <button type="button" className="on" onClick={() => void sendValve('ON')}>
            ON
          </button>
          <button type="button" className="off" onClick={() => void sendValve('OFF')}>
            OFF
          </button>
        </div>
      </div>

      <div className="chart-wrap">
        <h2 style={{ fontSize: '1rem', color: '#9aba9f', margin: '0 0 0.75rem' }}>Histórico (humedad y radiación)</h2>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={history}>
            <CartesianGrid stroke="#2a3d2e" strokeDasharray="3 3" />
            <XAxis dataKey="t" tick={{ fill: '#7a9a82', fontSize: 11 }} />
            <YAxis yAxisId="l" tick={{ fill: '#7a9a82', fontSize: 11 }} />
            <YAxis yAxisId="r" orientation="right" tick={{ fill: '#7a9a82', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#131a14', border: '1px solid #2a3d2e' }}
              labelStyle={{ color: '#c8e6c9' }}
            />
            <Legend />
            <Line
              yAxisId="l"
              type="monotone"
              dataKey="soil_moisture"
              name="Humedad %"
              stroke="#81c784"
              dot={false}
              strokeWidth={2}
            />
            <Line
              yAxisId="r"
              type="monotone"
              dataKey="radiation"
              name="Radiación"
              stroke="#ffb74d"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
        <button type="button" className="ghost" style={{ marginTop: '0.75rem' }} onClick={() => void refreshHistory()}>
          Refrescar histórico
        </button>
      </div>
    </div>
  )
}
