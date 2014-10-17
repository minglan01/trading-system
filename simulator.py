# -*- coding: utf-8 -*-

import common as cm
import numpy as np
import pandas as pd

class singleSimulator:
    def __init__(self,stockName,testStartDate, testEndDate, flagPeriod, reportPeriod):
        '''
        @@summary: backtest one stock from testStartDate to testEndDate
        '''
        self.stockName = stockName
        self.testStartDate = testStartDate
        self.testEndDate = testEndDate
        self.flagPeriod = flagPeriod
        self.reportPeriod = reportPeriod
        
        
        cm.Quotes(startDate, endDate, stockName)
        
    def sim1day1stock(self,startDate ,   
                       endDate, 
                       stockName = self.stockName,
                       flags=[0.08,0.16,0.2,0.275,0.30,0.33,0.5,1], 
                       tolerance = 0.0075, 
                       toler50 = 0.02,
                       toler100 = 0.025,
                       flagWeights = [1,1,1,1,1,1,1,1], 
                       timeWeights = False,
                       sizeBackForward=[30,30],
                       fineSizeBackForward=[15,15],
                       finalSizeBackForward=[10,5],
                       liveData=False):
        
        stockFlagObj = cm.CurrentFlaggerSingleStock(startDate = startDate,   
                                           endDate = endDate, 
                                           stockName = stock,
                                           flags=flags, 
                                           tolerance = tolerance, 
                                           toler50=toler50,
                                           toler100=toler100,
                                           flagWeights =flagWeights, 
                                           timeWeights = timeWeights,
                                           sizeBackForward=sizeBackForward,
                                           fineSizeBackForward=fineSizeBackForward,
                                           finalSizeBackForward=finalSizeBackForward,
                                           liveData=liveData)
                                           
        # check whether it's flagging using flagChecker method                              
        stockFlagObj.flagChecker()
        # using the result to make a report and plot the chart
        if stockFlagOb.score > 0:
            
                           
                           
        
        flagObj.flagChecker
        score = flagObj.score
        return score
        
    def orderBook(self):
        
    def cashHold(self):
        
    def reportMaker(self):
        
        
        
            c = currentFlaggerSingleStock(startDate = (2012,9,29),   
                       endDate = (2014,10,13), 
                       stockName = 'CAT',
                       flags=[0.08,0.16,0.2,0.275,0.30,0.33,0.5,1], 
                       tolerance = 0.0075, 
                       toler50 = 0.02,
                       toler100 = 0.025,
                       flagWeights = [1,1,1,1,1,1,1,1], 
                       timeWeights = False,
                       sizeBackForward=[30,30],
                       fineSizeBackForward=[15,15],
                       finalSizeBackForward=[10,5],
                       liveData=True)
        