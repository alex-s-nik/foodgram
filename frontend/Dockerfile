FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build


FROM nginx:1.25.1
COPY --from=build /app/build /usr/share/nginx/html/