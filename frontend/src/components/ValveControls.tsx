type Props = {
  onSendValve: (valve: 'ON' | 'OFF') => void
}

export function ValveControls({ onSendValve }: Props) {
  return (
    <div style={{ marginTop: '1.25rem' }}>
      <h2 style={{ fontSize: '1rem', color: '#9aba9f', margin: '0 0 0.5rem' }}>Control de válvula</h2>
      <div className="controls">
        <button type="button" className="on" onClick={() => onSendValve('ON')}>
          ON
        </button>
        <button type="button" className="off" onClick={() => onSendValve('OFF')}>
          OFF
        </button>
      </div>
    </div>
  )
}
