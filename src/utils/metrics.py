from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
import time 

REQUEST_COUNT= Counter('http_requests_total', 'Total number of HTTP requests',['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'HTTP request latency in seconds', ['method', 'endpoint'])


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start_time

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
    
    
def setup_metrics(app: FastAPI):
    app.add_middleware(PrometheusMiddleware)

    @app.get("/metGHFHydve", include_in_schema=False)

    async def metrics():
        return Response( 
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )