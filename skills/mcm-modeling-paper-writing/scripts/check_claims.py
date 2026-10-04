#!/usr/bin/env python3
"""Check declared claim/evidence links, integrity and scope; not an automatic prose grade."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

NEEDS={'validated':{'out_of_sample','independent_validation','analytic_check'},
       'global_optimal':{'optimality_certificate','complete_enumeration'},
       'causal':{'causal_identification'},'significant':{'hypothesis_test'},
       'robust':{'sensitivity','perturbation','scenario_validation'}}
STRENGTHS=set(NEEDS)|{'descriptive','goal','proposal','hypothesis'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


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


def present(value):
    if value is None or isinstance(value,bool):return False
    if isinstance(value,str):return bool(value.strip())
    if isinstance(value,(list,dict)):return bool(value)
    return isinstance(value,(int,float))


def safe(root,value):
    path=(root/value).resolve()
    if not path.is_relative_to(root):raise ValueError('Evidence path escapes work root')
    return path


def check(root,ledger):
    root=Path(root).resolve();errors=[];warnings=[];registry={};rows=[]
    if not isinstance(ledger,dict):return {'status':'FAIL','errors':['Ledger must be an object']}
    if nonfinite(ledger):return {'status':'FAIL','errors':['Ledger contains nonfinite numbers']}
    if not isinstance(ledger.get('freeze_id'),str) or not ledger['freeze_id'].strip():
        return {'status':'FAIL','errors':['Current freeze_id required']}
    evidence=ledger.get('evidence')
    claims=ledger.get('claims')
    if not isinstance(evidence,list) or not isinstance(claims,list) or not claims:
        return {'status':'FAIL','errors':['Nonempty claims and an evidence array required']}
    for entry in evidence:
        try:
            if not isinstance(entry,dict) or not all(isinstance(entry.get(k),str) and entry[k].strip() for k in ['id','file','sha256','type','status','freeze_id']):raise ValueError('Incomplete or malformed evidence')
            if not isinstance(entry['id'],str):raise ValueError('Evidence ID must be a string')
            if not re.fullmatch(r'[0-9a-fA-F]{64}',entry['sha256']):raise ValueError('Evidence SHA-256 must contain 64 hexadecimal digits')
            if entry['id'] in registry:raise ValueError('Duplicate evidence ID '+entry['id'])
            path=safe(root,entry['file'])
            valid=path.is_file() and sha(path)==entry['sha256'].lower() and entry['status']=='PASS' and entry['freeze_id']==ledger.get('freeze_id')
            registry[entry['id']]={**entry,'valid':valid}
        except (ValueError,OSError,TypeError) as exc:errors.append(str(exc))
    seen=set()
    for claim in claims:
        issues=[]
        if not isinstance(claim,dict):errors.append('Non-object claim');continue
        identifier=claim.get('id')
        if not isinstance(identifier,str) or not identifier.strip() or identifier in seen:issues.append('Missing/duplicate claim ID')
        if isinstance(identifier,str):seen.add(identifier)
        if not all(isinstance(claim.get(k),str) and claim[k].strip() for k in ['statement','location','strength','scope']):issues.append('Missing statement/location/strength/scope')
        strength=claim.get('strength')
        if not isinstance(strength,str) or strength not in STRENGTHS:issues.append('Unknown claim strength');strength=None
        refs=claim.get('evidence_ids')
        if not isinstance(refs,list):issues.append('Evidence IDs must be an array');refs=[]
        if not all(isinstance(i,str) for i in refs):issues.append('Evidence IDs must be strings');refs=[i for i in refs if isinstance(i,str)]
        reported=claim.get('reported',True)
        if type(reported) is not bool:issues.append('reported must be a boolean')
        if reported:
            if not refs:issues.append('Reported claim has no evidence')
            invalid=[i for i in refs if i not in registry or not registry[i]['valid']]
            if invalid:issues.append('Missing/stale/failed evidence: '+str(invalid))
            types={registry[i]['type'] for i in refs if i in registry and registry[i]['valid']}
            needed=NEEDS.get(strength)
            if needed and not types&needed:issues.append('Claim strength exceeds declared evidence type')
            if strength=='significant' and (not all(isinstance(claim.get(k),str) and claim[k].strip() for k in ['test_method','sample_scope']) or not all(present(claim.get(k)) for k in ['effect_size','threshold'])):
                issues.append('Significance needs test/effect/threshold/sample scope')
            if strength=='robust' and not claim.get('perturbed_factors'):issues.append('Robustness needs actually tested factors/ranges')
        else:
            if strength not in ['goal','proposal','hypothesis']:issues.append('Unreported statement must remain a goal/proposal/hypothesis')
        rows.append({'id':identifier,'status':'FAIL' if issues else 'PASS','issues':issues})
    failed=errors or any(r['status']=='FAIL' for r in rows)
    return {'status':'FAIL' if failed else 'CLAIM_PRECHECK_PASS','errors':errors,'claims':rows,
            'scope':'Checks declared links/hash/scope only. Evidence contents, reasoning and narrative quality still require review.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        root=a.root.resolve();source=safe(root,str(a.ledger));payload=json.loads(source.read_text(),object_pairs_hook=unique_object,parse_constant=reject_constant);result=check(root,payload)
        if a.output:
            target=safe(root,str(a.output))
            if target==source:raise ValueError('Output cannot overwrite ledger')
            targets={safe(root,e['file']) for e in (payload.get('evidence',[]) if isinstance(payload,dict) and isinstance(payload.get('evidence'),list) else []) if isinstance(e,dict) and isinstance(e.get('file'),str)}
            if target in targets:raise ValueError('Output cannot overwrite evidence')
            if target.exists() and any(target.samefile(p) for p in targets|{source} if p.exists()):raise ValueError('Output is a hardlink to an input')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='CLAIM_PRECHECK_PASS' else 1
    except (OSError,ValueError,TypeError,KeyError,RecursionError) as exc:
        print(json.dumps({'status':'ERROR','error':str(exc)},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
