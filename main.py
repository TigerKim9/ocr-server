from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
import io
import logging
from typing import Optional
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Local OCR Server",
    description="로컬에서 실행되는 OCR 서버 - Tesseract 기반",
    version="1.0.0"
)

# CORS 설정 (필요시 origins를 특정 도메인으로 제한)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """웹 GUI 제공"""
    index_file = Path(__file__).parent / "static" / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    else:
        return {
            "message": "OCR Server is running",
            "version": "1.0.0",
            "endpoints": {
                "/ocr": "POST - 이미지 OCR 처리",
                "/health": "GET - 서버 상태 확인",
                "/docs": "GET - API 문서"
            }
        }

@app.get("/api")
async def api_info():
    """API 정보 확인"""
    return {
        "message": "OCR Server API",
        "version": "1.0.0",
        "endpoints": {
            "/ocr": "POST - 이미지 OCR 처리",
            "/ocr/detailed": "POST - 상세 OCR 처리",
            "/health": "GET - 서버 상태 확인",
            "/docs": "GET - API 문서"
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # Tesseract 설치 확인
        version = pytesseract.get_tesseract_version()
        return {
            "status": "healthy",
            "tesseract_version": str(version)
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/ocr")
async def perform_ocr(
    file: UploadFile = File(...),
    lang: Optional[str] = "eng+kor"
):
    """
    이미지에서 텍스트 추출

    Args:
        file: 업로드된 이미지 파일 (jpg, png, etc.)
        lang: OCR 언어 설정 (기본값: eng+kor)
              - 영어만: eng
              - 한글만: kor
              - 영어+한글: eng+kor

    Returns:
        JSON 형식의 추출된 텍스트
    """
    try:
        # 파일 형식 확인
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="이미지 파일만 업로드 가능합니다."
            )

        # 이미지 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        logger.info(f"Processing image: {file.filename}, size: {image.size}, mode: {image.mode}")

        # OCR 수행
        text = pytesseract.image_to_string(image, lang=lang)

        # 추가 정보 추출 (선택사항)
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)

        # 신뢰도 점수 계산
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "success": True,
            "filename": file.filename,
            "text": text,
            "language": lang,
            "confidence": round(avg_confidence, 2),
            "word_count": len(text.split()),
            "char_count": len(text)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR 처리 중 오류 발생: {str(e)}"
        )

@app.post("/ocr/detailed")
async def perform_ocr_detailed(
    file: UploadFile = File(...),
    lang: Optional[str] = "eng+kor"
):
    """
    이미지에서 텍스트 추출 (상세 정보 포함)

    각 단어의 위치, 신뢰도 등 상세 정보 제공
    """
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="이미지 파일만 업로드 가능합니다."
            )

        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # 상세 데이터 추출
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)

        # 단어별 정보 구성
        words = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # 신뢰도가 0보다 큰 것만
                words.append({
                    "text": data['text'][i],
                    "confidence": int(data['conf'][i]),
                    "bbox": {
                        "x": data['left'][i],
                        "y": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i]
                    }
                })

        # 전체 텍스트
        full_text = pytesseract.image_to_string(image, lang=lang)

        return {
            "success": True,
            "filename": file.filename,
            "full_text": full_text,
            "language": lang,
            "words": words,
            "total_words": len(words)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detailed OCR processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR 처리 중 오류 발생: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
