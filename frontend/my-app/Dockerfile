FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# FROM nginx:1.22.1-alpine
# WORKDIR /usr/share/nginx/html
# RUN rm -rf ./*
# COPY --from-builder /app/build .
# ENTRYPOINT ["nginx", "-g", "daemon off;"]