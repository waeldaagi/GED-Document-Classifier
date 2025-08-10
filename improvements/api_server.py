from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import asyncio
import aiofiles
import os
import tempfile
import time
from datetime import datetime
import json
import logging

# Import our classification modules
import sys
sys.path.append('..')
from advanced_classifier import AdvancedDocumentClassifier
from enhanced_ocr import EnhancedOCR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GED Document Classification API",
    description="Advanced document classification and OCR API",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
classifier = AdvancedDocumentClassifier()
ocr = EnhancedOCR()

# Load models
try:
    classifier.load_model()
    logger.info("✅ Models loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Could not load models: {e}")

# Pydantic models
class ClassificationRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = None

class ClassificationResponse(BaseModel):
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    processing_time: float
    timestamp: str

class DocumentResponse(BaseModel):
    filename: str
    classification: ClassificationResponse
    ocr_text: str
    structured_data: Dict
    file_size: int

class BatchResponse(BaseModel):
    total_files: int
    successful: int
    failed: int
    results: List[DocumentResponse]
    processing_time: float

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GED Document Classification API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "/classify/text": "Classify text input",
            "/classify/file": "Classify uploaded file",
            "/classify/batch": "Classify multiple files",
            "/health": "Health check",
            "/stats": "API statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if models are loaded
        model_status = "loaded" if classifier.calibrated_model else "not_loaded"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "models": model_status,
            "version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/classify/text", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    """Classify text input"""
    start_time = time.time()
    
    try:
        # Perform classification
        result = classifier.predict_with_confidence(request.text)
        
        processing_time = time.time() - start_time
        
        return ClassificationResponse(
            prediction=result['prediction'],
            confidence=result['confidence'],
            probabilities=result['probabilities'],
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/classify/file", response_model=DocumentResponse)
async def classify_file(file: UploadFile = File(...)):
    """Classify uploaded file"""
    start_time = time.time()
    
    # Validate file type
    allowed_types = ['.pdf', '.docx', '.jpg', '.jpeg', '.png']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {allowed_types}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text using OCR
        if file_ext in ['.jpg', '.jpeg', '.png']:
            ocr_result = ocr.ocr_with_enhancements(temp_file_path)
            text = ocr_result['all_text']
            structured_data = ocr_result['structured_data']
        elif file_ext == '.pdf':
            # Handle PDF processing
            ocr_result = ocr.ocr_with_enhancements(temp_file_path)
            text = ocr_result['all_text']
            structured_data = ocr_result['structured_data']
        elif file_ext == '.docx':
            # Handle DOCX processing
            from docx import Document
            doc = Document(temp_file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            structured_data = ocr.extract_structured_data(text)
        
        # Classify the text
        classification_result = classifier.predict_with_confidence(text)
        
        processing_time = time.time() - start_time
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return DocumentResponse(
            filename=file.filename,
            classification=ClassificationResponse(
                prediction=classification_result['prediction'],
                confidence=classification_result['confidence'],
                probabilities=classification_result['probabilities'],
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            ),
            ocr_text=text[:1000] + "..." if len(text) > 1000 else text,  # Truncate for response
            structured_data=structured_data,
            file_size=len(content)
        )
    
    except Exception as e:
        logger.error(f"File classification error: {e}")
        raise HTTPException(status_code=500, detail=f"File classification failed: {str(e)}")

@app.post("/classify/batch", response_model=BatchResponse)
async def classify_batch(files: List[UploadFile] = File(...)):
    """Classify multiple files in batch"""
    start_time = time.time()
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            # Process each file
            result = await classify_file(file)
            results.append(result)
            successful += 1
        except Exception as e:
            logger.error(f"Batch processing error for {file.filename}: {e}")
            failed += 1
    
    processing_time = time.time() - start_time
    
    return BatchResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results,
        processing_time=processing_time
    )

@app.get("/stats")
async def get_stats():
    """Get API usage statistics"""
    # This would typically connect to a database
    # For now, return basic stats
    return {
        "total_requests": 0,  # Would be tracked in database
        "successful_classifications": 0,
        "average_processing_time": 0.0,
        "model_accuracy": 0.85,  # Example
        "uptime": "24h",  # Would be calculated
        "last_updated": datetime.now().isoformat()
    }

# Background tasks
async def process_document_background(file_path: str, callback_url: str = None):
    """Background task for document processing"""
    try:
        # Process document
        result = await classify_file(file_path)
        
        # Send callback if URL provided
        if callback_url:
            # Implementation for callback
            pass
        
        logger.info(f"Background processing completed for {file_path}")
    
    except Exception as e:
        logger.error(f"Background processing failed: {e}")

@app.post("/classify/async")
async def classify_async(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    callback_url: str = None
):
    """Asynchronous document classification"""
    # Save file and process in background
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    if background_tasks:
        background_tasks.add_task(
            process_document_background, 
            temp_file_path, 
            callback_url
        )
    
    return {
        "message": "Document queued for processing",
        "filename": file.filename,
        "job_id": f"job_{int(time.time())}",
        "callback_url": callback_url
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 GED Document Classification API starting up...")
    # Initialize any startup tasks here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 GED Document Classification API shutting down...")
    # Cleanup tasks here

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
