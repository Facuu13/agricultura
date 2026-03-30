import { describe, expect, it } from 'vitest'
import { httpBaseToWsUrl } from './httpToWs'

describe('httpBaseToWsUrl', () => {
  it('convierte http a ws', () => {
    expect(httpBaseToWsUrl('http://localhost:8001')).toBe('ws://localhost:8001/ws')
  })

  it('quita barra final', () => {
    expect(httpBaseToWsUrl('http://api.test/')).toBe('ws://api.test/ws')
  })

  it('convierte https a wss', () => {
    expect(httpBaseToWsUrl('https://demo.example/api')).toBe('wss://demo.example/api/ws')
  })
})
