import type { SensorReading, WsReadingPayload } from '../api'

type Props = {
  latestForDevice: SensorReading | WsReadingPayload | null
}

export function MetricsCards({ latestForDevice }: Props) {
  return (
    <div className="cards">
      <div className="card">
        <h2>Humedad suelo</h2>
        <div>
          <span className="value">{latestForDevice != null ? latestForDevice.soil_moisture.toFixed(1) : '—'}</span>
          <span className="unit">%</span>
        </div>
      </div>
      <div className="card">
        <h2>Lluvia (lectura)</h2>
        <div>
          <span className="value">{latestForDevice != null ? latestForDevice.rain_mm.toFixed(2) : '—'}</span>
          <span className="unit">mm</span>
        </div>
      </div>
      <div className="card">
        <h2>Viento</h2>
        <div>
          <span className="value">{latestForDevice != null ? latestForDevice.wind_speed.toFixed(1) : '—'}</span>
          <span className="unit">m/s</span>
        </div>
      </div>
      <div className="card">
        <h2>Radiación</h2>
        <div>
          <span className="value">{latestForDevice != null ? latestForDevice.radiation.toFixed(0) : '—'}</span>
          <span className="unit">W/m²</span>
        </div>
      </div>
    </div>
  )
}
