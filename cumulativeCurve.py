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
  def __init__(x,y,delta=0):  
    assert(len(x)=len(y))
    self._N=len(x)
    self._x=x
    self._y=y
    self._delta=delta
    self._xmax=x[-1]
    self._xmin=x[0]
    self._ymax=y[-1]
    self._ymin=y[0]
    k=[np.inf if (self._y[i+1]==self._y[i]) else (self._x[i+1]-self._x[i])/(self._y[i+1]-self._y[i]) for i in range(self._N-1)]
  
  def __init__(xy,delta=0):  
    self._N
    self._x=xy[0]
    self._y=xy[1]
    self._delta=delta
    self._xmax=self._x[-1]
    self._xmin=self._x[0]
    self._ymax=self._y[-1]
    self._ymin=self._y[0]
    k=[np.inf if (self._y[i+1]==self._y[i]) else (self._x[i+1]-self._x[i])/(self._y[i+1]-self._y[i]) for i in range(self._N-1)]

  def eval(self, x):
    if x>= self._xmax : return self._ymax
    if x< self._xmin :  return self._ymin-delta
    
    i=1
    while (i<self._N) :
      if x > x[i] : i=i+1

    if x==self._x[i-1] : return self._y[i-1]
    
    return y[i]-k*(x[i]-x)
    
class cumulativeCurve :
  def __init__(self, pb=none):
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
     self._pb=np.hstack((range(0,101,1),[0.1,0.5,99.5,99.9],[0.27,4.55,95.45,99.73]))
     self._pb.sort()

   self._N=0
   self._bin=none
   
  def curveFromBin(self,binValues,sorted = False,delta=1) :
    if not sorted :
      binValues.sort()
    self._N=binValues.size    
    binCumulateCountPercentage=np.array(range(1,self._N+1,1))*100/self._N
    li=linearInterpolate(binCumulateCountPercentage,binValues,delta)
    self._bin=np.array([li.eval(x) for x in self._pb])
    self._linearInterpolateFromBin=none
    self._linearInterpolateFromPercentage=none
    
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
    
  def max(self) :
    return self._bin[-1]
    
  def mix(self) :
    return self._bin[0]+delta
    
  def count(self) :
    return self._N
    
  def p(self,r) :
    if not self._linearInterpolateFromPercentage :
      self._linearInterpolateFromPercentage=linearInterpolate(_pb,_bin,0)
    _linearInterpolateFromPercentage.eval(r)  
    
  def median(self) :
    return p(self,50)  
   
  def cumulativeCount(self,b) :
    if not self._linearInterpolateFromBin :
      self._linearInterpolateFromBin=linearInterpolate(_bin,_pb,0)
    self._linearInterpolateFromBin(b)*self._N

  def binCount(self,a,b) :
    cumulativeCount(self,b) - cumulativeCount(self,a) 
    
class cumulativeCurve :

   
binValues=np.loadtxt("20200101.txt",delimiter=',', usecols=(2), unpack=True)
binValues.sort()
_N=binValue.size
_pb=np.hstack((range(0,101,1),[0.1,0.5,99.5,99.9],[0.27,4.55,95.45,99.73]))
_pb.sort()

'''
  binValues: np.arrar递增序列，可以重复
  pb: 累积百分比序列递增序列，不可重复，0开始，100结束
  
  返回List，元素是与pb对应的分位值bin，小于等于bin的元素个数为pb
'''
def curveFromBin(binValues,pb):
  _N=binValues.size
  binCumulateCountPercentage=np.array(range(1,_N+1,1))*100/_N
  return [_linearInterpolate(x,binCumulateCountPercentage,binValues) for x in _pb]


dt = np.dtype([('bin',  'float'),('count',  int)])
binValues1=np.loadtxt("20200101.txt",delimiter=',', usecols=(2), unpack=True,dtype=dt)
binValues1.sort()
bin1=curveFromBin(binValues1,_pb)

binValues2=np.loadtxt("20200102.txt",delimiter=',', usecols=(2), unpack=True)
binValues2.sort()
bin2=curveFromBin(binValues2,_pb)

bins=np.unique(np.hstack((bin1,bin2)))
  
bin_sum= [ _linearInterpolate(x,np.array(bin1),_pb*bin1[-1]/100,delta=0) +_linearInterpolate(x,np.array(bin2),_pb*bin2[-1]/100,delta=0) for x in bins]
 
[ _linearInterpolate(x,np.array(bin_sum)/bin_sum[-1],bins,delta=0) for x in _pb]
 
  
_delta=1

 _pb: np.array
     概率分档
     缺省为[0,0.1,0.27,0.5,1,2...4,4.55,5...95,95.45,96,98,99,99.5,99.73,99.9,100]
	 递增
	 增加0.1,0.27,0.5,4.55和95.45,99.5,99.73,99.9可以改善类似正态分布的两端密度过小，导致bin区间过大
	   0.27,4.55,95.45,99.73分别对应正态分布的3std和2std
 _bin: np.array 
     元素是每个概率点对应的值，表示<=bin的概率
     _bin[0]=输入数据最小值-_delta
	 _bin[-1]=输入数据最大值
	 递增，可以重复	 
 _cnt: np.array 
     元素是每个概率点对应的频数上限，_bins*_N，是浮点值
     floor(_bin*_N)是<=bin的频数
	 递增	  
 _interpolatFromBin: 用vBin值线性插值，返回_count

filepattern=sys.argv[1]
outfile=sys.argv[2]
v=[]
for fname in sorted(glob.glob(filepattern)):
  with open(fname,'rt') as f:
    reader=csv.reader(f)
    for row in reader:
      v.append(int(row[2]))

v.sort()
vlen=len(v)

with open(outfile,'wt') as f:
  writer=csv.writer(f)
  writer.writerow((v[0],0,1/vlen))  
  for i in range(1,100):
    d=i*vlen/100
    dfloor=math.floor(d)
    dceil=math.ceil(d)
    if (dceil>dfloor):
      writer.writerow((v[dfloor]+(v[dceil]-v[dfloor])*(d-dfloor),i,d))
    else:
      writer.writerow((v[dfloor],i,d))
  writer.writerow((v[-1],100,vlen))


