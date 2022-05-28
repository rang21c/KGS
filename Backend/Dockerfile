FROM node:17
WORKDIR /app
COPY package*.json ./
RUN npm install --silent
COPY . .
CMD [ "npm", "start" ]
EXPOSE 4000