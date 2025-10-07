import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
from typing import List

class UploadService:
    @staticmethod
    async def upload_product_image(file: UploadFile) -> str:
        """Upload a product image and return the URL"""
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (10MB default)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = settings.max_upload_mb * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.max_upload_mb}MB"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        upload_dir = Path(settings.upload_dir) / "products"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / unique_filename
        
        # Save file
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Return API endpoint URL with proper MIME type handling
        return f"/api/images/{unique_filename}"
    
    @staticmethod
    async def upload_multiple_images(files: List[UploadFile]) -> List[str]:
        """Upload multiple images and return URLs"""
        urls = []
        for file in files:
            url = await UploadService.upload_product_image(file)
            urls.append(url)
        return urls
    
    @staticmethod
    def delete_image(image_url: str) -> bool:
        """Delete an image file"""
        try:
            # Extract filename from URL
            filename = image_url.split('/')[-1]
            file_path = Path(settings.upload_dir) / "products" / filename
            
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
