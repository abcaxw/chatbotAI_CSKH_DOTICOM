from fastapi import APIRouter
from starlette.responses import JSONResponse

import dlog
from common_utils.system_info import get_system_info
from object_models.exceptions import HealthCheckException
from dconfig import config_object

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get('')
async def health():
    try:
        system_info = get_system_info()
        return JSONResponse({
            "status": "OK",
            "data": {
                "system_info": system_info,
                "version": config_object.VERSION
            }
        }, status_code=200)
    except HealthCheckException as exc:
        dlog.dlog_e(exc)
        return JSONResponse({
            "status": "error",
            "message": f"Error at {exc.module} module"
        }, status_code=400)
    except Exception as exc:
        dlog.dlog_e(exc)
        return JSONResponse({
            "status": "error",
            "message": "Cannot get health data"
        }, status_code=400)
