# -*- coding:utf-8 -*-

import numpy as np
import math


class Interpolate:

    """
    内插
      x:必须递增，允许相同，相同时k为np.inf
      x和y的长度必须相等
      大于xMax，返回yMax
      小于xMin，返回yMin-delta
    """

    def __init__(self, x: np.array, y: np.array, delta=0):
        assert(len(x) == len(y))
        self._N = len(x)
        self._x, self._y = x, y
        self._delta = delta
        self._xmin, self._xmax = x[0], x[-1]
        self._ymin, self._ymax = y[0], y[-1]
        self._k = [np.inf
                   if (self._x[i+1] == self._x[i])
                   else (self._y[i+1] - self._y[i]) /
                        (self._x[i+1] - self._x[i])
                   for i in range(self._N - 1)]

    def __hash__(self):
        return hash((self._x.tobytes(), self._y.tobytes(), self._delta))
        
    def __expr__(self):
        return "x: {}\ny: {}\ndelta: {}".format(self._x, self._y, self._delta)
        
    @staticmethod
    def almostEqual(a,b):
        if a==b: 
            return True
        if a.__class__ != b.__class__: 
            return False 
        if a._delta != b._delta : 
            return False 
        if a._N != b._N : 
            return False 
        if ((max(abs(a._x - b._x)) < 1E-5) and
            (max(abs(a._y - b._y)) < 1E-5)): 
            return True        
        return False   
        
    def innerEval(self, x):
        '''
        x>_xmin and x<_xmix 一定是内插
        '''
        assert(x >= self._xmin and x < self._xmax)
        i = np.searchsorted(self._x, [x], side="right")[0]
        if x == self._x[i - 1]:
            return self._y[i - 1]
        return self._y[i] - self._k[i-1] * (self._x[i]-x)

    def eval(self, x):
        if x >= self._xmax:
            return self._ymax
        if x < self._xmin:
            return self._ymin - self._delta
        return self.innerEval(x)

    def innerEvalFast(self, x, istart):
        '''
        x>_xmin and x<_xmix 一定是内插
        从istart开始搜索插入节点
        x<_x[istart]表示_x[istart-1]<= x <_x[istart]
        '''
        assert(x >= self._xmin and x < self._xmax)

        i = istart
        while (i < self._N and x >= self._x[i]):
            i += 1

        if x == self._x[i - 1]:
            return self._y[i - 1], i

        assert(self._k[i - 1] != np.inf)
        return self._y[i] - self._k[i-1] * (self._x[i] - x), i

    def evalFast(self, x, istart):
        if x >= self._xmax:
            return self._ymax, istart
        if x < self._xmin:
            return self._ymin - self._delta, istart
        return self.innerEvalFast(x, istart)

    def evalArray(self, xs, sorted=False):
        '''
        xs是np.array
        '''
        if sorted:
            n = len(xs)
            res = np.zeros(n)
            istart = 0
            for i in range(n):
                res[i], istart = self.evalFast(xs[i], istart)
            return res
        else:
            return np.array([self.eval(x) for x in xs])
