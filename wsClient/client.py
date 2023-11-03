import websocket

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Closed with status code {close_status_code}: {close_msg}")

def on_open(ws):
    ws.send("Hello, server!")

if __name__ == "__main__":
    websocket.enableTrace(True)  # 开启调试信息

    addr = "ws://10.177.29.86:8080/websocket"


    # 连接到 WebSocket 服务器
    ws = websocket.WebSocketApp("ws://localhost:8888/websocket",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)

    ws.on_open = on_open
    ws.run_forever()
