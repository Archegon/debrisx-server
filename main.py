from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host='127.0.0.1', port=5000, reload=True)