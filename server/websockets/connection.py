import asyncio
from fastapi import WebSocket, WebSocketDisconnect

clients = {
    "raspberry": [],
    "frontend": []
}

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_type = websocket.query_params.get("client")

    if client_type not in clients:
        await websocket.close(code=1000, reason="Invalid client type")
        return

    clients[client_type].append(websocket)
    client_ip = websocket.client.host  # Get the client IP address
    print(f"Connection accepted from {client_ip} ({client_type})")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from {client_ip} ({client_type}): {data}")
            target_client_type = "frontend" if client_type == "raspberry" else "raspberry"
            await broadcast_message(f"Message text was: {data}", target_client_type)
    except WebSocketDisconnect:
        print(f"Connection closed from {client_ip} ({client_type})")
    finally:
        clients[client_type].remove(websocket)

async def broadcast_message(message: str, target_client_type: str):
    for client in clients[target_client_type]:
        try:
            await client.send_text(message)
        except Exception as e:
            print(f"Error sending message to client ({target_client_type}): {e}")
            clients[target_client_type].remove(client)