import socket
import uvicorn
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"Current local IP address: {local_ip}")
    uvicorn.run("server.app:app", host='0.0.0.0', port=5000, reload=True)
