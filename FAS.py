from tkinter import *
from tkinter import filedialog
import cv2
import face_recognition
import numpy as np
import os,glob
import datetime
from tkinter.messagebox import *
import shutil
import imghdr
import re
from PIL import ImageTk, Image

PATH='images'

class HomeWindow(Tk):


    def __init__(self):
        super().__init__()
        self.fm=FileManager()
        self.images=os.listdir(PATH)
        self.title("FAS")
        self.geometry("1050x620")
        self.bg=ImageTk.PhotoImage(Image.open("Bgimage.png"))
        Label(self,image=self.bg).place(x=0,y=0)#E7F6F2
        Label(text="Facial Recognition Attendance System",font="Algerian 32",bg="White").place(x=200,y=10)
        Button(text="Start Attendence",font="bold 18",bg="#F7F7F7",padx=20,pady=10,relief=RAISED,borderwidth=4,command=self.newwin).place(x=290,y=150)
        Button(text="Add Image",font="bold 18",bg="#F7F7F7",padx=20,pady=10,relief=RAISED,borderwidth=4,command=self.selctFile).place(x=220,y=250)
        Button(text="Show file",font="bold 18",bg="#F7F7F7",padx=30,pady=10,relief=RAISED,borderwidth=4,command=self.showFile).place(x=220,y=350)
        Button(text="Remove Image",font="bold 18",bg="#F7F7F7",padx=20,pady=10,relief=RAISED,borderwidth=4,command=self.remove_file).place(x=270,y=450)
        Button(text="Quit",font="bold 18",bg="#F7F7F7",padx=20,pady=10,relief=RAISED,borderwidth=4,command=quit).place(x=420,y=550)
        self.state('zoomed')
    
    
    def newwin(self):
        if len(self.images)>0:
            nw=NewWindow(self)
            nw.StartWindow()
            nw.grab_set()
        else:
            showwarning(title="Warning",message="No Data Found!")


    def selctFile(self):
        self.fm.fileSelection()
        self.images=os.listdir(PATH)

    
    def showFile(self):
        if len(self.fm.fileShow())>0:
            sw=NewWindow(self)
            sw.showWindow(self.fm.fileShow())
            sw.grab_set()
        else:
            showinfo(title="Warning",message="No data found!")
    
    
    def remove_file(self):
        if len(self.images)>0:
            self.fm.fileDeletion()
            self.images=os.listdir(PATH)
        else:
            showwarning(title="Error",message="No Data Found!")



class NewWindow(Toplevel):


    def __init__(self,parent):
        super().__init__(parent)
        self.regex=re.compile('[.,@_![#$%^&*()<>?/\|}{~:]')
        self.number=['1','2','3','4','5','6','7','8','9','0']
        self.en=StringVar()
        self.box=Listbox(self)
        
    
    def detectface(self):
        if len(self.en.get().split()) != 0:
            if self.en.get()[0] not in self.number:
                if not self.regex.search(self.en.get()) and not re.search('[]]', self.en.get()):
                    dect=Detection()
                    dect.FaceDetect(self.en.get())
                    self.destroy()
                    showinfo(title="Attendance Complete",message="Attendence completed successfully")
                else:
                    showerror("Error",message='Make sure subject name deos not contain any special character!')
                    self.destroy()
            else:
                showerror("Warning","Subject name can not start with number!")
                self.destroy()
        else:
            showerror(title="Error",message="Please Enter Subject Name")
    
    
    def StartWindow(self):
        self.geometry("300x250")
        self.maxsize("300","250")
        Label(self,text="Subject Name",font="bold 12").place(relx = 0.1,rely = 0.2)
        Entry(self,textvariable=self.en,font="bold 10").place(relx = 0.45,rely = 0.22)
        Button(self,text="Start",font="bold 12",command=self.detectface).pack(anchor=CENTER,pady=90)
    
    
    def showWindow(self,files):
        self.geometry("200x180")
        self.maxsize("200","180")
        self.box=Listbox(self,height = 10,width = 35,font="bold 10")
        scrollbar= Scrollbar(self, orient= 'vertical')
        scrollbar.pack(side= RIGHT, fill= BOTH)
        self.box.pack()
        Scrollbar(self.box).pack
        for file in files:
            self.box.insert(END,file)
        self.box.config(yscrollcommand= scrollbar.set)
        scrollbar.config(command= self.box.yview)
        self.box.bind("<Double 1>", self.curserSelection)
    
    
    def curserSelection(self,event):
        x = self.box.curselection()[0]
        file = self.box.get(x)
        f=FileManager()
        f.startFile(file)
            


class Detection():   # detection and attendance
    
    
    def __init__(self):
        self.names=[]
        self.time=datetime.datetime.now()
        self.cap = cv2.VideoCapture(0)
    

    def FaceDetect(self,en):
        encodedlist=self.encoding()
        while(True):
        # Capture frame-by-frame
            ret, frame = self.cap.read()
            faces=face_recognition.face_locations(cv2.resize(frame, (0,0), None, 0.5,0.5))  # model hog by default
            encode_current_image=face_recognition.face_encodings(cv2.resize(frame, (0,0), None, 0.5,0.5),faces)
            y=int(len(faces)/4*10)
            for encoded_face,faceL in zip(encode_current_image,faces):
                top, right, bottom, left = faceL
                top*=2 
                right*=2
                bottom*=2
                left*=2 
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                try:
                    matchface=face_recognition.compare_faces(encodedlist, encoded_face)
                    result=face_recognition.face_distance(encodedlist, encoded_face)
                    index=np.argmin(result)
                    if matchface[index]:
                        name=self.names[index].upper()
                        self.takeAtttendance(name,en)
                        cv2.putText(frame,f"{name}",(left+5,top),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        cv2.putText(frame,f"{name}'s attendance marked",(200,50+y),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        y-=15
                    else:
                        cv2.putText(frame,"UNKNOWN",(left,bottom),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                # cv2.rectangle(frame, (left, bottom-35), (right, bottom), (0, 255, 0), cv2.FILLED)
                except:
                    cv2.putText(frame,"UNKNOWN",(left,bottom),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
            cv2.putText(frame,"Found {0} faces!".format(len(faces)),(10,30),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,0),2)
            cv2.putText(frame,"Press Q to quit",(10,450),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,0),2)
            # Display the resulting frame
            cv2.imshow('Attendence', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()


    def encoding(self):
        ername=""
        encode=[]     
        imageList=[]
        ext=[]
        self.names.clear()
        images=os.listdir(PATH)
        for cl in images:
            pimg=cv2.imread(f"{PATH}/{cl}")
            imageList.append(pimg)
            self.names.append(os.path.splitext(cl)[0])
            ext.append(os.path.splitext(cl)[1])
        for img,nm,ex in zip(imageList,self.names,ext):
            try:
                image=cv2.resize(img, (0,0), None, 0.25,0.25)
                encoded_face = face_recognition.face_encodings(image)[0]
                encode.append(encoded_face)
            except:
                ername=ername+" "+nm+ex
        if ername:
            ename=ername.split(" ")[1:]
            for n in ename:
                os.remove(f"{PATH}/{n}")
            showerror(title="Error",message=f"{ername.replace(' ', ',')[1:]} is not clear or no face detected")
            return False
        return encode


    def takeAtttendance(self,name,en):
        try:
            with open(f"{en.replace(' ','')} {self.time.day}-{self.time.month}.csv","r") as f:
                if name not in f.read():
                    with open(f"{en.replace(' ', '')} {self.time.day}-{self.time.month}.csv","a") as f2:
                        f2.write(f"\n{name},{self.time.hour}:{self.time.minute}")
        except FileNotFoundError:
            with open(f"{en.replace(' ','')} {self.time.day}-{self.time.month}.csv","w") as f:
                f.write("Name,Time")
                f.write(f"\n{name},{self.time.hour}:{self.time.minute}")
        
 
class FileManager():
    def __init__(self):
        self.file=(('jpg files','*.jpg*'),('png files', '*.png'),('All files','*.*'))
        self.name=""
        self.f=Detection()
        

    def fileSelection(self):
        self.name=""
        filenames=filedialog.askopenfilenames(title='Open files',initialdir='/',filetypes=self.file)
        if filenames:
            for filename in filenames:
                if imghdr.what(filename):
                    if not os.path.exists(PATH+"\\"+os.path.basename(filename)):
                        shutil.copy(filename,PATH)
                        self.name=self.name+os.path.basename(filename)+","
                    else:
                        showinfo(message="File already exist",title="Existing Data")
                else:
                    showwarning(title="Warning",message="Please select images")
            if self.name:
                if self.f.encoding():
                    showinfo(title="Image Addition",message=f"{self.name[:-1]} added")
    

    def fileShow(self):
        files=glob.glob("*.csv")
        return files


    def startFile(self,file):
        os.startfile(file)


    def fileDeletion(self):
        name=""
        filenames=filedialog.askopenfilenames(title='Open files',initialdir=PATH,filetypes=self.file)
        if filenames:
            for filename in filenames:
                if os.getcwd()+"\\"+PATH == os.path.dirname(filename).replace("/","\\"):
                    os.remove(filename)
                    name+=os.path.basename(filename)+","
                else:
                    showerror(message="Please select image from the current folder",title="Out of range")
            if name:
                showinfo(message=f"{name[:-1]} deleted",title="Image Deletion")
        


if __name__=="__main__":
    if PATH not in os.listdir():
        os.mkdir(PATH)
    hw=HomeWindow()
    hw.mainloop()
