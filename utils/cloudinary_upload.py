"""
Cloudinary upload utility for blog and event images.
Falls back to local storage if Cloudinary is not configured.
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from config import get_settings

settings = get_settings()

# Configure Cloudinary if credentials are present
_cloudinary_configured = bool(
    settings.CLOUDINARY_CLOUD_NAME
    and settings.CLOUDINARY_API_KEY
    and settings.CLOUDINARY_API_SECRET
)

if _cloudinary_configured:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_image(file: UploadFile, folder: str = "5wof") -> str:
    """
    Upload an image to Cloudinary.
    Returns the secure URL of the uploaded image.
    Falls back to local upload if Cloudinary is not configured.
    """
    if not _cloudinary_configured:
        raise RuntimeError("Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in .env")

    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type="image",
        overwrite=True,
        transformation=[
            {"quality": "auto", "fetch_format": "auto"}
        ],
    )
    return result["secure_url"]


def is_cloudinary_configured() -> bool:
    """Check if Cloudinary credentials are available."""
    return _cloudinary_configured
