온라인 만세력 웹 애플리케이션
생년월일시를 입력받아 사주팔자(년주, 월주, 일주, 시주)를 계산해주는 파이썬 Flask 기반의 웹 애플리케이션입니다.

프로젝트 구조
manse-ryeok-app/
├── main.py             # Flask 애플리케이션의 핵심 로직 파일
├── requirements.txt    # 프로젝트에 필요한 라이브러리 목록
├── templates/
│   └── index.html      # 사용자에게 보여질 웹 페이지
└── README.md           # 프로젝트 설명 및 실행/배포 안내

로컬 환경에서 실행하기
프로젝트 클론 또는 다운로드
코드를 로컬 컴퓨터에 다운로드합니다.

가상 환경 생성 및 활성화
프로젝트 폴더 내에서 터미널을 열고 다음 명령어를 실행합니다.

# 가상 환경 생성 (Windows)
python -m venv venv
# 가상 환경 활성화 (Windows)
.\venv\Scripts\activate

# 가상 환경 생성 (macOS/Linux)
python3 -m venv venv
# 가상 환경 활성화 (macOS/Linux)
source venv/bin/activate

필요 라이브러리 설치
requirements.txt 파일에 명시된 라이브러리들을 설치합니다.

pip install -r requirements.txt

Flask 애플리케이션 실행
main.py 파일을 실행합니다.

flask run
# 또는 python main.py

웹 브라우저에서 확인
웹 브라우저를 열고 주소창에 http://127.0.0.1:5000 또는 http://localhost:5000을 입력하여 접속합니다.

Render에 배포하기
Render는 간단한 설정으로 웹 애플리케이션을 배포할 수 있는 클라우드 플랫폼입니다.

GitHub 저장소 생성 및 코드 푸시

GitHub에 새로운 저장소(repository)를 생성합니다.

로컬에 있는 프로젝트 코드를 생성된 GitHub 저장소에 푸시합니다.

Render 회원가입 및 로그인

Render 웹사이트에 접속하여 GitHub 계정으로 회원가입 또는 로그인을 합니다.

새로운 Web Service 생성

Render 대시보드에서 [New +] 버튼을 누르고 **[Web Service]**를 선택합니다.

"Build and deploy from a Git repository" 옵션을 선택하고, 1번에서 생성한 GitHub 저장소를 연결합니다.

배포 설정

Name: 원하는 서비스 이름을 입력합니다 (예: my-manse-ryeok).

Region: 원하는 서버 지역을 선택합니다 (예: Singapore).

Branch: 배포할 브랜치를 선택합니다 (보통 main 또는 master).

Root Directory: 비워둡니다 (프로젝트 루트에 main.py가 있으므로).

Runtime: Python 3를 선택합니다.

Build Command: pip install -r requirements.txt (자동으로 채워집니다).

Start Command: gunicorn main:app (Render는 보통 gunicorn을 사용합니다. 이를 위해 requirements.txt에 gunicorn을 추가해야 합니다.)

중요: requirements.txt 파일에 gunicorn을 추가하고 GitHub에 다시 푸시해주세요.

Flask
korean-lunar-calendar
gunicorn

배포 시작

[Create Web Service] 버튼을 클릭하여 배포를 시작합니다.

배포 로그를 통해 빌드 및 시작 과정을 확인할 수 있습니다.

배포가 완료되면 Render에서 제공하는 고유한 .onrender.com 주소로 웹 애플리케이션에 접속할 수 있습니다.