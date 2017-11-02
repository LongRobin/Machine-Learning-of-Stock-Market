# -*- coding: utf-8 -*-
"""
Created on Thu Nov 02 10:18:35 2017

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 10:06:08 2017

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 13:06:04 2017

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:55:56 2017

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding:utf-8 -*-

from CloudQuant import SDKCoreEngine  # 导入量子金服SDK
from CloudQuant import AssetType
from CloudQuant import QuoteCycle
from sklearn.preprocessing import Imputer
from sklearn import linear_model,metrics
from sklearn.ensemble import RandomForestClassifier
from gcForest.GCForest import gcForest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import datetime
import numpy as np      #使用numpy
import time     #使用时间戳
import os
os.chdir("C:\Users\Administrator\Downloads\libsvm-3.22\libsvm-3.22\python")
from svmutil import *
import math
import random
import pandas as pd
os.getcwd()
'''用户只需要先设置好账号、密码、基础数据存放路径以及仿真回放相关的资金及时间等参数'''
'''allowForTodayFactors:
        string array类型。可选项。
        指定可在回测时获取到当日数据的因子文件名，通常
        有LZ_CN_STKA_QUOTE_TOPEN，LZ_CN_STKA_SLCIND_STOP_FLAG等。
        不在列表中的因子文件只能取得当日之前的数据，以避免产生未来数据的问题。 '''
config = {
    'username': 'tip',
    'password': 'test123',
    'rootpath': 'C:\cStrategy',  # 客户端所在路径
    'initCapitalStock': 10000000,  # 初始资金
    'startDate': 20170101,      # 交易开始日期
    'endDate': 20171001,        # 交易结束日期
    'cycle': QuoteCycle.D,      # 回测粒度为日线
    'strategyName': 'DateTest',    # 策略名
    'stockFeeRate': 0.0015,      # 手续费率
    'logfile': 'Test.log',     # 在策略中调用log方法所生成的日志文件名
    'strategyID': '123456',
    'dealByVolume': True,       # 在策略中撮合考虑实际交易量成交
    'allowForTodayFactors': ['LZ_CN_STKA_SLCIND_STOP_FLAG',  # 停牌因子
                             'LZ_CN_STKA_SLCIND_ST_FLAG',  # st因子
                             'LZ_CN_STKA_SLCIND_TRADEDAYCOUNT',  # 新股上市天数
                             ' LZ_CN_STKA_CMFTR_CUM_FACTOR ',  # 复权因子
                             'LZ_CN_STKA_QUOTE_TOPEN',  # 开盘价
                             'LZ_CN_STKA_INDEX_CSI500WEIGHT ',  # 中证500成分股权重
                             ' LZ_CN_STKA_INDEX_HS300WEIGHT ']  # 沪深300成分股权重
}


HOLDINGPERIOD = 20      # 持有股票日期为20天
HOLDINGNUMBER = 300     # 股票数量为300只





'''应用场景：用于查询持仓股票代码，以lis形式返回，如果为空仓，则返回空列表'''
'''getPositions(tsInd, code): 
        查询持仓信息（返回今仓、昨仓数量、开仓时间、价格等。
        code：String类型。可选项，默认为None。查询的标的代码。
        tsInd：int类型。指定进行此操作的市场，定义在枚举AssetType中。可选值为：Stock=1,Future=2,
        nsiteFund=4,OTCFund=8,Bond=16,ReverseRepo=32,Option=64。
        返回值：PositionRecord List类型。返回指定市场指定标的的持仓，如果没有指定标的，返回指定市场的所有持
        仓列表。PositionRecord对象包含今日和昨日的总持仓量，可平量，市场均价。'''
def getPositionList(sdk):       # 定义获取持仓列表函数
    """
    返回持仓股票代码的列表，返回值为list类型
    """
    posList = []        # 设置posList为列表
    position = sdk.getPositions()       # 查询持仓信息
    if position == None:
        print 'getPositions error!'
        return None
    for stock in position:
        posList.append(stock.code)      # 在posList列表末尾加上股票代码

    return posList      # 返回postList列表


'''应用场景：用于返回持仓股票代码字典，键为股票代码，值为可买股票数量以dict形式返回。如果为空仓，则返回空字
            典。'''
'''posDict[stock.code]= stock.optPosition：将可卖股票数量赋值给相应的posDict股票代码
            stock.code：string类型，股票代码
            stock.optPosition：int类型，股票可卖数量'''
def getPositionDict(sdk):
    """
    返回持仓股票代码的字典，键为股票代码，值为可卖股票数量，返回值为dict类型
    """
    posDict = {}        # 设置posDict为字典
    position = sdk.getPositions()
    if position == None:
        print 'getPositions error!'
        return None
    for stock in position:
        posDict[stock.code] = stock.optPosition     # 将可卖股票数量赋值给相应的posDict股票代码

    return posDict      # 返回postDict列表


'''应用场景：用于返回持仓股票代码的字典，键为股票代码，值为总持仓、可平数量、今日持仓数量、持仓总成本的list，
            返回值为dict类型。如果为空仓，则返回空字典。'''
'''posDict[stock.code]= [stock.totalPosition, stock.optPosition, stock.todayPosition, stock.totalCost]：
            将股票总持仓量、可卖股票数量、今日总持仓量、持股总成本赋值给相应的posDict股票代码
            stock.code：string类型，股票代码
            stock.totalPosition：int类型，总持仓量
            stock.optPosition：int类型，可卖数量
            stock.todayPosition：int类型，今日总持仓量
            stock.totalCost：float类型，持股总成本'''
def getPositionDictDetail(sdk):
    """
    返回持仓股票代码的字典，键为股票代码，值为总持仓、可平数量、今日持仓数量、持仓总成本的list，返回值为dict类型
    """
    posDict = {}
    position = sdk.getPositions()       # 查询持仓信息
    if position == None:
        print 'getPositions error!'
        return None
    for stock in sdk.getPositions():
        posDict[stock.code] = [stock.totalPosition, stock.optPosition, stock.todayPosition, stock.totalCost]
        # 将总持仓、可平数量、今日持仓数量、持仓总成本赋值给相应的posDict股票代码
    return posDict      # 返回postDict列表



'''应用场景：定义买入股票函数，把资金按照条件设定分配给买入股票品种，买入后更新持仓。然后比较前后持股票品种和
            持仓量，将买入部分在ret列表中返回'''
'''getAccountInfo(tsInd=AssetType.Stock): 查询资产明细。可能返回None
            参数
            • tsInd: int类型。可选项，默认为股票（1）。
            指定进行此操作的市场，定义在枚举AssetType中。可选值为：Stock=1,Future=2,OnsiteFund=4,
            OTCFund=8,Bond=16,ReverseRepo=32,Option=64。注意：目前正式支持的是股票和期货，其它品种还处在
            试验阶段，暂不对外提供支持。
            返回值:AccountInfo类型。包含帐户的前日权益（previousAsset）、前日市值（previousMarketValue）、
            前日资金（previousBalance）、当前资金（balance）、冻结资金（frozenValue）、
            可用资金（availableCash）、保证金（margin）。'''
''' len():int类型，返回对象的长度'''
'''round():int类型，返回对象的四舍五入值'''
'''np.floor()：int类型，调用numpy里的floor函数，取小于对象之的最近的整数'''
'''try:except: 将可能发生错误的语句放在try模块里，用except来处理异常'''
def buyStockList(sdk, stockToBuyList, quotes, tradingNumber=None, budgetPercent=0.995):
    """
    批量买入股票的函数，stockToBuyList为股票列表，quotes为报单价格的dict，
    tradingNumber为限制买入的股票数量，如果不设置任何值默认值为None，
    budgetPercent为买入每只股票分配的资金，默认值为0.995
    ret为返回值，类型为dict
    EX：buyStockList（sdk，stockToBuyList，quotes）-》表示满仓买入stockToBuyList里的股票
        buyStockList（sdk，stockToBuyList，quotes，tradingNumber = 100）-》表示限制股数为100
    """
    # pdb.set_trace()
    posList = getPositionList(sdk)      # 调用PositionList(sdk)函数，函数返回值赋给posList
    if posList == None:
        return None
    positionBefore = getPositionDictDetail(sdk)     # 调用PositionDictDetail(sdk)函数，函数返回值赋给positionBefore
    if positionBefore == None:
        return None

    orders = []
    if tradingNumber is None:
        accountInfo = sdk.getAccountInfo()  # 资金账户查询（返回：帐户的可用资金、交易冻结、保证金占用、手续费等）
        if accountInfo == None:
            return None
        budget = budgetPercent * accountInfo.availableCash / (1+len(stockToBuyList))    # 将资金在买入股票列表中平均分配
    else:
        accountInfo = sdk.getAccountInfo()
        if accountInfo == None:
            return None
        if tradingNumber - len(posList) <= 0:       # 如果限制买入的股票数量小持仓股票数量
            return {}
        budget = budgetPercent * accountInfo.availableCash / (tradingNumber - len(posList))
        # 将资金在剔除已有股票后在平均分配

    for stock in stockToBuyList:
        price = round(quotes[stock] * 100) / 100        # 使在四舍五入后保留两位小数
        volume = np.floor(budget / price / 100) * 100   # 交易量取小于对象的最近的整数
        if price > 0 and volume > 0:
            orders.append([stock, price, volume, 'BUY'])        # 定义买入指令内容

    try:
        sdk.sdklog(orders)      # 将交易指令记入日志
        sdk.makeOrders(orders)
    except:
        print 'makeOrders error!'
        return None

    positionAfter = getPositionDictDetail(sdk)      # 更新详细持仓字典
    if positionAfter == None:
        return None
    ret = {}

    setBefore = set(positionBefore.keys())      # 前期持仓股票代码列表
    setAfter = set(positionAfter.keys())        # 更新后持仓股票代码列表

    if len(setAfter - setBefore) > 0:       # 如果新买入了股票品种
        for stock in list(setAfter - setBefore):
            ret[stock] = positionAfter[stock][0]        # 将新买入股票赋值给ret列表
    else:
        for stock in positionAfter.keys():
            if positionAfter[stock][0] > positionBefore[stock][0]:      # 更新后股票品种持仓量大于原有该股票持仓量
                ret[stock] = positionAfter[stock][0] - positionBefore[stock][0]     # 将原股票增仓量赋值给ret列表

    return ret


'''应用场景：定义卖出股票函数，查询持仓信息后，将可卖数量全部卖出，卖入后更新持仓。然后比较前后持股票品种和
            持仓量，将买出部分在ret列表中返回'''
def sellStockList(sdk, stockToSellList, quotes):
    """
    批量卖出股票的函数，stockToSellList为股票列表，quotes为报单价格的dict
    ret为返回值，类型为dict
    """
    posDict = getPositionDict(sdk)      # 调用PositionDictDetail(sdk)函数，函数返回值赋给posDict
    if posDict == None:
        return None
    positionBefore = getPositionDictDetail(sdk)     # 调用PositionDictDetail(sdk)函数，函数返回值赋给positionBefore
    if positionBefore == None:
        return None

    orders = []
    for stock in stockToSellList:
        price = round(quotes[stock] * 100) / 100
        volume = posDict[stock]     # 将持仓股票可卖数量全部卖出
        if price > 0 and volume > 0:
            orders.append([stock, price, volume, 'SELL'])       # 定义卖出指令内容

    try:
        sdk.makeOrders(orders)
        sdk.sdklog(orders)
    except:
        print 'makeOrders error!'
        return

    positionAfter = getPositionDictDetail(sdk)      # 更新详细持仓字典
    if positionAfter == None:       # 如果是空仓
        return None
    ret = {}

    setBefore = set(positionBefore.keys())
    setAfter = set(positionAfter.keys())

    if len(setBefore - setAfter) > 0:       # 有股票品种全部卖出
        for stock in list(setBefore - setAfter):
            ret[stock] = positionBefore[stock][0]       # 将全部卖完的股票代码在ret列表上指明
    else:
        for stock in positionBefore.keys():
            if positionBefore[stock][0] > positionAfter[stock][0]:      # 更新后股票品种持仓量小于原有该股票持仓量
                ret[stock] = positionBefore[stock][0] - positionAfter[stock][0]     # 将原股票减仓量赋值给ret列表

    return ret


'''setGlobal(name, value): 设置用户自定义变量。
            参数
            • name: String类型。全局变量的名称。
            • value: 全局变量的值。
            返回值: 无'''
'''initial(sdk):在回测执行之前会运行的方法。可以在其中添加只会运行一次而不需要在回测过程中反复执行的部分，例
            如读取数据文件，设置全局变量常数等等。可选。
            返回值：无
            参数
            • sdk: object类型。必填项。
            sdk对象: 为了在函数内部调用sdk提供的方法，需要用这个参数来接收sdk对象。'''

def initial(sdk):       # 写整个回测前要做的操作
    if sdk.getGlobal('TRADEDATEFLAG') == None:
        sdk.setGlobal('TRADEDATEFLAG', -1)
    if sdk.getGlobal('TRADELASTDATE') == None:
        sdk.setGlobal('TRADELASTDATE',sdk.getNowDate())
    if sdk.getGlobal('Figure') == None:    
        sdk.setGlobal('FIGURE',True)
    print 'initial Done!'

'''initPerDay(sdk): 在分钟线回测时，每日策略执行之前会运行的方法。可以在其中添加只会每日需要准备的部分，例如
            设置选股池和买卖点等等。可选。
            返回值: 无
            示例
            • sdk: object类型。必填项。
            sdk对象: 为了在函数内部调用sdk提供的方法，需要用这个参数来接收sdk对象。'''
def initPerDay(sdk):        # 每天回测前要做的操作
    pass


'''应用场景：定义买卖策略。把股票按市值大小排列，停盘股、ST股、新股放在最后，每隔20个交易日以开盘价买入股票、
            卖出全部可卖持仓'''
'''getGlobal(name): 获取用户自定义变量。
            参数
            • name: String类型。全局变量的名称。
            返回值: 变量内容，如果全局变量未设置则返回None'''
'''getFactorData(factorName): 获取因子矩阵。可能返回None
            参数
            • factorName: String类型。
            因子名称，具体因子名称可查阅因子字典，或从客户端因子文件列表获得。
            返回值: numpy.array类型。返回到上一交易日为止的因子数据矩阵。如果因子名在回测参数
            allowForTodayFactors中指定了，则返回到当前交易日为止的因子数据矩阵。'''
'''getQuotes(codes, tsInd=AssetType.Stock): 获取股票列表的盘口信息。未上市、退市、错误的股票代码会返回None，
            使用前需要判断，否则会导致程序崩溃
            参数
            • codes: String List类型。查询的标的代码的列表。
            • tsInd: int类型。可选项，默认为股票（1）。指定进行此操作的市场，定义在枚举AssetType中。可选值
            为：Stock=1,Future=2,OnsiteFund=4,OTCFund=8,Bond=16,ReverseRepo=32,Option=64。
            注意：目前正式支持的是股票和期货，其它品种还处在试验阶段，暂不对外提供支持。
            返回值: Dictionary类型。key为标的代码，value为StockTick类型的行情信息。包含当前价格，委托价格，
            委托交易量等。'''
'''sort(): 用于在原位置对列表排序,让元素按一定的顺序排列'''
'''zip():用来进行并行迭代,把两个序列压缩在一起,然后返回一个元组的列表 '''
'''list(): 将对象内容以列表的形式返回，list函数适用于所有类型的序列，不只是字符串'''
def sign(i,j):
    if i<j:
        k=-1
    else:
        if i>j:
            k=1
        else:
            k=0
    return k

def Factors(sdk,time):
    factor = []
    factor.append(np.array(sdk.getFactorData("RiskFactorsBeta")[time]))##beta
    factor.append(np.array(sdk.getFactorData("RiskFactorsBTOP")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsEarningsYield")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsGrowth")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsLeverage")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsLiquidity")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsMomentum")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsNonSize")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsResidualVolatility")[time]))
    factor.append(np.array(sdk.getFactorData("RiskFactorsSize")[time]))
    factor.append(np.array(sdk.getFactorData("LZ_CN_STKA_SLCIND_STOP_FLAG")[time]))
    factor.append(np.array(sdk.getFactorData("LZ_CN_STKA_SLCIND_ST_FLAG")[time]))
    factor.append(np.array(sdk.getFactorData("LZ_CN_STKA_SLCIND_TRADEDAYCOUNT")[time]))
    factor.append(np.array(sdk.getFactorData("LZ_CN_STKA_QUOTE_TCLOSE")[time]))
    factor.append(np.array(sdk.getFactorData("LZ_CN_STKA_QUOTE_TCLOSE")[-1]))
    factor.append(np.array(sdk.getFactorData("LZ_CN_STKA_VAL_A_TCAP")[time]))
    industry = sdk.getFactorData("LZ_CN_STKA_INDU_ZX")[-1]
    length = len(factor)
    for i in range(0,30):
        aa = [0 for ii in range(0,len(factor[0]))]
        factor.append(aa)
    for i in range(0,len(factor[0])):
        ind =industry[i]
        factor[length+ind][i] = 1
        
    factor = np.transpose(factor)
    factor = [i for i in factor if i[10]==0 and i[11]==0 and i[12]>60]
    factor = np.transpose(factor)
    factor = factor.tolist()
    return factor




def strategy(sdk):
    ###################
    #    股票策略     #
    ###################
    tradeNowDate = sdk.getNowDate()
    tradeLastDate = sdk.getGlobal('TRADELASTDATE') 
    tradeDateFlag = sdk.getGlobal('TRADEDATEFLAG')
    Figure = sdk.getGlobal("FIGURE")
    if tradeNowDate!=tradeLastDate:
        tradeDateFlag += 1
        sdk.setGlobal('TRADEDATEFLAG', tradeDateFlag) 
        sdk.setGlobal('TRADELASTDATE',tradeNowDate)
        sdk.setGlobal('FIGURE',True)
    

    if tradeDateFlag % HOLDINGPERIOD == 0 and Figure :
        Figure = False
        sdk.setGlobal('FIGURE',Figure)
        print sdk.getNowDate()





'''time():time模块包含的函数能实现以下功能，获取当地时间、操作时间和日期、从字符串读取时间以及格式化时间为字
            符串。'''
def main():
    # 将策略函数加入
    config['initial'] = initial
    config['strategy'] = strategy
    config['preparePerDay'] = initPerDay
    # 启动SDK
    t0 = time.time()
    SDKCoreEngine(**config).run()
    t1 = time.time()
    print "start from", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t0)), ", end in", time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(t1)), ". total time took", t1 - t0, " seconds"


if __name__ == "__main__":
    main()
