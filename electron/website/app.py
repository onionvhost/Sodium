from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from concurrent.futures import ThreadPoolExecutor
import asyncio

from traffic import TrafficMiddleware, traffic_tracker

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

@app.get("/app")
async def initiate(request: Request):
    session = request.cookies.get("session")
    if not session:
        return RedirectResponse(url="/login")
    content = await render_template('app.html', {"request": request})
    return HTMLResponse(content=content)

@app.get("/login")
async def login(request: Request):
    content = await render_template('login.html', {"request": request})
    return HTMLResponse(content=content)

@app.post("/login")
async def login_post(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return JSONResponse({"error": "Username and password are required."}, status_code=400)
    else:
        return JSONResponse({"error": "Invalid credentials."}, status_code=401)

if __name__ == "__main__":
    import os
    import sys
    import uvicorn

    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    sys.path.insert(0, os.path.dirname(current_dir))

    from website.app import app

    uvicorn.run(app, host="127.0.0.1", port=8080, reload=False)