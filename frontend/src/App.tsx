import { useCallback, useState } from 'react'
import './App.css'
import { getActuatorApiKey, getApiBase, postActuator, type WsReadingPayload } from './api'
import { HistoryChart } from './components/HistoryChart'
import { MetricsCards } from './components/MetricsCards'
import { ValveControls } from './components/ValveControls'
import { useAgroWebSocket } from './hooks/useAgroWebSocket'
import { useSensorsData } from './hooks/useSensorsData'

export default function App() {
  const [apiBaseInput, setApiBaseInput] = useState(getApiBase)
  const [actuatorKeyInput, setActuatorKeyInput] = useState(getActuatorApiKey() ?? '')
  const [deviceId, setDeviceId] = useState('dev1')
  const [manualValve, setManualValve] = useState<string | null>(null)
  const { history, loading, error, latestForDevice, setLive, setError, refreshHistory, refreshSensors } =
    useSensorsData(deviceId)

  const handleReading = useCallback(
    (payload: WsReadingPayload) => {
      setLive(payload)
      if (payload.device_id === deviceId) setManualValve(null)
    },
    [deviceId, setLive],
  )

  const handleManualActuator = useCallback((payload: { device_id: string; valve: string }) => {
    setManualValve(payload.valve)
  }, [])

  const { wsState } = useAgroWebSocket({
    onReading: handleReading,
    onManualActuator: handleManualActuator,
  })

  const applyApiBase = () => {
    localStorage.setItem('agro_api_base', apiBaseInput.trim())
    window.location.reload()
  }

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

  const applyActuatorKey = () => {
    const value = actuatorKeyInput.trim()
    if (value) {
      localStorage.setItem('agro_actuator_api_key', value)
    } else {
      localStorage.removeItem('agro_actuator_api_key')
    }
  }

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
          API key actuador
          <input type="text" value={actuatorKeyInput} onChange={(e) => setActuatorKeyInput(e.target.value)} />
        </label>
        <button type="button" className="ghost" onClick={applyActuatorKey}>
          Guardar API key
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

      <MetricsCards latestForDevice={latestForDevice} />

      <ValveControls onSendValve={(valve) => void sendValve(valve)} />

      <HistoryChart history={history} onRefresh={() => void refreshHistory()} />
    </div>
  )
}
