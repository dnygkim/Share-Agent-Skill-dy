#!/usr/bin/env node
// run.json 에 TC 결과 1건(또는 여러 건) append — 손으로 JSON 을 고치지 않기 위한 입구
//   node add_result.mjs --run <run.json> --file <result.json>      # {..} 또는 [{..},{..}]
//   node add_result.mjs --run <run.json> --tc TC-ORD-001 --result Pass [--scenario TS-ORD-001]
//        [--actual "..."] [--repro "..."] [--env "..."] [--hold PRECOND] [--note "..."]
//        [--evidence a.png,b.png] [--manual-step 3 --manual-what "OTP 입력"] [--console "err1||err2"]
//   node add_result.mjs --run <run.json> --scope-file <scope.json>   # scope 갱신
//   node add_result.mjs --run <run.json> --finish                     # finished 시각 기록
// 같은 tc_id 가 이미 있으면 교체(재수행)한다.
import { parseArgs, readJson, writeJson, nowIso, die } from './_common.mjs';

const a = parseArgs();
if (!a.run) die('--run <run.json> 필요');
const run = readJson(a.run);

const VALID = new Set(['Pass', 'Fail', 'Block']);
const HOLD = new Set(['MANUAL', 'PRECOND', 'NATIVE', 'EXPECT', 'UNSURE', 'ACCESS', 'TOOL', 'DATA']);
const SECRET_HINT = /(password|passwd|비밀번호|otp)\s*[:=]\s*\S+/i;

function normalize(r) {
  if (!r.tc_id) die('tc_id 없음');
  if (!VALID.has(r.result)) die(`${r.tc_id}: result 는 Pass | Fail | Block (받은 값: ${r.result})`);
  if (r.result === 'Block' && !HOLD.has(r.hold_code)) die(`${r.tc_id}: Block 은 hold_code 필수 (${[...HOLD].join('|')})`);
  if (r.result !== 'Block') r.hold_code = null;
  for (const k of ['actual', 'repro', 'note', 'env']) {
    r[k] = r[k] || '';
    if (SECRET_HINT.test(r[k])) die(`${r.tc_id}: ${k} 에 비밀값 패턴이 있습니다 — 기록 금지`);
  }
  r.evidence = Array.isArray(r.evidence) ? r.evidence : (r.evidence ? String(r.evidence).split(',').map(s => s.trim()).filter(Boolean) : []);
  r.console_errors = Array.isArray(r.console_errors) ? r.console_errors : (r.console_errors ? String(r.console_errors).split('||') : []);
  r.manual = r.manual || null;
  r.scenario_id = r.scenario_id || '';
  r.started = r.started || nowIso();
  r.finished = r.finished || nowIso();
  return r;
}

let items = [];
if (a.finish) {
  run.finished = nowIso();
} else if (a['scope-file']) {
  run.scope = readJson(a['scope-file']);
} else if (a.file) {
  const j = readJson(a.file);
  items = Array.isArray(j) ? j : [j];
} else if (a.tc) {
  const r = {
    tc_id: a.tc, scenario_id: a.scenario || '', result: a.result, actual: a.actual, repro: a.repro, env: a.env,
    hold_code: a.hold || null, note: a.note, evidence: a.evidence, console_errors: a.console,
  };
  if (a['manual-step']) r.manual = { step: Number(a['manual-step']), what: a['manual-what'] || '', by: '사용자' };
  items = [r];
} else die('--file 또는 --tc … 또는 --scope-file 또는 --finish 중 하나');

for (const raw of items) {
  const r = normalize(raw);
  const idx = run.results.findIndex(x => x.tc_id === r.tc_id);
  if (idx >= 0) run.results[idx] = r; else run.results.push(r);
}
writeJson(a.run, run);
const c = { Pass: 0, Fail: 0, Block: 0 };
run.results.forEach(r => c[r.result]++);
console.log(`${a.run}: results ${run.results.length}건 (Pass ${c.Pass} · Fail ${c.Fail} · Block ${c.Block})${items.length ? ' — 기록: ' + items.map(i => i.tc_id).join(', ') : ''}`);
