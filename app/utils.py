import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

def init_logging(logger_name: str = "") -> logging.Logger:
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file_path = os.path.join(os.path.dirname(__file__), "storage", "logs", f"{logger_name}.log")

    # Create file handler with rotation (e.g., 1MB per file, keep last 5 logs)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=1_000_000, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def dd(*args: object) -> None:
    # die and dump
    import sys

    dump(args)
    sys.exit(1)


def dump(*args: object) -> None:
    import pprint

    for value in args:
        if isinstance(value, tuple) and len(value) == 1:
            value = value[0]
        if isinstance(value, str):
            print(value)
        else:
            pprint.pprint(value)


from fastapi.responses import JSONResponse
from fastapi import Request
import pprint

def dd_http(data: object, status_code: int = 200):
    """Return debug data as HTTP response (for use inside route functions)"""
    pretty = pprint.pformat(data, indent=2, width=100)
    raise DebugResponse(content={"dd": pretty}, status_code=status_code)

class DebugResponse(Exception):
    def __init__(self, content: dict, status_code: int = 200):
        self.content = content
        self.status_code = status_code

def register_debug_exception_handler(app):
    """Register handler to catch DebugResponse and convert to HTTP JSONResponse"""
    from fastapi import Request

    @app.exception_handler(DebugResponse)
    async def debug_exception_handler(request: Request, exc: DebugResponse):
        return JSONResponse(
            content=exc.content,
            status_code=exc.status_code
        )