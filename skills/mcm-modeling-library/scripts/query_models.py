#!/usr/bin/env python3
"""Search supplied model knowledge; never open original private materials."""
import argparse
import json
import math
import re
from pathlib import Path

HINTS={'optimization':['优化','规划','约束','容量','资源','目标函数','整数'],
       'discrete':['图','路径','网络流','背包','动态规划','组合'],
       'evaluation':['评价','排名','排序','权重','指标'],
       'statistics':['回归','检验','置信','关联','分布','统计','效应'],
       'time-series':['时间序列','时序','季节','预测未来','波动'],
       'machine-learning':['分类','聚类','学习','神经网络','特征','识别'],
       'mechanisms':['微分','守恒','机理','热方程','生态','动力'],
       'simulation':['仿真','模拟','排队','随机过程','蒙特卡洛','马尔可夫'],
       'inverse':['反演','隐变量','校准','逆问题','病态','可识别'],
       'numerical':['插值','求根','积分','数值','线性代数'],
       'signals-images':['信号','图像','频谱','滤波','几何','小波'],
       'games':['博弈','联盟','策略','合作','竞争'],
       'control':['控制','反馈','卡尔曼','稳定','状态估计']}


def normalize(text):return re.sub(r'[^a-z0-9\u4e00-\u9fff]+','',text.lower())


def validate_cards(cards):
    if not isinstance(cards,list):raise ValueError('Catalog cards must be an array')
    seen=set()
    for card in cards:
        if not isinstance(card,dict):raise ValueError('Each catalog card must be an object')
        if nonfinite(card):raise ValueError('Card contains nonfinite numbers')
        for key in ['id','name','purpose','family','kind','knowledge_level']:
            if not isinstance(card.get(key),str) or not card[key].strip():raise ValueError('Card needs a nonempty '+key)
        if card['id'] in seen:raise ValueError('Duplicate model id: '+card['id'])
        seen.add(card['id'])
        if card['family'] not in HINTS:raise ValueError('Unknown card family: '+card['family'])
        if card['kind'] not in ['model','method','solver','auxiliary']:raise ValueError('Unknown card kind')
        if card['knowledge_level'] not in ['INDEXED_ONLY','THEORY_GUIDE_REVIEWED','REFERENCE_IMPL_TESTED','REAL_CASE_REPRODUCED']:raise ValueError('Unknown knowledge level')
        for key in ['aliases','assumptions']:
            values=card.get(key,[])
            if not isinstance(values,list) or not all(isinstance(x,str) and x.strip() for x in values):raise ValueError(key+' must be an array of nonempty strings')


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


def search(cards,query='',family=None,identifier=None,limit=10):
    validate_cards(cards)
    if not isinstance(query,str):raise ValueError('Query must be a string')
    if family is not None and family not in HINTS:raise ValueError('Unknown selected family')
    if type(limit) is not int or not 1<=limit<=1000:raise ValueError('limit must be 1..1000')
    if identifier is not None:
        if not isinstance(identifier,str) or not identifier.strip():raise ValueError('Model id must be a nonempty string')
        result=[c for c in cards if c['id']==identifier]
        if not result:raise ValueError('Unknown model id: '+identifier)
        if family and result[0]['family']!=family:raise ValueError('Model id conflicts with selected family')
        return result
    query=query.strip(); nq=normalize(query); terms=re.findall(r'[a-zA-Z][a-zA-Z0-9_-]*',query.lower())
    scored=[]
    for card in cards:
        if family and card['family']!=family:continue
        names=[card['name'],card['id']]+card.get('aliases',[])
        score=0
        if not query:score=1
        else:
            for name in names:
                nn=normalize(name)
                if nq==nn:score=max(score,100)
                elif nq and nn and nq in nn:score=max(score,70)
                elif len(nn)>=2 and nn in nq:score=max(score,60)
            body=normalize(' '.join(names+[card['purpose'],' '.join(card['assumptions'])]))
            if nq and nq in body:score=max(score,35)
            score+=sum(8 for term in terms if normalize(term) in body)
            score+=sum(4 for hint in HINTS.get(card['family'],[]) if hint in query)
        if score:scored.append((score,card))
    return [c for score,c in sorted(scored,key=lambda pair:(-pair[0],pair[1]['id']))[:limit]]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--catalog',type=Path,default=Path(__file__).resolve().parents[1]/'assets/catalog.json')
    p.add_argument('--query',default='');p.add_argument('--family',choices=list(HINTS));p.add_argument('--id');p.add_argument('--limit',type=int,default=10);p.add_argument('--full',action='store_true');a=p.parse_args()
    if not 1<=a.limit<=1000:p.error('limit must be 1..1000')
    try:
        payload=json.loads(a.catalog.read_text(),object_pairs_hook=unique_object,parse_constant=reject_constant)
        if not isinstance(payload,dict) or 'cards' not in payload:raise ValueError('Catalog must be an object with cards')
        cards=payload['cards'];result=search(cards,a.query,a.family,a.id,a.limit)
        if not a.full:result=[{k:c[k] for k in ['id','name','family','kind','knowledge_level','purpose']} for c in result]
        print(json.dumps({'status':'MATCHES' if result else 'NO_MATCH','results':result,'note':'Matches are candidate knowledge, not a suitability or correctness verdict.'},ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'ERROR','error':str(exc)},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
