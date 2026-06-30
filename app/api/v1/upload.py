from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, UploadFile

from app.containers import Container
from app.models.response import UploadResponse
from app.services.indexing import IndexingService

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
@inject
async def upload_documents(
    file: UploadFile = File(..., description="PDF or text file to index"),
    indexing_service: IndexingService = Depends(Provide[Container.indexing_service]),
) -> UploadResponse:
    result = await indexing_service.index_document(file)
    return UploadResponse(**result)
