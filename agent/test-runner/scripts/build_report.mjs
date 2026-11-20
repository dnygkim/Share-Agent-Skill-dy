#!/usr/bin/env node
// run.json + tc.json → 하우스 스타일 문서형 HTML 리포트 (자기완결 단일 파일)
//   node build_report.mjs --run <run.json> --tc <tc.json> --out <리포트.html>
//        [--css <house-style.css 경로>] [--embed] [--client "클라이언트명"] [--author "작성자"] [--doc-name "테스트실행결과"]
// --embed : 증적 PNG 를 base64 로 인라인(공유용). 기본은 output/{slug}/ 기준 상대경로 링크.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { parseArgs, readJson, ymd, ymdDash, die } from './_common.mjs';

const a = parseArgs();
for (const k of ['run', 'tc', 'out']) if (!a[k]) die(`--${k} 필요`);
const run = readJson(a.run);
const tc = readJson(a.tc);
const here = path.dirname(fileURLToPath(import.meta.url));

// ── 스타일 정본 찾기: --css > ~/.claude/house-style > 리포 global-house-style
const cssCandidates = [a.css, path.join(os.homedir(), '.claude', 'house-style', 'house-style.css'),
  path.join(here, '..', '..', '..', 'global-house-style', 'house-style.css')].filter(Boolean);
const cssPath = cssCandidates.find(p => fs.existsSync(p));
if (!cssPath) die(`house-style.css 를 찾지 못했습니다: ${cssCandidates.join(' | ')}`);
const css = fs.readFileSync(cssPath, 'utf8');

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
const nl = (s) => esc(s).replace(/\n/g, '<br>');
const client = a.client || run.task_name || run.slug;
const author = a.author || run.tester || '';
const docName = a['doc-name'] || '테스트실행결과';
const today = ymd(); const todayDash = ymdDash();
const outDir = path.dirname(path.resolve(a.out));

// ── 데이터 정리
const tcById = new Map(tc.testcases.map(t => [t.tc_id, t]));
const resById = new Map(); for (const r of run.results) resById.set(r.tc_id, r);
const scopeIds = run.scope?.tc_ids?.length ? run.scope.tc_ids : tc.testcases.map(t => t.tc_id);
const scopeSet = new Set(scopeIds);
const resultOf = (id) => resById.get(id)?.result || (scopeSet.has(id) ? '미실행' : '미실행');
const count = { 전체: tc.testcases.length, Pass: 0, Fail: 0, Block: 0, 미실행: 0 };
for (const t of tc.testcases) count[resultOf(t.tc_id)]++;
const PR = { '상': 0, '중': 1, '하': 2 };
const fails = run.results.filter(r => r.result === 'Fail').sort((x, y) => (PR[tcById.get(x.tc_id)?.priority] ?? 9) - (PR[tcById.get(y.tc_id)?.priority] ?? 9) || x.tc_id.localeCompare(y.tc_id));
const blocks = run.results.filter(r => r.result === 'Block').sort((x, y) => x.tc_id.localeCompare(y.tc_id));
const manuals = run.results.filter(r => r.manual);
const remaining = blocks.filter(r => ['MANUAL', 'NATIVE', 'UNSURE', 'EXPECT'].includes(r.hold_code));

const scnRows = [];
const scnMap = new Map(tc.scenarios.map(s => [s.id, s]));
const groups = {};
for (const t of tc.testcases) (groups[t.scenario_id || '(없음)'] ||= []).push(t);
for (const [sid, list] of Object.entries(groups)) {
  const c = { Pass: 0, Fail: 0, Block: 0, 미실행: 0 };
  list.forEach(t => c[resultOf(t.tc_id)]++);
  scnRows.push({ id: sid, name: scnMap.get(sid)?.name || '', total: list.length, ...c });
}

// ── 증적 src
function evidenceSrc(rel) {
  const abs = path.resolve(outDir, rel);
  if (a.embed) {
    if (!fs.existsSync(abs)) return null;
    return `data:image/png;base64,${fs.readFileSync(abs).toString('base64')}`;
  }
  return fs.existsSync(abs) ? rel.replace(/\\/g, '/') : null;
}
const tag = (res) => res === 'Pass' ? '<span class="tag pick">Pass</span>'
  : res === 'Fail' ? '<span class="tag" style="background:var(--ink);color:var(--paper);border-color:var(--ink)">Fail</span>'
  : res === 'Block' ? '<span class="tag chk">Block</span>' : '<span class="tag">미실행</span>';
const envLine = `${run.device} · ${run.profile?.name || ''} · ${run.profile?.browser || ''} · ${run.profile?.os || ''} · ${run.profile?.viewport || ''}`;
const engineKo = run.engine === 'playwright' ? 'Playwright' : 'claude-in-chrome(Chrome 확장)';
const deviceKo = { PC: 'PC 웹', MW: '모바일 웹', 'APP-WV': '앱 웹뷰(모바일 웹 대체)' }[run.device] || run.device;

// ── 섹션 본문
const failBlocks = fails.map(r => {
  const t = tcById.get(r.tc_id) || {};
  const imgs = (r.evidence || []).map(ev => { const s = evidenceSrc(ev); return s ? `<figure style="margin:8px 0"><img src="${esc(s)}" alt="${esc(path.basename(ev))}" style="max-width:100%;width:420px;border:1px solid var(--line);display:block"><figcaption class="small muted">${esc(path.basename(ev))}</figcaption></figure>` : `<p class="small muted">증적 파일 없음: ${esc(ev)}</p>`; }).join('');
  return `<h3 id="f-${esc(r.tc_id)}">${esc(r.tc_id)} · ${esc(t.cat3 || t.cat2 || '')} <span class="tag chk">${esc(t.priority || '')}</span></h3>
<div class="table-scroll"><table>
<tbody>
<tr><th style="width:120px">시나리오</th><td>${esc(r.scenario_id || t.scenario_id || '')} ${esc(scnMap.get(r.scenario_id || t.scenario_id)?.name || '')}</td></tr>
<tr><th>테스트 절차</th><td>${nl(t.steps)}</td></tr>
<tr><th>입력 데이터</th><td>${nl(t.data)}</td></tr>
<tr><th>기대결과</th><td>${nl(t.expected)}</td></tr>
<tr><th>실제 결과</th><td><b>${nl(r.actual)}</b></td></tr>
${r.repro ? `<tr><th>재현 절차</th><td>${nl(r.repro)}</td></tr>` : ''}
${r.console_errors?.length ? `<tr><th>콘솔 오류</th><td class="path">${r.console_errors.map(esc).join('<br>')}</td></tr>` : ''}
<tr><th>발견 환경</th><td>${esc(r.env)}</td></tr>
</tbody></table></div>
${imgs}`;
}).join('\n');

const blockRows = blocks.map(r => { const t = tcById.get(r.tc_id) || {}; return `<tr><td>${esc(r.tc_id)}</td><td>${esc(t.cat3 || '')}</td><td class="c">${esc(t.priority || '')}</td><td class="c"><span class="tag chk">${esc(r.hold_code)}</span></td><td>${nl(r.note)}${r.actual ? `<br><span class="muted small">관찰: ${nl(r.actual)}</span>` : ''}</td></tr>`; }).join('\n');

const manualRows = manuals.map(r => `<tr><td>${esc(r.tc_id)}</td><td class="c">절차 ${esc(r.manual.step)}</td><td>${esc(r.manual.what)}</td><td class="c">${tag(r.result)}</td></tr>`).join('\n');
const remainRows = remaining.map(r => { const t = tcById.get(r.tc_id) || {}; return `<tr><td>${esc(r.tc_id)}</td><td>${esc(t.cat3 || '')}</td><td class="c">${esc(r.hold_code)}</td><td>${nl(r.note)}</td></tr>`; }).join('\n');

const allRows = tc.testcases.map(t => {
  const r = resById.get(t.tc_id); const res = resultOf(t.tc_id);
  const ev = (r?.evidence || []).map(e => { const s = evidenceSrc(e); return s ? `<a class="ext" href="${esc(s)}" target="_blank" rel="noopener">${esc(path.basename(e))}</a>` : esc(path.basename(e)); }).join('<br>');
  const detail = res === 'Fail' ? `<a class="jump" href="#f-${esc(t.tc_id)}">${nl(r.actual)}</a>` : res === 'Block' ? `[${esc(r.hold_code)}] ${nl(r.note)}` : (r?.note ? nl(r.note) : '');
  return `<tr><td style="white-space:nowrap">${esc(t.tc_id)}</td><td style="white-space:nowrap">${esc(t.scenario_id)}</td><td>${esc(t.cat2)}${t.cat2 && t.cat3 ? ' · ' : ''}${esc(t.cat3)}</td><td class="c">${esc(t.priority)}</td><td class="c">${tag(res)}</td><td>${detail}</td><td class="small">${ev}</td></tr>`;
}).join('\n');

const warnList = (tc.warnings || []).length ? `<div class="findings alert"><ul>${tc.warnings.map(w => `<li>${esc(w)}</li>`).join('')}</ul></div>` : '';
const excluded = run.scope?.excluded || [];

// ── 거버닝 메시지 (명사형 상태 묘사)
const H = {
  s1: '한 디바이스, 한 범위로 묶인 실행 회차',
  s2: '흐름 단위로 읽는 정상·오류의 분포',
  s3: fails.length ? '기대와 다르게 동작한 화면과 그 증적' : '기대와 어긋난 화면이 없는 회차',
  s4: blocks.length ? '수행이 막힌 케이스와 막힌 사유' : '수행이 막힌 케이스가 없는 회차',
  s5: '사람 손을 거친 단계와 아직 남은 확인',
  s6: '회차에 포함된 모든 케이스의 판정',
};
const concept = count.Fail === 0 && count.Block === 0
  ? `대상 ${count.전체 - count.미실행}건 전부 기대결과와 일치한 회차`
  : `정상 ${count.Pass}건 뒤에 남은 오류 ${count.Fail}건, 보류 ${count.Block}건`;

const html = `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="revision" content="${today}">
<!-- ═══ 수정 이력 ═══
[${today}] ${esc(author)} · 수정 페이지: 전체 · 내역: 최초 생성 (run ${esc(run.run_id)}, build_report.mjs)
-->
<title>${esc(docName)} ${esc(run.run_id)} — ${esc(client)}</title>
<style>
/* ▼▼▼ house-style.css 전문 삽입 (${esc(path.basename(cssPath))}) ▼▼▼ */
${css}
/* ▲▲▲ 삽입 끝 ▲▲▲ */
</style>
</head>
<body id="top">

<header class="topbar">
  <div class="topbar-inner">
    <span class="logo">${esc(client)}<span class="divider">-</span><span class="sub">${esc(docName)}</span></span>
    <span class="topbar-meta">${today}<span class="divider">/</span><b>${esc(author)}</b></span>
  </div>
</header>

<div class="layout">

<aside class="lnb" aria-label="섹션 이동">
  <ul>
    <li><a href="#s0"><b>·</b>문서 구성</a></li>
    <li><a href="#s1"><b>1</b>실행 개요</a></li>
    <li><a href="#s2"><b>2</b>시나리오별 결과</a></li>
    <li><a href="#s3"><b>3</b>오류(Fail) 목록</a></li>
    <li><a href="#s4"><b>4</b>보류(Block) 목록</a></li>
    <li><a href="#s5"><b>5</b>수동 확인</a></li>
    <li><a href="#s6"><b>6</b>전체 TC 결과</a></li>
    <li><a href="#ssrc"><b>·</b>출처</a></li>
  </ul>
</aside>

<div class="doc">

<header class="cover">
  <p class="eyebrow">${esc(client)} · ${esc(deviceKo)} 테스트 회차 ${esc(run.run_id)}</p>
  <h1>
    <span class="lead">${esc(concept)}</span>
    ${esc(docName)}
  </h1>
  <p class="muted" style="margin:0;max-width:660px;">
    qa-master 테스트케이스 ${count.전체}건 중 ${count.전체 - count.미실행}건을 ${esc(engineKo)}로 수행한 기록. <strong>판정 기준은 테스트케이스의 기대결과 하나</strong>
  </p>
  <div class="meta">
    <span><b>대상</b> ${esc(run.base_url || '-')}</span>
    <span><b>환경</b> ${esc(envLine)}</span>
    <span><b>실행일</b> ${esc((run.started || '').slice(0, 10))}</span>
    <span><b>실행자</b> ${esc(author)}</span>
  </div>
</header>

<nav class="toc" id="s0" aria-label="목차">
  <h2>구성내용 (목차)</h2>
  <ol>
    <li><a href="#s1"><span class="n">1</span>실행 개요</a> — 회차 · 환경 · 범위 · 집계</li>
    <li><a href="#s2"><span class="n">2</span>시나리오별 결과</a> — 흐름 단위 Pass/Fail/Block</li>
    <li><a href="#s3"><span class="n">3</span>오류(Fail) 목록</a> ${fails.length ? `<span class="tag chk">${fails.length}건</span>` : ''}</li>
    <li><a href="#s4"><span class="n">4</span>보류(Block) 목록</a> ${blocks.length ? `<span class="tag chk">${blocks.length}건</span>` : ''}</li>
    <li><a href="#s5"><span class="n">5</span>수동 확인</a> — 개입 이력 · 남은 확인</li>
    <li><a href="#s6"><span class="n">6</span>전체 TC 결과</a></li>
  </ol>
  <p class="small muted" style="margin:12px 0 0">부속 — <a class="jump" href="#ssrc">출처</a></p>
</nav>

<section>
  <h2 id="s1"><span class="num">1</span>${H.s1}</h2>
  <p class="small muted">실행 개요 · ${esc(run.run_id)} · ${esc(deviceKo)}</p>
  <div class="stats">
    <div class="stat"><div class="v">${count.전체}<span class="u">건</span></div><div class="l">전체 TC</div></div>
    <div class="stat"><div class="v">${count.Pass}<span class="u">건</span></div><div class="l">정상(Pass)</div></div>
    <div class="stat"><div class="v">${count.Fail}<span class="u">건</span></div><div class="l">오류(Fail)</div></div>
    <div class="stat"><div class="v">${count.Block}<span class="u">건</span></div><div class="l">보류(Block)</div></div>
    <div class="stat"><div class="v">${count.미실행}<span class="u">건</span></div><div class="l">미실행</div></div>
  </div>
  <div class="table-scroll"><table>
    <caption>회차 정보 · run.json 기준</caption>
    <tbody>
      <tr><th style="width:160px">회차 ID</th><td>${esc(run.run_id)}</td></tr>
      <tr><th>디바이스 · 프로필</th><td>${esc(deviceKo)} · ${esc(run.profile?.name || '')} · ${esc(run.profile?.viewport || '')} · DPR ${esc(run.profile?.dpr ?? '')}${run.profile?.note ? ` <span class="muted small">(${esc(run.profile.note)})</span>` : ''}</td></tr>
      <tr><th>엔진 · 브라우저</th><td>${esc(engineKo)} · ${esc(run.profile?.browser || '')} · ${esc(run.profile?.os || '')}</td></tr>
      <tr><th>대상 URL</th><td class="path">${esc(run.base_url || '-')}</td></tr>
      <tr><th>테스트 계정</th><td>${esc(run.account_id || '-')}</td></tr>
      <tr><th>실행 시간</th><td>${esc(run.started || '')} ~ ${esc(run.finished || '(진행 중)')}</td></tr>
      <tr><th>수동 개입 모드</th><td>${run.manual_mode === 'unattended' ? '무인(보류 처리)' : '유인(그 자리에서 처리)'}</td></tr>
      <tr><th>실행 범위</th><td>${esc(run.scope?.description || '전체')} · 대상 ${scopeIds.length}건${excluded.length ? ` · 제외 ${excluded.length}건(${excluded.map(e => `${esc(e.tc_id)} ${esc(e.reason)}`).join(', ')})` : ''}</td></tr>
      <tr><th>테스트 베이시스</th><td class="path">${esc(path.basename(tc.source || run.source_xlsx || ''))}</td></tr>
    </tbody>
  </table></div>
  ${warnList ? `<h3>TC 엑셀 경고</h3>${warnList}` : ''}
</section>

<section>
  <h2 id="s2"><span class="num">2</span>${H.s2}</h2>
  <p class="small muted">시나리오별 결과 · 시나리오 ID 순 · 결과값 qa-master 드롭다운 기준</p>
  <div class="table-scroll"><table>
    <thead><tr><th>시나리오 ID</th><th>시나리오명</th><th class="c">TC</th><th class="c">Pass</th><th class="c">Fail</th><th class="c">Block</th><th class="c">미실행</th></tr></thead>
    <tbody>
    ${scnRows.map(s => `<tr><td>${esc(s.id)}</td><td>${esc(s.name)}</td><td class="c">${s.total}</td><td class="c">${s.Pass}</td><td class="c">${s.Fail ? `<b>${s.Fail}</b>` : 0}</td><td class="c">${s.Block}</td><td class="c">${s.미실행}</td></tr>`).join('\n')}
    </tbody>
  </table></div>
</section>

<section>
  <h2 id="s3"><span class="num">3</span>${H.s3}</h2>
  <p class="small muted">오류(Fail) 목록 · 우선순위 상→하 · 증적 포함</p>
  ${fails.length ? failBlocks : '<p class="note">이번 회차 범위에서 Fail 판정 없음</p>'}
</section>

<section>
  <h2 id="s4"><span class="num">4</span>${H.s4}</h2>
  <p class="small muted">보류(Block) 목록 · 사유 코드 = references/result-rules.md §3</p>
  ${blocks.length ? `<div class="table-scroll"><table>
    <thead><tr><th>TC ID</th><th>소분류</th><th class="c">우선순위</th><th class="c">사유</th><th>내용</th></tr></thead>
    <tbody>${blockRows}</tbody></table></div>` : '<p class="note">이번 회차 범위에서 Block 판정 없음</p>'}
</section>

<section>
  <h2 id="s5"><span class="num">5</span>${H.s5}</h2>
  <p class="small muted">수동 확인 · 개입 이력(유인 모드) · 남은 확인(보류 중 사람 확인이 필요한 것)</p>
  <h3>개입 이력</h3>
  ${manuals.length ? `<div class="table-scroll"><table><thead><tr><th>TC ID</th><th class="c">단계</th><th>처리 내용</th><th class="c">최종 판정</th></tr></thead><tbody>${manualRows}</tbody></table></div>` : '<p class="muted">사용자 개입 없이 수행</p>'}
  <h3>남은 확인</h3>
  ${remaining.length ? `<div class="findings alert"><ul>${remaining.map(r => `<li><b>${esc(r.tc_id)}</b> — [${esc(r.hold_code)}] ${esc(r.note)}</li>`).join('')}</ul></div>` : '<p class="muted">남은 수동 확인 없음</p>'}
</section>

<section>
  <h2 id="s6"><span class="num">6</span>${H.s6}</h2>
  <p class="small muted">전체 TC 결과 · 엑셀 「테스트케이스」 시트 순서 · 미실행 = 이번 회차 범위 밖</p>
  <div class="table-scroll"><table>
    <thead><tr><th>TC ID</th><th>시나리오</th><th>분류</th><th class="c">우선순위</th><th class="c">결과</th><th>실제 결과 · 비고</th><th>증적</th></tr></thead>
    <tbody>${allRows}</tbody>
  </table></div>
</section>

<section>
  <div class="closing">
    <p>${esc(concept)}</p>
    <p class="sub">Fail은 결함 등록 대상, Block은 조건을 갖춘 뒤 재실행 대상. <strong>재실행 회차는 새 run_id</strong></p>
  </div>
</section>

<section>
  <h2 id="ssrc"><span class="num">·</span>출처</h2>
  <div class="table-scroll"><table class="src">
    <thead><tr><th class="col-n">#</th><th>자료</th><th>경로</th></tr></thead>
    <tbody>
      <tr><td class="col-n">1</td><td>테스트케이스 엑셀(테스트 베이시스)</td><td class="path">${esc(tc.source || run.source_xlsx || '')}</td></tr>
      <tr><td class="col-n">2</td><td>회차 실행 기록(run.json)</td><td class="path">${esc(path.relative(process.cwd(), path.resolve(a.run)))}</td></tr>
      <tr><td class="col-n">3</td><td>증적 폴더</td><td class="path">evidence/${esc(run.run_id)}/</td></tr>
    </tbody>
  </table></div>
</section>

<footer>
  ${esc(client)} · ${esc(docName)} ${esc(run.run_id)} — ${esc(author)}, ${todayDash}<br>
  본 문서는 내부 검토용이며 외부 배포 시 별도 승인이 필요하다.
</footer>

</div><!-- /doc -->
</div><!-- /layout -->

<a class="totop" href="#top" aria-label="맨 위로">↑</a>

<script>
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.lnb a'));
  var map = {};
  links.forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });
  var heads = Object.keys(map).map(function(id){ return document.getElementById(id); }).filter(Boolean);
  function onScroll(){
    var cur = null;
    for (var i = 0; i < heads.length; i++){ if (heads[i].getBoundingClientRect().top <= 96) cur = heads[i]; }
    if (!cur) cur = heads[0];
    links.forEach(function(a){ a.classList.remove('active'); });
    if (cur && map[cur.id]) map[cur.id].classList.add('active');
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', onScroll);
  onScroll();
})();
</script>
</body>
</html>
`;
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(a.out, html, 'utf8');
console.log(`HTML 리포트 저장: ${a.out} (${(Buffer.byteLength(html) / 1024).toFixed(0)} KB, 스타일 ${cssPath})`);
console.log(`집계 — 전체 ${count.전체} · Pass ${count.Pass} · Fail ${count.Fail} · Block ${count.Block} · 미실행 ${count.미실행}`);
