/**
 * Comedy Club draft station handoff. Pure eligibility checks; NO network side effects.
 * Actual station inventory must originate in authenticated MAESTRO backend after
 * tenant, user role, station plan and content policy enforcement.
 */
export const RATING_RANK = Object.freeze({'PG':0,'PG-13':1,'R':2});
export function eligibleStations({stations, rating, ownerId}){
 if(!Array.isArray(stations) || !Object.hasOwn(RATING_RANK,rating) || !ownerId) return [];
 return stations.filter(s=>{
  if(!s || typeof s.id!=='string' || !s.id.trim())return false;
  if(!s.can_stage_comedy || !s.can_upload || !s.entitlement_active)return false;
  if(s.owner_id!==ownerId && !s.delegated_comedy_publish)return false;
  if(!Object.hasOwn(RATING_RANK,s.max_rating))return false;
  if(RATING_RANK[rating]>RATING_RANK[s.max_rating])return false;
  if(rating==='R' && !(s.adult_content_enabled && s.age_gate_verified))return false;
  return true;
 });
}
export function planStationHandoff({routine,station,ownerId,approved=false,rightsConfirmed=false}){
 if(!approved || !rightsConfirmed) throw new Error('Approved audio and confirmed rights are required');
 if(!routine || !routine.title || !routine.settings || !routine.settings.rating) throw new Error('Valid routine required');
 if(!eligibleStations({stations:[station],rating:routine.settings.rating,ownerId}).length) throw new Error('Station not authorized or rating incompatible');
 return {
  kind:'comedy-maestro-handoff-v1', state:'staging_request_only',
  routine_title:routine.title,station_id:station.id,requested_rating:routine.settings.rating,
  note:'Backend must recheck fresh station ACL, ownership, rights, reviewed audio and entitlements before upload. No automatic airtime.',
  scheduling:'manual_or_existing_authorized_rule_only',
  dispatchAuthorized:false
 };
}
