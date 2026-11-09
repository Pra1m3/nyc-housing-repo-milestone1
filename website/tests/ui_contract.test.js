import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
test('form controls cannot shadow native reset and submit methods',()=>{
 const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
 const form=html.match(/<form\b[\s\S]*?<\/form>/)[0];
 assert.doesNotMatch(form,/(?:id|name)="(?:reset|submit)"/);
});
