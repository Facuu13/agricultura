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

import type { HistoryPoint } from '../hooks/useSensorsData'

type Props = {
  history: HistoryPoint[]
  onRefresh: () => void
}

export function HistoryChart({ history, onRefresh }: Props) {
  return (
    <div className="chart-wrap">
      <h2 style={{ fontSize: '1rem', color: '#9aba9f', margin: '0 0 0.75rem' }}>Histórico (humedad y radiación)</h2>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={history}>
          <CartesianGrid stroke="#2a3d2e" strokeDasharray="3 3" />
          <XAxis dataKey="t" tick={{ fill: '#7a9a82', fontSize: 11 }} />
          <YAxis yAxisId="l" tick={{ fill: '#7a9a82', fontSize: 11 }} />
          <YAxis yAxisId="r" orientation="right" tick={{ fill: '#7a9a82', fontSize: 11 }} />
          <Tooltip contentStyle={{ background: '#131a14', border: '1px solid #2a3d2e' }} labelStyle={{ color: '#c8e6c9' }} />
          <Legend />
          <Line yAxisId="l" type="monotone" dataKey="soil_moisture" name="Humedad %" stroke="#81c784" dot={false} strokeWidth={2} />
          <Line yAxisId="r" type="monotone" dataKey="radiation" name="Radiación" stroke="#ffb74d" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
      <button type="button" className="ghost" style={{ marginTop: '0.75rem' }} onClick={onRefresh}>
        Refrescar histórico
      </button>
    </div>
  )
}
