import { defineConfig } from 'vite';
import { api } from './server/api.mjs';
export default defineConfig({
 publicDir:false,
 server:{fs:{deny:['**/.git/**','**/.private/**','**/.env*','**/data/**','**/server/**','**/scripts/**','**/tests/**']}},
 plugins:[{name:'private-window-api',configureServer(server){server.middlewares.use(api);},configurePreviewServer(server){server.middlewares.use(api);}}]
});
