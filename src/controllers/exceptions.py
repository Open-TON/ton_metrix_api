import logging

from fastapi import FastAPI
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


def register_handle_errors(app: FastAPI):
    @app.exception_handler(ValidationError)
    async def handle_no_data(request: Request, exc):
        logging.error('Wrong request from client %s.', request.client.host)
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={'message': 'Data is not valid.'}
        )
