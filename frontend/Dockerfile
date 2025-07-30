# frontend/Dockerfile
FROM node:20-alpine 

WORKDIR /app 

COPY package.json ./
COPY package-lock.json ./

RUN npm cache clean --force

RUN npm install

EXPOSE 3000

CMD ["npm", "start"]