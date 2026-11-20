#!/usr/bin/env node
// qa-master 테스트케이스 엑셀 → tc.json
//   node load_tc.mjs <엑셀경로> --out _workspace/{slug}/tc.json
// 시트는 이름으로, 컬럼은 헤더명으로 찾는다(제출용 변형 · 순서 변경 허용).
import ExcelJS from 'exceljs';
import { parseArgs, cellText, headerMap, norm, nowIso, writeJson, die } from './_common.mjs';

const args = parseArgs();
const src = args._[0];
if (!src) die('사용법: node load_tc.mjs <엑셀경로> --out <tc.json>');
const outPath = args.out || 'tc.json';

const NATIVE_KEYWORDS = ['푸시', '카메라', '갤러리', '생체인증', 'FaceID', 'Face ID', '지문', '인앱', '앱 결제', '앱결제',
  '딥링크', '앱 권한', '백그라운드', '위젯', '앱 업데이트'];

// TC 컬럼 — 헤더명(공백 제거) → 필드명
const TC_COLS = {
  'TCID': 'tc_id', '대분류': 'cat1', '중분류': 'cat2', '소분류': 'cat3', '시나리오ID': 'scenario_id',
  '우선순위': 'priority', '적용기법': 'technique', '사전조건': 'precond', '테스트절차': 'steps',
  '입력데이터': 'data', '기대결과': 'expected', '출처': 'source',
  '실행결과': 'exec_result', '실제결과': 'actual', '재현절차': 'repro', '발견환경': 'env',
  '상태': 'status', '결함ID': 'defect_id', '비고': 'note',
};
const SCN_COLS = {
  '시나리오ID': 'id', '구분(대분류)': 'category', '구분': 'category', '시나리오명': 'name',
  '설명(사용자관점흐름)': 'desc', '설명': 'desc', '연관TC수': 'tc_count', '근거(출처)': 'source', '근거': 'source', '출처': 'source',
};

const wb = new ExcelJS.Workbook();
await wb.xlsx.readFile(src);

const findSheet = (...names) => wb.worksheets.find(ws => names.some(n => norm(ws.name) === norm(n)))
  || wb.worksheets.find(ws => names.some(n => norm(ws.name).includes(norm(n))));
const wsTc = findSheet('테스트케이스');
const wsScn = findSheet('테스트 시나리오', '시나리오');
const wsOv = findSheet('개요');
if (!wsTc) die(`「테스트케이스」 시트를 찾지 못했습니다. 시트 목록: ${wb.worksheets.map(w => w.name).join(', ')}`);

function readTable(ws, colDef, requiredKey) {
  const hm = headerMap(ws);
  const colOf = {};
  for (const [h, f] of Object.entries(colDef)) if (hm[h] && !colOf[f]) colOf[f] = hm[h];
  if (!colOf[requiredKey]) return { rows: [], missing: Object.keys(hm), colOf };
  const rows = [];
  for (let r = 2; r <= ws.rowCount; r++) {
    const row = ws.getRow(r);
    const key = cellText(row.getCell(colOf[requiredKey]));
    if (!key) continue;
    const obj = { row: r };
    for (const [f, c] of Object.entries(colOf)) obj[f] = cellText(row.getCell(c));
    rows.push(obj);
  }
  return { rows, colOf };
}

const warnings = [];
const tc = readTable(wsTc, TC_COLS, 'tc_id');
if (!tc.rows.length) die(`「테스트케이스」 시트에서 「TC ID」 헤더를 찾지 못했습니다. 발견한 헤더: ${tc.missing?.join(' | ')}`);

const scenarios = wsScn ? readTable(wsScn, SCN_COLS, 'id').rows.map(s => ({
  id: s.id, category: s.category || '', name: s.name || '', desc: s.desc || '',
  tc_count: Number(s.tc_count) || 0, source: s.source || '', row: s.row,
})) : [];
if (!wsScn) warnings.push('「테스트 시나리오」 시트 없음 — 시나리오 집계는 TC의 시나리오 ID로만 구성');
const scnIds = new Set(scenarios.map(s => s.id));

const overview = [];
if (wsOv) for (let r = 2; r <= wsOv.rowCount; r++) {
  const k = cellText(wsOv.getRow(r).getCell(1)); const v = cellText(wsOv.getRow(r).getCell(2));
  if (k) overview.push([k, v]);
}

const seen = new Map();
const testcases = tc.rows.map(t => {
  const flags = [];
  if (/\[확인\s*필요\]/.test(t.expected || '')) flags.push('EXPECT_TBD');
  const hay = `${t.cat3 || ''} ${t.steps || ''} ${t.data || ''} ${t.precond || ''}`;
  if (NATIVE_KEYWORDS.some(k => hay.includes(k))) flags.push('NATIVE');
  if (!t.source) { flags.push('NO_SOURCE'); warnings.push(`${t.tc_id}: 출처 비어 있음`); }
  if (seen.has(t.tc_id)) { flags.push('DUP_ID'); warnings.push(`${t.tc_id}: TC ID 중복 (행 ${seen.get(t.tc_id)} · ${t.row})`); }
  seen.set(t.tc_id, t.row);
  if (t.scenario_id && scnIds.size && !scnIds.has(t.scenario_id)) warnings.push(`${t.tc_id}: 시나리오 ${t.scenario_id} 없음`);
  return {
    row: t.row, tc_id: t.tc_id, cat1: t.cat1 || '', cat2: t.cat2 || '', cat3: t.cat3 || '',
    scenario_id: t.scenario_id || '', priority: t.priority || '', technique: t.technique || '',
    precond: t.precond || '', steps: t.steps || '', data: t.data || '', expected: t.expected || '',
    source: t.source || '', note: t.note || '', flags,
  };
});

const out = { source: src, loaded_at: nowIso(), overview, scenarios, testcases, warnings };
writeJson(outPath, out);

// 요약 출력 (GATE 표 재료)
const byScn = {};
for (const t of testcases) (byScn[t.scenario_id || '(없음)'] ||= []).push(t);
console.log(`tc.json 저장: ${outPath}`);
console.log(`시나리오 ${scenarios.length}건 · TC ${testcases.length}건 · 경고 ${warnings.length}건`);
console.log('');
console.log('시나리오 ID | 시나리오명 | TC 수 | 상/중/하 | 플래그');
for (const [sid, list] of Object.entries(byScn)) {
  const name = scenarios.find(s => s.id === sid)?.name || '';
  const pr = ['상', '중', '하'].map(p => list.filter(t => t.priority === p).length).join('/');
  const fl = list.flatMap(t => t.flags).reduce((m, f) => (m[f] = (m[f] || 0) + 1, m), {});
  const flStr = Object.entries(fl).map(([k, v]) => `${k}×${v}`).join(' ');
  console.log(`${sid} | ${name} | ${list.length} | ${pr} | ${flStr}`);
}
if (warnings.length) { console.log(''); console.log('경고:'); warnings.forEach(w => console.log(' - ' + w)); }
