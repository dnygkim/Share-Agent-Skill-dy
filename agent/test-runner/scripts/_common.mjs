// 공통 유틸 — 인자 파싱 · 셀 텍스트 · 날짜
import fs from 'node:fs';
import path from 'node:path';

/** --key value / --flag 형식 인자를 객체로. 위치 인자는 _ 배열 */
export function parseArgs(argv = process.argv.slice(2)) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const eq = a.indexOf('=');
      if (eq > 0) { out[a.slice(2, eq)] = a.slice(eq + 1); continue; }
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) out[key] = true;
      else { out[key] = next; i++; }
    } else out._.push(a);
  }
  return out;
}

/** exceljs 셀 값 → 문자열 (richText · formula · date · hyperlink 대응) */
export function cellText(cell) {
  if (!cell) return '';
  let v = cell.value;
  if (v === null || v === undefined) return '';
  if (typeof v === 'object') {
    if (Array.isArray(v.richText)) return v.richText.map(r => r.text).join('');
    if (v.result !== undefined) v = v.result;
    else if (v.text !== undefined) v = v.text;          // hyperlink
    else if (v instanceof Date) return v.toISOString().slice(0, 10);
    else if (v.error) return '';
  }
  return String(v).replace(/\r\n/g, '\n').trim();
}

/** 헤더 행 → {헤더명: 열번호}. 공백 제거·대소문자 무시 */
export function headerMap(ws, rowNo = 1) {
  const map = {};
  ws.getRow(rowNo).eachCell((cell, col) => {
    const key = cellText(cell).replace(/\s+/g, '');
    if (key) map[key] = col;
  });
  return map;
}
export const norm = (s) => String(s || '').replace(/\s+/g, '');

export function nowIso() {
  const d = new Date();
  const tz = -d.getTimezoneOffset();
  const sign = tz >= 0 ? '+' : '-';
  const pad = (n) => String(Math.abs(n)).padStart(2, '0');
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 19)
    + `${sign}${pad(Math.trunc(tz / 60))}:${pad(tz % 60)}`;
}
export function ymd(d = new Date()) {
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}`;
}
export function ymdDash(d = new Date()) { const s = ymd(d); return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`; }

export function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }
export function writeJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + '\n', 'utf8');
}
export function die(msg, code = 1) { console.error(`[오류] ${msg}`); process.exit(code); }
