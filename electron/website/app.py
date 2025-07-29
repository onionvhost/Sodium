from fastapi import FastAPI, Request, Response, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime

from traffic import TrafficMiddleware, traffic_tracker
from func.user import addUser, getUser
from func.session import encrypt, decrypt

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="website/static"), name="static")
app.add_middleware(TrafficMiddleware)

templates = Jinja2Templates(directory="website/templates")
executor = ThreadPoolExecutor()

async def render_template(template_name: str, context: dict):
  return await asyncio.get_event_loop().run_in_executor(
    executor, lambda: templates.get_template(template_name).render(context)
  )

@app.get("/traffic")
def get_traffic(request: Request):
    token = request.headers.get("Authorization")
    if token != "your_secret_token":
        return Response(status_code=404, content="not found")

    timestamp, incoming, outgoing = traffic_tracker.get_current()
    return {
        "timestamp": timestamp,
        "incoming": incoming,
        "outgoing": outgoing,
    }

@app.get("/")
async def read_root(request: Request):
    content = await render_template('index.html', {"request": request})
    return HTMLResponse(content=content)

@app.get("/login")
async def login(request: Request):
    content = await render_template('login.html', {"request": request})
    return HTMLResponse(content=content)

@app.get("/signup")
async def signup(request: Request):
    content = await render_template('signup.html', {"request": request})
    return HTMLResponse(content=content)


@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if not username or not password:
        return JSONResponse({"error": "Username and password are required."}, status_code=400)
    state = await getUser(username, password)
    if not state:
        raise HTTPException(status_code=400, detail="Invalid username and/or password")
    token = await encrypt(username, password, str(datetime.utcnow()))
    return RedirectResponse(f"/app?token={token}", status_code=303)
    
@app.post("/signup")
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and Password required")
    state = await addUser(username, password)
    if not state:
        raise HTTPException(status_code=400, detail="Not able to add User")
    token = await encrypt(username, password, str(datetime.utcnow()))
    return RedirectResponse(f"/app?token={token}", status_code=303)

@app.get("/app")
async def loadapplication(request: Request):
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=500, detail="No token provided")
    dectoken = await decrypt(token)
    if not dectoken:
        raise HTTPException(status_code=500, detail="Invalid token")
    content = await render_template("app.html", {"request": request})
    return HTMLResponse(content=content)

@app.get("/static/icons/{file}")
async def staticicons(request: Request, file: str):
    filepath = f"static/icons/{file}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(filepath, "rb") as f:
        content = f.read()
    
    return Response(content, media_type="image/svg+xml")
    


if __name__ == "__main__":
    import os
    import sys
    import uvicorn

    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    sys.path.insert(0, os.path.dirname(current_dir))

    uvicorn.run("website.app:app", host="127.0.0.1", port=8080, reload=True)