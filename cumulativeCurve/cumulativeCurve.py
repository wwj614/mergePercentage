# -*- coding: utf-8 -*-
import numpy as np
import collections

import csv
import math
import os.path

from interpolate import Interpolate


class CumulativeCurve:
    """
    累积概率曲线定义为小于等于bin值的概率
      最大值对应100
      最小值对应1/Count，略大于0，因此概率0对应的bin值取为min-delta
    pb: 累积概率曲线的概率分档点，缺省为
      range(0,101,1),[0.01,0.1,0.5,99.5,99.9,99.99],[0.27,4.55,95.45,99.73]
    delta: 原始数据的min和累积概率为0时分档bin间的差，缺省为
      0
    """
    pb=np.hstack((range(0,101,1),[0.01,0.1,0.5,99.5,99.9,99.99],[0.27,4.55,95.45,99.73]))
    pb.sort()
    
    def __init__(self, bin, cnt):
        self._bin, self._cnt = bin, cnt
        self._N = cnt[-1]
        self._pb = cnt * 100 / self._N
        self._interpolateFromPct = None
        self._interpolateFromBin = None
        self._sum = None
        self._sum2 = None

    def __hash__(self):
        return hash((self._bin.tobytes(), self._cnt.tobytes()))
        
    def __repr__(self):
        return "bin: {}\ncnt: {}\n".format(self._bin, self._cnt)
        
    @staticmethod
    def almostEqual(a,b):
        if a==b: 
            return True
        if a.__class__ != b.__class__: 
            return False 
        if a._N != b._N : 
            return False 
        if ((max(abs(a._bin - b._bin)) < 1E-5) and
            (max(abs(a._cnt - b._cnt)) < 1E-5)): 
            return True        
        return False   

    @staticmethod
    def importCSV(filename):
        """
        文件格式
        bin         pb    cnt
        13518.0 ,  0.0,   0.0
        15635.97, 0.01, 7.705
        ......
        """
        bin, cnt = np.loadtxt(filename, delimiter=',',
                              usecols=(0, 2), unpack=True)
        return CumulativeCurve(bin, cnt)

    def exportCSV(self, filename):
        with open(filename, 'wt') as f:
            writer = csv.writer(f)
            for i in range(len(self._pb)):
                writer.writerow((self._bin[i], self._pb[i], self._cnt[i]))

    def getCurve(self):
        return self._bin, self._cnt

    @property
    def max(self):
        return self._bin[-1]

    @property
    def min(self):
        '''比实际的最小值小delta'''
        return self._bin[0]

    @property
    def count(self):
        return self._N

    def p(self, r):
        if self._interpolateFromPct is None:
            self._interpolateFromPct = Interpolate(self._pb, self._bin, 0)
        return self._interpolateFromPct.innerEval(r)

    @property
    def median(self):
        return self.p(50)

    def cumulativeCount(self, b):
        if not self._interpolateFromBin:
            self._interpolateFromBin = Interpolate(self._bin, self._cnt, 0)
        return self._interpolateFromBin.eval(b)

    def cumulativePercentage(self, b):
        if not self._interpolateFromBin:
            self._interpolateFromBin = Interpolate(self._bin, self._cnt, 0)
        return self._interpolateFromBin.eval(b) / self._N

    def rangeCount(self, a, b):
        return self.cumulativeCount(b)-self.cumulativeCount(a)

    def binCount(self):
        cntlen = len(self._cnt)
        v = []
        v.append((self._bin[0], 0))
        for i in range(1, cntlen):
            v.append(((self._bin[i] + self._bin[i-1]) / 2,
                      self._cnt[i] - self._cnt[i-1]))
        v.append((self._bin[-1], 0))
        return v

    @property
    def sum(self):
        if self._sum is not None:
          return self._sum
        s = 0
        for b, c in self.binCount():
            s += b * c
        self._sum = s    
        return s

    @property
    def sum2(self):
        if self._sum2 is not None:
          return self._sum2
        s2 = 0
        for b, c in self.binCount():
            s2 += b * b * c
        self._sum2 = s2    
        return s2

    @property
    def avg(self):
        return self.sum / self._N

    @property
    def std(self):
        s = self.sum
        s2 = self.sum2
        n = self._N
        assert(n > 1)
        return math.sqrt((s2 - s * s / n) / (n - 1))

    def sample(n=1):
        assert(n > 0)
        if n == 1:
            return self.p(np.random.rand())
        else:
            return [self.p(np.random.rand()) for i in range(n)]

    @staticmethod
    def curveFromBin(binValues, pb, delta=1):
        '''
        binValues: 经排序的数值列表
        '''
        N = len(binValues)
        binCumulateCount = np.array(range(1, N + 1))
        li = Interpolate(binCumulateCount, binValues, delta)
        cnt = pb * N / 100
        bin=li.evalArray(cnt, sorted=True)
        return CumulativeCurve(bin, cnt)

    @staticmethod
    def curveFromBinCount(binCounts, pb, delta=1):
        '''
        binCounts: 元素为(bin，count)元组的列表，可以是多次累积，bin可以无序
        '''
        from collections import Counter
        c0 = Counter()
        for bin, cnt in binCounts:
            c0[bin] += cnt

        c1 = sorted(c0.items(), key=lambda item: item[0])
        clen = len(c1)

        if c1[0][1] == 0:
            b = np.zeros(clen)
            binCumulateCount = np.zeros(clen)
            b[0] = c1[0][0]
            binCumulateCount[0] = 0
            for i in range(1, clen - 1):
                b[i] = b[i - 1] + 2 * (c1[i][0] - b[i - 1])
                binCumulateCount[i] = binCumulateCount[i - 1] + c1[i][1]
            b[-1] = c1[-1][0]
            binCumulateCount[-1] = binCumulateCount[-2]
        else:
            b = np.zeros(clen + 1)
            binCumulateCount = np.zeros(clen + 1)
            b[0] = c1[0][0] - delta
            binCumulateCount[0] = 0
            for i in range(clen):
                b[i + 1] = c1[i][0]
                binCumulateCount[i + 1] = binCumulateCount[i] + c1[i][1]

        N = binCumulateCount[-1]
        li = Interpolate(binCumulateCount, b, 0)
        cnt = pb * N / 100
        bin=li.evalArray(cnt, sorted=True)
        return CumulativeCurve(bin, cnt)

    @staticmethod
    def merge(curves, pb):
        """
        curves: 元素为(bins，counts)元组的列表
        """  
        binList = []
        for c in curves:
            binList.append(c[0])
        bs = np.unique(np.ravel(np.array(binList)))

        bsLen = len(bs)
        binCounts = np.zeros(bsLen)

        for cbin, cCount in curves:
            li = Interpolate(cbin, cCount, 0)
            cs=li.evalArray(bs, sorted=True)
            binCounts = binCounts + cs

        newTotal = binCounts[-1]
        li = Interpolate(binCounts * 100 / newTotal, bs, 0)
        newbin=li.evalArray(pb, sorted=True)
        return CumulativeCurve(newbin, pb * newTotal / 100)
