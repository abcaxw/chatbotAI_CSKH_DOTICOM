import os
import traceback
from typing import Optional
from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from starlette.templating import Jinja2Templates

from common_utils.dependencies.authen import get_current_user

import dlog
from common_utils.file_utils import save_fastapi_request_file
from database import minio_service
from dconfig import config_object
from object_models.db_obj import Document, ChunkRawData, DocumentPaginationData
from services.document_service import insert_document, insert_chunks, get_documents_by_pagination, get_document_by_id, \
    update_document_by_id, delete_document_by_id, update_content_by_document_id
from services.category_service import get_all_categories

router = APIRouter(
    prefix="/document",
    tags=["/document"],
    dependencies=[Depends(get_current_user)]
)
templates = config_object.TEMPLATES


@router.get("/web")
async def get(request: Request, page: int = 1, q: str = ""):
    return templates.TemplateResponse("document/list.html", {
        "request": request,
        "ws_url": "/document_manager/",
        "page": page,
        "query": q,
        "total_pages": 10,
        "now": datetime.now()
    })


@router.get("/edit/{id}")
async def edit(request: Request, id: str):
    document = get_document_by_id(int(id))
    categories = get_all_categories()
    documents, _ = get_documents_by_pagination(DocumentPaginationData(page_number=1, page_size=100))
    
    return templates.TemplateResponse("document/edit.html", {
        "request": request,
        "ws_url": "/edit/",
        "id": id,
        "document": document,
        "categories": categories,
        "documents": documents,
        "now": datetime.now()
    })


@router.get("/add")
async def add(request: Request):
    categories = get_all_categories()
    documents, _ = get_documents_by_pagination(DocumentPaginationData(page_number=1, page_size=100))
    
    return templates.TemplateResponse("document/add.html", {
        "request": request, 
        "ws_url": "/add/",
        "categories": categories,
        "documents": documents,
        "now": datetime.now()
    })


@router.post("/add-document")
async def add_document(file: UploadFile = File(None),
                       title: str = Form(...),
                       category_id: int = Form(...),
                       doc_type: str = Form(...),
                       content: Optional[str] = Form(None),
                       user_id: str = Form(...)):
    try:
        path_file = None
        if file is not None:
            if file.size != 0:
                path_file = save_fastapi_request_file(file)

        document = Document(filename="temp", title=title, category_id=category_id, doc_type=doc_type, user_id=user_id,
                            url="temp", content=content)
        document_id, content = insert_document(path_file, document)
        data = {
            "document_id": document_id,
            "content": content
        }
        return JSONResponse({"message": "insert document successfully", "data": data}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.post("/add-chunks")
async def add_chunks(chunk_raw: ChunkRawData):
    try:
        update_content_by_document_id(chunk_raw.document_id, chunk_raw.content)
        insert_chunks(chunk_raw.document_id, chunk_raw.content)
        return JSONResponse({"message": "insert chunk successfully", "data": chunk_raw.document_id}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.delete("/delete/{document_id}")
async def delete_document(document_id: str):
    try:
        document_id = int(document_id)
        document = get_document_by_id(document_id)
        deleted_count = delete_document_by_id(document_id)
        minio_service.delete_file(f"uploads/{document.get('filename')}")
        data = {"deleted_count": deleted_count}
        return JSONResponse({"message": "Delete successfully", "data": data}, status_code=200)
    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.put("/update-document/{document_id}")
async def update_document(document_id: str, document: Document):
    try:
        update_document_by_id(document_id, document)
        dlog.dlog_i(f"update document by id {document_id} successfully")
        return JSONResponse({"message": "update faq successfully"}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.post("/get-documents")
async def get_documents(document_pagination_data: DocumentPaginationData):
    try:
        documents, total_pages = get_documents_by_pagination(document_pagination_data)
        data = {
            "documents": documents,
            "total_pages": total_pages
        }
        json_message = "get documents successfully"
        dlog.dlog_i(json_message)
        return JSONResponse({"message": json_message, "data": data}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.get("/{document_id}")
async def get_document_by_document_id(document_id: str):
    try:
        document = get_document_by_id(int(document_id))
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        json_message = f"get document by id {document_id} successfully"
        dlog.dlog_i(json_message)
        return JSONResponse({"message": json_message, "data": document}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)
