# LLM Service
Langchain을 사용해 ChatAI Prototype 개발


# Skills
- Django
- Python
- Langchain


# 프로젝트 설정
1. Clone Repository
```
git clone https://github.com
```
2. Install Package
```
pip install -r requirements.txt
```
3. Run server
```
python3 manage.py server
```


# 메소드 및 import 경로 수정 시 오류
- 메소드 및 Import 경로 수정을 한 뒤 오류가 나면 가상환경 재설치 필요
1. 가상 환경 비활성화
```
deactivate
```

2. 가상 환경 삭제 (필요 시)
```
rm -rf .venv
```

3. 새로운 가상 환경 생성
```
python -m venv .venv
```

4. 가상 환경 활성화
```
source .venv/bin/activate
```

5. 패키지 재설치
```
pip install -r requirements.txt
```

