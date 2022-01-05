import serial_a as serial232
import time
import binascii
import sys
import json
import glob
# 泵头校准偏移量读取写入
def Config_deviation(dev):
    """
        1-6:M  7-12:R  13-18:L
    """
    fornum=0
    num_deviation=["deviation1","deviation2","deviation3", 
                   "deviation4", "deviation5","deviation6",
                   "deviation7","deviation8","deviation9",
                   "deviation10","deviation11","deviation12",
                   "deviation13","deviation14","deviation15",
                   "deviation16","deviation17","deviation18" 
                  ]
    x=glob.glob('/home/pi/megar/android/*.json')
    f =open(x[0],"r+")
    val=dict((json.loads(f.read())))
    f.seek(0,0)
    if not dev:
        for i in num_deviation:
                    Pumper_deviationlist[fornum] =val[i]
                    fornum+=1                          
    else:
        for i in num_deviation:
           val[i]= Pumper_deviationlist[fornum]
           fornum+=1 
        f.truncate()                  
        f.write(json.dumps(val,indent=4))
        time.sleep(0.5)
        f.flush()
    
    f.close()
# 应答返回  // v.0.0版设备上抛全为 0
ACK={
    "ACK":{
		"modem":0,   
		"moder":0,
		"model":0
	    }
}
# 设备状态返回  //泵头电机故障事件；
Status={
	"Pumperror":
			{
		    	"modem":"000000",
				"moder":"000000",
				"model":"000000"
			},					 	
	"materials":
			{
				"modem":"000000",               
				"moder":"000000",  
				"model":"000000"					
			},
	"event":{
				"Make":{
						"modem":"000000",
                        "moder":"000000",
						"model":"000000"
						 },
				"Cleaning":{
							"modem":"000000",
                            "moder":"000000",
							"model":"000000"
					        }	
	     	},	
	"deviation":"000"
}
#每个泵的校准偏移量
Pumper_deviationlist=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# 内部校准系数
Pumper_moduluslist=[1,1,1,1,1,1,
                    1,1,1,1,1,1,
                    1,1,1,1,1,1
                   ]
class Android232:
    __Read_time=0
    __numend=True
    # __Kl=0
    # __kr=0
    # __klsta=True
    # __krsta=True
    def __init__(self,name,bro=9600,deviation=False):
       self.Rs232=serial232.Serialport(name,bro)
       self.Rs232.portopen()
       Config_deviation(deviation)
       self.__Pack=""               #一包完整的协议指令                      
       self.__Rstr=list()           #读数据队列存储
       self.__Packlist=list()       #协议事件存储包
       self.Makelist=list()         #制作指令队列
       self.Cleaninglist=list()     #清洗指令队列
       self.Debuglist=list()        #调试指令队列
       self.Statuslist=list()       #状态请求队列
       self.Event=list()            #状态返回队列                   
    # 232数据 读处理
    def __Aread(self):
        val232=self.Rs232.read()
        if val232!=None:
            reval=val232.decode("utf-8")
            return reval
    # 232 数据写处理
    def Awrite(self,data):

        val=json.dumps(data)
        strval_list=list(val)
        strval_list.insert(0,"&&")
        strval_list.append("@@")
        val="".join(strval_list)
        # print("232send "+val)
        self.Rs232.write(val)
    
    def __clearnum(self):
            pass
    def __AgetPack2(self):
        while len(self.__Rstr)>0:       
            val=self.__Rstr.pop(0)
            if len(self.__Pack)>500:
                print("clear comnnt")
                self.__Pack=""
                self.__Rstr.clear()
                return False
            if val=="@":
                self.__Pack+=str(val)                
                Android232.__Read_time+=1
            else:
                self.__Pack+=str(val)     
            if Android232.__Read_time==2:
                Android232.__Read_time=0
                return True                            
    def __AgetPack3(self):
        sta=self.__Pack.count("&")
        end=self.__Pack.count("@")
        kl=self.__Pack.count("{")
        kr=self.__Pack.count("}")
        # print("sedd")
        if sta==2 and end==2 and kl==kr:
            if (self.__Pack[0]=="&"and self.__Pack[1]=="&")and(self.__Pack[-2]=="@"and self.__Pack[-1]=="@"):
                        self.__Packlist.append(self.__Pack[2:-2])
                        self.__Pack=""
            else:
                        self.__Pack=""
        else:
            self.__Pack="" 

    # 取一个完成的协议包
    def __AgetPack(self,packdata):
        data_list=list()
        if packdata!=None:
           data_list=list(packdata) 
           for i in data_list:
                self.__Rstr.append(i)              
        if self.__AgetPack2():
           self.__AgetPack3()
              
    # 从协议队列取事件弹包，分类（制作，清洗，调试，请求状态）
    def __AdetachPack(self):
        if len(self.__Packlist)>0:
            data_str=self.__Packlist.pop(0)
            if "make" in data_str:
                self.Makelist.append(json.loads(data_str))
                self.Awrite(ACK)
                print("JSON  Make"+str(len(self.Makelist)))    
            elif "cleaning" in data_str:
                self.Cleaninglist.append(json.loads(data_str))
                print("JSON  Cleaning"+str(len(self.Cleaninglist)))
                self.Awrite(ACK)
            elif "debug" in data_str:
                self.Debuglist.append(json.loads(data_str))
                print("JSON  debug"+str(len(self.Debuglist)))
                self.Awrite(ACK)
            elif "status" in data_str:
                self.Statuslist.append(json.loads(data_str))
                print("JSON  status"+str(len(self.Statuslist)))
                self.Awrite(Status)
    # 232数据业务处理
    def Aread(self):
        makedata=self.__Aread()
        # 重启清硬件缓存
        if Android232.__numend:
            makedata=""
            Android232.__numend=False
        self.__AgetPack(makedata)
        self.__AdetachPack()

# ww=Android232("/dev/USB1",115200)
# while 1:
#     ww.Aread()    
           