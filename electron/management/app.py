from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
import uvicorn
import subprocess
import asyncio
import sys

from func.config import configTable, checkConfig, addSuperuser, checkSuperuser

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/startup")
async def startup(request: Request):
    config = await checkConfig()
    if config and config[0] and config[1]:
        return JSONResponse({"hasUser": True}, status_code=200)
    else:
        return JSONResponse({"hasUser": False}, status_code=200)
    
@app.post("/setup")
async def setup(request: Request):
    data = await request.json()
    if not data.get("username") or not data.get("password"):
        return JSONResponse({"error": "Username and password are required."}, status_code=400)
    state = await addSuperuser(data["username"], data["password"])
    if state is None:
        return JSONResponse({"error": "Superuser already exists."}, status_code=400)
    elif state:
        return JSONResponse({"message": "Superuser created successfully."}, status_code=201)
    else:
        return JSONResponse({"error": "Failed to create superuser."}, status_code=500)
    
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    if not data.get("username") or not data.get("password"):
        return JSONResponse({"error": "Username and password are required."}, status_code=400)
    is_valid = await checkSuperuser(data["username"], data["password"])
    if is_valid:
        return JSONResponse({"message": "Login successful."}, status_code=200)
    else:
        return JSONResponse({"error": "Invalid username or password."}, status_code=401)
    

if __name__ == "__main__":
    import os
    import sys
    import uvicorn

    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    sys.path.insert(0, os.path.dirname(current_dir))

    from management.app import app

    asyncio.run(configTable())

    uvicorn.run(app, host="127.0.0.1", port=8081, reload=False)