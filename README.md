# React 세팅하기

🛠️ React 프로젝트 실행 가이드 (Node.js 설치부터)
사전 준비
이 프로젝트는 React 기반이며, 실행을 위해 Node.js가 필요합니다.

1. Node.js 설치
Node.js 공식 웹사이트 에서 LTS(Long Term Support) 버전을 설치하세요.

권장 버전: Node.js 18.x 이상

설치하면 npm도 함께 설치됩니다.

설치 확인:
```bash
node -v
npm -v
```

2. 프로젝트 클론
GitHub에서 프로젝트를 내려받고 폴더로 이동합니다:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

⚠️ your-username과 your-repo-name은 실제 GitHub 주소에 맞게 바꾸세요.

3. 의존성 설치
React 프로젝트에 필요한 라이브러리들을 설치합니다:

```bash
npm install
```

또는 yarn 사용 시:

```bash
yarn
```

4. 개발 서버 실행 
react 폴더 진입 후 npm start

```bash
cd react_app
npm start
```

또는 
```bash
yarn start
```

실행 후 브라우저에서 자동으로 열리며,
직접 열려면 http://localhost:3000에 접속하세요.

5. 배포용 빌드 (선택)
```bash
npm run build
```

build/ 폴더에 정적 파일이 생성됩니다.

📁 예시 폴더 구조
```bash
your-repo-name/
├── public/
├── src/
├── package.json
├── .gitignore
└── README.md
```

폴더의 주요 구성 요소에 대한 설명

    - node_modules/ : 프로젝트에 사용되는 외부 라이브러리와 모듈이 저장되는 폴더입니다. 이러한 라이브러리와 모듈은 npm install 명령어를 통해 설치되며, package.json 파일에 명시됩니다.
    - public/ : 정적 파일들이 저장되는 폴더로, HTML, 이미지, 아이콘 등이 포함됩니다. 주요 파일로는 index.html이 있으며, 이는 리액트 앱의 기본 템플릿으로 사용됩니다.
    - src/ : 애플리케이션의 소스 코드가 저장되는 폴더입니다. 이 폴더에는 컴포넌트, 스타일, 이미지 등의 파일이 포함됩니다. 주요 파일들은 다음과 같습니다.
    - index.js : 리액트 앱의 진입점입니다. ReactDOM.render()를 사용하여 App 컴포넌트를 index.html에 렌더링합니다.
    - App.js : 애플리케이션의 메인 컴포넌트입니다. 이 컴포넌트에서 다른 컴포넌트들을 불러와 렌더링합니다.
    - App.css : App 컴포넌트의 스타일을 정의하는 CSS 파일입니다.
    - App.test.js : App 컴포넌트에 대한 테스트 코드가 저장되는 파일입니다.
    - serviceWorker.js : Progressive Web App(PWA) 기능을 구현하는데 사용되는 서비스 워커 파일입니다. 이 파일을 수정하여 오프라인 경험, 백그라운드 동기화 등의 기능을 구현할 수 있습니다.
    - package.json : 프로젝트의 메타데이터와 의존성을 담고 있는 파일입니다. 프로젝트에 사용되는 라이브러리, 모듈, 스크립트 등이 이 파일에 명시됩니다.
    - .gitignore : Git 버전 관리 시 무시할 파일과 디렉토리를 명시하는 파일입니다. 일반적으로 node_modules 폴더, 빌드 결과물, 로그 파일 등이 이 파일에 포함됩니다.