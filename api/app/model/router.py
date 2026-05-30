import os
from typing import List

from app import db
from app import settings as config
from app import utils
from app.auth.jwt import get_current_user
from app.model.schema import PredictRequest, PredictResponse
from app.model.services import model_predict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/predict")
async def predict(file: UploadFile, current_user=Depends(get_current_user)):
    rpse = {"success": False, "prediction": None, "score": None}
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se ha proporcionado ningun archvo",
        )
    if utils.allowed_file(file.filename) == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type is not supported.",
        )
    hashed_file_name = await utils.get_file_hash(file)
    ruta = os.path.join(config.UPLOAD_FOLDER, hashed_file_name)
    with open(ruta, "wb") as encyclopedia:
        while chunk := await file.read(8192):
            encyclopedia.write(chunk)
    try:
        prediction, score = await model_predict(hashed_file_name)
    except Exception as e:
        print(f"Error al llamar a model_predict: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EL servicio de prediccion falló",
        )

    rpse["success"] = True
    rpse["prediction"] = prediction
    rpse["score"] = score
    rpse["image_file_name"] = hashed_file_name

    return PredictResponse(**rpse)
