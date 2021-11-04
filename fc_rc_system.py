#人脸识别门禁系统3.0
#引入库
import tkinter
import tkinter.messagebox
import sys
import os
import cv2

#定义函数
def add(): #添加新面部信息
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) #设置视频宽度
    cam.set(4, 480) #设置视频高度
     
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
     
    #face_id = input('\n enter user id end press <return> ==>  ')
    face_id = t1.get()
    print("\n正在初始化录入系统，请正对摄像头等待几秒钟……")
    #初始化
    count = 0
     
    while(True):
        ret, img = cam.read()
        #img = cv2.flip(img, -1) #反转图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
     
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
     
            #将拍摄的图片保存在文件夹
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
     
            cv2.imshow('image', img)
     
        k = cv2.waitKey(100) & 0xff # Press 'ESC' 退出
        if k == 27:
            break
        elif count >= 50: #拍50张照片
             break
     
    #清理工作
    print("\n正在退出程序和清理工作")
    cam.release()
    cv2.destroyAllWindows()
    print("录入编号："+t1.get()+"，名称："+t2.get()+"成功！")
    #tkinter.messagebox.showinfo('录入成功','录入成功！           ')
def train(): #训练新数据库
    os.system("python 02_face_training.py")
    print("更新面部识别库成功！")
def recognite(): #启动人脸识别
    print("正在启动人脸识别门禁系统")
    os.system("python 03_face_recognition.py")
def openfile(): #打开文件
    os.system("start explorer dataset")
    print("打开文件成功")
def openfacefile(): #打开人脸文件
    print("打开人脸文件夹成功")
def openxmlfile(): #打开训练集文件
    print("打开训练集文件成功")
def helpadd(): #录入帮助
    tkinter.messagebox.showinfo('帮助','录入帮助')
def helptrain(): #训练帮助
    tkinter.messagebox.showinfo('帮助','训练帮助')
def helprecognite(): #识别帮助
    tkinter.messagebox.showinfo('帮助','识别帮助')
def checknew(): #检查更新
    tkinter.messagebox.showinfo('检查更新','\n当前版本：3.0                       \n已是最新版本!\n')
def about(): #关于
    tkinter.messagebox.showinfo('关于','\n作者：张志昊\n时间：2021/4/17                           \n版本：3.0\n')
def exitsystem(): #退出系统
    sys.exit(0)

#定义窗体
window = tkinter.Tk()
window.title("人脸识别系统")
window.geometry('500x520')

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

#进入消息循环
window.mainloop()
