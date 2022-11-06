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


def openfile(event):
    x = box.curselection()[0]
    file = box.get(x)
    os.startfile(file)


def showFile():
    global box
    files=glob.glob("*.csv")
    if len(files)>0:
        win=Toplevel(root)
        win.geometry("200x180")
        win.maxsize("200","180")
        box=Listbox(win,height = 10,width = 35,font="bold 10")
        scrollbar= Scrollbar(win, orient= 'vertical')
        scrollbar.pack(side= RIGHT, fill= BOTH)
        box.pack()
        Scrollbar(box).pack
        for file in files:
            box.insert(END,file)
        box.config(yscrollcommand= scrollbar.set)
        scrollbar.config(command= box.yview)
        box.bind("<Double 1>", openfile)
    else:
        showinfo(message="No data found")


def selctFile():
    filet=(('jpg files','*.jpg*'),('All files', '*.*'))
    name=""
    filenames=filedialog.askopenfilenames(title='Open files',initialdir='/',filetypes=filet)
    if filenames:
        for filename in filenames:
            if imghdr.what(filename):
                if not os.path.exists(path+"\\"+os.path.basename(filename)):
                    shutil.copy(filename,path)
                    name=name+os.path.basename(filename)+","
                else:
                    showinfo(message="File already exist")
            else:
                showwarning(message="Please select images")
        if name:
            encoding()
            showinfo(message=f"{name[:-1]} added")
        


def remove_file():
    if len(images)>0:
        name=""
        filet=(('jpg files','*.jpg*'),('All files', '*.*'))
        filenames=filedialog.askopenfilenames(title='Open files',initialdir=path,filetypes=filet)
        
        if filenames:
            for filename in filenames:
                if os.getcwd()+"\\"+path == os.path.dirname(filename).replace("/","\\"):
                    os.remove(filename)
                    name+=os.path.basename(filename)+","
                    
                else:
                    showerror(message="Please select image from the current folder",title="Out of range")
            if name:
                showinfo(message=f"{name[:-1]} deleted")
    else:
        showinfo(title="Error",message="No Data Found!")


def encoding():
    ername=""
    encode=[]
    imageList=[]
    names.clear()
    images=os.listdir(path)
    for cl in images:
        pimg=cv2.imread(f"{path}/{cl}")
        imageList.append(pimg)
        names.append(os.path.splitext(cl)[0])
    for img,nm in zip(imageList,names):
        try:
            image=cv2.resize(img, (0,0), None, 0.25,0.25)
            encoded_face = face_recognition.face_encodings(image)[0]
            encode.append(encoded_face)
        except:
            
            ername=ername+" "+nm
    if ername:
        showwarning(message=f"{ername} is not clear or no face detected")
        
    return encode

def takeAtttendance(nm):
	time=datetime.datetime.now()
	try:
		with open(f"{en.get().replace(' ','')} {time.day}-{time.month}.csv","r") as f:
			if nm not in f.read():
				with open(f"{en.get().replace(' ', '')} {time.day}-{time.month}.csv","a") as f2:
					f2.write(f"\n{nm},{time.hour}:{time.minute}")
	except:
		with open(f"{en.get().replace(' ','')} {time.day}-{time.month}.csv","w") as f:
			f.write("Name,Time")
			f.write(f"\n{nm},{time.hour}:{time.minute}")


def detectface():
    # en=en.get()
    if len(en.get().split()) != 0:
        cap = cv2.VideoCapture(0)
        global encodedlist
        encodedlist=encoding()
        win.lift()
        while(True):
        # Capture frame-by-frame
            ret, frame = cap.read()
            faces=face_recognition.face_locations(frame)
            encode_current_image=face_recognition.face_encodings(frame,faces)
            for encoded_face,faceL in zip(encode_current_image,faces):
                top, right, bottom, left = faceL
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                try:
                    matchface=face_recognition.compare_faces(encodedlist, encoded_face)
                    result=face_recognition.face_distance(encodedlist, encoded_face)
                    index=np.argmin(result)
                    if matchface[index]:
                        name=names[index].upper()
                        takeAtttendance(name)
                        cv2.putText(frame,f"{name}",(left+5,top),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    else:
                        cv2.putText(frame,"UNKNOWN",(left,bottom),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                
                except:
                    cv2.putText(frame,"UNKNOWN",(left,bottom),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
            cv2.putText(frame,"Found {0} faces!".format(len(faces)),(10,30),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,0),2)
            # Display the resulting frame
            cv2.imshow('Attendence', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        showerror(title="Error",message="Enter Subject")
        win.lift()
    en.set("")
        

def newwin():
    if len(images)>0:
        global win
        win=Toplevel(root)
        win.geometry("300x250")
        win.maxsize("300","250")
        name=Label(win,text="Subject Name",font="bold 12").place(relx = 0.1,rely = 0.2)
        namen=Entry(win,textvariable=en,font="bold 10").place(relx = 0.45,rely = 0.22)
        bstart=Button(win,text="Start",font="bold 12",command=detectface).pack(anchor=CENTER,pady=90)
    else:
        showinfo(title="Error",message="No Data Found!")


if __name__=="__main__":
    root=Tk()
    names=[]
    path='images'
    images=os.listdir(path)
    if path not in os.listdir():
        os.mkdir(path)
    en=StringVar()
    root.title("Preview")
    root.geometry("500x500")
    root.configure(bg="skyblue")
    l1=Label(text="Welcome",font="bold 32",fg="red",bg="skyblue")
    l1.pack(side=TOP)
    but1=Button(text="Start Attendence",font="bold 18",fg="red",bg="yellow",padx=20,pady=10,command=newwin)
    but1.place(x=255,y=250)
    chosefile=Button(text="Add Image",font="bold 18",fg="brown",bg="yellow",padx=20,pady=10,command=selctFile)
    chosefile.place(x=800,y=250)
    showfile=Button(text="Show file",font="bold 18",bg="yellow",padx=20,pady=10,command=showFile)
    showfile.place(x=255,y=350)
    removefile=Button(text="Remove Image",font="bold 18",fg="red",bg="yellow",padx=20,pady=10,command=remove_file)
    removefile.place(x=800,y=350)
    quitbu=Button(text="Quit",font="bold 18",fg="red",bg="yellow",padx=20,pady=10,command=quit)
    quitbu.place(x=550,y=450)
    root.state('zoomed')
    root.mainloop()