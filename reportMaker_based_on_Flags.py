# -*- coding: utf-8 -*-

'''
This file is about class generating different type of reports(tables), given
two original tables (sellBook, buyBook)

NOTE: Please update(generate) sellBook.csv, buyBook.csv before use the classes
in this file

########## structure about sellBook, and buyBook ##################
(original Tables)
DataFrame

null | stockName |currentPrice|date_peak_or_trough|price(p,t)|indicator

(price(p,t): the price of flagging peak or trough)

NOTE: one line just show one flags for corresponding stock
a stock might have many flags, i.e., many lines

'''


import pandas as pd
import numpy as np
import pylab
import matplotlib.pyplot as py
import os

import ystockquote

def cls():
    # this function is used to clear the intepreter console
    os.system(['clear','cls'][os.name == 'nt'])
    

def height(heightDict, indexFlag):
    height = 0
    if indexFlag not in heightDict:
        heightDict[indexFlag] = 1
        
    else:
        height = heightDict[indexFlag]
        heightDict[indexFlag] += 1
    return height
        
def getChartForDay(longObj, shortObj, marketName, savePic=False):
    '''
    @@summary: This function is used to generate a graph with the amounts
    flags, amounts of tickers per flag, as well as the symbols
    
    line: amount of flags
    bar: amount of tickers
    
    green: for long 
    red: for short 
    '''
    lMergeDf, sMergeDf = longObj.mergeDf, shortObj.mergeDf
    #################### plot the amount of flags and tickers ################
    
    
    lsumByNumFlags, lsumByNumTickers = lMergeDf.sum(), lMergeDf.count()
    ssumByNumFlags, ssumByNumTickers = sMergeDf.sum(), sMergeDf.count()

        
    xlabels = lsumByNumFlags.index
    N = len(lsumByNumFlags)
   
    
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars
    
    fig, ax = py.subplots(figsize=(20,13))
    
    rects1 = ax.bar(ind, lsumByNumTickers, width, color='g',alpha=.3)
    rects2 = ax.bar(ind+width, ssumByNumTickers, width, color='r',alpha=.3)
    
    #rects3 = ax.plot(lsumByNumFlags, linestyle ='-', marker='o', linewidth=2.0,color='g',alpha=.3)
    #rects4 = ax.plot(ssumByNumFlags, linestyle ='-', marker='o', linewidth=2.0,color='r',alpha=.3)
    
    
    # add some text for labels, title and axes ticks
    ax.set_ylabel('amount')
    ax.set_xlabel('flags')
    ax.set_title('Symbols flagged'+'('+marketName+')')
    ax.set_xticks(ind+width)
    ax.set_xticklabels( xlabels )
    
    ax.legend( (rects1[0], rects2[0]), ('long', 'short') )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    #autolabel(rects3)
    #autolabel(rects4)
    
    #ax.set_yticks(np.arange(0,max(max(lsumByNumTickers), max(ssumByNumTickers)),2))
    
    
    
    heightDict = dict()
    for row in range(len(lMergeDf)):
        numFlags = 0
        xs = []
        ys = []
        for indexFlag, isExist in enumerate(lMergeDf.ix[row]):
            name = lMergeDf.index[row]
            if np.isnan(isExist) == True:
                continue
            else:
                
                x = indexFlag+0.05
                y = height(heightDict, indexFlag)
                ax.annotate(name+'('+str(int(isExist))+')',xy=(x, y),size = 9)
                
                xs.append(x+0.25)
                ys.append(y+0.1)
                numFlags += 1
        if numFlags > 1:
            
            ax.plot(xs,ys,linewidth=1,color='g', linestyle ='--', marker='*')
            
    
    heightDict = dict()
    for row in range(len(sMergeDf)):
        numFlags = 0
        xs = []
        ys = []
        for indexFlag, isExist in enumerate(sMergeDf.ix[row]):
            name = sMergeDf.index[row]
            if np.isnan(isExist) == True:
                continue
            else:
                
                x = indexFlag+0.4
                y = height(heightDict, indexFlag)
                ax.annotate(name+'('+str(int(isExist))+')',xy=(x, y),size=9)
                
                xs.append(x+0.25)
                ys.append(y+0.1)
                numFlags += 1
        if numFlags > 1:
            
            ax.plot(xs,ys,linewidth=1,color='r', linestyle ='--', marker='*')
                
    
#    for indexFlag in longObj.flags:
#        lNameFlag = lMergeDf.columns[indexFlag]
#        #sNameFlag = sMergeDf.columns[indexFlag]
#        
#        dfSelectByFlag = longObj.selectByFlag(indexFlag)
        
        
    
        
        
    
    
    
    
    py.grid()
    py.show()
    

    
    
    
    #################### plot interesting tickers ###########################
#    fig1, ax1 = py.subplots()
#    
#    for i in range(len(longObj)):
#        name = longObj.index[i]
#        numPerFlag = longObj.ix[i].values
#        ax1.plot(ind, numPerFlag, linestyle ='-', marker='o', linewidth=.5,color='g')
#        ax1.annotate(name,xy=(1,1))
#    
#    name = longObj.index[1]
#    numPerFlag = longObj.ix[1].values
#    ax1.plot(ind, numPerFlag, linestyle ='-', marker='o', linewidth=.5,color='g')
#    ax1.annotate(name,xy=(1,1))
        
def sectorAnalysis(mergeDf, sectorDf):
    a = mergeDf.join(sectorDf,how='left')
    pass
    return a
    

class TableMaker:
    def __init__(self, originTableName, flags, tradeType):
        self.originDf = pd.read_csv(originTableName)
        self.flags = flags
        self.tradeType = tradeType
        self.mergeDf = self.mergeByStock()
        
    def getStockDetail(self, stockName):
        # select all lines with 'stockName' column equals stockName
        # TODO: select ticker without knowledge about it's long or short
        return self.originDf[self.originDf['stockName'] == stockName]
        
    def selectByNumFlag(self, numFlag):
        gbStockOj = self.groupByStock
        countStock = gbStockOj.count()
        self.ori
        
    def selectByFlag(self, *args):
        
        assert len(args) <= len(self.flags)+1 
        assert type(args[0]) is float        
        
        if len(args) == 1:
            
            if self.tradeType is 'long':
                
                flag = str(-args[0]*100)+'%'
            else:
                flag = str(args[0]*100)+'%'
                
            selectDf = self.mergeDf.ix[:,[flag]].dropna()   
            
        else:
            flagsElem = args[0:-1]
            operator = args[-1]
            if self.tradeType is 'long':
                reqFlags = map(lambda x: str(-x*100)+'%', flagsElem)
            else:
                reqFlags = map(lambda x: str(x*100)+'%', flagsElem)
                
            if operator == 'or': 
                selectDf = self.mergeDf.ix[:,list(reqFlags)].dropna(thresh=1)
            elif operator == 'and':
                selectDf = self.mergeDf.ix[:,list(reqFlags)].dropna()
            else:
                print 'illegal operator'
            
        
        return selectDf

        
        
    

        
    def groupByStock(self):
        # gbStock is a group-by object
        # any further computation on gbStock is within the particular group
        gbStockOj = self.originDf.groupby(self.originDf['stockName'])
        return gbStockOj
        
        
    
    
    def mergeByStock(self, saveCSV=True):
        '''
        This function is to compute the number of flags per ticker per flag
        we will use the result for further computing
        
        return:
                 flag1(string) | flag2 | flag3 | ...
        ticker1    5               nan     1
        ticker2    2         ..       ...
        
        
        
        NOTE: this function highly dependents on the originTable's layout
        make sure the first column is stock name, the last column is flag(in string format)
        '''
        # convert flags to string format (easily to compare)
        # flags should be list type to use 'index' function
        assert type(self.flags) is list

        
        if self.tradeType is 'long':
            flagsForTrade = map(lambda x: str(-x*100) + '%', self.flags)
        else:
            flagsForTrade = map(lambda x: str(x*100) + '%', self.flags)
            

        mergeDict = dict()
        
        if len(self.originDf) != 0:
            for line in self.originDf.values:
                assert type(line[-1]) is str
            # to re
                if line[1] in mergeDict:
                    # find the index of corresponding flag in flags
                    flagIndex = flagsForTrade.index(line[-1])
                    # change the position value to True
                    if np.isnan(mergeDict[line[1]][flagIndex]) == True:
                        mergeDict[line[1]][flagIndex] = 1
                    else:
                        mergeDict[line[1]][flagIndex] += 1
                    
                else:
                    mergeDict[line[1]] = [NaN] * len(flagsForTrade)
                    # find the index of corresponding flag in flags
                    if line[-1] == '-100.0%':
                        pass
                    flagIndex = flagsForTrade.index(line[-1])
                    # change the position value to True
                    mergeDict[line[1]][flagIndex] = 1
        else:
            mergeDict = {'NAN':[NaN]*len(flagsForTrade)}
            
            
        
        #convert the dictionary to the dataFrame with right format      
       
        mergedTable = pd.DataFrame(mergeDict).T
        mergedTable.columns = flagsForTrade

        
#        if len(self.originDf) == 0:
#            mergedTable = pd.DataFrame(data=[[]])
        

        
        
        ############### Select tickers based on above results ################
        
        # select all the lines with 'flag' column == True
        
        if saveCSV==True:
            if self.tradeType == 'long':
                mergedTable.to_csv('mergeByStockBuy.csv')
            elif self.tradeType == 'short':
                mergedTable.to_csv('mergeByStockSell.csv')
            
        return mergedTable
        
        

        
if __name__=='__main__':
    
##################### Generate the current flag over several market ##########

    marketList = ['ftse1002014','sp5002014','stoxx502014','aex252014','cac402014','ibex352014','mib402014']
    savePic = True
    for market in marketList:
        fileCSV1 = 'outputbuy'+'('+market+')'+'.csv'
        fileCSV2 = 'outputsell'+'('+market+')'+'.csv'
        
        b = TableMaker(fileCSV1,tradeType='long', 
                       flags = [0.08,0.16,0.2,0.275,0.30,0.33,0.5,1.0])
                       
        s = TableMaker(fileCSV2,tradeType='short', 
                       flags = [0.08,0.16,0.2,0.275,0.30,0.33,0.5,1.0])  
                       
        getChartForDay(b, s, marketName=market)
        
        if savePic == True:
            py.savefig('pic/flagByMarkets_current/'+market+'.png', format='png')
    #a =  b.selectByFlag(0.08,0.16,'or')
        
####################### sector Analysis ################################
    
#    mergeDf = pd.read_csv('mergeByStockBuy.csv')
#    mergeDf.index = mergeDf['Symbol']
#    del mergeDf['Symbol']
#    sectorDf = pd.read_csv('sectorsp.csv')
#    sectorDf.index = sectorDf['Symbol']
#    a = sectorAnalysis(mergeDf, sectorDf)
