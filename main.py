from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host='0.0.0.0', port=5000, reload=True)