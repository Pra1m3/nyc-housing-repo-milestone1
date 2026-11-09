import test from 'node:test';
import assert from 'node:assert/strict';
let core;
try { core = await import('../core.js'); } catch { core = {}; }
const available = name => { assert.equal(typeof core[name], 'function', `${name} must be implemented`); return core[name]; };
const data={housing:[[0,2022,0,4,100,0],[0,2022,1,2,50,0],[1,2022,0,2,80,1]],transport:[[0,2022,0,2,1,2],[0,2022,1,8,9,0],[1,2022,1,5,5,0]],housingZip:[[0,2023,0,'10451',1,75,0],[0,2023,0,'10452',1,25,0]],transportZip:[[0,2023,1,'10451',5,5,0],[0,2023,1,'10452',5,5,0]]};
test('search translates borough year housing and severity without confusing nonfatal',()=>{
 const p=available('parseSearch')('Brooklyn 2022 new buildings nonfatal crashes');
 assert.equal(p.borough,'BROOKLYN');assert.deepEqual(p.years,[2022]);assert.equal(p.housingType,'NEW CONSTRUCTION');assert.equal(p.severity,'SEVERE_NONFATAL');
});
test('unknown places, unsupported years and conflicting categories do not silently generate all data',()=>{
 const parse=available('parseSearch');
 assert.throws(()=>parse('London 2022'),/recogniz|understand|unknown/i);
 assert.throws(()=>parse('Brooklyn 2019'),/2022|year/i);
 assert.throws(()=>parse('Brooklyn new construction preservation'),/one|conflict/i);
 assert.deepEqual(parse('Queens 2022-2025').years,[2022,2023,2024,2025]);
});
test('housing and crash categories filter independently and report keeps citywide denominators',()=>{
 const build=available('buildReport');
 const r=build(data,{borough:'BRONX',years:[2022],housingType:'PRESERVATION',severity:'FATAL'});
 assert.equal(r.rows.length,1);assert.equal(r.rows[0].knownUnits,50);assert.equal(r.rows[0].crashes,2);
 const full=build(data,{borough:'BRONX',years:[2022],housingType:'ALL',severity:'ALL'});
 assert.equal(full.housingDenominator,230);assert.equal(full.crashDenominator,15);
 assert.equal(full.rows[0].crashes,10);
});
test('unknown unit values stay unknown and absent records stay null',()=>{
 const r=available('buildReport')(data,{borough:'ALL',years:[2022],housingType:'ALL',severity:'FATAL'});
 const bk=r.rows.find(x=>x.borough==='BROOKLYN');assert.equal(bk.units,null);assert.equal(bk.knownUnits,80);assert.equal(bk.crashes,null);
 const none=core.buildReport(data,{borough:'QUEENS',years:[2025],housingType:'ALL',severity:'ALL'});assert.equal(none.rows.length,0);
});
test('effective ZIP concentration uses matched cells and combines years by ZIP',()=>{
 const r=available('buildReport')(data,{borough:'ALL',years:[2023],housingType:'ALL',severity:'ALL'});
 assert.equal(r.zipPairs.length,2);assert.equal(r.concentration[0].housingEffectiveZips,1.6);assert.equal(r.concentration[0].transportEffectiveZips,2);
});
