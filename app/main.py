import os
import time
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

import dconfig
import dlog
from database import milvus_service, mysql_service, minio_service
from routes import health_route, faq_route, document_route, chat_route, meta_route, login_route, register_route, \
    logout_route, category_route, cake_route
from services import oauth2_scheme

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "web/static")), name="static")

# Cấu hình templates
templates = Jinja2Templates(directory="app/web/templates")
# templates.env.filters["datetime"] = datetime_filter

# ensure the instance folder exists
try:
    log_dir = dconfig.config_object.LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    temp_dir = os.path.join(dconfig.config_object.DATA_DIR, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
except OSError:
    pass


@app.on_event("shutdown")
def shutdown_event():
    milvus_service.disconnect()
    mysql_service.disconnect()
    minio_service.disconnect()


@app.get("/")
async def get():
    return {"message": f"AI Chatbot"}


@app.get("/dashboard")
def dashboard(request: Request, token: str = Depends(oauth2_scheme)):
    return {"message": "Welcome to Dashboard!"}


def datetime_filter(date):
    if date:
        return date.strftime('%d/%m/%Y %H:%M:%S')
    return 'N/A'


app.include_router(health_route.router)
app.include_router(faq_route.router)
app.include_router(document_route.router)
app.include_router(chat_route.router)
app.include_router(meta_route.router)
app.include_router(login_route.router)
app.include_router(register_route.router)
app.include_router(logout_route.router)
app.include_router(category_route.router)
app.include_router(cake_route.router)

if __name__ == '__main__':
    dlog.dlog_i(f"Server started at {dconfig.config_object.SERVER_NAME}:{dconfig.config_object.PORT_NUMBER}")
    uvicorn.run(
        app,
        host=dconfig.config_object.SERVER_NAME,
        port=int(dconfig.config_object.PORT_NUMBER),
        proxy_headers=True
    )
    # import cv2
    # import numpy as np
    # import io
    # from IPython.display import Image, display
    # from PIL import Image as PImage
    #
    # from coreAI.agents_workflow import TeamAgents
    #
    # team_agent = TeamAgents()
    # image_data = team_agent.chain.get_graph(xray=True).draw_mermaid_png()
    #
    # image = PImage.open(io.BytesIO(image_data))
    # image_array = np.array(image)
    # print(1)
