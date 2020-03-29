# -*- coding: utf-8 -*-
import numpy as np
import collections

import csv
import sys
import math
import os.path
import glob

from interpolate import Interpolate

class CumulativeCurve :
    """
    累积概率曲线定义为小于等于bin值的概率
      最大值对应100
      最小值对应1/Count，略大于0，因此概率0对应的bin值取为min-delta
    pb: 累积概率曲线的概率分档点，缺省为
      range(0,101,1),[0.01,0.1,0.5,99.5,99.9,99.99],[0.27,4.55,95.45,99.73]
    delta: 原始数据的min和累积概率为0时分档bin间的差，缺省为  
      0  
    """
    def __init__(self,bin,cnt) :
        self._bin=bin
        self._cnt=cnt
        self._N=cnt[-1]
        self._pb=cnt*100/self._N 
        self._interpolateFromPercentage=None
        self._interpolateFromBin=None
        
    @staticmethod  
    def load(filename) :
        """
        with open(filename, "r", encoding="UTF-8") as source:
            objects=json.load(source, object_hook= blog_decode)
        """    
        objects=None
        return objects
          
    def save(self,filename) :
        """
        with open(filename, "w", encoding="UTF-8") as target:
    　　    json.dump( self, target, separators=(',', ':'), default=blog_j2_encode )
        """
        pass
        
    @staticmethod  
    def importCSV(filename) :
        bin,cnt=np.loadtxt(filename,delimiter=',', usecols=(0,1,2), unpack=True)
        return cumulativeCurve(bin,cnt)
   
    def exoortCSV(self,filename) :
        with open(filename,'wt') as f:
            writer=csv.writer(f)
            for i in range(len(self._pb)):
                writer.writerow((self._bin[i],self._pb[i],self._cnt))
   
    @property  
    def max(self) :
        return self._bin[-1]
      
    @property
    def min(self) :
        '''比实际的最小值小delta'''
        return self._bin[0]
      
    @property
    def count(self) :
        return self._N
      
    def p(self,r) :
        if self._interpolateFromPercentage is None :
            self._interpolateFromPercentage=Interpolate(self._pb,self._bin,0)
        return self._interpolateFromPercentage.innerEval(r)  
      
    @property
    def median(self) :
        return self.p(50)  
     
    def cumulativeCount(self,b) :
        if not self._interpolateFromBin :
            self._interpolateFromBin=Interpolate(self._bin,self._cnt,0)
        return self._interpolateFromBin.eval(b)
   
    def cumulativePercentage(self,b) :
        if not self._interpolateFromBin :
            self._interpolateFromBin=Interpolate(_bin,_cnt,0)
        return self._interpolateFromBin(b)/self._N
   
    def rangeCount(self,a,b) :
        return self.cumulativeCount(self,b) - self.cumulativeCount(self,a) 
   
    def binCount(self) :
        cntlen=len(self._cnt)-1
        c=np.zeros(cntlen)
        b=np.zeros(cntlen)
        for i in range(cntlen):
            c[i]= self._cnt[i+1]-self._cnt[i]
            b[i]=(self._bin[i+1]+self._bin[i])/2
        return (b,c)
   
    @property
    def sum(self) :
        bs,cs=self.binCount()
        s=0
        for (b,c) in zip(bs,cs):
            s+=b*c
        return s
      
    @property
    def sum2(self) :
        b,c=self.binCount()
        s2=0
        for (b,c) in zip(bs,cs):
          s2+=b*b*c
        return s2
      
    @property
    def avg(self) :
        return self.sum()/self._N
      
    @property
    def std(self) :
        s=self.sum()
        s2=self.sum2()
        n=self._N
        assert(n>1)
        return sqrt((s2-s*s)/n/(n-1))
   
    def sample(n=1) :
        assert(n>0)
        if n==1 :
            return self.p(np.random.rand())
        else :
            return [self.p(np.random.rand()) for i in range(n)]
      
def curveFromBin(binValues,pb,delta=1) :
    '''
    binValues: 经排序的数值列表  
    '''
    N=len(binValues)    
    binCumulateCount=np.array(range(1,N+1))
    li=Interpolate(binCumulateCount,binValues,delta)
    cnt=pb*N/100
    bin=np.array([li.eval(x) for x in cnt])
    return CumulativeCurve(bin,cnt)

def curveFromBinCount(binCounts,pb,delta=1) :
    '''
    binCounts: 元素为(bins，counts)元组的列表
    '''
    from collections import Counter
    c0=Counter
    for (bins,counts) in binCounts :
        for (bin,cnt) in zip(bins,counts) :
            c0[bin] +=cnt
   
    c1 = sorted(c0.items(), key=lambda item: item[0])
    clen=len(c1)
    bins=np.zeros(clen)
    binCumulateCount=np.zeros(clen)
   
    bins[0]=c1[0][0]
    binCumulateCount[0]=c1[0][1]
    for i in range(1,clen) :
        bins[i]=c1[i][0]
        binCumulateCount[i]=binCumulateCount[i-1]+c1[i][1]
    
    N=binCumulateCount[-1]
    li=Interpolate(binCumulateCount,bins,delta)
    cnt=pb*N/100
    bin=np.array([li.eval(x) for x in cnt])  
    return CumulativeCurve(bin,cnt)
    
def merge(curvers,pb) :
    binList=[]    
    for c in curvers :
      binList.append(c[0])
    bs=np.unique(np.ravel(np.array(binList)))
   
    bsLen=len(bs)
    binCounts=np.zeros(bsLen)
   
    for (cbin,cCount) in curvers :
      li=linearInterpolate(cbin,cCount,0)
      cs=[li.eval(b) for b in bs]
      binCounts=binCounts+cs
   
    newTotal=binCounts[-1]
    li=Interpolate(binCounts*100/newTotal,bs,0) 
    newbin=np.array([li.innerEval(p) for p in pb])    
    return (newbin,pb,pb*newTotal/100)  
  

