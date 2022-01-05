#!/usr/bin/python3
import android.Rrw232 as Arw
import android.Pumpevent as Apum
import mos.ModbusIo as Mrw
import threading
import time
# led 4种状态 正常 1常亮:blue 2故障常亮 red  3缺料：常亮黄  4出品 blue 闪
Led=0x00

# 四种请求状态 前三种中准运行第一种
Make=False
Clean=False
Debug=False
Status=False
# 泵执行计数
Pumnum=0
# 0-2已开始执行泵数 3:清洗模块
Snum=[0,0,0,0]
# 实例化操作
Andio=Arw.Android232("/dev/USB1",115200)
Mdbus=Mrw.Modbus("/dev/USB0",115200)
Pum=Apum.Syrup()

"""
232数据收发
485发
"""
              
# 装载设备状态
def restatusflush():
    global Clean
    Arw.Status["materials"]["modem"]=Mdbus.Slavein1
    Arw.Status["materials"]["moder"]=Mdbus.Slavein2
    Arw.Status["materials"]["model"]=Mdbus.Slavein3
    Arw.Status["event"]["Make"]["modem"]=Mdbus.Slaveout1
    Arw.Status["event"]["Make"]["moder"]=Mdbus.Slaveout2
    Arw.Status["event"]["Make"]["model"]=Mdbus.Slaveout3
    if Clean:
        Arw.Status["event"]["Cleaning"]["model"]=Mdbus.Slaveout1
        Arw.Status["event"]["Cleaning"]["model"]=Mdbus.Slaveout2
        Arw.Status["event"]["Cleaning"]["model"]=Mdbus.Slaveout3
# 状态刷新
def reststatus():
    global Pumnum
    global Snum
    global Clean
    global Make
    global Led
    maval=Mdbus.Slaveout1.count("1")+Mdbus.Slaveout2.count("1")+Mdbus.Slaveout3.count("1")
    sout={
            "0":"",
            "1":Mdbus.Slaveout1,
            "2":Mdbus.Slaveout2,
            "3":Mdbus.Slaveout3
        }
    if not Make and maval!=0:
       
        Make=True
    elif Make and maval==0:
        Make=False
        print("Make end")    
    if not Clean and sout[str(Snum[3])]=="111111":
        Clean=True
    elif Clean and sout[str(Snum[3])]=="000000":
            print("clean end") 
            Clean=False 
    if not Make and (Mdbus.Slavein1.count("0")>0 or Mdbus.Slavein2.count("0")>0 or Mdbus.Slavein3.count("0")>0):
        Led=0x03
    elif Mdbus.Slavein1.count("1")==6 and Mdbus.Slavein2.count("1")==6 and Mdbus.Slavein3.count("1")==6:      
        Led=0x01
    elif Make:
        Led=0x04

def exemake():
    global Make
    global Snum
    global Led
    global Clean
    weith=0
    pval=Pum.Make(Andio.Makelist)
    pmval=Mdbus.Slaveout1.count("1")+Mdbus.Slaveout2.count("1")+Mdbus.Slaveout3.count("1")
    if pval[0]==1:
        for i in range(3):
            Mdbus.MwriteIooff(i+1,0x00)
            time.sleep(0.008)
        return 0        
    elif not Clean and pmval<=5 and pval[0]==0:
        for i in pval[1]:
            if len(Pum.weight)>0:
                # 液体流量计算（时间S）
                weith=Pum.weight.pop(0)
                Smu1=round(13/Arw.Pumper_deviationlist[i],1)
                # print(Smu1)
                time1=int(Smu1*10*weith+Arw.Pumper_moduluslist[i])
                # print(time1)
                Mdbus.Mwriteoutime(0x01,i,time1)
                time.sleep(0.008)
            else:
                return 0    
        for i in pval[2]:
            if len(Pum.weight)>0:    
                # 液体流量计算（时间S）
                weith=Pum.weight.pop(0)
                Smu2 = round(13/Arw.Pumper_deviationlist[5+i],1)
                # print(Smu2)
                time2=int(Smu2*10*weith+Arw.Pumper_moduluslist[5+i])
                # print(time2)
                Mdbus.Mwriteoutime(0x02,i,time2)
                time.sleep(0.008)
            else:
                return 0   
        for i in pval[3]:
            if len(Pum.weight)>0:
                # 液体流量计算（时间S）
                weith=Pum.weight.pop(0)
                Smu3=round(13/Arw.Pumper_deviationlist[11+i],1)
                # print(Smu3)
                time3=int(Smu3*10*weith+Arw.Pumper_moduluslist[11+i])
                # print(time3)
                Mdbus.Mwriteoutime(0x03,i,time3)
                time.sleep(0.008)
            else:
                return 0
        return True     
def execlean():
    global Clean
    global Snum
    global Make
    sanum=Pum.Cleaning(Andio.Cleaninglist)
    if not Make and not Clean and sanum!=0:
        Snum[3]=sanum
        print("开始清洗")
        for i in range(6):
            time1=(60+30)*10
            Mdbus.Mwriteoutime(sanum,i+1,time1)
            time.sleep(0.008)
        # time.sleep(3)

        
def exedebug():
   Debugreval=Pum.Debug(Andio.Debuglist)
   if Debugreval[0]==0x01:
       Arw.Pumper_deviationlist[Debugreval[1]-1]=Debugreval[2]
   elif Debugreval[0]==0x02:
       Arw.Pumper_deviationlist[5+Debugreval[1]]=Debugreval[2]
   elif Debugreval[0]==0x03:
       Arw.Pumper_deviationlist[11+Debugreval[1]]=Debugreval[2]
   if Debugreval[3]=="ff":
       Arw.Config_deviation(1)


def exestatus():
    Pum.Status(Andio.Statuslist)
        
def getcomnnet():
    global Make
    global Clean
    global Debug
    global Status
    
    if len(Andio.Makelist)>0:           
        exemake()
    elif len(Andio.Cleaninglist)>0:
        execlean() 
    elif len(Andio.Debuglist)>0:
        exedebug()
    if len(Andio.Statuslist)>0:
       exestatus()
     

# 出品LED灯效
def exeled():
    global Led
    bitp=0
    #正常待机 
    if Led==0x01:
        Mdbus.MwriteLed("blue")
        bitp+=1
    elif Led==0x03:
        Mdbus.MwriteLed("yellow")
        bitp+=1
    elif Led==0x02:
        Mdbus.MwriteLed("red")
        bitp+=1
    elif Led==0x04:
        Mdbus.MwriteLed("blue")
        time.sleep(0.3)
        Mdbus.MwriteLed("ledoff")
        time.sleep(0.3)
    time.sleep(0.005)            

"""
485数据接收线程
"""
def Tg1_read():
    print("threading 485 read status")
    while 1:        
        Mdbus.Mread()       
def Tg2_send():
    print("threading 485 status requst")
    while 1:
        getcomnnet()
        # exeled()
        Mdbus.MwriteQS()       
def Ad_read():
    print("threading 232 read start")
    while 1:
        Andio.Aread()
        restatusflush()
        reststatus()
                
Mreadthread=threading.Thread(target=Tg1_read)
Msendthread=threading.Thread(target=Tg2_send)
Areadthread=threading.Thread(target=Ad_read)
Mreadthread.start()
Msendthread.start()
Areadthread.start()
