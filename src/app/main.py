import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .api import monitor, token
from .utils.logs import RestLogger, log_http_request, log_http_response
from .utils.http import HTTPFactory


RestLogger.init_logger()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["token"]
)

# HTTP MIDDLEWARE : for adding request id and auth
@app.middleware("http")
async def add_request_id_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4()) if "X-Request-ID" not in request.headers else request.headers["X-Request-ID"]
    start_time = time.time()
    RestLogger.instance.request_id = request_id
    HTTPFactory.instance.request_id = request_id
    log_http_request(request.url, request.method, {item[0]: item[1] for item in request.headers.items()},
                     request.path_params)
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    log_http_response(formatted_process_time, response.status_code,
                      {item[0]: item[1] for item in response.headers.items()})
    return response


app.include_router(monitor.router, prefix="/monitor", tags=["monitoring"])
app.include_router(token.router, prefix="/auth", tags=["Oauth"])
