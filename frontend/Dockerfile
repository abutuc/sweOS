FROM node:20-alpine

WORKDIR /app

COPY package.json ./
COPY tsconfig.json next.config.ts next-env.d.ts ./
COPY app ./app
COPY components ./components
COPY lib ./lib

RUN npm install
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
