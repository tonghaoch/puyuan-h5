import { readFileSync, writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { createIllustrationProjector } from '../src/lib/illustrated-location.ts'
import { classifyFix, pointInRing } from '../src/lib/geography.ts'

const read = (relative) => JSON.parse(readFileSync(new URL(relative, import.meta.url), 'utf8'))
const baseline = read('../references/geodata/illustration-registration-baseline.json')
const candidate = read('../artifacts/location-calibration/release-07-model.json')
const geometry = read('../artifacts/location-calibration/release-07.json')
const ring = read('../public/geodata/boundary.geojson').features[0].geometry.coordinates[0]
const oldProject = createIllustrationProjector(baseline)
const newProject = createIllustrationProjector(candidate)
const fixAt = (x, y, accuracy) => ({
  longitude: (((baseline.world[4] + baseline.world[0] * x) / 6378137) * 180) / Math.PI,
  latitude:
    (Math.atan(Math.sinh((baseline.world[5] + baseline.world[3] * y) / 6378137)) * 180) / Math.PI,
  accuracy,
  timestamp: 0,
})
const coverage = []
for (const accuracy of [0, 5, 10, 30]) {
  const rows = {
    accuracy,
    stepPx: 5,
    parkSamples: 0,
    oldShown: 0,
    newShown: 0,
    added: [],
    removed: [],
  }
  for (let y = 0; y < 1200; y += 5) {
    for (let x = 0; x < 1400; x += 5) {
      const fix = fixAt(x, y, accuracy)
      if (!pointInRing([fix.longitude, fix.latitude], ring)) continue
      rows.parkSamples++
      const inside = classifyFix(fix, ring, 0) === 'inside'
      const before = inside && !!oldProject(fix)
      const after = inside && !!newProject(fix)
      rows.oldShown += Number(before)
      rows.newShown += Number(after)
      if (after && !before) rows.added.push([x, y])
      if (before && !after) rows.removed.push([x, y])
    }
  }
  if (rows.added.length)
    throw Error(`Release widened unverified visibility at accuracy ${accuracy}`)
  coverage.push(rows)
}
const checks = geometry.checks.map((point) => {
  const fix = fixAt(...point.satellitePx, 10)
  const status = classifyFix(fix, ring, 0)
  const before = status === 'inside' ? oldProject(fix) : null
  const after = status === 'inside' ? newProject(fix) : null
  if (before && !after) throw Error(`Previously visible check disappeared: ${point.id}`)
  return {
    id: point.id,
    status,
    oldPosition: before,
    newPosition: after,
    oldGeometryM: point.current.meters,
    newGeometryM: point.trial.meters,
  }
})
const result = {
  purpose:
    'Runtime visibility audit on every sampled park point and all retained checks; availability is not accuracy.',
  baselineSha256: geometry.baselineSha256,
  candidateSha256: createHash('sha256')
    .update(
      readFileSync(
        new URL('../artifacts/location-calibration/release-07-model.json', import.meta.url),
      ),
    )
    .digest('hex'),
  coverage,
  checks,
}
if (result.candidateSha256 !== geometry.candidateSha256)
  throw Error('Candidate model and geometry report differ')
writeFileSync(
  new URL('../artifacts/location-calibration/release-07-runtime.json', import.meta.url),
  JSON.stringify(result, null, 2) + '\n',
)
for (const row of coverage)
  console.log(
    `${row.accuracy}m: ${row.oldShown} → ${row.newShown}/${row.parkSamples}, added ${row.added.length}, removed ${row.removed.length}`,
  )
console.log('All retained checks inspected; every previously visible check remains visible.')
