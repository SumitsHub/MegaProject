from tkinter import *
from tkinter import messagebox as mb
from PIL import Image,ImageTk
import sqlite3
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2


def myfunc():
    # USAGE
    # python detect_drowsiness.py --shape-predictor shape_predictor_68_face_landmarks.dat
    # python detect_drowsiness.py --shape-predictor shape_predictor_68_face_landmarks.dat --alarm alarm.wav

    # import the necessary packages


    def sound_alarm(path):
        # play an alarm sound
        playsound.playsound(path)

    def eye_aspect_ratio(eye):
        # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", default='shape_predictor_68_face_landmarks.dat',
                    help="path to facial landmark predictor")
    ap.add_argument("-a", "--alarm", type=str, default="alarm.wav",
                    help="path alarm .WAV file")
    ap.add_argument("-w", "--webcam", type=int, default=0,
                    help="index of webcam on system")
    args = vars(ap.parse_args())

    # define two constants, one for the eye aspect ratio to indicate
    # blink and then a second constant for the number of consecutive
    # frames the eye must be below the threshold for to set off the
    # alarm
    EYE_AR_THRESH = 0.18
    EYE_AR_CONSEC_FRAMES = 40

    # initialize the frame counter as well as a boolean used to
    # indicate if the alarm is going off
    COUNTER = 0
    ALARM_ON = False

    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor
    # print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])

    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # start the video stream thread
    # print("[INFO] starting video stream thread...")
    vs = VideoStream(src=args["webcam"]).start()
    time.sleep(1.0)

    # loop over frames from the video stream
    while True:
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = detector(gray, 0)

        # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            # compute the convex hull for the left and right eye, then
            # visualize each of the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 255), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 255), 1)

            # check to see if the eye aspect ratio is below the blink
            # threshold, and if so, increment the blink frame counter
            if ear < EYE_AR_THRESH:
                COUNTER += 1

                # if the eyes were closed for a sufficient number of
                # then sound the alarm
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    # if the alarm is not on, turn it on
                    if not ALARM_ON:
                        ALARM_ON = True

                        # check to see if an alarm file was supplied,
                        # and if so, start a thread to have the alarm
                        # sound played in the background
                        if args["alarm"] != "":
                            t = Thread(target=sound_alarm,
                                       args=(args["alarm"],))
                            t.deamon = True
                            t.start()

                    # draw an alarm on the frame
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # otherwise, the eye aspect ratio is not below the blink
            # threshold, so reset the counter and alarm
            else:
                COUNTER = 0
                ALARM_ON = False

            # draw the computed eye aspect ratio on the frame to help
            # with debugging and setting the correct eye aspect ratio
            # thresholds and frame counters
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()


def afterlogin(w1,f1,uname1,passw1):
    # tl = Label(f1, text=uname1.get()+" "+ passw1.get())
    # tl.pack()
    conn1=sqlite3.connect('Information.db')
    cursr=conn1.cursor()
    locuname=uname1.get()
    locpass=passw1.get()
    cursr.execute("SELECT * FROM Login WHERE Email=? AND pass=?",(locuname,locpass))
    conn1.commit()
    res=cursr.fetchall()

    if len(res)==1:
        # lll=Label(f1,text="Access Granted!")
        # lll.grid(row=3,column=0)
        mb.showinfo('Success!','Access Granted! Wait for few seconds!')

        w1.destroy()
        myfunc()
    else:
        # lll=Label(f1,text="Access Denied!")
        # lll.grid(row=3,column=0)
        mb.showerror('Error!','Enter correct Username or Password')
    # print(res)
    # print(res[0][0])
    conn1.close()


def inpdetails(win,f,name,sname,passw,email,mob,landline,city,pin,dlno):

    if (len(mob)!= 10 or len(landline) != 10):
        mb.showerror("Validation Error", "Please enter valid Mobile or Landline Number")

    elif (len(passw) < 8):
        mb.showerror("Password requirement", "Minimum 8digit password required!")
    elif (len(dlno) != 15):
        mb.showerror("Licence valiation error", "Please enter proper licence number")
    else:
        conn2=sqlite3.connect('Information.db')
        curs=conn2.cursor()

        curs.execute('INSERT INTO Login VALUES (?,?,?,?,?,?,?,?,?)',(name,sname,passw,email,mob,landline,city,pin,dlno))
        conn2.commit()
        conn2.close()
        mb.showinfo('Success!','Congratulation ! Registration successful.')
        win.destroy()


def funclog():
    win1=Tk()
    win1.geometry("300x200")
    win1.title("Login Yourself")

    mainlabel=Label(win1,text="Enter credentials  below to Login!")
    mainlabel.pack()
    infoLabel=Label(win1,text="Note: Use your email as username",fg="red").pack()

    f1=LabelFrame(win1,text="Login!",width=300)

    unamelabel=Label(f1,text="Username:")
    unamelabel.grid(row=0,column=0)
    uname=Entry(f1)
    uname.grid(row=0,column=1)

    passlabel=Label(f1,text="Password:")
    passlabel.grid(row=1,column=0)
    passw=Entry(f1)
    passw.grid(row=1,column=1)

    lbutton=Button(f1,text="Login",command=lambda : afterlogin(win1,f1,uname,passw))
    lbutton.grid(row=2,columnspan=2)


    f1.pack(fill=X,padx=20)
    win1.mainloop()


def funcreg():
    win2=Tk()
    win2.geometry("512x512")
    win2.title("Register Yourself")

    mainlabel = Label(win2, text="Provide details below to Register!").pack()
    f1 = LabelFrame(win2, text="Registration!")
    namelabel=Label(f1,text="Name :")
    namelabel.grid(row=0,column=0)
    name1=Entry(f1)
    name1.grid(row=0,column=1)

    snamelabel = Label(f1, text="Surname :")
    snamelabel.grid(row=0, column=2)
    sname1 = Entry(f1)
    sname1.grid(row=0, column=3)

    passlabel = Label(f1, text="Password :")
    passlabel.grid(row=1, column=0)
    pass1 = Entry(f1)
    pass1.grid(row=1, column=1)

    emaillabel = Label(f1, text="E-mail :")
    emaillabel.grid(row=1, column=2)
    eml = Entry(f1)
    eml.grid(row=1, column=3)

    moblabel = Label(f1, text="Mobile No :")
    moblabel.grid(row=2, column=0)
    mob1 = Entry(f1)
    mob1.grid(row=2, column=1)

    landlabel = Label(f1, text="Landline No :")
    landlabel.grid(row=2, column=2)
    land1 = Entry(f1)
    land1.grid(row=2, column=3)

    citylabel = Label(f1, text="City :")
    citylabel.grid(row=3, column=0)
    cty1 = Entry(f1)
    cty1.grid(row=3, column=1)

    pinlabel = Label(f1, text="Pincode :")
    pinlabel.grid(row=3, column=2)
    pin1 = Entry(f1)
    pin1.grid(row=3, column=3)

    dlicncelabel = Label(f1, text="Driving Licence:")
    dlicncelabel.grid(row=4, column=0)
    drl = Entry(f1)
    drl.grid(row=4, column=1)


    regbutton=Button(f1,text="Register",command=lambda:inpdetails(win2,f1,name1.get(),sname1.get(),pass1.get(),eml.get(),mob1.get(),land1.get(),cty1.get(),pin1.get(),drl.get()))
    regbutton.grid(row=5,columnspan=4)

    f1.pack(fill=X)
    win2.mainloop()


def getdetails(win,namee,sname):
    conn=sqlite3.connect('Information.db')
    cursr=conn.cursor()

    cursr.execute('SELECT * FROM Login WHERE uname=(?) AND sname=(?)',(namee,sname))
    conn.commit()
    res=cursr.fetchall()
    # print(res)
    conn.close()

    fr1=Frame(win)
    nlabel=Label(fr1,text="Name : "+res[0][0])
    nlabel.grid(row=0,column=0)

    slabel = Label(fr1, text="Surname : "+res[0][1])
    slabel.grid(row=1, column=0)

    # plabel = Label(fr1, text="Password : "+res[0][2])
    # plabel.grid(row=2, column=0)

    elabel = Label(fr1, text="E-mail : "+res[0][3])
    elabel.grid(row=3, column=0)

    mlabel = Label(fr1, text="Mobile No : "+str(res[0][4]))
    mlabel.grid(row=4, column=0)

    llabel = Label(fr1, text="Landline No : "+str(res[0][5]))
    llabel.grid(row=5, column=0)

    clabel = Label(fr1, text="City : "+res[0][6])
    clabel.grid(row=6, column=0)

    pinlabel = Label(fr1, text="Pin Code : "+str(res[0][7]))
    pinlabel.grid(row=7, column=0)

    dllabel=Label(fr1,text="Driving Licence No : "+str(res[0][8]))
    dllabel.grid(row=8,column=0)

    fr1.grid()


def funcdetail():
    win3=Tk()
    win3.title("Get Details")

    win3.geometry("300x400")

    lab1=Label(win3,text="Name :")
    lab1.grid(row=0,column=0)

    ent1=Entry(win3)
    ent1.grid(row=0,column=1,pady=10)

    lab2 = Label(win3, text="Surname :")
    lab2.grid(row=1, column=0,pady=10)

    ent2 = Entry(win3)
    ent2.grid(row=1, column=1,pady=10)

    b1=Button(win3,text="Submit",command=lambda : getdetails(win3,ent1.get(),ent2.get()))
    b1.grid(row=2,columnspan=2,pady=10)

    win3.mainloop()


root=Tk()
root.geometry("512x400+200+100")
root.title("Drowsines Detection")
root.wm_iconbitmap('hnet.com-image.ico')

frame1=LabelFrame(root,width=500,bg="white")
l1=Label(frame1,text="Welcome to Drowsiness Detection System!",width=510,font="calibri",bg="white")
l1.pack()
logo1=Image.open('avatar.png')
# logo1.show()
logo2=logo1.resize((100,70))

logo=ImageTk.PhotoImage(logo2)

l2=Label(frame1,image=logo,bg="white")
l2.pack()
l3=Label(frame1,text="Make Tourself Confortable",bg="white")
l3.pack()

frame1.pack()

frame2=LabelFrame(root,width=600,border=3,bg="white")
l1=Label(frame2,text="New User? : ").grid(row=0,column=0,pady=20)
b1=Button(frame2,text="Register",command=funcreg).grid(row=0,column=1,pady=20)

lor=Label(frame2,text="OR").grid(row=1,columnspan=2)

l2=Label(frame2,text="Existing User? : ").grid(row=2,column=0,pady=20)
b2=Button(frame2,text="Login",command=funclog).grid(row=2,column=1,pady=20)

lor1=Label(frame2,text="OR").grid(row=3,columnspan=2)

l3=Label(frame2,text="Retrieve Information : ").grid(row=4,column=0,pady=20)
b3=Button(frame2,text="Get Details",command=funcdetail).grid(row=4,column=1,pady=20)
frame2.pack(pady=10)

root.mainloop()