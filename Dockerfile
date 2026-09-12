FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY index.html vite.config.js ./
COPY src ./src
COPY server ./server
COPY data ./data
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production HOST=0.0.0.0 PORT=5173 AUTH_FILE=/app/.private/auth.json
COPY --from=build /app/dist ./dist
COPY server ./server
COPY scripts/manageUser.mjs ./scripts/manageUser.mjs
COPY package.json ./
COPY data ./data
RUN mkdir .private && chown node:node .private
USER node
EXPOSE 5173
CMD ["node", "server/start.mjs"]
