import { useEffect, useRef, useState } from 'react'

import { getWsUrl, type WsReadingPayload } from '../api'

type WsMsg =
  | { type: 'reading'; payload: WsReadingPayload }
  | { type: 'actuator_manual'; payload: { device_id: string; valve: string } }

type UseAgroWebSocketArgs = {
  onReading: (payload: WsReadingPayload) => void
  onManualActuator: (payload: { device_id: string; valve: string }) => void
}

export function useAgroWebSocket({ onReading, onManualActuator }: UseAgroWebSocketArgs) {
  const [wsState, setWsState] = useState<'off' | 'connecting' | 'open'>('off')
  const reconnectDelayRef = useRef(1000)
  const reconnectTimerRef = useRef<number | null>(null)

  useEffect(() => {
    let ws: WebSocket | null = null
    let closedByHook = false

    const connect = () => {
      setWsState('connecting')
      ws = new WebSocket(getWsUrl())

      ws.onopen = () => {
        reconnectDelayRef.current = 1000
        setWsState('open')
      }

      ws.onerror = () => {
        setWsState('off')
      }

      ws.onclose = () => {
        setWsState('off')
        if (closedByHook) return
        reconnectTimerRef.current = window.setTimeout(() => {
          connect()
        }, reconnectDelayRef.current)
        reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 15000)
      }

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(String(ev.data)) as WsMsg
          if (msg.type === 'reading') onReading(msg.payload)
          if (msg.type === 'actuator_manual') onManualActuator(msg.payload)
        } catch {
          // Ignore malformed WS payloads.
        }
      }
    }

    connect()

    return () => {
      closedByHook = true
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current)
      }
      ws?.close()
    }
  }, [onManualActuator, onReading])

  return { wsState }
}
