#!/usr/bin/env python3
"""Search supplied model knowledge; never open original private materials."""
import argparse
import json
import math
import re
from pathlib import Path

HINTS={'optimization':['优化','规划','约束','容量','资源','目标函数','整数',
                       'optimization','constraint','capacity','resource','allocation','integer','binary'],
       'discrete':['图','路径','网络流','背包','动态规划','组合',
                   'graph','path','network flow','knapsack','dynamic programming','combinatorial'],
       'evaluation':['评价','排名','排序','权重','指标','evaluation','ranking','weight','criterion'],
       'statistics':['回归','检验','置信','关联','分布','统计','效应',
                     'regression','hypothesis test','confidence','association','distribution','statistics'],
       'time-series':['时间序列','时序','季节','预测未来','波动',
                      'time series','forecast','forecasting','seasonal','volatility'],
       'machine-learning':['分类','聚类','学习','神经网络','特征','识别',
                           'classification','clustering','machine learning','neural network','feature'],
       'mechanisms':['微分','守恒','机理','热方程','生态','动力',
                     'differential','conservation','mechanism','heat equation','ecology','dynamics'],
       'simulation':['仿真','模拟','排队','随机过程','蒙特卡洛','马尔可夫',
                     'simulation','queue','stochastic process','monte carlo','markov'],
       'inverse':['反演','隐变量','校准','逆问题','病态','可识别',
                  'inverse','calibration','ill posed','identifiability'],
       'numerical':['插值','求根','积分','数值','线性代数',
                    'interpolation','root finding','integration','numerical','linear algebra'],
       'signals-images':['信号','图像','频谱','滤波','几何','小波',
                         'signal','image','spectrum','filter','geometry','wavelet'],
       'games':['博弈','联盟','策略','合作','竞争','game','coalition','strategy','cooperation','competition'],
       'control':['控制','反馈','卡尔曼','稳定','状态估计','control','feedback','kalman','stability','state estimation']}

# The catalog prose is mostly Chinese. These are lexical translations, not
# suitability rules: retain the same candidate-only boundary as other matches.
QUERY_TRANSLATIONS={
    'forecast':('预测',), 'forecasting':('预测',),
    'time series':('时序','时间序列'), 'seasonal':('季节',),
    'integer':('整数',), 'binary':('二元','0-1'),
    'resource':('资源',), 'allocation':('分配',),
    'capacity':('容量',), 'constraint':('约束',),
    'optimization':('优化',), 'regression':('回归',),
    'classification':('分类',), 'clustering':('聚类',),
    'svm':('支持向量',), 'support vector machine':('支持向量',),
    'calibration':('校准',), 'identifiability':('可识别',),
    'conservation':('守恒',), 'simulation':('仿真','模拟'),
    'ranking':('排名','排序'), 'interpolation':('插值',),
    'wavelet':('小波',), 'feedback':('反馈',)}


def normalize(text):return re.sub(r'[^a-z0-9\u4e00-\u9fff]+','',text.lower())


def contains_phrase(text,phrase):
    """Use ASCII token boundaries; preserve Chinese substring lookup."""
    if re.fullmatch(r'[a-zA-Z0-9\s_-]+',phrase):
        words=re.findall(r'[a-z0-9]+',phrase.lower())
        if not words:return False
        pattern=r'(?<![a-z0-9])'+r'[\s_-]+'.join(map(re.escape,words))+r'(?![a-z0-9])'
        return re.search(pattern,text.lower()) is not None
    normalized=normalize(phrase)
    return bool(normalized) and normalized in normalize(text)


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
    translated={word for phrase,words in QUERY_TRANSLATIONS.items()
                if contains_phrase(query,phrase) for word in words}
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
                elif nq and nn and contains_phrase(name,query):score=max(score,70)
                elif len(nn)>=2 and contains_phrase(query,name):score=max(score,60)
            body=' '.join(names+[card['purpose'],' '.join(card['assumptions'])])
            if nq and contains_phrase(body,query):score=max(score,35)
            score+=sum(8 for term in terms if contains_phrase(body,term))
            score+=sum(4 for hint in HINTS.get(card['family'],[]) if contains_phrase(query,hint))
            for word in translated:
                # An explicit translated title outranks an incidental mention
                # in a different model's prose (e.g. RBF is not RBF-SVM).
                if any(contains_phrase(name,word) for name in names):score+=60
                elif contains_phrase(body,word):score+=8
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
