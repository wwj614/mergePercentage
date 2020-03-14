# -*- coding: utf-8 -*-
"""
累积概率密度曲线
"""

import numpy as np

import csv
import sys
import math
import os.path
import glob

class linearInterpolate:
  def __init__(self,x,y,delta=0):  
    assert(len(x)==len(y))
    self._N=len(x)
    self._x=x
    self._y=y
    self._delta=delta
    self._xmax=x[-1]
    self._xmin=x[0]
    self._ymax=y[-1]
    self._ymin=y[0]
    self._k=[np.inf if (self._x[i+1]==self._x[i]) else (self._y[i+1]-self._y[i])/(self._x[i+1]-self._x[i]) for i in range(self._N-1)]
  
  def eval(self, x):
    if x>= self._xmax : return self._ymax
    if x< self._xmin :  return self._ymin-self._delta
    
    i=0
    while (i<self._N): 
      if x >= self._x[i] : i=i+1
      else : break
      
    if x==self._x[i-1] : return self._y[i-1]
    '''if (self._k[i-1]==np.inf) : return self._y[i]'''
    
    return self._y[i]-self._k[i-1]*(self._x[i]-x)


    
class cumulativeCurve :
  def __init__(self, pb=None):
    """
    累积概率曲线定义为小于等于bin值的概率
      最大值对应100
      最小值对应1/Count，略大于0，因此概率0对应的bin值取为min-delta
    pb: 累积概率曲线的概率分档点，缺省为
      range(0,101,1),[0.1,0.5,99.5,99.9],[0.27,4.55,95.45,99.73]
    delta: 原始数据的min和累积概率为0时分档bin间的差，缺省为  
      0  
    """
    if pb : 
      self._pb=pb
    else :
      self._pb=np.hstack((range(0,101,1),[0.01,0.1,0.5,99.5,99.9,99.99],[0.27,4.55,95.45,99.73]))
      self._pb.sort()
    
    self._N=0
    self._bin=None
   
  def curveFromBin(self,binValues,sorted = False,delta=1) :
    if not sorted :
      binValues.sort()
    self._N=len(binValues)    
    binCumulateCountPercentage=np.array(range(1,self._N+1,1))*100/self._N
    li=linearInterpolate(binCumulateCountPercentage,binValues,delta)
    self._bin=np.array([li.eval(x) for x in self._pb])
    self._linearInterpolateFromBin=None
    self._linearInterpolateFromPercentage=None
    
  def curveFromBinCount(self,binCounts,sorted = False,delta=1) :
    n=len(binCounts)
    bins=np.empty[n]
    counts=np.empty[n]
    bins[0]=binCounts[0][0]
    counts[0]=binCounts[0][1]
    for i in range[1,n] :
      bins[i]=binCounts[i][0]
      counts[i]=counts[i-1]+binCounts[i][1]
    
    self._N=counts[-1]    
    binCumulateCountPercentage=counts*100/self._N
    li=linearInterpolate(binCumulateCountPercentage,bins,delta)
    self._bin=np.array([li.eval(x) for x in self._pb])
    self._linearInterpolateFromBin=none
    self._linearInterpolateFromPercentage=none

  def saveCurve(self,filename) :
    with open(filename,'wt') as f:
      writer=csv.writer(f)
      for i in range(len(self._pb)):
        writer.writerow((self._bin[i],self._pb[i],self._pb[i]*self._N/100))
  
  @staticmethod
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
    li=linearInterpolate(binCounts*100/newTotal,bs,0) 
    newbin=np.array([li.eval(p) for p in pb])    
    return (newbin,pb,pb*newTotal/100)  
          
  def loadCurve(self,filename) :
    self._bin,self._pb=np.loadtxt(filename,delimiter=',', usecols=(0,1), unpack=True,dtype=dt)
    self._N=self._bin[-1]
    
  def max(self) :
    return self._bin[-1]
    
  def min(self) :
    '''比实际的最小值小计算curve时小delta'''
    return self._bin[0]
    
  def count(self) :
    return self._N
    
  def p(self,r) :
    if self._linearInterpolateFromPercentage is None :
      self._linearInterpolateFromPercentage=linearInterpolate(self._pb,self._bin,0)
    return self._linearInterpolateFromPercentage.eval(r)  
    
  def median(self) :
    return self.p(self,50)  
   
  def cumulativeCount(self,b) :
    if not self._linearInterpolateFromBin :
      self._linearInterpolateFromBin=linearInterpolate(_bin,_pb,0)
    return self._linearInterpolateFromBin(b)*self._N

  def binCount(self,a,b) :
    return self.cumulativeCount(self,b) - self.cumulativeCount(self,a) 


pb=np.hstack((range(0,101,1),[0.01,0.1,0.5,99.5,99.9,99.99],[0.27,4.55,95.45,99.73]))
pb.sort()
c=cumulativeCurve()
v=[]
for fname in sorted(glob.glob("202001??.txt")):
  bv=np.loadtxt(fname,delimiter=',', usecols=(2), unpack=True)
  v.append(bv)  
  c.curveFromBin(bv)
  c.saveCurve(fname+"cur")
  
vs=np.hstack(v).ravel()
vs.sort()
c.curveFromBin(vs)
c.saveCurve("202001XX.cur")

cs=[]
for fname in sorted(glob.glob("202001??.txtcur")):
  c=np.loadtxt(fname,delimiter=',', usecols=(0,2), unpack=True)
  cs.append(c)  
res=cumulativeCurve.merge(cs,pb)
with open("202001XX.est",'wt') as f:
  writer=csv.writer(f)
  for i in range(len(pb)):
    writer.writerow((res[0][i],res[1][i],res[2][i]))

