import unittest

import numpy as np
import os
import csv

from cumulativeCurve import CumulativeCurve,curveFromBin


def cumulativeCurve_eq(a,b):
    if a==b : return True
    if a.__class__ != b.__class__ : return False 
    if a._N != b._N : return False 
    print (max(abs(a._bin-b._bin)))
    if ((max(abs(a._bin-b._bin)) < 1E-6) and
        (max(abs(a._pb -b._pb)) < 1E-6) and
        (max(abs(a._cnt-b._cnt)) < 1E-6) ): return True        
    return False   
        
class cumulativeCurveTest(unittest.TestCase):
    def setUp(self):
        x=[1,2,3,4,5,5,5,8,9,10]
        y=[11,21,31,41,51,61,81,81,81,101]
        self.pb=np.hstack((range(0,101,1),[0.01,0.1,0.5,99.5,99.9,99.99],[0.27,4.55,95.45,99.73]))
        self.pb.sort()
        bin0=np.array([13518.0, 15635.97, 18877.75, 20417.245, 21604.5, 22941.0, 24358.0, 25250.0, 25960.0, 26270.0, 26512.0, 26999.0, 27444.5, 27841.0, 28201.5, 28523.0, 28818.5, 29101.0, 29346.0, 29596.0, 29834.0, 30067.0, 30299.5, 30507.0, 30716.0, 30920.0, 31117.0, 31305.0, 31489.0, 31663.0, 31832.0, 31996.0, 32156.5, 32329.0, 32486.0, 32638.0, 32793.0, 32943.0, 33093.0, 33235.0, 33380.0, 33522.0, 33668.0, 33818.0, 33954.0, 34099.0, 34238.0, 34378.0, 34515.5, 34653.0, 34792.0, 34926.0, 35066.0, 35206.0, 35347.0, 35471.0, 35608.0, 35751.0, 35878.0, 36023.0, 36155.0, 36290.0, 36432.5, 36572.0, 36715.0, 36848.0, 36987.0, 37125.0, 37266.0, 37403.0, 37546.0, 37695.0, 37846.0, 38011.0, 38162.0, 38320.0, 38479.0, 38647.0, 38807.5, 38969.0, 39133.0, 39309.0, 39490.0, 39670.0, 39847.0, 40039.0, 40236.0, 40435.0, 40656.0, 40871.0, 41087.0, 41313.0, 41565.0, 41836.0, 42129.0, 42415.0, 42730.0, 43063.0, 43435.5, 43853.0, 44337.5, 44585.0, 44907.0, 45635.0, 46618.0, 48034.5, 49318.25, 50497.78999999998, 52162.99999999994, 55997.01999999973, 58616.0])
        cnt0=np.array([0.0, 7.705, 77.05, 208.035, 385.25, 770.5, 1541.0, 2311.5, 3082.0, 3505.775, 3852.5, 4623.0, 5393.5, 6164.0, 6934.5, 7705.0, 8475.5, 9246.0, 10016.5, 10787.0, 11557.5, 12328.0, 13098.5, 13869.0, 14639.5, 15410.0, 16180.5, 16951.0, 17721.5, 18492.0, 19262.5, 20033.0, 20803.5, 21574.0, 22344.5, 23115.0, 23885.5, 24656.0, 25426.5, 26197.0, 26967.5, 27738.0, 28508.5, 29279.0, 30049.5, 30820.0, 31590.5, 32361.0, 33131.5, 33902.0, 34672.5, 35443.0, 36213.5, 36984.0, 37754.5, 38525.0, 39295.5, 40066.0, 40836.5, 41607.0, 42377.5, 43148.0, 43918.5, 44689.0, 45459.5, 46230.0, 47000.5, 47771.0, 48541.5, 49312.0, 50082.5, 50853.0, 51623.5, 52394.0, 53164.5, 53935.0, 54705.5, 55476.0, 56246.5, 57017.0, 57787.5, 58558.0, 59328.5, 60099.0, 60869.5, 61640.0, 62410.5, 63181.0, 63951.5, 64722.0, 65492.5, 66263.0, 67033.5, 67804.0, 68574.5, 69345.0, 70115.5, 70886.0, 71656.5, 72427.0, 73197.5, 73544.225, 73968.0, 74738.5, 75509.0, 76279.5, 76664.75, 76841.965, 76972.95, 77042.295, 77050.0])
        self.c0=CumulativeCurve(bin0,cnt0)

 
    def test_curveFromBin(self):
        """从连续的数值返回累积分布"""
        fname=os.path.join(os.path.dirname(__file__), '20200101.txt')
        with open(fname,'rt') as f:       
          v=[]
          reader=csv.reader(f)
          for row in reader:
              v.append(int(row[2]))
        v.sort()
        c=curveFromBin(v,self.pb)
        self.assertTrue(cumulativeCurve_eq(c,self.c0))
        
    def test_max(self) :
        self.assertEqual(self.c0.max,58616)
      
    def test_min(self) :
        self.assertEqual(self.c0.min,13518)
      
    def test_count(self) :
        self.assertEqual(self.c0.count,77050)
      
    def test_p(self) :
        self.assertEqual(self.c0.p(5) ,26512)
        self.assertEqual(self.c0.p(25),31832)
        self.assertEqual(self.c0.p(75),39133)
        self.assertEqual(self.c0.p(95),44337.5)
      
    def test_median(self) :
        self.assertEqual(self.c0.median,35471)

    def test_cumulativeCount(self) :
        self.assertAlmostEqual(self.c0.cumulativeCount(10000),0)
        self.assertAlmostEqual(self.c0.cumulativeCount(30000),12106.43991416309)        
        self.assertAlmostEqual(self.c0.cumulativeCount(50000),76767.17664619259)
        self.assertAlmostEqual(self.c0.cumulativeCount(70000),77050)

        