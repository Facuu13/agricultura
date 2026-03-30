from fastapi import WebSocket


class WsHub:
    def __init__(self) -> None:
        self._clients: list[WebSocket] = []

    async def register(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.append(ws)

    def unregister(self, ws: WebSocket) -> None:
        if ws in self._clients:
            self._clients.remove(ws)

    async def broadcast(self, message: dict) -> None:
        stale: list[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_json(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.unregister(ws)
