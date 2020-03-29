from cumulativeCurve.interpolate import Interpolate

import unittest

import numpy as np


class interpolateTest(unittest.TestCase):
    def setUp(self):
        """cnt是累积计数和pct是累积百分比"""
        cnt0=np.array([10,20,30,40,50,60,70,80,90,100,100,100,100,200])
        bin0=np.array([ 1, 2, 3, 4, 5, 5, 5, 5, 5,  6,  7,  8,  9, 10])
        self.cntBin=Interpolate(cnt0,bin0,1)
        
        bin1=np.array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10,  11])
        cnt1=np.array([ 0,100,200,300,400,500,600,700,800,900,1000])
        self.binCnt=Interpolate(bin1,cnt1)      

    def test_innerEval(self):
        """测试内插"""
        self.assertEqual(self.cntBin.innerEval(15),1.5)    
        self.assertEqual(self.cntBin.innerEval(40),4)    
        """"相同的x取最大的y"""
        self.assertEqual(self.cntBin.innerEval(100),9)    
        self.assertEqual(self.cntBin.innerEval(150),9.5)    
        
    def test_eval(self):
        """测试边界"""
        self.assertEqual(self.cntBin.eval(9),0)    
        self.assertEqual(self.cntBin.eval(10),1)                                     
        self.assertEqual(self.cntBin.eval(200),10)    
        self.assertEqual(self.cntBin.eval(300),10)    

        self.assertEqual(self.binCnt.eval(0),0)    
        self.assertEqual(self.binCnt.eval(1),0)                                     
        self.assertEqual(self.binCnt.eval(11),1000)    
        self.assertEqual(self.binCnt.eval(12),1000)    

    def test_innerEvalFast(self):
        """测试快速定位"""
        self.assertEqual(self.cntBin.innerEvalFast(15,0),(1.5,1))    
        """输入的iatart与x值不符，系统不判断"""
        self.assertEqual(self.cntBin.innerEvalFast(30,7),(5  ,7))            
        self.assertEqual(self.cntBin.innerEvalFast(70,7),(5  ,7))    

    def test_evalArray(self):
        """测试数组"""
        cnts=[0,10,50,90,100]
        self.assertListEqual(self.cntBin.evalArray(cnts,sorted=True).tolist(),[0, 1, 5, 5, 9])
        cnts=[0,50,10,100,90]
        self.assertListEqual(self.cntBin.evalArray(cnts,sorted=False).tolist(),[0, 5, 1, 9, 5])
        