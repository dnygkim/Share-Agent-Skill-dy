#!/usr/bin/env node
// 회차(run) 초기화 — run_id 채번 + run.json 머리말 생성
//   node init_run.mjs --slug acme-shop --device PC --engine claude-in-chrome --profile PC-FHD \
//        --viewport 1920x1080 --dpr 1 --browser "Chrome 130.0.6723.92" --os "Windows 11" \
//        --monitor "sub(-1920,0 1920x1080)" --base-url https://stg.example --account qa_user01 \
//        --task ACME쇼핑몰 --tester 김단영 --manual attended \
//        --source-xlsx input/acme-shop/TC.xlsx --tc-json _workspace/acme-shop/tc.json [--note "..."] [--ws _workspace]
// 비밀번호·OTP는 인자로 받지 않는다.
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs, nowIso, ymd, writeJson, die } from './_common.mjs';

const a = parseArgs();
const need = (k) => { if (!a[k] || a[k] === true) die(`--${k} 필요`); return a[k]; };
const slug = need('slug');
const device = need('device').toUpperCase();
if (!['PC', 'MW', 'APP-WV'].includes(device)) die('--device 는 PC | MW | APP-WV');
const engine = need('engine');
if (!['claude-in-chrome', 'playwright'].includes(engine)) die('--engine 은 claude-in-chrome | playwright');
const ws = a.ws || '_workspace';
const runsDir = path.join(ws, slug, 'runs');
fs.mkdirSync(runsDir, { recursive: true });

const prefix = `${ymd()}-${device}-`;
const existing = fs.readdirSync(runsDir).filter(d => d.startsWith(prefix));
const nn = String(existing.length + 1).padStart(2, '0');
const runId = `${prefix}${nn}`;

const run = {
  run_id: runId,
  slug,
  task_name: a.task || '',
  device,
  engine,
  profile: {
    name: a.profile || (device === 'PC' ? 'PC-FHD' : 'iPhone 14'),
    viewport: a.viewport || (device === 'PC' ? '1920x1080' : '390x844'),
    dpr: Number(a.dpr) || (device === 'PC' ? 1 : 3),
    browser: a.browser || '',
    os: a.os || '',
    monitor: a.monitor || '',
    note: a.note || '',
  },
  base_url: a['base-url'] || '',
  account_id: a.account || '',
  tester: a.tester || '',
  manual_mode: a.manual || 'attended',
  started: nowIso(),
  finished: null,
  source_xlsx: a['source-xlsx'] || '',
  tc_json: a['tc-json'] || path.join(ws, slug, 'tc.json'),
  scope: { description: '', tc_ids: [], excluded: [] },
  results: [],
};
const p = path.join(runsDir, runId, 'run.json');
writeJson(p, run);
console.log(`run_id=${runId}`);
console.log(`run.json=${p}`);
console.log(`evidence_dir=output/${slug}/evidence/${runId}`);
