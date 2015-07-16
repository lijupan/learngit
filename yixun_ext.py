#!/usr/bin/python2
from odis.serialize.lib import MD5Writable
import json,re

# 错误的促销信息
Error = None
# 未配置促销信息
Info = []
# 结构化促销信息
Result = []

pricePattern = re.compile(u"([0-9]+)(?:\\.[0-9]0)?");

def appendError(newError):
    if newError is not None:
        global Error
        Error = (newError if Error is None else Error+";"+newError)

def filter(item):
    global Info
    global Result
    promoName = unicode(item["name"]).replace(",", "")
    promoDesc = unicode(item["desc"]).replace(",", "")
    promoType = str(item["discount_type"])
    promoId = str(MD5Writable.digest(promoName+promoDesc).halfDigest())
    if promoType == "5":
        promos = pricePattern.findall(promoName)
        if len(promos) == 2 and int(promos[0]) > int(promos[1]):
            Result.append(["110", promoId, promos[0], promos[1]])
        elif len(promos) == 4 and int(promos[0]) > int(promos[1]) and int(promos[0]) == int(promos[2]) and int(promos[1]) == int(promos[3]):
            Result.append(["120", promoId, promos[0], promos[1]])
        else:
            Info.append([promoType, promoId, promoDesc])
    elif promoType == "10":
        # 推荐促销，推荐促销不一定属于当前商品
        Info.append([promoType, promoId, u"推荐："+promoDesc])
    else:
        # 其他促销
        Info.append([promoType, promoId, promoDesc])

def solveJson(jsond):
    if jsond["info_list"] == None:
        appendError("No promotionInfoList")
        return
    for item in jsond["info_list"]:
        try:
            filter(item)
        except BaseException as b:
            appendError(str(b))

def solveJsonstr(value):
    try:
        jsond = json.loads(value)
        solveJson(jsond["data"][0])
    except BaseException as b:
        appendError(str(b))

def solve(inDict):
    for (key, value) in inDict.items():
        if key == "field_promotion":
            # 后台抓取
            solveJsonstr(value)
        elif key == "front_promotion":
            # 助手前端抓取
            solveJsonstr(value)
        else:
            appendError("Not recognized key" + key)

solve(inputDict)

