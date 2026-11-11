#!/usr/bin/env node
// run.json → 원본 엑셀 복제본에 실행 컬럼 기입 (qa-master 서식·드롭다운 유지)
//   node write_results.mjs --run <run.json> --src <원본.xlsx> --out <결과.xlsx>
import fs from 'node:fs';
import path from 'node:path';
import ExcelJS from 'exceljs';
import { parseArgs, cellText, headerMap, norm, readJson, die } from './_common.mjs';

const a = parseArgs();
for (const k of ['run', 'src', 'out']) if (!a[k]) die(`--${k} 필요`);
const run = readJson(a.run);

const wb = new ExcelJS.Workbook();
await wb.xlsx.readFile(a.src);
const ws = wb.worksheets.find(w => norm(w.name) === '테스트케이스') || wb.worksheets.find(w => norm(w.name).includes('테스트케이스'));
if (!ws) die('「테스트케이스」 시트 없음');
const hm = headerMap(ws);
const col = (name) => hm[norm(name)];
for (const need of ['TC ID', '실행결과']) if (!col(need)) die(`헤더 「${need}」 없음 — 발견: ${Object.keys(hm).join(' | ')}`);

const byId = new Map();
for (const r of run.results) byId.set(r.tc_id, r);   // 마지막 기록 우선

const setIf = (row, name, value) => { const c = col(name); if (c && value !== undefined) row.getCell(c).value = value; };
const basename = (p) => path.basename(p);

let written = 0, total = 0;
for (let r = 2; r <= ws.rowCount; r++) {
  const row = ws.getRow(r);
  const id = cellText(row.getCell(col('TC ID')));
  if (!id) continue;
  total++;
  const res = byId.get(id);
  if (!res) continue;
  const parts = [];
  const designNote = cellText(row.getCell(col('비고')));
  if (designNote) parts.push(designNote);
  if (res.evidence?.length) parts.push(`증적: ${res.evidence.map(basename).join(', ')}`);
  if (res.result === 'Block') parts.push(`[${res.hold_code}] ${res.note || ''}`.trim());
  else if (res.note) parts.push(res.note);
  if (res.manual) parts.push(`수동 처리: 절차 ${res.manual.step}(${res.manual.what})`);
  if (res.console_errors?.length && res.result === 'Fail') parts.push(`콘솔: ${res.console_errors[0]}`);

  setIf(row, '실행결과', res.result);
  setIf(row, '실제 결과', res.actual || '');
  setIf(row, '재현 절차', res.repro || '');
  setIf(row, '발견 환경', res.env || '');
  setIf(row, '상태', res.result === 'Fail' ? '신규' : '');
  setIf(row, '비고', parts.join(' / '));
  written++;
}

// 개요 시트 — 회차 정보 append
const ov = wb.worksheets.find(w => norm(w.name) === '개요');
const c = { Pass: 0, Fail: 0, Block: 0 };
for (const r of byId.values()) c[r.result]++;
const notRun = total - byId.size;
if (ov) {
  const last = ov.rowCount;
  const base = ov.getRow(last);
  const rows = [
    ['실행 회차', run.run_id],
    ['실행 디바이스 / 프로필', `${run.device} · ${run.profile?.name || ''} · ${run.profile?.viewport || ''}`],
    ['실행 엔진 / 브라우저', `${run.engine} · ${run.profile?.browser || ''} · ${run.profile?.os || ''}`],
    ['실행 일시', `${run.started || ''} ~ ${run.finished || ''}`],
    ['실행자', run.tester || ''],
    ['실행 범위', run.scope?.description || `TC ${byId.size}건`],
    ['실행 결과 집계', `Pass ${c.Pass} / Fail ${c.Fail} / Block ${c.Block} / 미실행 ${notRun} (총 ${total})`],
    ['증적 경로', `evidence/${run.run_id}/`],
  ];
  rows.forEach((vals, i) => {
    const row = ov.getRow(last + 1 + i);
    vals.forEach((v, j) => {
      const cell = row.getCell(j + 1);
      cell.value = v;
      const src = base.getCell(j + 1);
      if (src.style) cell.style = JSON.parse(JSON.stringify(src.style));
    });
    row.commit();
  });
}

fs.mkdirSync(path.dirname(a.out), { recursive: true });
await wb.xlsx.writeFile(a.out);
console.log(`결과 엑셀 저장: ${a.out}`);
console.log(`기입 ${written}건 / 전체 ${total}건 — Pass ${c.Pass} · Fail ${c.Fail} · Block ${c.Block} · 미실행 ${notRun}`);
if (written !== run.results.length && byId.size !== written) console.log(`[경고] run.json 결과 ${byId.size}건 중 엑셀에서 못 찾은 TC: ${[...byId.keys()].filter(id => !ws.getColumn(col('TC ID')).values.map(v => String(v ?? '').trim()).includes(id)).join(', ')}`);
