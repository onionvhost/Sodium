from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="website/static"), name="static")

templates = Jinja2Templates(directory="website/templates")
executor = ThreadPoolExecutor()

async def render_template(template_name: str, context: dict):
  return await asyncio.get_event_loop().run_in_executor(
    executor, lambda: templates.get_template(template_name).render(context)
  )

@app.get("/")
async def read_root(request: Request):
    content = await render_template('index.html', {"request": request})
    return HTMLResponse(content=content)