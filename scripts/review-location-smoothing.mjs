import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { createLocationSmoother, fixDistance } from '../src/lib/location-smoothing.ts'

const input = new URL('../references/geodata/device-filter-trial-06.json', import.meta.url)
const fixtureBytes = readFileSync(input)
const spec = JSON.parse(fixtureBytes)
const radius = 6378137
const radians = Math.PI / 180
function coordinate(x, y, timestamp, accuracy) {
  return {
    longitude: spec.origin[0] + x / (radius * Math.cos(spec.origin[1] * radians)) / radians,
    latitude: spec.origin[1] + y / radius / radians,
    timestamp,
    accuracy,
  }
}
function local(fix) {
  return [
    (fix.longitude - spec.origin[0]) * radians * radius * Math.cos(spec.origin[1] * radians),
    (fix.latitude - spec.origin[1]) * radians * radius,
  ]
}
function summary(rows, key) {
  const errors = rows.map((row) => row[key].errorM)
  return {
    samples: rows.length,
    missing: 0,
    below10: errors.filter((error) => error < 10).length,
    atLeast10: errors.filter((error) => error >= 10).length,
    rmsM: Math.sqrt(errors.reduce((sum, error) => sum + error ** 2, 0) / errors.length),
    maxM: Math.max(...errors),
  }
}
const cases = spec.scenarios.map((scenario) => {
  let randomState = scenario.seed
  const random = () => {
    randomState = (Math.imul(randomState, 1664525) + 1013904223) >>> 0
    return randomState / 4294967296
  }
  const smoother = createLocationSmoother()
  const times =
    scenario.timesMs ??
    Array.from(
      { length: scenario.knots.at(-1)[0] / spec.samplePeriodMs + 1 },
      (_, index) => index * spec.samplePeriodMs,
    )
  const rows = times.map((time, index) => {
    const endIndex = scenario.knots.findIndex((knot) => knot[0] >= time)
    const end = scenario.knots[endIndex]
    const start = scenario.knots[Math.max(0, endIndex - 1)]
    const fraction = end[0] === start[0] ? 0 : (time - start[0]) / (end[0] - start[0])
    const truthXY = [1, 2].map((axis) => start[axis] + (end[axis] - start[axis]) * fraction)
    const noise = [random(), random()].map((value) => (value * 2 - 1) * scenario.noiseM)
    const xy = truthXY.map(
      (value, axis) =>
        value +
        noise[axis] +
        (scenario.biasM?.[axis] ?? 0) +
        (scenario.spike?.index === index ? scenario.spike.offsetM[axis] : 0),
    )
    const truth = coordinate(...truthXY, time, 0)
    const raw = coordinate(...xy, time, scenario.accuracyM)
    const filtered = smoother.update(raw)
    return {
      timeMs: time,
      truthXY,
      raw: { ...raw, xy, errorM: fixDistance(raw, truth) },
      filtered: { ...filtered, xy: local(filtered), errorM: fixDistance(filtered, truth) },
      adjustmentM: fixDistance(raw, filtered),
    }
  })
  return {
    id: scenario.id,
    label: scenario.label,
    rows,
    raw: summary(rows, 'raw'),
    filtered: summary(rows, 'filtered'),
    maxAdjustmentM: Math.max(...rows.map((row) => row.adjustmentM)),
  }
})
const report = {
  purpose: spec.purpose,
  fixtureSha256: createHash('sha256').update(fixtureBytes).digest('hex'),
  implementationSha256: createHash('sha256')
    .update(readFileSync(new URL('../src/lib/location-smoothing.ts', import.meta.url)))
    .digest('hex'),
  calibrationSha256: createHash('sha256')
    .update(readFileSync(new URL('../src/data/illustration-registration.json', import.meta.url)))
    .digest('hex'),
  cases,
}
const output = new URL('../artifacts/location-calibration/', import.meta.url)
mkdirSync(output, { recursive: true })
writeFileSync(new URL('device-filter-06.json', output), JSON.stringify(report, null, 2) + '\n')
const payload = JSON.stringify(report).replaceAll('<', '\\u003c')
const html = `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>定位读数 · 在家模拟对照</title><style>body{max-width:1050px;margin:auto;padding:18px;background:#faf5e8;color:#302b24;font:16px system-ui}select,button{font:inherit;padding:8px}table{border-collapse:collapse;width:100%;margin:18px 0}th,td{text-align:left;padding:6px;border-bottom:1px solid #d6ccba}svg{width:100%;background:white;border-radius:8px}section{display:flex;gap:16px}figure{margin:0;flex:1;min-width:0}input{width:100%}.bad{color:#a52828}@media(max-width:650px){section{display:block}figure{margin:14px 0}table{font-size:13px}}</style>
<h1>手机读数：原始 / 平滑</h1><p>全部数据为合成轨迹，不读取手机位置。绿色为设定的真实路线，灰色为原始读数，靛蓝为应用平滑结果。时间滑块可以检查起步、转弯和跳点。置信圈保留设备报告范围，并补上平滑位移；没有声称范围变小。</p>
<p>这里比较设备读数处理，不包含手绘图配准或底图绝对误差。持续偏移和单次大跳点仍保留在分母，模拟小于 10 米不能证明全园实测小于 10 米。</p>
<select id="scenario" aria-label="模拟轨迹"></select><button id="play">播放</button><input id="time" type="range" min="0" value="0" step="1" aria-label="读数时刻"><p id="current"></p>
<section><figure><figcaption>原始读数</figcaption><svg id="raw" viewBox="0 0 480 340"></svg></figure><figure><figcaption>应用平滑</figcaption><svg id="filtered" viewBox="0 0 480 340"></svg></figure></section>
<table><thead><tr><th>轨迹</th><th>RMS 原始 → 平滑</th><th>最大误差 原始 → 平滑</th><th>平滑 ≥10 米 / 全部</th></tr></thead><tbody id="table"></tbody></table>
<p>即使一串读数完全相同，真实位置也可能不同。持续系统偏差无法由这些读数推断；把一次大变化直接删掉，也可能删掉一条正确的新位置。应用只修正邻近读数的小幅抖动，大变化和间断采样立即采用新读数，不把人吸到道路上。</p>
<script>const report=${payload};
const select=document.querySelector('#scenario'),slider=document.querySelector('#time');let timer;
for(const c of report.cases){const option=document.createElement('option');option.value=c.id;option.textContent=c.label;select.append(option)}
document.querySelector('#table').innerHTML=report.cases.map(c=>'<tr><td>'+c.label+'</td><td>'+c.raw.rmsM.toFixed(2)+' → '+c.filtered.rmsM.toFixed(2)+' 米</td><td>'+c.raw.maxM.toFixed(2)+' → '+c.filtered.maxM.toFixed(2)+' 米</td><td class="'+(c.filtered.atLeast10?'bad':'')+'">'+c.filtered.atLeast10+' / '+c.filtered.samples+'</td></tr>').join('');
function draw(){const c=report.cases.find(c=>c.id===select.value),row=c.rows[Number(slider.value)];
const points=c.rows.flatMap(r=>[r.truthXY,r.raw.xy,r.filtered.xy]);const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
const minX=Math.min(...xs)-10,maxX=Math.max(...xs)+10,minY=Math.min(...ys)-10,maxY=Math.max(...ys)+10;
const scale=Math.min(440/(maxX-minX),300/(maxY-minY)),px=p=>[20+(p[0]-minX)*scale,320-(p[1]-minY)*scale];
const line=pts=>pts.map((p,i)=>(i?'L':'M')+px(p).join(',')).join(' ');
for(const key of ['raw','filtered']){const pos=px(row[key].xy),truth=px(row.truthXY);document.querySelector('#'+key).innerHTML='<path d="'+line(c.rows.map(r=>r.truthXY))+'" fill="none" stroke="#32865c" stroke-width="3"/><path d="'+line(c.rows.slice(0,Number(slider.value)+1).map(r=>r[key].xy))+'" fill="none" stroke="'+(key==='raw'?'#858585':'#3d417a')+'" stroke-width="2"/><circle cx="'+pos[0]+'" cy="'+pos[1]+'" r="'+row[key].accuracy*scale+'" fill="#4b518715" stroke="#4b518755"/><circle cx="'+pos[0]+'" cy="'+pos[1]+'" r="5" fill="#3d417a"/><circle cx="'+truth[0]+'" cy="'+truth[1]+'" r="4" fill="#32865c"/><text x="15" y="20">'+row[key].errorM.toFixed(2)+' 米；同一尺度</text>'}
document.querySelector('#current').textContent=(row.timeMs/1000).toFixed(1)+' 秒 · 本次平滑位移 '+row.adjustmentM.toFixed(2)+' 米 · 两图使用同一比例';}
function choose(){clearInterval(timer);timer=undefined;document.querySelector('#play').textContent='播放';const c=report.cases.find(c=>c.id===select.value);slider.max=c.rows.length-1;slider.value=0;draw()}
select.onchange=choose;slider.oninput=draw;document.querySelector('#play').onclick=()=>{if(timer){clearInterval(timer);timer=undefined;document.querySelector('#play').textContent='播放';return}document.querySelector('#play').textContent='暂停';timer=setInterval(()=>{if(Number(slider.value)>=Number(slider.max))slider.value=0;else slider.value=Number(slider.value)+1;draw()},350)};choose();</script></html>`
writeFileSync(new URL('device-filter-06.html', output), html)
for (const c of cases)
  console.log(
    `${c.id}: RMS ${c.raw.rmsM.toFixed(2)} → ${c.filtered.rmsM.toFixed(2)}m; max ${c.raw.maxM.toFixed(2)} → ${c.filtered.maxM.toFixed(2)}m; >=10 ${c.filtered.atLeast10}/${c.filtered.samples}`,
  )
