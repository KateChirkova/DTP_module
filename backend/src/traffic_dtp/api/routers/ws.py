from fastapi import WebSocket, WebSocketDisconnect

connected_clients = []


@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
     # Уведомления
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"👥 WebSocket подключён: {len(connected_clients)}")

    try:
        while True:
            await websocket.receive_text()  # Ждём ping
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"👋 WebSocket отключён: {len(connected_clients)}")


# Рассылка при новой Detection
async def notify_new_detection(detection_id: int, confidence: float):
    message = f"🚗 НОВОЕ ДТП #{detection_id} (conf={confidence:.2f})"
    for client in connected_clients:
        await client.send_text(message)