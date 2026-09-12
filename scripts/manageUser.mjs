import { randomBytes } from 'node:crypto';
import { readState, saveState, passwordHash } from '../server/auth.mjs';
const [action,username]=process.argv.slice(2);
if(!['add','remove'].includes(action)||!username||!/^[a-zA-Z0-9_-]{3,48}$/.test(username)){console.error('Usage: npm run user:add -- username OR npm run user:remove -- username (3–48 letters/digits/_/-)');process.exit(1);}
const state=readState();
if(action==='remove'){delete state.users[username];saveState(state);console.log('Account removed.');}
else{
 if(state.users[username]){console.error('Account already exists. Remove it first to replace credentials.');process.exit(1);}
 const password=randomBytes(18).toString('base64url');
 state.users[username]=await passwordHash(password);saveState(state);
 console.log(`Username: ${username}\nPassword: ${password}\nSave this password now; only its salted hash is stored.`);
}
