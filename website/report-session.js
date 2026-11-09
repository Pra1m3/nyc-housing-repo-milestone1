export function createReportSession(build,render,onChange=()=>{}){
 let busy=false,current=null;
 const session={
  get busy(){return busy;},
  get report(){return busy?null:current;},
  async generate(filters){
   if(busy)return false;
   busy=true;onChange(session);
   try{const next=build(filters);await render(next);current=next;return true;}
   catch(error){current=null;throw error;}
   finally{busy=false;onChange(session);}
  }
 };
 return session;
}
