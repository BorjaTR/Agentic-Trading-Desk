"""Pure UTC population metadata resolution, staged for labcore.population.

No filesystem/store access, value decoding, event filtering, or wave computation.
Document source hashes are verified by the caller/CLI; payload hashes are also
included so the cache identity binds the actual in-memory metadata.
"""
import datetime as dt
import hashlib
import json
import re
from collections.abc import Mapping

API_VERSION='2.0-candidate'
UTC=dt.timezone.utc

class PopulationError(ValueError):
 def __init__(self,code,detail=''):
  self.code=code;self.detail=detail
  super().__init__(code+(':'+detail if detail else ''))

def _require(condition,code,detail=''):
 if not condition:raise PopulationError(code,detail)

def canonical_json(value):
 return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)

def _digest(value):return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()

def _clone(value,code):
 try:return json.loads(canonical_json(value))
 except (TypeError,ValueError) as error:raise PopulationError(code) from error

def _document(value,name):
 _require(isinstance(value,Mapping),'MALFORMED_DOCUMENT',name)
 source=value.get('source_sha256')
 _require(isinstance(source,str) and bool(re.fullmatch('[0-9a-fA-F]{64}',source)),'INVALID_SOURCE_HASH',name)
 data=_clone(value.get('data'),'MALFORMED_DOCUMENT')
 _require(isinstance(data,dict),'MALFORMED_DOCUMENT',name)
 return data,{'source_sha256':source.lower(),'payload_sha256':_digest(data)}

def _date(value):
 _require(isinstance(value,str),'MALFORMED_DATE')
 try:
  if re.fullmatch(r'\d{8}',value):return dt.datetime.strptime(value,'%Y%m%d').date()
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):return dt.date.fromisoformat(value)
 except ValueError as error:raise PopulationError('MALFORMED_DATE',value) from error
 raise PopulationError('MALFORMED_DATE',value)

def _day(value):return value.strftime('%Y%m%d')

def _range(first,last):
 first,last=_date(first),_date(last)
 _require(first<=last,'REVERSED_RANGE')
 return first,last

def _days(first,last):
 day=first
 while day<=last:
  yield day;day+=dt.timedelta(days=1)

def _coins(value,canonical,allow_all=False):
 if isinstance(value,str):
  if allow_all and value.strip().lower()=='all':return sorted(canonical)
  values=value.split(',')
 else:
  _require(isinstance(value,(list,tuple,set,frozenset)),'MALFORMED_COINS')
  values=list(value)
 _require(all(isinstance(c,str) and c.strip() for c in values),'MALFORMED_COINS')
 normalized=sorted({c.strip().upper() for c in values});unknown=set(normalized)-canonical
 _require(not unknown,'UNKNOWN_COIN',','.join(sorted(unknown)))
 return normalized

def _policy(value,first,last):
 _require(isinstance(value,Mapping),'MALFORMED_POLICY');policy=_clone(value,'MALFORMED_POLICY')
 _require(isinstance(policy.get('version'),str) and bool(policy['version'].strip()),'POLICY_VERSION_REQUIRED')
 _require(policy.get('timezone')=='UTC','UNSUPPORTED_TIMEZONE')
 allowed_first,allowed_last=_range(policy.get('allowed_first'),policy.get('allowed_last'))
 protected=policy.get('protected',[]);_require(isinstance(protected,list),'MALFORMED_POLICY')
 for interval in protected:
  _require(isinstance(interval,dict),'MALFORMED_POLICY');a,b=_range(interval.get('first'),interval.get('last'))
  _require(last<a or first>b,'PROTECTED_DATE',_day(a)+'..'+_day(b))
 _require(allowed_first<=first<=last<=allowed_last,'OUTSIDE_POLICY')
 return policy

def _roster(value):
 data,identity=_document(value,'roster');coins=data.get('coins')
 _require(isinstance(coins,list) and all(isinstance(c,str) and c and c==c.strip().upper() for c in coins),'MALFORMED_ROSTER')
 _require(len(coins)==len(set(coins)),'DUPLICATE_CANONICAL_MEMBER')
 availability=data.get('availability',{});_require(isinstance(availability,dict),'MALFORMED_ROSTER_COVERAGE')
 present={}
 for coin in coins:
  info=availability.get(coin)
  if info is None:present[coin]=None;continue
  _require(isinstance(info,dict) and isinstance(info.get('days'),list),'MALFORMED_ROSTER_COVERAGE',coin)
  dates={_day(_date(d)) for d in info['days']}
  if dates:
   if info.get('first') is not None:_require(_day(_date(info['first']))==min(dates),'MALFORMED_ROSTER_COVERAGE',coin)
   if info.get('last') is not None:_require(_day(_date(info['last']))==max(dates),'MALFORMED_ROSTER_COVERAGE',coin)
  present[coin]=dates
 source_days={_day(_date(d)) for d in data.get('source_days',[])}
 sources=data.get('source_sha256',{});_require(isinstance(sources,dict),'MALFORMED_ROSTER_SOURCES')
 for path in sources:
  match=re.search(r'(?:^|/)day=(\d{8})(?:/|$)',path)
  if match:source_days.add(_day(_date(match.group(1))))
 return set(coins),present,source_days,identity

def _groups(value,canonical):
 data,identity=_document(value,'groups')
 _require(type(data.get('schema_version')) is int and data['schema_version']==1,'UNSUPPORTED_GROUP_SCHEMA')
 _require(isinstance(data.get('version'),str) and bool(data['version'].strip()),'GROUP_VERSION_REQUIRED')
 _require(data.get('timezone')=='UTC','UNSUPPORTED_TIMEZONE')
 definitions=data.get('groups');_require(isinstance(definitions,dict),'MALFORMED_GROUPS')
 normalized={}
 for name,segments in definitions.items():
  _require(isinstance(name,str) and bool(name.strip()) and name==name.strip(),'MALFORMED_GROUP_NAME')
  _require(isinstance(segments,list),'MALFORMED_GROUP_INTERVAL',name);out=[]
  for segment in segments:
   _require(isinstance(segment,dict) and set(segment)=={'first','last','coins'},'MALFORMED_GROUP_INTERVAL',name)
   _require(isinstance(segment['coins'],list),'MALFORMED_GROUP_MEMBERS',name)
   a,b=_range(segment['first'],segment['last']);members=_coins(segment['coins'],canonical)
   out.append({'first':_day(a),'last':_day(b),'coins':members})
  out.sort(key=lambda x:(x['first'],x['last']))
  for previous,current in zip(out,out[1:]):_require(previous['last']<current['first'],'GROUP_INTERVAL_OVERLAP',name)
  normalized[name]=out
 return normalized,data['version'],identity

def _intervals(daily):
 out=[]
 for day,members,status in daily:
  stamp=_day(day)
  if out and out[-1]['coins']==members and out[-1]['membership_status']==status and _date(out[-1]['last'])+dt.timedelta(days=1)==day:out[-1]['last']=stamp
  else:out.append({'first':stamp,'last':stamp,'coins':list(members),'membership_status':status})
 return out

def _presence(daily,present,source_days):
 members=sorted({coin for _,coins,_ in daily for coin in coins});out=[]
 for coin in members:
  previous=None
  for day,coins,_ in daily:
   if coin not in coins:previous=None;continue
   stamp=_day(day);known=present[coin]
   if known is None:status,reason='COVERAGE_NOT_SUPPLIED','MEMBER_DAY_METADATA_NOT_SUPPLIED'
   elif stamp in known:status,reason='PRESENT_IN_ROSTER_METADATA','CANONICAL_MEMBER_ON_DECLARED_SOURCE_DAY'
   elif stamp in source_days:status,reason='ABSENT_FROM_ROSTER_METADATA','NOT_LISTED_IN_DECLARED_SOURCE_INDEX'
   else:status,reason='SOURCE_METADATA_NOT_PROVIDED','NO_DECLARED_ROSTER_INDEX_FOR_DATE'
   if previous is not None and previous['status']==status and previous['reason']==reason and _date(previous['last'])+dt.timedelta(days=1)==day:previous['last']=stamp
   else:
    previous={'coin':coin,'first':stamp,'last':stamp,'status':status,'reason':reason};out.append(previous)
 return out

def resolve_population(request,roster_document,*,policy,groups_document=None,coverage_document=None,population_reference=None):
 """Resolve declared UTC member windows and metadata coverage without I/O.

 Roster/group/coverage documents: ``{'data': decoded_dict,
 'source_sha256': caller_verified_file_hash}``. The policy and upstream
 reference are caller-owned metadata. Coverage describes roster presence only;
 consumer coverage is reported only when explicitly supplied by that consumer.
 """
 _require(isinstance(request,Mapping),'MALFORMED_REQUEST');q=_clone(request,'MALFORMED_REQUEST')
 _require(not set(q)-{'coins','group','start','end','timezone','endpoints'},'UNKNOWN_REQUEST_FIELD')
 has_coins=q.get('coins') is not None;has_group=q.get('group') is not None
 _require(has_coins!=has_group,'EXACTLY_ONE_SELECTION')
 _require(q.get('timezone')=='UTC','UNSUPPORTED_TIMEZONE')
 _require(q.get('endpoints','date_inclusive')=='date_inclusive','UNSUPPORTED_ENDPOINTS')
 first,last=_range(q.get('start'),q.get('end'));normalized_policy=_policy(policy,first,last)
 _require(last<dt.date.max,'UNREPRESENTABLE_END_BOUNDARY')
 canonical,present,source_days,roster_identity=_roster(roster_document);group_identity=None;selected_group_hash=None
 if has_coins:
  members=_coins(q['coins'],canonical,True);daily=[(day,members,'DEFINED') for day in _days(first,last)];selection={'mode':'coins','coins':members}
 else:
  _require(isinstance(q['group'],str) and bool(q['group'].strip()),'MALFORMED_GROUP_NAME');name=q['group'].strip()
  _require(groups_document is not None,'GROUP_DOCUMENT_REQUIRED');groups,version,group_identity=_groups(groups_document,canonical)
  _require(name in groups,'UNKNOWN_GROUP',name);definition=groups[name];selected_group_hash=_digest({'version':version,'timezone':'UTC','name':name,'intervals':definition});daily=[]
  for day in _days(first,last):
   stamp=_day(day);segment=next((x for x in definition if x['first']<=stamp<=x['last']),None)
   daily.append((day,segment['coins'] if segment else [],'DEFINED' if segment else 'GROUP_NOT_EFFECTIVE'))
  selection={'mode':'group','group':name,'group_version':version}
 intervals=_intervals(daily);members=sorted({coin for _,coins,_ in daily for coin in coins})
 coverage={'canonical_roster':_presence(daily,present,source_days),'source':{'status':'NOT_SUPPLIED'}}
 coverage_identity=None
 if coverage_document is not None:
  supplied,coverage_identity=_document(coverage_document,'coverage');coverage['source']={'status':'SUPPLIED_METADATA','identity':coverage_identity,'metadata':supplied}
 start=dt.datetime.combine(first,dt.time.min,UTC);exclusive=dt.datetime.combine(last+dt.timedelta(days=1),dt.time.min,UTC)
 core={'schema_version':2,'api_version':API_VERSION,'status':'RESOLVED' if members else 'EMPTY_MEMBERSHIP','requested':{**selection,'first':_day(first),'last':_day(last),'timezone':'UTC','endpoints':'date_inclusive','start_utc':start.strftime('%Y-%m-%dT%H:%M:%SZ'),'end_exclusive_utc':exclusive.strftime('%Y-%m-%dT%H:%M:%SZ')},'resolved':{'members':members,'intervals':intervals},'coverage':coverage,'identity':{'roster':roster_identity,'groups':group_identity,'selected_group_sha256':selected_group_hash,'policy_sha256':_digest(normalized_policy),'consumer_coverage':coverage_identity,'population_reference_sha256':_digest(population_reference)},'population_reference':_clone(population_reference,'MALFORMED_POPULATION_REFERENCE'),'diagnostics':{'group_gaps':[x for x in intervals if x['membership_status']=='GROUP_NOT_EFFECTIVE'],'coverage_meaning':'Canonical roster-index presence only; no listing inference, event count, price/outcome availability or value decoding','library_io':'NONE'}}
 return {**core,'cache_key':_digest(core)}
