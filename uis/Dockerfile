FROM node:22-alpine

WORKDIR /app/uis

COPY website/package.json website/package-lock.json ./website/
RUN npm ci --prefix ./website

COPY backoffice/dashboard/package.json backoffice/dashboard/package-lock.json ./backoffice/dashboard/
RUN npm ci --prefix ./backoffice/dashboard

COPY website ./website
COPY backoffice/dashboard ./backoffice/dashboard
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

EXPOSE 3000 3001

CMD ["./start.sh"]