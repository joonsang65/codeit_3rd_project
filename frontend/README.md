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
```bash
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


# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
