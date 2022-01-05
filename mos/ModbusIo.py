import serial_a as serial
import time
import binascii
import binhex
import ctypes
import threading
# 总线状态位 1发送 0接收
ll = ctypes.cdll.LoadLibrary
adder = ll('/home/pi/megar/mos/crc16.so')
Threadevent=threading.Event()
class Modbus():
    def __init__(self,name,bro=9600):
        self.Modbus485=serial.Serialport(name,bro)
        self.Modbus485.portopen()
        self.__Readata=list()
        self.Slavein1=""
        self.Slavein2=""
        self.Slavein3=""
        self.Slaveout1=""
        self.Slaveout2=""
        self.Slaveout3=""
      
    # 总线读操作
    def __Mread(self):
        val = self.Modbus485.read()
        if val!=None:
            val=binascii.b2a_hex(val).decode("utf-8")
            for i in range(0,len(val),2):
                val1=val[i]
                val2=val[i+1]
                self.__Readata.append(int(val1+val2,16))
    #数据 弹出
    def __pop(self,val):
        for i in range(len(val)):
            val.pop(0)
    #将读到的IO状态，装载到    
    def __Bitstatus(self,da):
        Bit=list()
        Fr=0
        re=""
        for i in range(6):
            Fr=da%2
            da=da//2
            Bit.insert(0,Fr)
        for i in Bit:
            re+=str(i)   
        return re
               
    #1号 从站读数据处理
    def __ReadSlave1(self,val):
        if val[0]==0x01 and val[1]==0x01:
            # print("Slave1 out"+str(val))
            self.Slaveout1=self.__Bitstatus(val[-3])
            self.__pop(val)
            return True
        elif val[0]==0x01 and val[1]==0x02:
            # print("Slave1 in"+str(val))
            self.Slavein1=self.__Bitstatus(val[-3])
            self.__pop(val)
            return True
    #2号 从站读数据处理
    def __ReadSlave2(self,val):
        if val[0]==0x02 and val[1]==0x01:
            # print("Slave2 out"+str(val))
            self.Slaveout2=self.__Bitstatus(val[-3])
            self.__pop(val)
            return True
        elif val[0]==0x02 and val[1]==0x02:
            # print("Slave2 in"+str(val))
            self.Slavein2=self.__Bitstatus(val[-3])
            self.__pop(val)
            return True

    #3号 从站读数据处理
    def __ReadSlave3(self,val):
        if val[0]==0x03 and val[1]==0x01:
            # print("Slave3 out"+str(val))
            self.Slaveout3=self.__Bitstatus(val[-3])
            self.__pop(val)
            return True
        elif val[0]==0x03 and val[1]==0x02:
            # print("Slave3 in"+str(val))
            self.Slavein3=self.__Bitstatus(val[-3])
            self.__pop(val)
            return True
        
    #io板读数据分包
    def __Unpack(self,val):
        if self.__ReadSlave1(val):
            pass
        elif self.__ReadSlave2(val):
            pass
        elif self.__ReadSlave3(val):
            pass
        
    def __crc(self,val,len):
        crc_val=adder.Crc_coffee(val,len)
        crc_h=crc_val>>8
        crc_l=crc_val&0xff
        return (crc_h,crc_l)      
    def __SlaveFilte(self,val):
        num_list=(0x01,0x02,0x03)
        instatust1=(0x01,0x02)
        instatust2=(0x10,0x0f)
        if len(val)==6 and val[0] in num_list and val[1] in instatust1:
            crc=self.__crc(bytes(val[0:-2]),len(val[0:-2]))
            if crc[0]==val[-1]and crc[1]==val[-2]:
              self.__Unpack(val)
    # # 读数据过滤操作
    def __FilterData(self,val):
        # self.__LedFilter(val,21)
        self.__SlaveFilte(val)
        self.__pop(val)

    def Mread(self):
        # Threadevent.wait()
        self.__Mread()
        self.__FilterData(self.__Readata)
        

    # led写操作
    def MwriteLed(self,colour):
        
        colour_dict={
            "blue":(0xDD,0x55,0xEE,0x00,0x01,0x00,0x01,0x00,0x99,0x01,0x00,0x00,0x00,0x03,0x00,0x08,0x00,0x80,0x00,0xAA,0xBB),
            "yellow":(0xDD,0x55,0xEE,0x00,0x01,0x00,0x01,0x00,0x99,0x01,0x00,0x00,0x00,0x03,0x00,0x08,0xFF,0x00,0x80,0xAA,0xBB),
            "red":(0xDD,0x55,0xEE,0x00,0x01,0x00,0x01,0x00,0x99,0x01,0x00,0x00,0x00,0x03,0x00,0x08,0x97,0x00,0x00,0xAA,0xBB),
            "ledoff":(0xDD,0x55,0xEE,0x00,0x01,0x00,0x01,0x00,0x99,0x01,0x00,0x00,0x00,0x03,0x00,0x08,0x00,0x00,0x00,0xAA,0xBB)
        }
        self.Modbus485.write(colour_dict[colour])
        # Threadevent.set()
    # 关IO
    def MwriteIooff(self,num,data):
       
        valf = [0x0f,0x00,0x00,0x00,0x08,0x01]
        valf.insert(0,num)
        valf.append(data)
        crc=self.__crc(bytes(valf),len(valf))
        valf.append(crc[1])
        valf.append(crc[0])
        self.Modbus485.write(valf)
        # Threadevent.set()
    # 闪开IO
    def Mwriteoutime(self,num,data,time):
        
        data=(data-1)*5+3
        valt = [0x10,0x00,0x02,0x04,0x00,0x04]
        valt.insert(0,num)
        valt.insert(2,0x00)
        valt.insert(3,data)
        valt.append(time>>8)
        valt.append(time&0xff)
        crc=self.__crc(bytes(valt),len(valt))
        valt.append(crc[1])
        valt.append(crc[0])
        self.Modbus485.write(valt)
        # Threadevent.set()
    # 请求从站 IO输入，输出状态
    def MwriteQS(self):
        # Threadevent.wait()
        Seva_listout=[[0x01,0x01,0x00,0x00,0x00,0x08,0x3D,0xCC],
                        [0x02,0x01,0x00,0x00,0x00,0x08,0x3D,0xFF],
                            [0x03,0x01,0x00,0x00,0x00,0x08,0x3C,0x2E]]
        Seva_listin=[[0x01,0x02,0x00,0x00,0x00,0x08,0x79,0xCC],
                        [0x02,0x02,0x00,0x00,0x00,0x08,0x79,0xFF],
                            [0x03,0x02,0x00,0x00,0x00,0x08,0x78,0x2E]]                    
        for i in range(3):
            self.Modbus485.write(Seva_listout[i])
            # Threadevent.set()
            time.sleep(0.008)
        for t in range(3):
            self.Modbus485.write(Seva_listin[t])
            # Threadevent.set()
            time.sleep(0.008)    
# dev_0808D =Modbus("/dev/USB0",115200)