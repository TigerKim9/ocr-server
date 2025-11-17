"""
OCR 서버 테스트 클라이언트

사용법:
    python test_client.py <image_file_path>
"""

import requests
import sys
import json

def test_ocr(image_path: str, lang: str = "eng+kor"):
    """OCR 서버 테스트"""

    url = "http://localhost:8000/ocr"

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"lang": lang}

            print(f"이미지 업로드 중: {image_path}")
            response = requests.post(url, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print("\n=== OCR 결과 ===")
                print(f"파일명: {result['filename']}")
                print(f"언어: {result['language']}")
                print(f"신뢰도: {result['confidence']}%")
                print(f"단어 수: {result['word_count']}")
                print(f"문자 수: {result['char_count']}")
                print(f"\n추출된 텍스트:\n{result['text']}")
            else:
                print(f"오류 발생: {response.status_code}")
                print(response.json())

    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {image_path}")
    except requests.exceptions.ConnectionError:
        print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

def test_health():
    """서버 상태 확인"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 서버가 정상 작동 중입니다.")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print("❌ 서버 상태가 정상이 아닙니다.")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("서버 상태 확인 중...")
        test_health()
        print("\n사용법: python test_client.py <image_file_path> [language]")
        print("예시: python test_client.py sample.jpg eng+kor")
    else:
        image_path = sys.argv[1]
        lang = sys.argv[2] if len(sys.argv) > 2 else "eng+kor"
        test_ocr(image_path, lang)
