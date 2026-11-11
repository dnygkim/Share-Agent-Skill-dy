#!/usr/bin/env node
// Playwright 플랜 실행기 — 시나리오 단위 플랜(JSON)을 받아 스텝을 수행하고 결과 JSON·스크린샷을 남긴다.
//   node pw_run.mjs --check
//   node pw_run.mjs --plan plan_TS-ORD-001.json --out pw_TS-ORD-001.json --evidence output/{slug}/evidence/{run_id}
//        [--headed] [--user-data-dir <폴더>] [--monitor sub|primary|X,Y] [--timeout 15000] [--slowmo 0]
// 판정은 하지 않는다 — expect 실패는 Fail 후보일 뿐이고 최종 판정은 에이전트가 기대결과와 대조해 내린다.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { parseArgs, readJson, writeJson, nowIso, die } from './_common.mjs';

const a = parseArgs();
const require = createRequire(import.meta.url);

let pw;
try { pw = await import('playwright'); } catch { die('playwright 미설치 — scripts/ 에서 npm install 후 npx playwright install chromium webkit'); }
const { chromium, webkit, firefox, devices } = pw;

if (a.check) {
  const ver = require('playwright/package.json').version;
  console.log(`playwright ${ver}`);
  for (const [name, b] of [['chromium', chromium], ['webkit', webkit], ['firefox', firefox]]) {
    let p = ''; try { p = b.executablePath(); } catch {}
    console.log(`${name}: ${p && fs.existsSync(p) ? '설치됨 ' + p : '미설치 (npx playwright install ' + name + ')'}`);
  }
  process.exit(0);
}

for (const k of ['plan', 'out', 'evidence']) if (!a[k]) die(`--${k} 필요`);
const plan = readJson(a.plan);
const evidenceDir = a.evidence;
fs.mkdirSync(evidenceDir, { recursive: true });
const timeout = Number(a.timeout) || 15000;
const headed = !!a.headed || !!a['user-data-dir'];
const browserName = plan.browser || 'chromium';
const launcher = { chromium, webkit, firefox }[browserName];
if (!launcher) die(`browser 는 chromium | webkit | firefox (받은 값: ${browserName})`);

// ── 서브모니터 좌표 (Windows · chromium 만 창 위치 지정 가능)
function subMonitor() {
  if (process.platform !== 'win32') return null;
  try {
    const ps = 'Add-Type -AssemblyName System.Windows.Forms; $s=[System.Windows.Forms.Screen]::AllScreens | Where-Object { -not $_.Primary } | Select-Object -First 1; if($s){ "$($s.Bounds.X),$($s.Bounds.Y),$($s.Bounds.Width),$($s.Bounds.Height)" }';
    const out = execFileSync('powershell', ['-NoProfile', '-Command', ps], { encoding: 'utf8' }).trim();
    if (!out) return null;
    const [x, y, w, h] = out.split(',').map(Number);
    return { x, y, w, h };
  } catch { return null; }
}
const launchArgs = [];
let monitorNote = '';
if (headed && (a.monitor === undefined || a.monitor === 'sub' || /^-?\d+,-?\d+$/.test(String(a.monitor)))) {
  let pos = null;
  if (/^-?\d+,-?\d+$/.test(String(a.monitor))) { const [x, y] = String(a.monitor).split(',').map(Number); pos = { x, y, w: 1920, h: 1032 }; }
  else pos = subMonitor();
  if (pos && browserName === 'chromium') { launchArgs.push(`--window-position=${pos.x},${pos.y}`, `--window-size=${pos.w},${Math.max(600, pos.h - 48)}`); monitorNote = `sub(${pos.x},${pos.y} ${pos.w}x${pos.h})`; }
  else if (pos) monitorNote = `${browserName}는 창 위치 지정 미지원 — 주 모니터`;
  else monitorNote = '서브모니터 없음 — 주 모니터';
}

// ── 컨텍스트 옵션
const ctxOpts = {};
if (plan.device) { if (!devices[plan.device]) die(`Playwright 디바이스 「${plan.device}」 없음`); Object.assign(ctxOpts, devices[plan.device]); }
else if (plan.viewport) ctxOpts.viewport = plan.viewport;
if (plan.locale) ctxOpts.locale = plan.locale;
if (plan.storage_state && fs.existsSync(plan.storage_state)) ctxOpts.storageState = plan.storage_state;

let browser = null, context;
if (a['user-data-dir']) {
  context = await launcher.launchPersistentContext(a['user-data-dir'], { headless: !headed, args: launchArgs, slowMo: Number(a.slowmo) || 0, ...ctxOpts });
} else {
  browser = await launcher.launch({ headless: !headed, args: launchArgs, slowMo: Number(a.slowmo) || 0 });
  context = await browser.newContext(ctxOpts);
}
context.setDefaultTimeout(timeout);
const page = context.pages()[0] || await context.newPage();
const consoleErrors = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push(String(e.message || e)));

const base = (plan.base_url || '').replace(/\/$/, '');
const url = (u) => /^https?:/i.test(u) ? u : base + (u.startsWith('/') ? u : '/' + u);
function loc(s) {
  if (s.selector) return page.locator(s.selector).first();
  if (s.role) return page.getByRole(s.role, s.name ? { name: s.name } : {}).first();
  if (s.text) return page.getByText(s.text, { exact: !!s.exact }).first();
  if (s.label) return page.getByLabel(s.label).first();
  if (s.placeholder) return page.getByPlaceholder(s.placeholder).first();
  throw new Error('대상 없음: selector | text | role+name | label | placeholder 중 하나 필요');
}
async function shot(name) { const p = path.join(evidenceDir, `${name}.png`); await page.screenshot({ path: p, fullPage: false }); return p; }

async function runStep(s) {
  switch (s.action) {
    case 'goto': await page.goto(url(s.url), { waitUntil: s.wait_until || 'load' }); break;
    case 'click': await loc(s).click(s.options || {}); break;
    case 'dblclick': await loc(s).dblclick(); break;
    case 'fill': await loc(s).fill(String(s.value ?? '')); break;
    case 'type': await loc(s).pressSequentially(String(s.value ?? ''), { delay: s.delay || 30 }); break;
    case 'press': if (s.selector || s.text || s.role || s.label) await loc(s).press(s.key); else await page.keyboard.press(s.key); break;
    case 'select': await loc(s).selectOption(s.value); break;
    case 'check': await loc(s).check(); break;
    case 'uncheck': await loc(s).uncheck(); break;
    case 'hover': await loc(s).hover(); break;
    case 'scroll': await page.mouse.wheel(0, Number(s.dy) || 600); break;
    case 'wait':
      if (s.ms) await page.waitForTimeout(Number(s.ms));
      else if (s.selector || s.text) await loc(s).waitFor({ state: s.state || 'visible' });
      else if (s.url) await page.waitForURL(u => u.toString().includes(s.url));
      else await page.waitForLoadState(s.state || 'networkidle');
      break;
    case 'expect_text': {
      const hay = (s.selector || s.role || s.label) ? await loc(s).innerText() : await page.locator('body').innerText();
      if (!hay.includes(s.value)) throw new Error(`텍스트 없음: "${s.value}"`);
      break;
    }
    case 'expect_url': { const u = page.url(); if (!u.includes(s.contains ?? s.value)) throw new Error(`URL 불일치: ${u}`); break; }
    case 'expect_visible': if (!(await loc(s).isVisible())) throw new Error('보이지 않음'); break;
    case 'expect_hidden': if (await loc(s).isVisible()) throw new Error('보임(숨김 기대)'); break;
    case 'expect_value': { const v = await loc(s).inputValue(); if (v !== String(s.value)) throw new Error(`값 불일치: "${v}"`); break; }
    case 'expect_count': { const n = await page.locator(s.selector).count(); if (n !== Number(s.value)) throw new Error(`개수 불일치: ${n}`); break; }
    case 'screenshot': return { screenshot: await shot(s.name || 'shot') };
    case 'console_snapshot': return { console_errors: [...consoleErrors] };
    default: throw new Error(`알 수 없는 action: ${s.action}`);
  }
  return {};
}

const results = [];
for (const t of plan.tcs || []) {
  const rec = { tc_id: t.tc_id, ok: true, steps: [], screenshots: [], console_errors: [], started: nowIso(), finished: null };
  consoleErrors.length = 0;
  let tookShot = false;
  for (let i = 0; i < (t.steps || []).length; i++) {
    const s = t.steps[i]; const t0 = Date.now();
    const st = { i: i + 1, action: s.action, ok: true, error: null, ms: 0 };
    try {
      const r = await runStep(s);
      if (r.screenshot) { rec.screenshots.push(r.screenshot); tookShot = true; }
    } catch (e) {
      st.ok = false; st.error = String(e.message || e).split('\n')[0]; rec.ok = false;
      try { rec.screenshots.push(await shot(`${t.tc_id}_fail`)); } catch {}
      st.ms = Date.now() - t0; rec.steps.push(st);
      break;   // expect/조작 실패 뒤는 수행하지 않는다
    }
    st.ms = Date.now() - t0; rec.steps.push(st);
  }
  if (!tookShot) { try { rec.screenshots.push(await shot(t.tc_id)); } catch (e) { rec.steps.push({ i: 0, action: 'auto_screenshot', ok: false, error: String(e.message) }); } }
  rec.console_errors = [...consoleErrors];
  rec.finished = nowIso();
  results.push(rec);
  console.log(`${t.tc_id}: ${rec.ok ? 'ok' : 'FAIL@' + rec.steps.find(x => !x.ok)?.i + ' ' + rec.steps.find(x => !x.ok)?.error}`);
}

writeJson(a.out, { plan: a.plan, browser: browserName, device: plan.device || null, headed, monitor: monitorNote, results });
if (a['keep-open']) { console.log('--keep-open: 브라우저를 닫지 않습니다 (Ctrl+C 로 종료)'); await new Promise(() => {}); }
await context.close(); if (browser) await browser.close();
console.log(`결과 저장: ${a.out} (${results.length}건 · 실패 ${results.filter(r => !r.ok).length}건)${monitorNote ? ' · 창 ' + monitorNote : ''}`);
