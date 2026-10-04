#!/usr/bin/env python3
"""Check contract completeness and data boundary consistency; not mathematical proof."""
import argparse
import json
import math
from pathlib import Path


def data_ids(items):
    if not isinstance(items,list):raise ValueError('Data boundary entries must be arrays')
    ids=[]
    for item in items:
        value=item if isinstance(item,str) else item.get('id') if isinstance(item,dict) else None
        if not isinstance(value,str) or not value.strip():raise ValueError('Every data entry needs a nonempty id')
        ids.append(value)
    if len(set(ids))!=len(ids):raise ValueError('Duplicate source id inside boundary')
    return set(ids)


def nonfinite(value):
    if isinstance(value,float):return not math.isfinite(value)
    if isinstance(value,dict):return any(nonfinite(x) for x in value.values())
    if isinstance(value,(list,tuple)):return any(nonfinite(x) for x in value)
    return False


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate JSON key: '+key)
        result[key]=value
    return result


def reject_constant(value):raise ValueError('Nonfinite JSON number: '+value)


def content(value):
    return isinstance(value,(str,list,dict)) and bool(value) and (not isinstance(value,str) or bool(value.strip()))


def validate(data):
    errors=[]
    if not isinstance(data,dict):return {'status':'FAIL','errors':['Contract must be an object']}
    if data.get('status') not in ['DRAFT','FROZEN','STALE']:errors.append('Invalid state')
    frozen=data.get('status')=='FROZEN'
    required=['schema_version','status','freeze_id','task','problem_evidence','allowed_data','variables','assumptions','models','validation_plan','uncertainty','handoffs','limits']
    errors.extend('Missing '+k for k in required if k not in data)
    if type(data.get('schema_version')) is not int or data.get('schema_version')!=1:errors.append('Unsupported schema_version')
    if nonfinite(data):errors.append('Contract contains nonfinite numbers')
    for key in ['problem_evidence','variables','assumptions','models','validation_plan','uncertainty','handoffs','limits']:
        if key in data and not isinstance(data[key],list):errors.append(key+' must be an array')
    task=data.get('task')
    if not isinstance(task,dict):errors.append('task must be an object')
    else:
        if task.get('request') is not None and (not isinstance(task['request'],str) or not task['request'].strip()):errors.append('task request must be text or null in DRAFT')
        for key in ['outputs','acceptance']:
            values=task.get(key)
            if not isinstance(values,list):errors.append('task '+key+' must be an array')
            elif any(not isinstance(x,(str,dict)) or not x or isinstance(x,str) and not x.strip() for x in values):errors.append('Malformed task '+key+' entry')
    if data.get('freeze_id') is not None and (not isinstance(data['freeze_id'],str) or not data['freeze_id'].strip()):errors.append('freeze_id must be nonempty text or null')
    if frozen:
        if not isinstance(data.get('freeze_id'),str) or not data['freeze_id'].strip():errors.append('FROZEN needs freeze_id')
        task=data.get('task',{})
        if not isinstance(task,dict) or not isinstance(task.get('request'),str) or not task['request'].strip() or not task.get('outputs') or not task.get('acceptance'):errors.append('FROZEN task/outputs/acceptance incomplete')
        for key in ['problem_evidence','variables','models','validation_plan']:
            if not isinstance(data.get(key),list) or not data[key]:errors.append('FROZEN '+key+' empty')
    try:
        boundary=data.get('allowed_data',{})
        if not isinstance(boundary,dict):raise ValueError('allowed_data must be an object')
        if any(k not in boundary for k in ['model_inputs','background_only','excluded']):errors.append('Data boundary must declare all three source roles')
        allowed=data_ids(boundary.get('model_inputs',[]));background=data_ids(boundary.get('background_only',[]));excluded=data_ids(boundary.get('excluded',[]))
        if allowed&background or allowed&excluded or background&excluded:errors.append('Conflicting source roles')
        for model in data.get('models',[]) if isinstance(data.get('models'),list) else []:
            if not isinstance(model,dict):errors.append('Non-object model');continue
            used=data_ids(model.get('input_sources',[]))
            if not used<=allowed:errors.append('Model uses non-permitted sources: '+str(sorted(used-allowed)))
            if frozen and 'input_sources' not in model:errors.append('FROZEN model must declare input_sources, including parameter sources')
            if frozen:
                if not isinstance(model.get('model_id'),str) or not model['model_id'].strip() or not all(content(model.get(k)) for k in ['baseline','core']):errors.append('Incomplete frozen model definition')
                outputs=model.get('outputs')
                if not isinstance(outputs,list) or not outputs or not all(content(x) for x in outputs):errors.append('FROZEN model outputs must be a nonempty array')
    except (ValueError,AttributeError,TypeError) as exc:errors.append(str(exc))
    for variable in data.get('variables',[]) if isinstance(data.get('variables'),list) else []:
        if not isinstance(variable,dict) or not all(isinstance(variable.get(k),str) and variable[k].strip() for k in ['name','meaning','unit']) or not all(content(variable.get(k)) for k in ['domain','source']):errors.append('Incomplete variable/unit/domain/source')
    for check in data.get('validation_plan',[]) if isinstance(data.get('validation_plan'),list) else []:
        if not isinstance(check,dict) or not all(isinstance(check.get(k),str) and check[k].strip() for k in ['check','method']) or check.get('expected') is None or check.get('expected')=='':errors.append('Incomplete validation check')
    return {'status':'FAIL' if errors else 'CONTRACT_PRECHECK_PASS','contract_state':data.get('status'),'errors':errors,
            'scope':'Structural/data-boundary check only; units and equations need actual mathematical review.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);a=p.parse_args()
    try:result=validate(json.loads(a.path.read_text(),object_pairs_hook=unique_object,parse_constant=reject_constant))
    except (OSError,ValueError,RecursionError) as exc:result={'status':'FAIL','errors':[str(exc)]}
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['status']=='CONTRACT_PRECHECK_PASS' else 1)
