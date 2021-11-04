#人脸识别门禁系统7.0

#引入库
import tkinter
import tkinter.messagebox
import sys
import os
import cv2
import datetime
import socket
import numpy as np
from PIL import Image
import pyttsx3
import RPi.GPIO as GPIO
from time import sleep
from mlx90614 import MLX90614

#初始化MLX引脚，IIC
thermometer_address = 0x5a

#初始化语言
word = pyttsx3.init()#初始化
rate = word.getProperty('rate')#设置语速
word.setProperty('rate', 125)
word.setProperty('voice', 'zh')#设置中文

#初始化舵机
def tonum(num):  # 角度转换
    fm = 10.0 / 180.0
    num = num * fm + 2.5
    num = int(num * 10) / 10.0
    return num
GPIO.setmode(GPIO.BOARD)
 
In_Pin1=36#door
In_Pin2=38#up-down
In_Pin3=40#left-right

GPIO.setup(In_Pin1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(In_Pin2,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(In_Pin3,GPIO.OUT,initial=GPIO.LOW)

p1 = GPIO.PWM(In_Pin1,50)
p2 = GPIO.PWM(In_Pin2,50)
p3 = GPIO.PWM(In_Pin3,50)

p1.start(tonum(90))#door
p2.start(tonum(120))#up-down
p3.start(tonum(90))#left-right
sleep(0.5)

p1.ChangeDutyCycle(0) #清除当前占空比
p2.ChangeDutyCycle(0)
p3.ChangeDutyCycle(0)
sleep(0.1)

def door(): #开门
    #p1 = GPIO.PWM(In_Pin1,50)
    p1.ChangeDutyCycle(tonum(180))
    sleep(1)
    p1.ChangeDutyCycle(tonum(90))
    sleep(0.1)
    p1.ChangeDutyCycle(0)  #清除当前占空比
    sleep(0.01)
    
#舵机角度变量
global sp
global cz
sp=90
cz=120

#创建socket链接
#tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建socket
server_addr = ("*.*.*.*", *) # 链接mysql服务器

#变量定义
id = 0 #人脸编号
names = ['None','hao','qing'] #人脸名称数组，与id对应

#提前加载分类器，提高代码运行速度
face_detector = cv2.CascadeClassifier('cascade_classifier/haarcascade_frontalface_default.xml')

#定义函数
def add(): #添加新面部信息
    face_id = t1.get()
    face_name = t2.get()
    #if len(face_id) == 0:
    if ((len(face_id) == 0) or (len(face_name) == 0)):
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
        text.insert(tkinter.END, time+'->编号或名称不能为空！\n')
        text.see(tkinter.END)
        text.update()
        return
    #names.append(face_name)
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->正在录入面部信息，请正对摄像头等待几秒钟……\n')#输出框显示信息
    word.say('请正对摄像头')
    word.runAndWait()
    text.see(tkinter.END)#输出框输入柄到尾部
    text.update()#输出框实时更新数据
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) #设置视频宽度
    cam.set(4, 480) #设置视频高度
     
    #print("\n正在初始化录入系统，请正对摄像头等待几秒钟……")
    #初始化
    count = 0#拍照数量计数器
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
     
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
     
            #将拍摄的图片保存在文件夹
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.imshow('录入面部信息', img)
     
        k = cv2.waitKey(100) & 0xff # 按 'ESC' 退出
        if k == 27:
            break
        elif count >= 50: #拍50张照片
             break
     
    #清理工作
    cam.release()
    cv2.destroyAllWindows()
    #print("录入编号："+t1.get()+"，名称："+t2.get()+"成功！")
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->录入编号：'+t1.get()+'，名称：'+t2.get()+'成功！\n')
    text.see(tkinter.END)
    text.update()
    #tkinter.messagebox.showinfo('录入成功','录入成功！           ')
def train(): #训练新数据库
    path = 'dataset' # 照片库的路径
    if len(os.listdir(path)) == 0:
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
        text.insert(tkinter.END, time+'->面部数据库为空，请先录入数据！\n')
        text.see(tkinter.END)
        text.update()
        return
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->正在训练数据，请耐心等待几秒……\n')
    text.see(tkinter.END)
    text.update()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("cascade_classifier/haarcascade_frontalface_default.xml");
     
    # 获取图像
    def getImagesAndLabels(path):
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L') # 将其转化为灰度
            img_numpy = np.array(PIL_img,'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
        return faceSamples,ids
     
    #print ("\n正在训练数据，请耐心等待几秒……")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))
     
    # 保留模型到 trainer/trainer.yml
    recognizer.write('trainer/trainer.yml')
    
    #print("\n成功训练了{0}个数据。正在退出……".format(len(np.unique(ids))))
    number = format(len(np.unique(ids)))
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->成功训练'+number+'个数据\n')
    text.see(tkinter.END)
    text.update()
    word.say('数据训练完成')
    word.runAndWait()
def recognite(): #启动人脸识别

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->成功启动人脸识别\n')
    text.see(tkinter.END)
    text.update()
    #os.system("python 03_face_recognition.py")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "cascade_classifier/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
     
    font = cv2.FONT_HERSHEY_SIMPLEX
    before = 0 #识别位
    after = 0 #识别位
     
    # 初始化识别，启动摄像头
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # 设置视频宽度
    cam.set(4, 480) # 设置视频高度
     
    #定义最小窗口大小以识别人脸
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)
     
    while True:
        ret, img =cam.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
         
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           ) 
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,190), 2)#脸部识别框配置
            id,confidence = recognizer.predict(gray[y:y+h,x:x+w])
            
            # 检查confidence是否在id已经定义
            if (confidence < 100):
                before = id
                id = names[id]
                confidence = "Similarity{0}%".format(round(100 - confidence))
                if (before!=after):
                    #print("Name->",id,",time->",time)
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
                    #word.say('请将手腕放于体温测量处')
                    #word.runAndWait()
                    thermometer = MLX90614(thermometer_address)
                    temp=thermometer.get_obj_temp()
                    if(temp<37.20000):
                        text.insert(tkinter.END, time+'->'+id+'进入，体温：'+str(temp)+'\n')
                        text.see(tkinter.END)
                        text.update()
                        send_data = """{"name":"%s","temp":"%f"}"""%(id,temp)
                        try:
                            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建socket
                            tcp_socket.connect(server_addr)
                            tcp_socket.send(send_data.encode("utf8"))
                            tcp_socket.close() # 关闭套接字
                        except IOError:
                            text.insert(tkinter.END, time+'->'+'服务器链接失败，请检查服务器监听程序\n')
                            text.see(tkinter.END)
                            text.update()
                            word.say('连接服务器失败')
                            word.runAndWait()
                            exitsystem()
                        after = before
                        door()
                    else:
                        word.say('体温异常，禁止入内')
                        word.runAndWait()
            else:
                id = "未授权用户"
                confidence = "{0}%".format(round(100 - confidence))
             
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
         
        cv2.imshow('人脸识别门禁系统',img) 
     
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
     
    # 退出并清理
    #print("\n正在退出程序和清理工作")
    cam.release()
    cv2.destroyAllWindows()
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->退出人脸识别系统\n')
    text.see(tkinter.END)

def up():
    global cz
    if cz>100 and cz<150:
        cz=cz-10
        p2.ChangeDutyCycle(tonum(cz))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p2.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
    else:
        cz=120
        p2.ChangeDutyCycle(tonum(cz))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p2.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
def down():
    global cz
    if cz>100 and cz<150:
        cz=cz+10
        p2.ChangeDutyCycle(tonum(cz))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p2.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
    else:
        cz=120
        p2.ChangeDutyCycle(tonum(cz))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p2.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
def left():
    global sp
    if sp>0 and sp<180:
        sp=sp-10
        p3.ChangeDutyCycle(tonum(sp))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p3.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
    else:
        sp=90
        p3.ChangeDutyCycle(tonum(sp))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p3.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
def right():
    global sp
    if sp>0 and sp<180:
        sp=sp+10
        p3.ChangeDutyCycle(tonum(sp))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p3.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
    else:
        sp=90
        p3.ChangeDutyCycle(tonum(sp))  #执行角度变化，跳转到q列表中对应第c位元素的角度
        sleep(0.1)
        p3.ChangeDutyCycle(0)  #清除当前占空比，使舵机停止抖动
        sleep(0.01)
def openfile(): #打开文件
    #os.system('start explorer' dataset)
    #os.startfile('dataset')
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->打开文件夹成功\n')
    text.see(tkinter.END)
def openfacefile(): #打开人脸文件
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->打开人脸数据库文件夹成功\n')
    text.see(tkinter.END)
def openxmlfile(): #打开训练集文件
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->打开训练集文件夹成功\n')
    text.see(tkinter.END)
def helpadd(): #录入帮助
    tkinter.messagebox.showinfo('帮助','录入帮助')
def helptrain(): #训练帮助
    tkinter.messagebox.showinfo('帮助','训练帮助')
def helprecognite(): #识别帮助
    tkinter.messagebox.showinfo('帮助','识别帮助')
def checknew(): #检查更新
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->检查更新\n')
    text.see(tkinter.END)
    text.update()
    tkinter.messagebox.showinfo('检查更新','\n当前版本：7.0                       \n已是最新版本!\n')
def about(): #关于
    tkinter.messagebox.showinfo('关于','\n作者：张志昊\n时间：2021/5/23                           \n版本：7.0\n')
def exitsystem(): #退出系统
    GPIO.cleanup()
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
    text.insert(tkinter.END, time+'->正在退出系统\n')
    text.see(tkinter.END)
    text.update()
    sys.exit(0)

#定义窗体
window = tkinter.Tk()
window.title("人脸识别系统")
window.geometry('950x520')

#定义菜单栏
f = tkinter.Menu(window) #创建根菜单
window["menu"]=f

f1 = tkinter.Menu(f,tearoff=False) #创建子菜单
f2 = tkinter.Menu(f,tearoff=False)

f1.add_command(label="打开系统文件",command=openfile) #子菜单栏f1
f1.add_command(label="打开面部库文件夹",command=openfacefile)
f1.add_command(label="打开训练集文件夹",command=openxmlfile)
#f1.add_command(label="重启系统")
f1.add_command(label="退出系统",command=exitsystem)

f2.add_command(label="录入信息帮助",command=helpadd) #子菜单栏f2
f2.add_command(label="训练数据帮助",command=helptrain)
f2.add_command(label="启动系统帮助",command=helprecognite)

f.add_cascade(label="菜单",menu=f1) #创建顶级菜单栏，并关联子菜单
f.add_cascade(label="帮助",menu=f2)
f.add_command(label="检查更新",command=checknew)
f.add_command(label="关于",command=about)

#定义文本框、输入框及按钮
tkinter.Label(window,text="\n请先输入编号和名称，再点击录入面部信息").place(x=140) #新建标签
t1 = tkinter.StringVar() #用来读取输入框内容
t2 = tkinter.StringVar()
tkinter.Label(window,text="编号：").place(x=42,y=60)
tkinter.Label(window,text="名称：").place(x=260,y=60)
tkinter.Entry(window,textvariable = t1).place(x=80,y=60) #输入框entry
tkinter.Entry(window,textvariable = t2).place(x=300,y=60)
tkinter.Button(window,text="点击录入新面部信息",command=add,width=15,height=4,fg='red').place(x=180,y=100) #设置按钮，fg为字体颜色，bg为背景色
tkinter.Label(window,text="\n更新面部识别库\n").place(x=210,y=200) #新建标签
tkinter.Button(window,text="点击更新面部识别库",command=train,width=15,height=4,fg='yellow').place(x=180,y=250)
tkinter.Label(window,text="\n运行系统\n").place(x=225,y=350) #新建标签
tkinter.Button(window,text="点击运行门禁系统",command=recognite,width=15,height=4,fg='green').place(x=180,y=400)

#定义输出框
tkinter.Label(window,text="系统日志").place(x=675,y=25)
text=tkinter.Text(window,width=57,height=15)
text.place(x=480,y=52)
time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #时间
text.insert(tkinter.END, time+'->人脸识别门禁系统初始化完成……\n')
text.see(tkinter.END)

#定义舵机控制按钮
tkinter.Label(window,text="舵机控制").place(x=675,y=310)
tkinter.Button(window,text="⬆UP⬆",command=up,width=10,height=2).place(x=650,y=340)
tkinter.Button(window,text="⬇DOWN⬇",command=down,width=10,height=2).place(x=650,y=460)
tkinter.Button(window,text="⬅LEFT",command=left,width=10,height=2).place(x=540,y=400)
tkinter.Button(window,text="RIGHT➡",command=right,width=10,height=2).place(x=760,y=400)

#进入消息循环
window.mainloop()