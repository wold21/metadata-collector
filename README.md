## 버전
version 3.11.5(버전 준수)

## 설치 
환경변수 셋팅 후 터미널에서 python 입력 시 아래랑 비슷하게 떠야함.

```shell
Python 3.11.5 (tags/v3.11.5:cce6ba9, Aug 24 2023, 14:38:34) [MSC v.1936 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

## 실행방법
1. 터미널에서 `pip instapll -r ./requirements.txt`
2. 라이브러리 설치 완료되면
3. `python ./main.py` 실행

## commit / push
초기 셋팅 말고 작업 중에 pip install하여 다른 라이브러리를 설치했을 경우 작업 완료 후 `pip freeze > requirements.txt` 실행하여 라이브러리 목록 추출 후 해당 목록 반영하여 push 부탁.... (requirements 변경될 경우 기존 파일 `_x`로 버전 명시)

