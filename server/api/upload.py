import os
from fastapi import UploadFile, File, Form, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from database.models import ImageData
from .router import api_router

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api_router.post("/upload")
async def upload_file(image: UploadFile = File(...), type: str = Form(...), db: Session = Depends(get_db)):
    if type not in ["train", "validate", "test"]:
        raise HTTPException(status_code=400, detail="Invalid type")

    # Create directory if not exists
    directory = f"uploads/{type}"
    os.makedirs(directory, exist_ok=True)

    # Calculate new file name
    files = db.query(ImageData).filter(ImageData.type == type).all()
    new_file_name = f"{len(files) + 1}.jpg"
    file_path = os.path.join(directory, new_file_name)

    # Save file to directory
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    # Save file information to database
    db_image = ImageData(type=type, filename=new_file_name)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return {"message": "Image uploaded successfully", "file_name": new_file_name}

@api_router.delete("/delete/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(ImageData).filter(ImageData.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Construct file path
    file_path = os.path.join(f"uploads/{db_image.type}", db_image.filename)

    # Remove the image file from the filesystem
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Delete the image record from the database
    db.delete(db_image)
    db.commit()

    return {"message": "Image deleted successfully"}

@api_router.get("/image/{image_id}")
async def get_image_url(image_id: int, request: Request, db: Session = Depends(get_db)):
    db_image = db.query(ImageData).filter(ImageData.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    file_url = request.url_for('static', path=f"uploads/{db_image.type}/{db_image.filename}")
    return {"image_url": file_url}