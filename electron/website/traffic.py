from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from collections import deque
import time

class TrafficTracker:
    def __init__(self):
        self.current_timestamp = int(time.time())
        self.incoming = 0
        self.outgoing = 0

    def log(self, incoming: int, outgoing: int):
        now = int(time.time())
        if now != self.current_timestamp:
            self.current_timestamp = now
            self.incoming = 0
            self.outgoing = 0
        self.incoming += incoming
        self.outgoing += outgoing

    def get_current(self):
        return (self.current_timestamp, self.incoming, self.outgoing)

traffic_tracker = TrafficTracker()

class TrafficMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_len = int(request.headers.get("content-length", 0))
        response: Response = await call_next(request)
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        resp_len = len(resp_body)
        traffic_tracker.log(req_len, resp_len)
        return Response(content=resp_body, status_code=response.status_code, headers=dict(response.headers))