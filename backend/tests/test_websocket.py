def test_websocket_accepts_connection(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_text("ping")
