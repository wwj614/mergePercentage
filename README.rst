class curve
 _N: 样本总数
 _delta: 缺省为1
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
     vBin <= _bin[0]，返回0
	 vBin >= _bin[-1]，返回_N
	 当vBin对应的_bin中元素有重复时，返回最大的count，如
	   _N:100
	   max:900
	   min:100
	     min有相同的10个
	   其中400有30个，500有20个，(100,200,700,800,900)各10个
	   _bin：[99,100,200,400,400,400,500,500,700,800,900]
 	   _pb : [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90,100]
	   _cnt: [ 0, 10, 20, 50, 50, 50, 60, 70, 80, 90,100]
       30~50的分位点都是40	
       当vBin为400时，vcnt为50，不是30	   
 _interpolatFromPb: 用vpb值线性插值，返回_bin
     vpb必须在0~100之间
	 
 binCount(binRange): 概率累积密度转换为分区频数
   返回 bins和binCnts
   binRange缺省为_bin下标[0,0.5,1.5...-1.5,-0.5,-1]
     bins[0]=_bin[0] cnts=_count[0]	 
     bins[i]=_bin[i] cnts=bin[i-0.5],bin[i],bin[i+0.5]对应的_probability值围成的面积*_N
	                            = _interpolatFromBin(bin[i+0.5])-_interpolatFromBin(bin[i-0.5])
	                      bin[i-0.5]=(bin[i-1]+bin[i])/2
						  bin[i+0.5]=(bin[i+1]+bin[i])/2				
     bins[-1]=_bin[-1] cnts=_count[-1]
   转换后cnts中各元素的和与_N有误差！！！
   
 统计值
   当有数据更新时，缓存的统计值失效
 count(): _N 精确
 sum(): bins的binCnts加权和 估计
 avg(): sum()/binCnts和  估计
 std：sqrt(((bins*bins的binCnts加权和)-sum()平方)/_binCnt和*(_binCnt和-1))
 min(): _bin[0]+_delta 精确
 max(): _bin[-1] 精确
 p(cent): f(_bin,_probability)用_probability=cent插值  估计
 median(): p(50)  估计
 cumulativeProbabilityDensity(vBin):返回小于vBin的概率
 ProbabilityDensity(low,up):返回bin介于(low,up)之间的的概率
   =cumulativeProbabilityDensity(up)-cumulativeProbabilityDensity(low)
'''

class curveFromBin(curve)
'''
  bin值为区间的上端，如
    区间(0,1](1,2],(2,3]
	bin(1,2,3)
  _binValue: np.array
    缓存导入的数据，cacl后清空
   
  appandFromFile(filename):
    文件中包含单列数值，可重复
  appandFromFiles(pattern):
	pattern: 文件通配符
    文件中包含单列数值，可重复
  appand(iter):	
    iter：可迭代数值
  calc():
    基于基类curve的_pb，计算导入数据的_N，_bin，_cnt
	与基类cueve中的_N，_bin，_cnt用Merge算法合并
'''
    

class curveFromBinCount(curve)
'''
  _Value: sortlist(bin,cnt)
    缓存导入的数据，cacl后清空
    元素值为bin，cnt组合，多次append时，要合并cnt
    bin:元素值为唯一，递增
	cnt:为整数
   
  appandFromFile(filename):
    文件中包含双列数值，bin，cnt，bin 唯一
  appandFromFiles(pattern):
	pattern: 文件通配符
    文件中包含双列数值，bin，cnt，bin 唯一
  appand(iter):	
    iter：可迭代(bin,cnt)，bin 唯一
  cacl():
    基于基类curve的_pb，计算导入数据的_N，_bin，_cnt
	与基类cueve中的_N，_bin，_cnt用Merge算法合并
'''

class merge(curve)
'''
  _curveList: list(curve)
    元素为需要合并的curve
	
  append(curve):
    将需要合并的curve缓存到_curveList
  appandFromFile(filename):
    文件中包含双列数值，bin，cnt。bin递增，可以重复
	appandFromFiles(pattern):
	pattern: 文件通配符
    文件中包含双列数值，bin，cnt。bin递增，可以重复
  
  calc():
    算法原理
	  合并后的_N是各个元素_N的和
	  合并后的max是各个元素max的max
	  合并后的min是各个元素min的min
	  合并时curve的vBin取为各个元素bin的并集binUnion
	  对于binUnion中的每个vb，通过_interpolatFromBin依据每条curve的(_bin,_cnt)插值得到vcnt的和vcntSum
      合并得到的binUnion和vcntSum，将cnts归一化为概率值pbNew
	  用_pb的各个元素值通过_interpolatFromPb依据(binUnion,pbNew)插值得到vBinNew
	  _pb和vBinNew就是合并后的curve
	  当基类的_N>0，且vcntSum不空时，_curveList中将包含self的一个副本，参与合并
	  合并可以是的增量的
	    合并后，保留curveList，每次从新计算，算法简单
		合并后，清空curveList，新计算的binUnion与先前的有重复时要合并vcntSum。算法复杂
'''  

