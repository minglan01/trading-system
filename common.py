# -*- coding: utf-8 -*-
"""
Created on Wed Oct 01 14:47:19 2014




@author: ACCA4
"""
from matplotlib.finance import quotes_historical_yahoo, candlestick
import numpy as np
from pylab import *
import matplotlib.pyplot as py
import QSTK.qstkutil.DataAccess as da
import pandas as pd
import datetime
from copy import deepcopy
import time
import operator
import profile


import ystockquote



DAYSYEAR = 251
class Quotes:
    '''
    @@summary: This class access the historical data
    NOTE: the newest data we are able to access is yesterday.
    '''
    def __init__(self, startDate, endDate, stockName):
        '''
        historical data from startDate and endDate about stockName
        '''
        
        self.startDate = startDate
        self.endDate = endDate
        self.stockName = stockName
        
    def dataAccess(self):
        # access data from yahoo
        # return: date, open, close, high, low, volume
        quotes = quotes_historical_yahoo(self.stockName, self.startDate, self.endDate)
        
        # if error
        if len(quotes) == 0:
            print self.stockName
            raise SystemExit   
        #quotes = np.array(map(list, quotes))
        quotes = np.array(quotes)
        
        return quotes
        
        
class PeakValleyFinder:
    def __init__(self, startDate, endDate, stockName, others=[]):
        #self.getData()
        if others == []:
            
            quotesOj = Quotes(startDate, endDate, stockName)
            print stockName
            quotes = quotesOj.dataAccess()
            self.quotes = quotes
        else:
            self.quotes = others
                     
    def getPeaksValleys(self):
        return self.peakValleyAlgorithm()
        
    def plot(self):
        self.peakValleyPlot()
        #TODO
        pass
        
class PeakValleyFinderWin(PeakValleyFinder):
    
    def __init__(self, startDate, endDate, stockName,sizeBackForward=[30,30],
                 fineSizeBackForward=[15,15],finalSizeBackForward=[10,4], others=[]):
                     
        PeakValleyFinder.__init__(self, startDate, endDate, stockName, others=others)                  
        self.sizeBackForward = sizeBackForward
        self.fineSizeBackForward = fineSizeBackForward
        self.finalSizeBackForward = finalSizeBackForward
        
        self.peakPrices = None
        self.valleyPrices = None
        
    def getQuotes(self):
        return self.quotes
        
    def __str__(self):
        return stockName
        
        
    def peakValleyAlgorithm(self):
        ###################
        ## peack and vally#    
        ###################
        highPrices,lowPrices,days = self.quotes[:,3],self.quotes[:,4],len(self.quotes)
        
    
        # initial the flags of peaks and valley 
        # this two lists would store the absolute position of peaks and troughs
        flagPeaks =[]
        flagValleys = []
        # move the window, looking for the peaks and troughs
        startPoint = 0
        flagPeaks, flagValleys, endStartPoint = self._moveWindow(flagPeaks=flagPeaks, 
                                                                flagValleys=flagValleys,
                                                                startPoint=startPoint, 
                                                                endPoint=days,
                                                                highPrices=highPrices,
                                                                lowPrices=lowPrices, 
                                                                sizeBackForward=self.sizeBackForward)
        
        # for recent time (last two month), shrink the size of windows
        flagPeaks, flagValleys, endStartPoint = self._moveWindow(flagPeaks=flagPeaks, 
                                                                flagValleys=flagValleys,
                                                                startPoint=endStartPoint, 
                                                                endPoint=days,
                                                                highPrices=highPrices,
                                                                lowPrices=lowPrices, 
                                                                sizeBackForward=self.fineSizeBackForward)
        # for the most recent week                                                        
        flagPeaks, flagValleys, endStartPoint = self._moveWindow(flagPeaks=flagPeaks, 
                                                                flagValleys=flagValleys,
                                                                startPoint=endStartPoint, 
                                                                endPoint=days,
                                                                highPrices=highPrices,
                                                                lowPrices=lowPrices, 
                                                                sizeBackForward=self.finalSizeBackForward)
        
        # mark the prices by using flags
        #TODO the start and end consideration for peak and drop
        '''
        self.peakPrices = highPrices * np.array(flagPeaks)
        self.valleyPrices = lowPrices * np.array(flagValleys)
        '''
        self.peakPrices = [highPrices[i] for i in flagPeaks]
        self.valleyPrices = [lowPrices[i] for i in flagValleys]
        return self.peakPrices, self.valleyPrices, flagPeaks, flagValleys
        
    def _moveWindow(self, flagPeaks, flagValleys, startPoint, endPoint, highPrices,
                   lowPrices, sizeBackForward,isLast=False):
        '''
        @@summary:
        This function is to find the peak and trough within pre-defined window 
        size. 
        
        flagPeaks,flagValeys: lists that store peaks and troughs. might be a empty,
        might be not, in this case, the new peaks and troughs found should be appended.
        
        startPoint, endPoint: the first start point and the last end point of the window.
        
        sizeBackForward: a list with two elements. define the position of max(min) 
        element in the window
        
         
        '''
        
            
       
        # initialization
        # maxIdex and minIndex is 1 less than the startPoint so that it will 
        # trigger the first case in for loop)

        maxIndex = startPoint-1
        minIndex = startPoint-1
        midPosition = sizeBackForward[0] + startPoint
        endStartPoint = endPoint-sizeBackForward[0] - sizeBackForward[1]-1
        # the start point for each window ranges from startPoint to endStartPoint
            
        
        for windowStart in range(startPoint,endStartPoint):
            '''
            within each windown, we try to compare the price of middle point with
            the max point and min point within the window. 
            
            if it equals to the max point --> peak
            else --> trough
            
            after one iteration, the windown move a step forward. 
            
            NOTE: to improve the effciency, we only compare the max,min of previous
            window and the new coming point with the new middle point(if the previous
            max, min points still in the new window, if they are not, compare all
            points within new window with the new middle point) 
            '''
            # got the new middle prices in new window
            midDateHighPrice = highPrices[windowStart+sizeBackForward[0]]  
            midDateLowPrice = lowPrices[windowStart+sizeBackForward[0]] 
            # check if old max, min points still in the new window
            # if they aren't, try to find the new max, min points and record their
            # indices.
            if maxIndex == windowStart-1 or minIndex == windowStart-1:
                maxCandidates = highPrices[windowStart:windowStart+sizeBackForward[0]+sizeBackForward[1]+1] 
                minXCandidates = lowPrices[windowStart:windowStart+sizeBackForward[0]+sizeBackForward[1]+1]
                
                minIndex, minForPart = min(enumerate(minXCandidates), key=operator.itemgetter(1))
                maxIndex, maxForPart = max(enumerate(maxCandidates), key=operator.itemgetter(1))
                
                # convert to the absolute index value
                minIndex += windowStart
                maxIndex += windowStart
                
                
            else:
                # if they are, only compare max, min, new point, middle point

                maxCandidates = [maxForPart, midDateHighPrice, highPrices[windowStart+sizeBackForward[0]+sizeBackForward[1]]]
                minXCandidates = [minForPart, midDateLowPrice, lowPrices[windowStart+sizeBackForward[0]+sizeBackForward[1]]]
                maxForPart = max(maxCandidates)
                minForPart = min(minXCandidates)
            
            
            
            # check if either the max, min points equal to middle point 
            if  maxForPart == midDateHighPrice:
            # if max == middle  --> middle point is peak
                #flagPeaks[midPosition] = 1
                flagPeaks.append(midPosition)
            elif minForPart == midDateLowPrice:
            # else if min == middle --> middle point is trough
                #flagValleys[midPosition] = 1
                flagValleys.append(midPosition)

            # update the middle point    
            midPosition += 1
            
        
        return flagPeaks, flagValleys, endStartPoint
        
    def peakValleyPlot(self):
        fig = py.figure()
        fig.subplots_adjust(bottom=0.2)
        ax = fig.add_subplot(111)
        candlestick(ax,self.quotes, width=0.6)   
        ax.xaxis_date()
        ax.autoscale_view()
        setp( gca().get_xticklabels(), rotation=45, horizontalalignment='right')        
        # plot the peaks and valleys
        plot(self.quotes[:,0],self.peakPrices,'go',markersize = 6)
        
        plot(self.quotes[:,0],self.valleyPrices,'r^', markersize = 6)       
        #show()
        

class CurrentFlaggerSingleStock():
    def __init__(self, startDate, endDate, stockName,flags,tolerance,toler50,toler100,
                 flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,finalSizeBackForward,liveData,others=[]):
                     
        self.peakValleyFinder = PeakValleyFinderWin(startDate=startDate, endDate=endDate, 
                                                    stockName=stockName,
                                                    sizeBackForward=sizeBackForward,
                                                    fineSizeBackForward=fineSizeBackForward,
                                                    finalSizeBackForward=finalSizeBackForward,
                                                    others=others)
                                                    
        self.stock = stockName
        self.quotes = self.peakValleyFinder.getQuotes()
        '''
        self.peakPrices, self.valleyPrices = self.peakValleyFinder.getPeaksValleys()
        '''
        self.peakPrices,self.valleyPrices,self.flagPeaks,self.flagValleys=self.peakValleyFinder.getPeaksValleys()
        self.flagWeights = np.array(flagWeights)
        self.timeWeights = np.array(timeWeights)
        self.tolerance=tolerance
        self.toler50 = toler50
        self.toler100 = toler100
        self.flags=np.array(flags)
        self.periods = len(self.quotes)
        self.tradeType='None'
        self.score = 0
        self.flagIndicatorsCounter = []
        self.comparators = []
        self.annotation = []
        self.flagPrices=[]
        self.liveData = liveData
        self.currentPriceWeCare=0
    

        
        
        
    def getAnnotation(self):
        # return a copy of self.annotation
        # dont wanna change it unintentionally outside
        return deepcopy(self.annotation)
        

    def flagChecker(self,isBackTest=False):
        # choose one type of trade stradgy(long/short) based on the nearest points
        # then to find the flaging score of current price based on the stradgey type
                
        if isBackTest:
            self.checkAlgorithmBackTesting()
            
        else:
            self.checkAlgorithm() 
      
    
        
    def plot(self, savePic=False):
        self.plotByChange(savePic)
            
             
        
        
#    flagsDetails = self.annotation
#    return flagPrices, score,flagsDetals, tradeType
        
class FlaggerByChangeSingle(CurrentFlaggerSingleStock):
    '''
    @@summary: this calss is inheritated from CurrentFlaggerSingleStock
    overide the flagging method via flagger function
    overide the plot method via plot method
    '''
    def __init__(self, startDate, endDate, stockName,flags,tolerance,toler50,toler100,
                 flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,
                 finalSizeBackForward,liveData,others=[]):
                     
        CurrentFlaggerSingleStock.__init__(self, startDate, endDate, stockName,
                                           flags,tolerance,toler50,toler100,
                                           flagWeights, timeWeights, sizeBackForward,
                                           fineSizeBackForward,finalSizeBackForward,
                                           liveData,
                                           others=others)
                                           
        self.entryPrice = None
                 
    def checkAlgorithmBackTesting(self):
        '''
        @@summary: this function use the exact flag values to do the backtesting
        without the tolerence.
        '''
        # after this function, flags are minus flags if trade type is long
        self.comparators, self.comparatorIndices, oppoComparators, oppoComparatorIndices,self.currentPriceWeCare = self._shortLongChecker()
       
        timeAxis = self.quotes[:,0]
    
        ## rule out the invalid peaks and troughs based on higherhigh and lowerlow
        ## update the comparators, comparatorIndices based on the result.
        if self.tradeType == 'long':
#            dt = datetime.date.fromordinal(int(self.quotes[-1,0]) )
#            if dt.strftime('%Y%m%d') == '20080122':
#                pass
            # isValid may like [T, T, F, F,T,...]
            # is invalid by no means if less then the lowest
            notValid = oppoComparators<self.quotes[-1,4]
            
            # find the position of the last invalid point.
            # rule out the position before that
            if all(notValid) == True:
                minBoundary = oppoComparatorIndices[-1] 
            elif any(notValid) == False:
                minBoundary = -1
            else:
                minBoundary = oppoComparatorIndices[notValid][-1]
                
            isValid = self.comparatorIndices > minBoundary
            
            self.comparatorIndices = self.comparatorIndices[isValid]
            self.comparators = self.comparators[isValid]
            
            # if there is no valid flag point, score = 0 and return
            if self.comparators == []:
                self.score =0
                return
                    
            self.flagIndicatorsCounter = [[0 for row in range(len(self.comparators))] for col in range(len(self.flags))]
            
         
            
            for iflag, flag in enumerate(self.flags):
                desiredPrices = (flag+1)*self.comparators
                for comparatorIndex, desiredPrice in enumerate(desiredPrices):
                    if self.quotes[-1,4]<=desiredPrice<=self.quotes[-1,3]:
                        # and if there is no lower low < the desired Price
                        # --> flag the current price, record
                        position = self.comparatorIndices[comparatorIndex]
                        # all the previous lowest point should be larger than the desiredPrice
                        # disgard the last one of quotes
                        if all(self.quotes[position:-1,4]>= desiredPrice):
                            self.flagIndicatorsCounter[iflag][comparatorIndex] = 1
                           
                            price = self.comparators[comparatorIndex]
                            self.annotation.append([timeAxis[self.comparatorIndices[comparatorIndex]], round(price,2),str(self.flags[iflag]*100)+'%'])
                            
                            
                            ##### entry Price #####
                            ## some tricks: 1. the desired value of the largest valid flagger
                            ##              2. for same flagger, the desired value of the nearest
                            ## so just the last record would automatically holds the above two.
                            self.entryPrice = desiredPrice
                        
                        # if there is lower low, irrelevent. check the next desire price
                        else:
                            continue
                    # if the desired price is not within the range, check the next desire price                        
                    else:
                        continue
                    
                    
                            
        else:
            # the first true to the left end --> invalid(abandant)
                    
            # isValid may like [T, T, F, F,T,...]
            # is invalid by no means if less then the lowest
            notValid = oppoComparators>self.quotes[-1,3]
            dt = datetime.date.fromordinal(int(self.quotes[-1,0]) )
            if dt.strftime('%Y%m%d') == '20111013':
                pass
            # find the position of the last invalid point.
            # rule out the position before that
            if all(notValid) == True:
                minBoundary = oppoComparatorIndices[-1]
            elif any(notValid) == False:
                minBoundary = -1
            else:
                minBoundary = oppoComparatorIndices[notValid][-1] 
            isValid = self.comparatorIndices>minBoundary
            self.comparatorIndices = self.comparatorIndices[isValid]
            self.comparators = self.comparators[isValid]
            
            # if there is no valid flag point, score = 0 and return
            if self.comparators == []:
                self.score =0
                return
                    

            self.flagIndicatorsCounter = [[0 for row in range(len(self.comparators))] for col in range(len(self.flags))]
    
            
            
            for iflag, flag in enumerate(self.flags):
                desiredPrices = (flag+1)*self.comparators
                for comparatorIndex, desiredPrice in enumerate(desiredPrices):
                    if self.quotes[-1,4]<=desiredPrice<=self.quotes[-1,3]:
                        # and if there is no lower low < the desired Price
                        # --> flag the current price, record
                        position = self.comparatorIndices[comparatorIndex]
                        if all(self.quotes[position:-1,3] <= desiredPrice):
                            self.flagIndicatorsCounter[iflag][comparatorIndex] = 1
                            price = self.comparators[comparatorIndex]
                            self.annotation.append([timeAxis[self.comparatorIndices[comparatorIndex]], round(price,2),str(self.flags[iflag]*100)+'%'])
                            
                            
                            ##### entry Price #####
                            ## some tricks: 1. the desired value of the largest valid flagger
                            ##              2. for same flagger, the desired value of the nearest
                            ## so just the last record would automatically holds the above two.
                            self.entryPrice = desiredPrice
                        
                        # if there is lower low, irrelevent. check the next desire price
                        else:
                            continue
                    # if the desired price is not within the range, check the next desire price                        
                    else:
                        continue
        
            
        # construct the flaggers vectors of the flagbook
        ######   flaggers vector ########
        ## vec = [3,2,0,1,..]   len(vec) == no. of flags,  element == amount of peaks(troughs) that flag.
        
        self.score =sum( sum(self.flagIndicatorsCounter,1) *  np.array(self.flagWeights))
        print 'finish'  
            
            
        
        
        
    def checkAlgorithm(self):
        self.comparators, self.comparatorIndices, oppoComparators, oppoComparatorIndices,self.currentPriceWeCare = self._shortLongChecker()
        
        temp = self.currentPriceWeCare
        # use the live current data (5mins delay) if necessary
        if self.liveData == True:
            self.currentPriceWeCare = float(ystockquote.get_price(self.stock))
            if self.currentPriceWeCare == 0.0:
                self.currentPriceWeCare = temp
        
        timeAxis = self.quotes[:,0]
        # flagPoints is 2D list storing flagging points for each flag
        # initial as NaN for each element
        
        
        returns = self.currentPriceWeCare/self.comparators - 1
        

                
        upperBoundFlagging = [flag+self.tolerance if abs(flag)<0.5 else flag+self.toler50 if abs(flag)==0.5\
        else flag+self.toler100 for flag in self.flags]
        
        lowerBoundFlagging = [flag-self.tolerance if abs(flag)<0.5 else flag-self.toler50 if abs(flag)==0.5\
        else flag-self.toler100 for flag in self.flags]
        
#        upperBoundFlagging = self.flags + self.tolerance
#        lowerBoundFlagging = self.flags - self.tolerance

        self.flagIndicatorsCounter = [[0 for row in range(len(self.comparators))] for col in range(len(self.flags))]
        
        
        
        # iterate each relative change for that peaks or troughs with repect to current data    
        for position, returnE in reversed(list(enumerate(returns))):
            
            # using three steps to check if this peak or tough are interesting one
            # if it lower than lower Bound of all Flags, ignore
            if not True in (returnE >= lowerBoundFlagging):
                pass
                
            # if it high than upper Bound of all Flags, ignore
            elif not False in (returnE >= upperBoundFlagging):
                pass
            # if it within the tolenrence, find which flag it satisfied
            else:
                
                boundary1 = returnE >= lowerBoundFlagging
                boundary2 = returnE <= upperBoundFlagging
                

                for flagIndex in range(len(boundary1)):
                    if boundary1[flagIndex] and boundary2[flagIndex]:
                        ####################################
                        ## check the lower low/higher high #
                        ####################################
                        # iterate the oppoComparatorIndices
                        '''
                                                   <--
                        position      [..,..,..,..,..,]
                                      -->
                        oppoPosition  [..,..,..,..,..,]
                        '''
                        for oppoI in range(len(oppoComparatorIndices)):
                            # if out of range, do nothing
                            if self.comparatorIndices[position] > oppoComparatorIndices[oppoI]:
                                pass
                            # if within the range, compare the value with the current price
                            else:
                                # if long, compare the lower low
                                if self.tradeType == 'long':
                                    #if any lower low within range less than the current price
                                    # finish the flagchecker (all the peaks before is meaningless)
                                
                                    if any(oppoComparators[oppoI:] < self.currentPriceWeCare):
                                        self.score =sum( sum(self.flagIndicatorsCounter,1) *  np.array(self.flagWeights))
                                        return
                                    # if not, this flag is valid, go to next
                                    else:
                                        break
                                # if short, compare the higher high
                                else:
                                    # if any higher high within range is greater than current price
                                    # finish the process (all the troughs before is meaningless)

                                    if any(oppoComparators[oppoI:] > self.currentPriceWeCare):
                                        # exit the function, compute the whole score
                                        self.score =sum( sum(self.flagIndicatorsCounter,1) *  np.array(self.flagWeights))
                                        return 
                                    else:
                                        break
                            
                        # update the flagIndicatorCounter
                        self.flagIndicatorsCounter[flagIndex][position] = 1
                        # for each flaging peaks or trough, record its (x(time),y(price),flagging_indicator)
                        self.annotation.append([timeAxis[self.comparatorIndices[position]], round(self.comparators[position],2),str(self.flags[flagIndex]*100)+'%'])         
                        break

                            
    
        # compute the final score based on flagWeights and flagCounter                
        
        self.score =sum( sum(self.flagIndicatorsCounter,1) *  np.array(self.flagWeights))
        
                        
                        
        # find the correspoinding prices based on the flag matrices
       
        print 'finish'
        # for each flags
        
    def _shortLongChecker(self):
     
     
    # check which strategy should be applied(short/long)
    # from the current date track back
 
    
    # if the position of last peak behind that of valley
    # long it
        if self.flagPeaks[-1] > self.flagValleys[-1]:
            # long trade stradgy
            self.tradeType = 'long'
            currentPrice = self.quotes[-1,4]
            self.flags = -1*self.flags
            self.comparators = self.peakPrices
            self.comparatorIndices = self.flagPeaks
            oppoComparators = self.valleyPrices
            oppoComparatorIndices = self.flagValleys
            
                
        else:
            currentPrice = self.quotes[-1,3]
            # short trade stradgy
            self.tradeType = 'short'     
            self.comparators = self.valleyPrices
            self.comparatorIndices = self.flagValleys
            oppoComparators = self.peakPrices
            oppoComparatorIndices =self. flagPeaks
        
    
        return np.array(self.comparators), np.array(self.comparatorIndices),np.array(oppoComparators), np.array(oppoComparatorIndices),currentPrice
        
    def plotByChange(self, savePic):
        timeAxis=self.quotes[:,0]
        fig = py.figure()
        
        fig.subplots_adjust(bottom=0.2)
        ax = fig.add_subplot(111)
        candlestick(ax, self.quotes, width=0.6)
        
        ax.xaxis_date()
        ax.autoscale_view()
        setp( gca().get_xticklabels(), rotation=45, horizontalalignment='right')

        plot(timeAxis[self.flagPeaks],self.peakPrices,'go',markersize = 6)
        plot(timeAxis[self.flagValleys],self.valleyPrices,'r^', markersize = 6)
        

                     
                     
        if self.score != 0:
            # check if the peak or trough flag the current price    
            for i in range(len(self.comparators)):
                if sum(self.flagIndicatorsCounter,0)[i] == 0:
                    continue
                else:
                    
                    plot(timeAxis[self.comparatorIndices[i]], self.comparators[i], '*')
                    
             
        for e in self.annotation:
            time = e[0]
            price = e[1]
            flag = e[2]
            ax.annotate(str(price)+'('+flag+')',xy=(time,price))
                
        
        #ax.annotate(str(round(self.quotes[-1,4],2)),xy=(timeAxis[-1],self.quotes[-1,4]))
        ax.annotate(str(round(self.currentPriceWeCare,2)),xy=(timeAxis[-1],self.quotes[-1,4]))
        
        currentTime = str(datetime.date.fromordinal(int(timeAxis[-1]))) 
        title=['Flagging points for',self.tradeType,'trading strategy of',self.stock,currentTime]
        py.title(' '.join(title))
        py.grid()
        
        
        if savePic==True:
            if 1:
                py.savefig('pic/all/'+self.stock+currentTime+'.png', format='png')
            else:
                py.savefig('pic/sell_ft/'+self.stock+currentTime+'.png', format='png')
            py.clf()
            py.close()
        
                                            

        
 
class MultiObjFlagger():
    
    def __init__(self, startDate, endDate, stockNames,flags,tolerance,toler50,toler100,
                     flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,
                     finalSizeBackForward,saveToCsv,savePic,liveData=False):
        
        self.sellBook =[]
        self.buyBook=[]
        self.sellBookDataFrame=pd.DataFrame()
        self.buyBookDataFrame=pd.DataFrame()
        
        self.startDate = startDate
        self.endDate = endDate
        self.stockNames = stockNames
        self.flags = flags
        self.tolerance = tolerance
        self.toler50 = toler50
        self.toler100 = toler100
        self.flagWeights = flagWeights
        self.timeWeights = timeWeights
        self.sizeBackForward = sizeBackForward
        self.fineSizeBackForward = fineSizeBackForward
        self.finalSizeBackForward = finalSizeBackForward
        self.saveToCsv =  saveToCsv   
        self.savePic=savePic
        self.liveData = liveData
        self.stockNames = stockNames
        
    def flagCheckers(self):
        
#        self.mergeStock = mergeStock
        self.multiStrategy()

       
    
class MultiStockFlagger(MultiObjFlagger):
    def __init__(self,  startDate, endDate, stockNames,flags,tolerance,toler50,toler100,
                     flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,
                     finalSizeBackForward,saveToCsv,savePic,liveData=False):
        MultiObjFlagger.__init__(self, startDate, endDate, stockNames,flags,tolerance,toler50,toler100,
                     flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,
                     finalSizeBackForward,saveToCsv,savePic,liveData)
        
    def multiStrategy(self):
        stockNames = self.stockNames
        if type(stockNames) is str:
        
            dataobj = da.DataAccess('Yahoo')
        
            ls_symbols = dataobj.get_symbols_from_list(stockNames)    
        else:
            ls_symbols = stockNames
            
        
    
        
        for stock in ls_symbols:

            if stock =='ADT':
                pass
            
            '''
            for each stock, create object CurrentFlaggerSingleStock
            use the output of the object to creat report and plot the chart
            '''
            # use the
            stockFlagObj = FlaggerByChangeSingle(startDate = self.startDate,   
                                           endDate = self.endDate, 
                                           stockName = stock,
                                           flags=self.flags, 
                                           tolerance = self.tolerance, 
                                           toler50=self.toler50,
                                           toler100=self.toler100,
                                           flagWeights =self.flagWeights, 
                                           timeWeights = self.timeWeights,
                                           sizeBackForward=self.sizeBackForward,
                                           fineSizeBackForward=self.fineSizeBackForward,
                                           finalSizeBackForward=self.finalSizeBackForward,
                                           liveData=self.liveData)
                                           
            # check whether it's flagging using flagChecker method                              
            stockFlagObj.flagChecker()
            # using the result to make a report and plot the chart
            self._reportPlotMaker(stock,stockFlagObj)  
            
        
        
        # integrate the each report of the stock into one
        # NOTE: in sellBookDataFrame/buy, one line means one flag such that a
        # same stock can have many lines records
        columns = ['stockName','currentPrice','date_peak_or_trough','price(p,t)','indicator']
        if self.sellBook == []:
            self.sellBook = None
            
        if self.buyBook == []:
            self.buyBook = None
            
        self.sellBookDataFrame = pd.DataFrame(data=self.sellBook, columns=columns)    
        self.buyBookDataFrame = pd.DataFrame(data=self.buyBook, columns=columns)   

        if self.saveToCsv == True:
            self.buyBookDataFrame.to_csv('outputbuy'+'('+stockNames+')'+'.csv')
            self.sellBookDataFrame.to_csv('outputsell'+'('+stockNames+')'+'.csv')
            

        
        #return self.sellBookDataFrame, self.buyBookDataFrame
        

                
        
        
    def _reportPlotMaker(self,stock,stockFlagObj):
        '''
        this private function use the result generated by CurrentFlaggerSingleStock
        to classify 
        '''
        score, flagsDetails, tradeType, currentPrice = stockFlagObj.score,stockFlagObj.getAnnotation(),\
                                                           stockFlagObj.tradeType,stockFlagObj.currentPriceWeCare
        #print   flagsDetails
        if score == 0:
            print 'Finish ' + stock + ' no!!!!!'
            pass

        elif tradeType == 'long':
            for i in range(len(flagsDetails)):
                flagsDetails[i].insert(0,stock)
                flagsDetails[i].insert(1,currentPrice)
                self.buyBook.append(flagsDetails[i])
            if self.savePic == True:
                stockFlagObj.plot(savePic=self.savePic)
           
            
            print 'Finish ' + stock + ' buy!!!!!'
        else:
            # insert the stock name into each match flag
            # for each record item, the format
            # stockname | date(ordinal) | flagging price | flaging indicator
            for i in range(len(flagsDetails)):
                flagsDetails[i].insert(0,stock)
                flagsDetails[i].insert(1,currentPrice)
                self.sellBook.append(flagsDetails[i])
            if self.savePic == True:
                stockFlagObj.plot(savePic=self.savePic)
            print 'Finish ' + stock + ' sell!!!!!'
        
               
        
        
        
        
        
class MultiTimeFlagger(MultiObjFlagger):
    '''
    @@summary: this class is to flagger a single stock over a period.
    '''
    def __init__(self, startDate, endDate, stockName, flagPeriod, flags,tolerance,toler50,toler100,
                 flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,
                 finalSizeBackForward,saveToCsv,savePic,liveData=False,isBackTest=False):
                     
#        MultiObjFlagger.__init__(self, startDate, endDate, stockName,flags,tolerance,toler50,toler100,
#                     flagWeights, timeWeights, sizeBackForward,fineSizeBackForward,
#                     finalSizeBackForward,saveToCsv,savePic,liveData=False)
                     
        self.testStart = startDate
        self.testEnd = endDate
        self.stockName = stockName
        self.flagPeriod = flagPeriod
        
        self.flags = flags
        self.tolerance = tolerance
        self.toler50 = toler50
        self.toler100 = toler100
        self.flagWeights = flagWeights
        self.timeWeights = timeWeights
        self.sizeBackForward = sizeBackForward
        self.fineSizeBackForward = fineSizeBackForward
        self.finalSizeBackForward = finalSizeBackForward
        self.savePic = savePic
        self.isBackTest =isBackTest
        self.saveToCsv = saveToCsv
        self.isBackTest=isBackTest
        
        # Access all historical data required for back testing
        startAccessedData = (self.testStart[0]-self.flagPeriod, self.testStart[1],self.testStart[2]) 
        self.dataObj = Quotes(startAccessedData, self.testEnd, self.stockName)
             
    def multiStrategy(self):
        import datetime
        quotes = self.dataObj.dataAccess()
        
        # flagBook
        ###################################
        ##    date | name | entryPrice | flagger
        self.flagBook = []
        
        for periodStart in range(len(quotes)-self.flagPeriod*DAYSYEAR):
            periodEnd = periodStart+self.flagPeriod*DAYSYEAR

            objForDay = FlaggerByChangeSingle(startDate=None, endDate=None, stockName=self.stockName,
                                           flags=self.flags,tolerance=self.tolerance,
                                           toler50=self.toler50,toler100=self.toler100,
                                           flagWeights=self.flagWeights, timeWeights=self.timeWeights, 
                                           sizeBackForward=self.sizeBackForward,
                                           fineSizeBackForward=self.fineSizeBackForward,
                                           finalSizeBackForward=self.finalSizeBackForward,
                                           liveData=False, others = quotes[periodStart:periodEnd])
                                           
            
            objForDay.flagChecker(isBackTest=self.isBackTest)
            
            if objForDay.score > 0:
                print '!!!!!!!!!!!!!!',objForDay.tradeType
                flaggingDate = datetime.date.fromordinal(int(objForDay.quotes[-1,0]))
                tradeType = objForDay.tradeType
                #TODO: CHANGE THE SHARE VALUE
                
                
                print 'find 1'
                
                
                ################# record the flaggers for generating flag book ####
                vec = sum(objForDay.flagIndicatorsCounter,1)
                self.flagBook.append([flaggingDate, self.stockName,tradeType,
                                      objForDay.entryPrice,vec])
                if self.savePic:
                    objForDay.plot(savePic=self.savePic)
            
                
            print 'finish 1 day'
            
        if self.saveToCsv:
            
            pdflagBook = pd.DataFrame(data=self.flagBook,columns=['date','stockName',
            'tradeType','entryPrice','flagState'])
            pdflagBook.to_csv('backTestOrder.csv')
        return pdflagBook
        
    
                
                                        
                 
        


                     
                     
    
         
         
      
       
if __name__=='__main__':
                       
#    finder = PeakValleyFinderWin(startDate = (2012,9,29), 
#                                 endDate = (2014,9,30), 
#                                 stockName = 'BABA', 
#                                 sizeBackForward=30,
#                                 fineSizeBackForward=15)
#                 
#    a,b = finder.getPeaksValleys()
#    finder.plot()
#    c = FlaggerByChangeSingle(startDate = (2006,1,1),   
#                       endDate = (2008,1,22), 
#                       stockName = 'CAT',
#                       flags=[0.08,0.16,0.2,0.28,0.30,0.33,0.5,1], 
#                       tolerance = 0.0075, 
#                       toler50 = 0.02,
#                       toler100 = 0.025,
#                       flagWeights = [1,1,1,1,1,1,1,1], 
#                       timeWeights = False,
#                       sizeBackForward=[30,30],
#                       fineSizeBackForward=[15,15],
#                       finalSizeBackForward=[10,5],
#                       liveData=False)
#    #profile.run('c.flagChecker()')
#    c.flagChecker(isBackTest=False)                   
#    c.plot()
###    
#############################################################################
#    a  = MultiStockFlagger(startDate = (2012,9,29),   
#                       endDate = (2014,10,15), 
#                       stockNames = 'sp5002014',
#                       flags=[0.08,0.16,0.2,0.275,0.30,0.33,0.5,1], 
#                       tolerance = 0.0075, 
#                       toler50 = 0.02,
#                       toler100 = 0.025,
#                       flagWeights = [1,1,1,1,1,1,1,1], 
#                       timeWeights = False,
#                       sizeBackForward=[30,30],
#                       fineSizeBackForward=[15,15],
#                       finalSizeBackForward=[10,5],
#                       saveToCsv=True,savePic=False,liveData=False)
#    st = time.clock()
#    
#    a.flagCheckers()
#    t = time.clock()
#    d = t-st
#    print d
##                       
                       
############################  test over several market #######################

    #marketList = ['ftse1002014','sp5002014','stoxx502014','aex252014','cac402014','ibex352014','mib402014']
#    marketList = ['stoxx502014']
#    for marketName in marketList:
#        a  = MultiStockFlagger(startDate = (2012,9,29),   
#                           endDate = (2014,10,17), 
#                           stockNames = marketName,
#                           flags=[0.08,0.16,0.2,0.275,0.30,0.33,0.38,0.5,1], 
#                           tolerance = 0.0075, 
#                           toler50 = 0.02,
#                           toler100 = 0.025,
#                           flagWeights = [1,1,1,1,1,1,1,1], 
#                           timeWeights = False,
#                           sizeBackForward=[30,30],
#                           fineSizeBackForward=[15,15],
#                           finalSizeBackForward=[10,5],
#                           saveToCsv=True,savePic=True,liveData=False)
#        st = time.clock()
#        
#        a.flagCheckers()
#        t = time.clock()
#        d = t-st
#        print d

############################### Back testing for one stock ####################
##
    btOneStock = MultiTimeFlagger(startDate=(2010,1,1), endDate=(2013,2,14), stockName='CAT', 
                                  flagPeriod=2, flags=[0.16,0.2,0.28,0.30,0.33,0.5,1], 
                                  tolerance = 0.0075, 
                                  toler50 = 0.02,
                                  toler100 = 0.025,
                                  flagWeights = [1,1,1,1,1,1,1], 
                                  timeWeights = False,
                                  sizeBackForward=[30,30],
                                  fineSizeBackForward=[15,15],
                                  finalSizeBackForward=[10,5],savePic=False,saveToCsv=True,
                                  isBackTest=True)
    a = btOneStock.flagCheckers()