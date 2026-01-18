import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from werkzeug.utils import secure_filename
import uvicorn

from config import settings
from models.schemas import (
    TextBriefRequest,
    CaptionResponse,
    ErrorResponse,
    HealthResponse
)
from services.image_processor import ImageProcessor
from services.ai_service import AIService

# Initialize services
image_processor = ImageProcessor()
ai_service = AIService(api_key=settings.GOOGLE_API_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("=" * 50)
    print("AI Social Media Caption Creator API Starting...")
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    print(f"Max file size: {settings.MAX_FILE_SIZE / (1024*1024)}MB")
    print(f"Server running on http://{settings.HOST}:{settings.PORT}")
    print("=" * 50)
    
    # Validate API key
    if ai_service.validate_api_key():
        print("✓ Google Gemini API key is valid")
    else:
        print("✗ Warning: Google Gemini API key validation failed")
    
    yield
    
    # Shutdown
    print("Shutting down AI Caption Creator API...")
    print("Cleanup completed")


# Initialize FastAPI app
app = FastAPI(
    title="AI Social Media Caption Creator API",
    description="Backend API for AI-powered social media caption generation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def allowed_file(filename: str, file_type: str = "image") -> bool:
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == "image":
        return ext in settings.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == "text":
        return ext in settings.ALLOWED_TEXT_EXTENSIONS
    
    return False


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "message": "AI Social Media Caption Creator API is running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Server is running"
    }


@app.post("/generate/image", response_model=CaptionResponse, status_code=status.HTTP_200_OK)
async def generate_from_image(file: UploadFile = File(...)):
    """
    Generate captions from product image.
    
    Args:
        file: Image file upload
        
    Returns:
        Generated captions, hashtags, and posting time
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        if not allowed_file(file.filename, "image"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only image files are allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # Validate image
        if not image_processor.validate_image(filepath):
            os.remove(filepath)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file"
            )
        
        # Generate captions
        try:
            result = ai_service.generate_captions_from_image(filepath)
        finally:
            # Clean up file
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return CaptionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@app.post("/generate/text", response_model=CaptionResponse, status_code=status.HTTP_200_OK)
async def generate_from_text(request: TextBriefRequest):
    """
    Generate captions from text brief.
    
    Args:
        request: Text brief request
        
    Returns:
        Generated captions, hashtags, and posting time
    """
    try:
        # Generate captions
        result = ai_service.generate_captions_from_text(request.text_brief)
        
        return CaptionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@app.post("/generate/file", response_model=CaptionResponse, status_code=status.HTTP_200_OK)
async def generate_from_file(file: UploadFile = File(...)):
    """
    Generate captions from text file.
    
    Args:
        file: Text file upload
        
    Returns:
        Generated captions, hashtags, and posting time
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        if not allowed_file(file.filename, "text"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only text files (.txt) are allowed"
            )
        
        # Read file content
        file_content = await file.read()
        text_brief = file_content.decode('utf-8')
        
        if not text_brief or len(text_brief.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text file is empty or too short"
            )
        
        # Generate captions
        result = ai_service.generate_captions_from_text(text_brief)
        
        return CaptionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )