# import uvicorn
#
# if __name__ == "__main__":
#     uvicorn.run("app.app:app", host="127.0.0.1",port=8888, log_level="info")
from fastapi import FastAPI

app = FastAPI()

# a test change for vercel
@app.get("/")
async def root():
    return {"message": "Hello World"}
