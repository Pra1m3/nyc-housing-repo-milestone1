import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildReport,DEFAULTS,BOROUGHS,TYPES,SEVERITIES,toCSV} from '../core.js';
const data=JSON.parse(readFileSync(new URL('../data/nyc.json',import.meta.url),'utf8'));
test('default website data reproduce the validated Member3 analysis',()=>{
 const r=buildReport(data);assert.deepEqual(r.totals,{housing:103912,crashes:11921,missingUnits:2,matchedCells:20});assert.equal(r.zipPairs.length,306);
 assert.ok(Math.abs(r.shares.reduce((s,v)=>s+v.housingShare,0)-1)<1e-12);
 assert.ok(Math.abs(r.concentration[0].housingEffectiveZips-11.84547615899515)<1e-10);
 assert.ok(r.concentration.every(v=>v.housingEffectiveZips<v.transportEffectiveZips));
 assert.ok(!r.rows.some(v=>v.year===2026));assert.ok(toCSV(r.rows).includes('"BRONX","2024","9800",,"1"'));
});
test('every offered dropdown combination yields finite nullable measures and unique rows',()=>{
 for(const borough of ['ALL',...BOROUGHS])for(const year of [2022,2023,2024,2025,2026])for(const housingType of ['ALL',...TYPES])for(const severity of ['ALL',...SEVERITIES]){
  const r=buildReport(data,{borough,years:[year],housingType,severity});
  assert.equal(new Set(r.rows.map(v=>`${v.borough}|${v.year}`)).size,r.rows.length);
  for(const row of r.rows)for(const [key,value] of Object.entries(row))if(typeof value==='number')assert.ok(Number.isFinite(value),key);
  if(year===2022||year===2026)assert.equal(r.zipPairs.length,0);
 }
});
