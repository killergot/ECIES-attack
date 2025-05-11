from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from fastapi.responses import Response

from src.logic_server import ECIES_encrypt, ECIES_decrypt,Q
import uvicorn


app = FastAPI()


@app.post("/encrypt")
async def encrypt_file(file: UploadFile = File(...)):
    try:
        # Читаем содержимое файла
        file_content = await file.read()

        # Шифруем данные
        encrypted_data = ECIES_encrypt(file_content)

        # Возвращаем зашифрованные данные как файл
        return Response(
            content=encrypted_data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=encrypted_{file.filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decrypt")
async def decrypt_file(file: UploadFile = File(...)):
    try:
        # Читаем содержимое зашифрованного файла
        encrypted_data = await file.read()

        # Дешифруем данные
        decrypted_data = ECIES_decrypt(encrypted_data)

        if decrypted_data is None:
            raise HTTPException(status_code=400, detail="Decryption failed - invalid MAC or corrupted data")

        # Возвращаем расшифрованные данные как файл
        return Response(
            content=decrypted_data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=decrypted_{file.filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    print(Q)
    uvicorn.run(app, port=8001)