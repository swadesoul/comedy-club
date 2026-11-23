export const RATINGS = Object.freeze(['PG','PG-13','R']);
export const ROOMS = Object.freeze([25,50,100,150,250]);
export const CAST = Object.freeze([
  {id:'marcus',name:'Marcus "Big Truth" Coleman',style:'Observational storytelling',rating:'PG-13'},
  {id:'tasha',name:'Tasha "No Filter" Monroe',style:'Relationships and family',rating:'PG-13'},
  {id:'eddie',name:'Eddie "Sideways" Miller',style:'Dry absurdity',rating:'PG'},
  {id:'jamal',name:'Jamal "Quickfire" Banks',style:'Roast and crowd work',rating:'PG-13'},
  {id:'pearl',name:'Auntie Pearl',style:'Generations and family',rating:'PG'},
  {id:'reggie',name:'Uncle Reggie Brooks',style:'Warm family storytelling',rating:'PG'}
]);
export const DEFAULT_SETTINGS = Object.freeze({
  comedian:'marcus',rating:'PG-13',roomSize:100,durationSeconds:180,
  crowdWork:true,callback:true,roomTone:'intimate',laughIntensity:'natural',
  introSeconds:5,introAudienceSeconds:3.5,locale:'en-US',musicBed:false
});
function assert(condition,message){if(!condition)throw new Error(message);}
export function validateSettings(input={}){
 const s={...DEFAULT_SETTINGS,...input};
 assert(CAST.some(c=>c.id===s.comedian),'Choose an original comedian');
 assert(RATINGS.includes(s.rating),'Invalid rating');
 assert(ROOMS.includes(Number(s.roomSize)),'Invalid room size');
 assert(Number.isInteger(Number(s.durationSeconds)) && +s.durationSeconds>=60 && +s.durationSeconds<=180,'Set 60–180 seconds');
 assert(s.introSeconds===5,'Reuse the approved five-second liner');
 assert(typeof s.introAudienceSeconds==='number' && Number.isFinite(s.introAudienceSeconds) && s.introAudienceSeconds>=1.5 && s.introAudienceSeconds<=8,'Opening audience response must be 1.5-8 seconds after the intro');
 assert(['intimate','warm','lively'].includes(s.roomTone),'Invalid room tone');
 assert(['subtle','natural','lively'].includes(s.laughIntensity),'Invalid laughter profile');
 assert(typeof s.crowdWork==='boolean' && typeof s.callback==='boolean','Invalid audience options');
 return {...s,roomSize:Number(s.roomSize),durationSeconds:Number(s.durationSeconds)};
}
export function createRoutine({title,script,settings={},source='authored',rightsConfirmed=true}){
 assert(typeof title==='string' && title.trim().length>=3 && title.length<=120,'Title must be 3–120 characters');
 assert(typeof script==='string' && script.trim().length>=20 && script.length<=16000,'Routine must be 20–16,000 characters');
 assert(['authored','imported'].includes(source),'Invalid source');
 assert(rightsConfirmed===true,'Rights confirmation required');
 return {title:title.trim(),script:script.trim(),source,rightsConfirmed:true,settings:validateSettings(settings),state:'draft'};
}
export function makeCuePlan(routine){
 const r=createRoutine(routine);
 const max=r.settings.durationSeconds;
 const openingLaugh=r.settings.introAudienceSeconds;
 const speechStart=5+openingLaugh;
 const spoken=max-speechStart;
 assert(spoken>=45,'Time budget insufficient after intro and opening crowd');
 const stages=[
  {id:'liner',at:0,seconds:5,stem:'approved-station-liner',instruction:'Play approved five-second MAESTRO comedy introduction first; no laughter ahead of the announcement'},
  {id:'intro-crowd',at:5,seconds:openingLaugh,stem:'crowd-laughter',instruction:'After the introduction, bring in a spatially diffuse real audience response and decay naturally before the comedian begins'},
  {id:'setup',at:speechStart,seconds:Math.round(spoken*.22),stem:'comedian',instruction:'Enter after the room settles; establish premise and seed'},
  {id:'escalation',at:Math.round(speechStart+spoken*.22),seconds:Math.round(spoken*.33),stem:'comedian',instruction:'Escalate and vary punchlines'},
  {id:'crowd',at:Math.round(speechStart+spoken*.55),seconds:Math.round(spoken*.18),stem:'audience-member',instruction:r.settings.crowdWork?'Audience reply and comedian response; location-linked voice':'Natural group laughter, no forced reply'},
  {id:'callback',at:Math.round(speechStart+spoken*.73),seconds:Math.round(spoken*.21),stem:'comedian',instruction:r.settings.callback?'Return to exact opening seed with surprising payoff':'Build final punchline without mandatory callback'},
  {id:'outro',at:Math.round(speechStart+spoken*.94),seconds:Math.max(0,max-Math.round(speechStart+spoken*.94)),stem:'crowd',instruction:'Applause taper; do not mask the final word'}
 ];
 return {title:r.title,settings:r.settings,stages,requirements:{
  separateStems:['comedian','audience-members','crowd-laughter','club-ambience','approved-station-liner'],
  originalVoicesOnly:true,rightsConfirmed:true,needsListeningReview:true,
  introRule:'Comedy introduction at 0:00, then audience reaction, then comedian when laughter naturally decays; never pre-roll laughter',
  laughRule:'Start after marked punchline word-end; wait for measured laugh decay before next line; automated audience is an acoustic simulation, not a live crowd',
  timingRule:'The planned timestamps are editable targets; actual final audio must be measured and <= durationSeconds',
  callbackMap:r.settings.callback?['seed','reinforcement','return','payoff']:[],
  radioHandoff:'manual approval only',costAuthorization:'not granted'
 }};
}
export function planBatch(routines){
 assert(Array.isArray(routines)&&routines.length>0&&routines.length<=10,'Batch must have 1–10 routines');
 return {kind:'comedy-batch-plan-v1',state:'planned',dispatchAuthorized:false,
  requests:routines.map(makeCuePlan),numberOfRoutines:routines.length,
  guardrails:{maxRoutines:10,externalSpendAuthorized:false,autoPublish:false,stagingRequiresHumanApproval:true,
   unknownProviderOutcome:'stop-and-reconcile'}};
}
