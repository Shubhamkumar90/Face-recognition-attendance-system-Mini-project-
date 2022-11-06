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

PATH='images'
class HomeWindow(Tk):
    def __init__(self):
        super().__init__()
        self.fm=FileManager()
        self.images=os.listdir(PATH)
        self.title("Preview")
        self.geometry("500x500")
        # self.iconphoto(False,ph1)
        self.configure(bg="skyblue")
        Label(text="Welcome",font="bold 32",fg="red",bg="skyblue").pack(side=TOP)
        # l2=Label(text="Enter some data",font="bold 18",fg="red")
        # l2.pack(side=TOP)
        Button(text="Start Attendence",font="bold 18",fg="red",bg="yellow",padx=20,pady=10,command=self.newwin).place(x=255,y=250)
        Button(text="Add Image",font="bold 18",fg="brown",bg="yellow",padx=20,pady=10,command=self.selctFile).place(x=800,y=250)
        Button(text="Show file",font="bold 18",bg="yellow",padx=20,pady=10,command=self.showFile).place(x=255,y=350)
        Button(text="Remove Image",font="bold 18",fg="red",bg="yellow",padx=20,pady=10,command=self.remove_file).place(x=800,y=350)
        Button(text="Quit",font="bold 18",fg="red",bg="yellow",padx=20,pady=10,command=quit).place(x=550,y=450)
        self.state('zoomed')
    
    
    def newwin(self):
        if len(self.images)>0:
            nw=NewWindow(self)
            nw.StartWindow()
            nw.grab_set()
        else:
            showinfo(title="Error",message="No Data Found!")


    def selctFile(self):
        self.fm.fileSelection()
        self.images=os.listdir(PATH)

    
    def showFile(self):
        if len(self.fm.fileShow())>0:
            sw=NewWindow(self)
            sw.showWindow(self.fm.fileShow())
            sw.grab_set()
        else:
            showinfo(message="No data found")
    
    
    def remove_file(self):
        if len(self.images)>0:
            self.fm.fileDeletion()
            self.images=os.listdir(PATH)
        else:
            showinfo(title="Error",message="No Data Found!")



class NewWindow(Toplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.regex=re.compile('[.@_![#$%^&*()<>?/\|}{~:]')
        self.en=StringVar()
        self.box=Listbox(self)
        
    
    def detectface(self):
        if len(self.en.get().split()) != 0:
            if not self.regex.search(self.en.get()) or not re.search('[]]', self.en.get()):
                dect=Detection()
                dect.FaceDetect(self.en.get())
                self.en.set("")
            else:
                showerror("Error",message='Make sure subject name deos not contain any special character!')
        else:
            showerror(title="Error",message="Enter Subject name")
    
    
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
            # self.reset
    
    
    def curserSelection(self,event):
        x = self.box.curselection()[0]
        file = self.box.get(x)
        f=FileManager()
        f.stratFile(file)
            


class Detection():   # detection and attendance
    def __init__(self):
        # self.en=name
        # self.PATH='images'
        self.names=[]
        self.time=datetime.datetime.now()
        self.encodedlist=self.encoding()
        self.cap = cv2.VideoCapture(0)
    

    def FaceDetect(self,en):
        while(True):
        # Capture frame-by-frame
            ret, frame = self.cap.read()
            faces=face_recognition.face_locations(frame)
            encode_current_image=face_recognition.face_encodings(frame,faces)
            for encoded_face,faceL in zip(encode_current_image,faces):
                top, right, bottom, left = faceL
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                try:
                    matchface=face_recognition.compare_faces(self.encodedlist, encoded_face)
                    result=face_recognition.face_distance(self.encodedlist, encoded_face)
                    index=np.argmin(result)
                    if matchface[index]:
                        name=self.names[index].upper()
                        self.takeAtttendance(name,en)
                        cv2.putText(frame,f"{name}",(left+5,top),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        cv2.putText(frame,f"{name}'s attendance marked",(200,50),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    else:
                        cv2.putText(frame,"UNKNOWN",(left,bottom),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                # cv2.rectangle(frame, (left, bottom-35), (right, bottom), (0, 255, 0), cv2.FILLED)
                except:
                    cv2.putText(frame,"UNKNOWN",(left,bottom),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
            cv2.putText(frame,"Found {0} faces!".format(len(faces)),(10,30),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,0),2)
            cv2.putText(frame,"Press Q to quit",(10,450),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,0),2)
            # Display the resulting frame
            cv2.imshow('Attendence', frame)
            # cv2.waitKey(1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()


    def encoding(self):
        ername=""
        encode=[]     
        imageList=[]
        self.names.clear()
        images=os.listdir(PATH)
        for cl in images:
            pimg=cv2.imread(f"{PATH}/{cl}")
            imageList.append(pimg)
            self.names.append(os.path.splitext(cl)[0])
        for img,nm in zip(imageList,self.names):
            try:
                image=cv2.resize(img, (0,0), None, 0.25,0.25)
                encoded_face = face_recognition.face_encodings(image)[0]
                encode.append(encoded_face)
            except:
                # print(nm)
                ername=ername+" "+nm
        if ername:
            showwarning(message=f"{ername} is not clear or no face detected")
        # print(names)
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
        self.file=(('jpg files','*.jpg*'),('All files', '*.*'))
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
                        # showinfo(message=f"{os.PATH.basename(filename)} added")
                    else:
                        showinfo(message="File already exist")
                else:
                    showwarning(message="Please select images")
            if self.name:
                self.f.encoding()
                showinfo(message=f"{self.name[:-1]} added")
    

    def fileShow(self):
        files=glob.glob("*.csv")
        return files


    def stratFile(self,file):
        os.startfile(file)


    def fileDeletion(self):
        name=""
        filet=(('jpg files','*.jpg*'),('All files', '*.*'))
        filenames=filedialog.askopenfilenames(title='Open files',initialdir=PATH,filetypes=filet)
        if filenames:
            for filename in filenames:
                if os.getcwd()+"\\"+PATH == os.path.dirname(filename).replace("/","\\"):
                    os.remove(filename)
                    name+=os.path.basename(filename)+","
                    # showinfo(message=f"{os.path.basename(filename)} deleted")
                else:
                    showerror(message="Please select image from the current folder",title="Out of range")
            if name:
                showinfo(message=f"{name[:-1]} deleted")
        


if __name__=="__main__":
    if PATH not in os.listdir():
        os.mkdir(PATH)
    b=HomeWindow()
    b.mainloop()
