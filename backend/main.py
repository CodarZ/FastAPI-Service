from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"code": 200, "data": "Hello World", "message": "success"}
