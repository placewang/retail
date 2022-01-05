class Syrup():
    def __init__(self):
        self.weight=list()
    def __Make1(self,data):
        if len(data)>0:
            return True
        else:
            return False    
    def __Make2(self,data):
        mnum=list()
        rnum=list()
        lnum=list()
        isstop="0"
        isstop= int(data["make"]["isstop"])
        self.weight.clear()
        for w in data["make"]["weight"]:
            self.weight.append(int(w))
           
        for i in range(len(data["make"]["modem"]["num"])-1,-1,-1):
            if data["make"]["modem"]["num"][i]=="1":
               mnum.append(6-i)
        
        for i in range(len(data["make"]["moder"]["num"])-1,-1,-1):
            if data["make"]["moder"]["num"][i]=="1":
               rnum.append(6-i)    
        for i in range(len(data["make"]["model"]["num"])-1,-1,-1):
            if data["make"]["model"]["num"][i]=="1":
               lnum.append(6-i)         
        
        return (isstop,mnum,rnum,lnum)
    # 返回  0:stop 1:主泵位2:右泵位3:左泵位   
    def Make(self,data):
        if self.__Make1(data):
           return self.__Make2(data.pop(0))
        else:
            return 0   
    def __cleaing(self,cleadata1):
        if len(cleadata1)>0:
            return True
        else:
            return False    
    def __cleaing2(self,cleadata2):
        if cleadata2["cleaning"]["modem"]=="111111":      
            return 0x01
        elif cleadata2["cleaning"]["moder"]=="111111":
           return 0x02
        elif cleadata2["cleaning"]["model"]=="111111":       
            return 0x03
        else:
            return 0    
    #返回要清洗的模块（从站号）    
    def Cleaning(self,clean):
        if self.__cleaing(clean):
           return self.__cleaing2(clean.pop(0))
        else:
            return 0   

    def __Debug1(self,debugdata1):
        if len(debugdata1)>0:
            return True
        else:
            return False
    def __Debug2(self,debugdata2):
        Lnum=0
        devait=0
        save=debugdata2["debug"]["save"]
        if debugdata2["debug"]["modem"]=="m":
               for i in range(len(debugdata2["debug"]["num"])-1,-1,-1):
                   if  debugdata2["debug"]["num"][i]=="1":
                       Lnum=6-i
                       devait=float(debugdata2["debug"]["deviation"])/1000
                       return (0x01,Lnum,devait,save)
                   
        elif debugdata2["debug"]["modem"]=="r":
                for i in range(len(debugdata2["debug"]["num"])-1,-1,-1):
                   if  debugdata2["debug"]["num"][i]=="1":
                       Lnum=6-i
                       devait=float(debugdata2["debug"]["deviation"])/1000
                       return (0x02,Lnum,devait,save)
        elif debugdata2["debug"]["modem"]=="l":
                for i in range(len(debugdata2["debug"]["num"])-1,-1,-1):
                   if  debugdata2["debug"]["num"][i]=="1":
                       Lnum=6-i
                       devait=float(debugdata2["debug"]["deviation"])/1000
                       return (0x03,Lnum,devait,save)
    # 返回模块号 模块中泵位，偏移量（float）,校准值是否永久生效
    def Debug(self,debug):
        if self.__Debug1(debug):
            return self.__Debug2(debug.pop(0))
        else:
            return 0
    def __status1(self,stadata1):
        if len(stadata1)>0:
            return True
        else:    
            return False
    def __status2(self,stadata2):
        if stadata2["status"]["modem"]=="111111":
            return True
        elif stadata2["status"]["moder"]=="111111":   
            return True
        elif stadata2["status"]["model"]=="111111":    
            return True
        else:
            return False    
# 上位机状态请求
    def Status(self,stadata):
        if self.__status1(stadata):
           return self.__status2(stadata.pop(0))

# dev_android = ad.Android232("/dev/USB1",115200) 
# pum=Syrup()

# while 1:
#     dev_android.Aread()
#     hh=pum.Make(dev_android.Makelist)
#     tt=pum.Cleaning(dev_android.Cleaninglist)
#     yy=pum.Debug(dev_android.Debuglist)
#     ss=pum.Status(dev_android.Statuslist)
#     if hh!=0:
#         print(type(hh))
#         print(hh,pum.weight)
#     if tt!=0:
#         print(type(tt))
#         print(tt)    
#     if yy!=0:
#         print(type(yy))
#         print(yy)
#     if ss :
#         print(type(ss))
#         print(ss)               


