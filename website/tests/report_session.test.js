import test from 'node:test';
import assert from 'node:assert/strict';
let createReportSession;
try { ({createReportSession}=await import('../report-session.js')); } catch {}
test('exportable report is withheld until the matching render completes and concurrent runs are ignored',async()=>{
 assert.equal(typeof createReportSession,'function');
 let release,hold=false,calls=0;
 const session=createReportSession(f=>{calls++;return f;},async()=>{if(hold)await new Promise(resolve=>release=resolve);});
 await session.generate('old');assert.equal(session.report,'old');
 hold=true;const running=session.generate('new');
 assert.equal(session.busy,true);assert.equal(session.report,null);
 assert.equal(await session.generate('ignored'),false);assert.equal(calls,2);
 release();await running;assert.equal(session.report,'new');assert.equal(session.busy,false);
});
test('render failures cannot expose a stale report for export',async()=>{
 assert.equal(typeof createReportSession,'function');
 let fail=false;
 const session=createReportSession(f=>f,async()=>{if(fail)throw new Error('render failed');});
 await session.generate('old');fail=true;await assert.rejects(()=>session.generate('new'),/render failed/);
 assert.equal(session.report,null);assert.equal(session.busy,false);
});
