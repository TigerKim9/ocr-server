// DOM 요소
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const processBtn = document.getElementById('processBtn');
const langSelect = document.getElementById('langSelect');
const detailedMode = document.getElementById('detailedMode');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const resultSection = document.getElementById('resultSection');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const copyBtn = document.getElementById('copyBtn');

let selectedFile = null;

// 업로드 영역 클릭
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// 파일 선택
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

// 드래그 앤 드롭
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragging');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragging');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragging');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    } else {
        showError('이미지 파일만 업로드 가능합니다.');
    }
});

// 파일 처리
function handleFile(file) {
    selectedFile = file;

    // 미리보기 표시
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // 버튼 활성화
    processBtn.disabled = false;

    // 이전 결과 숨기기
    resultSection.style.display = 'none';
    error.style.display = 'none';
}

// OCR 처리
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // UI 업데이트
    loading.style.display = 'block';
    resultSection.style.display = 'none';
    error.style.display = 'none';
    processBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('lang', langSelect.value);

        const endpoint = detailedMode.checked ? '/ocr/detailed' : '/ocr';

        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '서버 오류가 발생했습니다.');
        }

        const result = await response.json();
        displayResult(result);

    } catch (err) {
        showError(err.message);
    } finally {
        loading.style.display = 'none';
        processBtn.disabled = false;
    }
});

// 결과 표시
function displayResult(result) {
    resultSection.style.display = 'block';

    if (detailedMode.checked) {
        // 상세 모드
        document.getElementById('resultFilename').textContent = result.filename;
        document.getElementById('resultLanguage').textContent = result.language;
        document.getElementById('resultConfidence').textContent = '-';
        document.getElementById('resultWordCount').textContent = result.total_words;
        document.getElementById('resultText').value = result.full_text;

        // 단어별 상세 정보
        const detailedResult = document.getElementById('detailedResult');
        const detailedWords = document.getElementById('detailedWords');
        detailedResult.style.display = 'block';
        detailedWords.innerHTML = '';

        result.words.forEach(word => {
            const wordItem = document.createElement('div');
            wordItem.className = 'word-item';
            wordItem.innerHTML = `
                <div class="word-text">${escapeHtml(word.text)}</div>
                <div class="word-info">
                    신뢰도: ${word.confidence}% |
                    위치: (${word.bbox.x}, ${word.bbox.y}) |
                    크기: ${word.bbox.width}x${word.bbox.height}
                </div>
            `;
            detailedWords.appendChild(wordItem);
        });

    } else {
        // 기본 모드
        document.getElementById('resultFilename').textContent = result.filename;
        document.getElementById('resultLanguage').textContent = result.language;
        document.getElementById('resultConfidence').textContent = result.confidence + '%';
        document.getElementById('resultWordCount').textContent = result.word_count;
        document.getElementById('resultText').value = result.text;

        document.getElementById('detailedResult').style.display = 'none';
    }

    // 결과로 스크롤
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 복사 버튼
copyBtn.addEventListener('click', () => {
    const resultText = document.getElementById('resultText');
    resultText.select();
    document.execCommand('copy');

    // 피드백
    const originalText = copyBtn.textContent;
    copyBtn.textContent = '✓ 복사됨!';
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
});

// 에러 표시
function showError(message) {
    error.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    error.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 페이지 로드 시 서버 상태 확인
async function checkServerHealth() {
    try {
        const response = await fetch('/health');
        if (!response.ok) {
            showError('서버 상태가 정상이 아닙니다. Tesseract가 설치되어 있는지 확인하세요.');
        }
    } catch (err) {
        showError('서버에 연결할 수 없습니다.');
    }
}

checkServerHealth();
