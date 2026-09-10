import { cpSync } from 'node:fs';
// Keep report-relative sources and overlays available in the production build.
cpSync(new URL('../data',import.meta.url),new URL('../dist/data',import.meta.url),{recursive:true});
cpSync(new URL('../kingswood-report.html',import.meta.url),new URL('../dist/kingswood-report.html',import.meta.url));
