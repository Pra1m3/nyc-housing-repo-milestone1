import {mkdir,copyFile,cp,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist',{recursive:true});
for(const file of ['index.html','styles.css','app.js','core.js','report-session.js','icon.svg'])await copyFile(file,`dist/${file}`);
await cp('data','dist/data',{recursive:true});
console.log('Static production output ready in dist/');
