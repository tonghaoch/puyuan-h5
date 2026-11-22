import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { classifyFix, mercator, pointInRing } from '../src/lib/geography.ts'
import { illustratedBearing, projectIllustratedFix } from '../src/lib/illustrated-location.ts'
import registration from '../src/data/illustration-registration.json' with { type: 'json' }

const output = new URL('../artifacts/location-calibration/', import.meta.url)
const read = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'))
const ring = read('../public/geodata/boundary.geojson').features[0].geometry.coordinates[0]
const report = read('../artifacts/location-calibration/park-report.json')
const world = registration.world
const pixel = (coordinate) => {
  const [east, north] = mercator(coordinate)
  return [(east - world[4]) / world[0], (north - world[5]) / world[3]]
}
const outline = ring.map(pixel)
const boundary =
  outline.map(([x, y], index) => `${index ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join('') +
  'Z'
const coverage = []
for (const accuracy of [5, 10, 30]) {
  let parkCells = 0
  let drawnCells = 0
  let mask = ''
  for (let y = 0; y < 1200; y += 5) {
    let start = null
    for (let x = 0; x <= 1400; x += 5) {
      const longitude = (((world[4] + x * world[0]) / 6378137) * 180) / Math.PI
      const latitude = (Math.atan(Math.sinh((world[5] + y * world[3]) / 6378137)) * 180) / Math.PI
      let drawn = false
      if (pointInRing([longitude, latitude], ring)) {
        parkCells++
        const fix = { longitude, latitude, accuracy, timestamp: 0 }
        drawn = classifyFix(fix, ring, 0) === 'inside' && !!projectIllustratedFix(fix)
      }
      if (drawn) {
        drawnCells++
        start ??= x
      } else if (start !== null) {
        mask += `M${start - 2.5} ${y}h${x - start}`
        start = null
      }
    }
  }
  coverage.push({ accuracy, parkCells, drawnCells, fraction: drawnCells / parkCells, mask })
}
const cards = coverage.map(
  ({ accuracy, fraction, mask }) =>
    `<figure><figcaption>设备精度 ${accuracy} 米 · 约 ${(100 * fraction).toFixed(1)}% 园区面积可画约位</figcaption><svg viewBox="0 0 1400 1200" role="img" aria-label="园区位置覆盖"><path fill="#eadbc5" d="${boundary}"/><path fill="none" stroke="#417778" stroke-width="5" d="${mask}"/><path fill="none" stroke="#796844" stroke-width="3" d="${boundary}"/></svg></figure>`,
)
const samples = [...report.checks, ...report.releaseChecks].map((point) => {
  const [longitude, latitude] = point.referenceLonLat
  const fix = { longitude, latitude, accuracy: 10, timestamp: 0 }
  const inside = classifyFix(fix, ring, 0)
  const position = inside === 'inside' ? projectIllustratedFix(fix) : null
  const label = inside !== 'inside' ? '园外或边界不确定' : position ? '手绘约位' : '仅园区小图'
  const bearings = position
    ? Array.from({ length: 73 }, (_, index) => +illustratedBearing(position, 5 * index).toFixed(2))
    : []
  return { name: `${point.id} ${point.label}`, position, bearings, label, latitude, longitude }
})
const rows = samples.map(
  ({ name, latitude, longitude, label }) =>
    `<tr><th>${name}</th><td>${latitude.toFixed(6)}, ${longitude.toFixed(6)}</td><td>${label}</td></tr>`,
)
const scene = readFileSync(
  new URL('../public/art/puyuan-original-scope.webp', import.meta.url),
).toString('base64')
mkdirSync(output, { recursive: true })
writeFileSync(
  new URL('coverage.json', output),
  JSON.stringify(
    coverage.map(({ mask, ...summary }) => summary),
    null,
    2,
  ) + '\n',
)
writeFileSync(
  new URL('coverage.html', output),
  `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>手绘定位 · 实际显示覆盖</title>
<style>body{max-width:980px;margin:auto;padding:16px;background:#faf5e8;color:#302b24;font:16px/1.5 system-ui}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}figure{margin:0}svg{width:100%}td,th{padding:4px;text-align:left;border-bottom:1px solid #decdb2}table{font-size:.86rem}</style>
<h1>哪儿会显示手绘约位？</h1><p>北朝上，青色是实际应用会显示约位的范围。杏色是园区内但不画点的区域。按公开园界每 5 个影像像素采样，面积比例不代表游览路线覆盖率。</p><section>${cards.join('')}</section>
<p>园界 © OpenStreetMap contributors。仅示意是否显示，不包含手机实测。<a href="park-review.html">查看逐点卫星／插画对照</a></p>
<h2>在家模拟</h2><p>选择一个地标，查看设备报告精度为 10 米时，正式定位算法给出的结果。此页不读取你的位置。</p>
<label>模拟地标 <select id="sites">${samples.map(({ name }, index) => `<option value="${index}">${name}</option>`).join('')}</select></label> · <b id="status" role="status"></b>
<p><label>模拟手机朝向 <input id="heading" type="range" min="0" max="360" step="5" value="0"></label> <output id="degrees" for="heading"></output>（0° 北，90° 东）</p>
<svg viewBox="0 0 1520 1240" role="img" aria-label="模拟定位的手绘导览"><image width="1520" height="1240" href="data:image/webp;base64,${scene}"/><g id="marker"><circle id="radius" fill="#416d9938" stroke="#284d70" stroke-width="2" stroke-dasharray="5 4"/><g id="fan" stroke="#fff3d2" stroke-width="2"><path d="M0 0 -17 -29 Q0 -41 17 -29 Z" fill="#386780" fill-opacity=".6"/><path d="M0 -42 6 -31 0 -34 -6 -31 Z" fill="#28475e"/></g><circle r="11" fill="#294760" stroke="#fff3cf" stroke-width="3"/></g></svg>
<table><tr><th>地标</th><th>纬度、经度</th><th>10 米读数</th></tr>${rows.join('')}</table>
<script>const samples=${JSON.stringify(samples)};const sites=document.querySelector('#sites'),marker=document.querySelector('#marker'),heading=document.querySelector('#heading');function update(){const sample=samples[sites.value];document.querySelector('#status').textContent=sample.label;marker.style.display=sample.position?'':'none';heading.disabled=!sample.position;document.querySelector('#degrees').textContent=heading.value+'°';if(sample.position){marker.setAttribute('transform','translate('+sample.position.x+' '+sample.position.y+')');document.querySelector('#radius').setAttribute('r',sample.position.radius);document.querySelector('#fan').setAttribute('transform','rotate('+sample.bearings[heading.value/5]+')')}}sites.onchange=update;heading.oninput=update;update()</script></html>`,
)
console.log(
  coverage
    .map(({ accuracy, fraction }) => `${accuracy} m: ${(100 * fraction).toFixed(1)}%`)
    .join(' · '),
)
