from __future__ import division 
import numpy as np
from matplotlib import pyplot as plt
import scipy.signal as signal
import csv
import os
import string
from matplotlib import style
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

def search(path=".", name="0"):#在特定目录下搜索关键字文件名  
    """
输入搜索路径和关键字
返回完整文件路径
    """
    for item in os.listdir(path):  
        item_path = os.path.join(path, item)  
        if os.path.isdir(item_path):  
            search(item_path, name)  
        elif os.path.isfile(item_path):  
            if name in item:  
                return item_path          

def read_wavecsv(name_key,search_path="C:\Users\Ludwig\Desktop\pythonworkspace",ch = 2):#读取指定路径下的指定关键字文件的电压和时间数据
    """
输入csv文件关键字和搜索路径
输出(时间序列,电压序列)
    """
    data1 = csv.reader(open(search(search_path,name_key)))
    second_temp = np.array([x[0] for x in data1])
    data2 = csv.reader(open(search(search_path,name_key)))
    volt_temp = np.array([y[ch] for y in data2])
    second = []
    for index1 in second_temp:
        try:
            second.append(string.atof(index1))
        except ValueError:
            continue
    volt = []
    for index2 in volt_temp:
        try:
            volt.append(string.atof(index2))
        except ValueError:
            continue
    if volt[0] == 1:
        del volt[0]
    elif len(volt) == 1999:
        volt.append(volt[len(volt)-1])
    else:
        pass
    return (second,volt)

#
#          max.
#            . .
#           .   .
#          .     .
#        1.       .1
#        .         .
#       .           .
#*******    argmax   *************
#输出尖峰位置序列
def cal_wavepara(array):
    """        
输入脉冲序列，输出尖峰位置序列和符号
((脉冲序列),(源信号边沿状态，1为上升沿，2为下降沿))
    """
    out = []
    signal = []
    index1 = 0
    for index in range(0, len(array)):
        if index < index1:#跳过已被[index:index1+1]切片搜索过的值
            continue
        else:
           if abs(array[index]) > 1:#脉冲尖峰搜索范围阀值
            for index1 in range(index, len(array)):
                if abs(array[index1]) < 1:
                    out.append(np.argmax(array[index:index1+1])+index)
                    if array[index] > 0:
                        signal.append(1)
                    elif array[index] < 0:
                        signal.append(-1)
                    break
    return (out,signal)


def measure(edge=[],second=[],volt=[]):
    """
测量函数
输入差分脉冲序列，时间序列，电压序列
输出((高电平时间,低电平时间),(高电平电压,低电平电压))
    """
    if edge[1][0] == 1:
        high_period = ((edge[0][1]-edge[0][0])/2000)*(second.max()-second[0])
        low_period = ((edge[0][2]-edge[0][1])/2000)*(second.max()-second[0])
        high_volt = volt[int((edge[0][1]-edge[0][0])/2)+edge[0][0]]
        low_volt = volt[int((edge[0][2]-edge[0][1])/2)+edge[0][1]]
    else:
        low_period = ((edge[0][1]-edge[0][0])/2000)*(second.max()-second[0])
        high_period = ((edge[0][2]-edge[0][1])/2000)*(second.max()-second[0])
        low_volt = volt[int((edge[0][1]-edge[0][0])/2)+edge[0][0]]
        high_volt = volt[int((edge[0][2]-edge[0][1])/2)+edge[0][1]]
    return (high_period,low_period),(high_volt,low_volt)



def main_process(name_key,search_path="C:\Users\Ludwig\Desktop\pythonworkspace",ch = 2):
    data = read_wavecsv(name_key,search_path,ch)
    second = np.array(data[0])#读出的时间序列
    volt = np.array(data[1])#读出的电压序列
   
    if ch == 2:
        name = raw_input("file number:%s the singal is:"%name_key)
        volt_medfilt = signal.medfilt(volt,kernel_size=3)#中值滤波
        volt_medfilt_diff = np.diff(volt_medfilt)#差分运算
        edge = cal_wavepara(volt_medfilt_diff)#尖峰序列     
        measurement  = measure(edge,second,volt)
        high_period = measurement[0][0]
        low_period = measurement[0][1]
        high_volt = measurement[1][0]
        low_volt = measurement[1][1]
        
        print "频率=%d赫兹"%(1/(high_period+low_period))
        print "高电平时间:%.2f微秒"%np.round(high_period*1000000,2)
        print "低电平时间:%.2f微秒"%np.round(low_period*1000000,2)
        print "高电平电压:%.2f伏特"%np.round(high_volt)
        print "低电平电压:%.2f伏特"%np.round(low_volt)
        plt.plot(np.arange(0,len(volt))*(second.max()-second[0])/2,volt+string.atoi(name_key)*30,label=name,linewidth=0.5)
        plt.plot(np.arange(0,len(volt))*(second.max()-second[0])/2,
                 string.atoi(name_key)*30+np.ones_like(np.arange(0,len(volt))*(second.max()-second[0]))*0,'--',linewidth=0.3)
        #plt.yticks(volt+string.atoi(name_key)*30,name,rotation=30)
        return measurement
    elif ch == 1:
        name = raw_input("the name of reference signal")
        plt.plot(np.arange(0,len(volt))*(second.max()-second[0])/2,volt+(string.atoi(name_key)-1)*30,label=name,linewidth=0.5)
        plt.plot(np.arange(0,len(volt))*(second.max()-second[0])/2,
                 (string.atoi(name_key)-1)*30+np.ones_like(np.arange(0,len(volt))*(second.max()-second[0]))*0,'--',linewidth=0.3)



###############################################################
#                                                             #
#                     以下是主执行函数                         #
#                                                            #
#############################################################
 
name_key = raw_input("Please input the <start number> of wave_date:")
date_count = input("Please intput the amount of wave_data:")
main_process("0",ch=1)#基准触发信号
for index in xrange(string.atoi(name_key),date_count):
    try:
        main_process("%d"%index)
    except TypeError:
        continue
#读取CSV数据后存入变量 

ax=plt.gca() 
xmajorLocator   = MultipleLocator(0.01)#将x主刻度标签设置为20的倍数  
#xmajorFormatter = FormatStrFormatter('%1.1f') #设置x轴标签文本的格式 
xminorLocator   = MultipleLocator(0.001) #将x轴次刻度标签设置为5的倍数  

ymajorLocator   = MultipleLocator(10) #将y轴主刻度标签设置为0.5的倍数  
#ymajorFormatter = FormatStrFormatter('%1.1f') #设置y轴标签文本的格式  
yminorLocator   = MultipleLocator(1) #将此y轴次刻度标签设置为0.1的倍数  




#设置主刻度标签的位置,标签文本的格式  
ax.xaxis.set_major_locator(xmajorLocator)  
#ax.xaxis.set_major_formatter(xmajorFormatter)  
  
ax.yaxis.set_major_locator(ymajorLocator)  
#ax.yaxis.set_major_formatter(ymajorFormatter)  
  
#显示次刻度标签的位置,没有标签文本  
ax.xaxis.set_minor_locator(xminorLocator)  
ax.yaxis.set_minor_locator(yminorLocator)  

ax.grid(True, color = "#054E9F",linewidth=0.1) 
plt.xlabel("time/ms")
plt.ylabel("voltage/V")
plt.legend()
style.use("ggplot")
plt.show()
