#人脸识别门禁系统1.0
#引入库
import tkinter
import tkinter.messagebox

#定义函数
def add(): #添加新面部信息
    print("录入编号："+t1.get()+"成功！")
def train(): #训练新数据库
    print("更新面部识别库成功！")
def recognite(): #启动人脸识别
    print("正在启动人脸识别门禁系统")
def openfile(): #打开文件
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
    tkinter.messagebox.showinfo('检查更新','当前已是最新版本！')
def about(): #关于
    tkinter.messagebox.showinfo('关于','hao')

#定义窗体
window = tkinter.Tk()
window.title("人脸识别系统")
window.geometry('500x620')

#定义菜单栏
f = tkinter.Menu(window) #创建根菜单
window["menu"]=f

f1 = tkinter.Menu(f,tearoff=False) #创建子菜单
f2 = tkinter.Menu(f,tearoff=False)

f1.add_command(label="打开系统文件",command=openfile) #子菜单栏f1
f1.add_command(label="打开面部库文件夹",command=openfacefile)
f1.add_command(label="打开训练集文件夹",command=openxmlfile)
f1.add_command(label="重启系统")
f1.add_command(label="退出系统")

f2.add_command(label="录入信息帮助",command=helpadd) #子菜单栏f2
f2.add_command(label="训练数据帮助",command=helptrain)
f2.add_command(label="启动系统帮助",command=helprecognite)


f.add_cascade(label="菜单",menu=f1) #创建顶级菜单栏，并关联子菜单
f.add_cascade(label="帮助",menu=f2)
f.add_command(label="检查更新",command=checknew)
f.add_command(label="关于",command=about)

#定义文本框、输入框及按钮
tkinter.Label(window,text="\n请先输入编号，再点击录入面部信息").pack() #新建标签
t1 = tkinter.StringVar() #用来读取输入框内容
tkinter.Entry(window,textvariable = t1).pack() #输入框entry
tkinter.Button(window,text="点击录入新面部信息",command=add,width=15,height=4,fg='red').pack() #设置按钮，fg为字体颜色，bg为背景色
tkinter.Label(window,text="\n更新面部识别库\n").pack() #新建标签
tkinter.Button(window,text="点击更新面部识别库",command=train,width=15,height=4,fg='yellow').pack()
tkinter.Label(window,text="\n运行系统\n").pack() #新建标签
tkinter.Button(window,text="点击运行门禁系统",command=recognite,width=15,height=4,fg='green').pack()

#进入消息循环
window.mainloop()