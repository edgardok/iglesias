// Falla el build si algún archivo de dist supera 20 MiB (Cloudflare corta en 25 MiB) o si hay más de 90.000 archivos (límite 100.000).
import { readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
const LIMITE = 20 * 1024 * 1024, MAX_ARCHIVOS = 18000; // plan gratuito: 20.000 archivos estáticos
let n = 0; const grandes = [];
(function recorrer(d) { for (const f of readdirSync(d)) { if (f === '_worker.js') continue; const r = join(d, f); const s = statSync(r); if (s.isDirectory()) recorrer(r); else { n++; if (s.size > LIMITE) grandes.push(`${r} (${(s.size / 1048576).toFixed(1)} MiB)`); } } })('dist');
console.log(`dist: ${n} archivos`);
if (grandes.length) { console.error('Archivos que superan 20 MiB:\n  ' + grandes.join('\n  ')); process.exit(1); }
if (n > MAX_ARCHIVOS) { console.error(`Demasiados archivos: ${n} > ${MAX_ARCHIVOS}`); process.exit(1); }
