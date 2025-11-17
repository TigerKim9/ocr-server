# 로컬 OCR 서버

FastAPI와 Tesseract를 사용한 로컬 OCR 서버입니다. 이미지에서 텍스트를 추출할 수 있습니다.

## 기능

- ✅ 웹 GUI 인터페이스 (드래그 앤 드롭 지원)
- ✅ 이미지에서 텍스트 추출
- ✅ 한글/영어 동시 지원
- ✅ 신뢰도 점수 제공
- ✅ 상세 정보 추출 (단어별 위치, 신뢰도)
- ✅ RESTful API

## 설치 방법

### 1. Tesseract OCR 설치

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-kor
```

#### macOS
```bash
brew install tesseract tesseract-lang
```

#### Windows
[Tesseract 다운로드](https://github.com/UB-Mannheim/tesseract/wiki) 에서 설치 파일을 다운로드하여 설치

### 2. Python 의존성 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

## 실행 방법

```bash
python main.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 `http://localhost:8000` 에서 실행됩니다.

## 사용 방법

### 웹 GUI 사용 (추천)

1. 서버 실행 후 브라우저에서 접속:
   ```
   http://localhost:8000
   ```

2. 웹 페이지에서:
   - 이미지를 드래그 앤 드롭하거나 클릭하여 업로드
   - 언어 선택 (한글+영어, 한글만, 영어만 등)
   - "텍스트 추출" 버튼 클릭
   - 결과 확인 및 복사

3. 상세 모드:
   - "상세 모드" 체크박스 활성화
   - 단어별 위치, 신뢰도 정보 확인 가능

### API 사용법 (프로그래밍)

### 1. 서버 상태 확인

```bash
curl http://localhost:8000/health
```

### 2. 기본 OCR (텍스트 추출)

```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" \
  -F "lang=eng+kor"
```

**응답 예시:**
```json
{
  "success": true,
  "filename": "image.jpg",
  "text": "추출된 텍스트 내용",
  "language": "eng+kor",
  "confidence": 87.5,
  "word_count": 15,
  "char_count": 50
}
```

### 3. 상세 OCR (단어별 정보 포함)

```bash
curl -X POST "http://localhost:8000/ocr/detailed" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" \
  -F "lang=eng+kor"
```

**응답 예시:**
```json
{
  "success": true,
  "filename": "image.jpg",
  "full_text": "추출된 전체 텍스트",
  "language": "eng+kor",
  "words": [
    {
      "text": "단어",
      "confidence": 95,
      "bbox": {
        "x": 100,
        "y": 50,
        "width": 80,
        "height": 30
      }
    }
  ],
  "total_words": 15
}
```

## 언어 옵션

- `eng`: 영어만
- `kor`: 한글만
- `eng+kor`: 영어 + 한글 (기본값)
- 기타 언어는 Tesseract에서 지원하는 언어 코드 사용

## 엔드포인트

- `http://localhost:8000` - 웹 GUI
- `http://localhost:8000/api` - API 정보
- `http://localhost:8000/docs` - Swagger API 문서
- `http://localhost:8000/redoc` - ReDoc API 문서

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Python 코드 예제

```python
import requests

url = "http://localhost:8000/ocr"
files = {"file": open("image.jpg", "rb")}
data = {"lang": "eng+kor"}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"추출된 텍스트: {result['text']}")
print(f"신뢰도: {result['confidence']}%")
```

## JavaScript 코드 예제

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('lang', 'eng+kor');

fetch('http://localhost:8000/ocr', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log('추출된 텍스트:', data.text);
    console.log('신뢰도:', data.confidence);
  });
```

## Docker로 실행

Docker를 사용하면 Tesseract 설치 없이 바로 실행할 수 있습니다:

```bash
# Docker 이미지 빌드
docker-compose up --build

# 또는 직접 빌드
docker build -t ocr-server .
docker run -p 8000:8000 ocr-server
```

서버가 http://localhost:8000 에서 실행됩니다.

## 문제 해결

### Tesseract를 찾을 수 없다는 오류

Windows에서 Tesseract 경로를 수동으로 지정해야 할 수 있습니다:

```python
# main.py 상단에 추가
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 한글이 인식되지 않는 경우

한글 언어 팩이 설치되어 있는지 확인:

```bash
# 설치된 언어 확인
tesseract --list-langs

# 한글 언어 팩 설치 (Ubuntu/Debian)
sudo apt-get install tesseract-ocr-kor
```

## 라이선스

MIT License

## 기여

이슈나 PR은 언제나 환영합니다!
