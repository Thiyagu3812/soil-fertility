# main.py
import os
import base64
import io
import math
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import mysql.connector
import hashlib
import datetime
import calendar
import random
from random import randint
from urllib.request import urlopen
import webbrowser
#from plotly import graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import urllib.request
import urllib.parse
import csv
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import NearestNeighbors
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  charset="utf8",
  database="crop"

)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = { 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####
@app.route('/', methods=['GET', 'POST'])
def index():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM register WHERE uname = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('userhome'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html',msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html',msg=msg)

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM register WHERE uname = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('userhome'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login_user.html',msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    #import student
    msg=""
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        uname=request.form['uname']
        pass1=request.form['pass']
        
        
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM register where uname=%s",(uname,))
        cnt = mycursor.fetchone()[0]

        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
                    
            sql = "INSERT INTO register(id,name,mobile,email,uname,pass) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (maxid,name,mobile,email,uname,pass1)
            mycursor.execute(sql, val)
            mydb.commit()            
            #print(mycursor.rowcount, "Registered Success")
            msg="success"
            
        else:
            msg='Already Exist'
    return render_template('register.html',msg=msg)

@app.route('/add_fert', methods=['GET', 'POST'])
def add_fert():
    msg=""
    mycursor = mydb.cursor()

    dv = pd.read_csv('dataset/soil_data.csv')
    dtt=[]
    for dd in dv.values:
        dtt.append(dd[7])
    crop2=unique(dtt)

    
    if request.method=='POST':
        crop=request.form['crop']
        fert=request.form['fert']
        pest=request.form['pest']
        
        

        mycursor.execute("SELECT max(id)+1 FROM fert_data")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
                
        sql = "INSERT INTO fert_data(id,crop,fert,pest) VALUES (%s, %s, %s, %s)"
        val = (maxid,crop,fert,pest)
        mycursor.execute(sql, val)
        mydb.commit()            
        #print(mycursor.rowcount, "Registered Success")
        msg="success"
        return redirect(url_for('add_fert'))
        
    mycursor.execute("SELECT * FROM fert_data")
    data = mycursor.fetchall()

    
    return render_template('add_fert.html',msg=msg,data=data,crop2=crop2)

def unique(list1):
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    #for x in unique_list:
    #    print x,
    return unique_list

@app.route('/user_sample', methods=['GET', 'POST'])
def user_sample():
    msg=""
    cnt=0
    crop=[]
    st=""
    st2=""
    crop2=[]
    data=[]
    result=""
    uname=""
    act = request.args.get('act')
    cat = request.args.get('cat')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where uname=%s",(uname,))
    usr = mycursor.fetchone()

    dv = pd.read_csv('dataset/soil_data.csv')
    dv2 = pd.read_csv('dataset/fertilizer.csv')
    x=0

    ff=open("static/crops.txt","r")
    crop1=ff.read()
    ff.close()
    if len(crop1)>0:
        crop2=crop1.split(',')

    ##
    df = pd.read_csv('dataset/soil_data.csv')

    # Columns for matching
    feature_cols = ['N', 'P', 'K', 'Temperature', 'Humidity', 'pH', 'Rainfall']
    X = df[feature_cols]

    # Fit model
    model = NearestNeighbors(n_neighbors=1)
    model.fit(X)
    ##

                
    if request.method=='POST':
        if act=="1":
            v1=request.form['v1']
            v2=request.form['v2']
            v3=request.form['v3']
            temp=request.form['temp']
            hu=request.form['humidity']
            ph=request.form['ph']
            rain=request.form['rainfall']

       
            v11=float(v1)
            v22=float(v2)
            v33=float(v3)
            t11=float(temp)
            h11=float(hu)
            p11=float(ph)
            r11=float(rain)

            n1=v11-15
            n2=v11+15

            p1=v22-15
            p2=v22+15

            k1=v33-15
            k2=v33+15

            t1=t11-15
            t2=t11+15

            h1=h11-15
            h2=h11+15

            dt=[]
            for dd in dv2.values:
                if n1<=v11 and n2>=v11 and p1<=v22 and p2>=v22 and k1<=v33 and k2>=v33 and t1<=t11 and t2>=t11 and h1<=h11 and h2>=h11:
                    dt.append(dd[4])
                
            ncrop=len(dt)
            if ncrop>0:
                crop=unique(dt)
                cc=','.join(crop)
                ff=open("static/crops.txt","w")
                ff.write(cc)
                ff.close()
                st="1"
            else:
                st="2"

            ####
        elif act=="2":
            cnt=0
            s1="1"
            crop3=request.form['crop3']
            dt=[]
            for dd in dv2.values:
                if dd[4]==crop3:
                    cnt+=1
                    dtt=[]
                    dtt.append(dd[3])
                    dtt.append(dd[8])
                    data.append(dtt)
            if cnt>0:
                result="1"
            else:
                result="2"
    
    return render_template('user_sample.html',msg=msg,usr=usr,st=st,result=result,crop2=crop2,data=data,st2=st2)

def getValue(arr):
    #arr = [10, 89, 9, 56, 4, 80, 8]
    mini = arr[0]
    maxi = arr[0]

    for i in range(len(arr)):
      if arr[i] < mini: mini = arr[i] 
      
    if arr[i] > maxi: maxi = arr[i]

    #print (mini)
    #print (maxi)
    mini1=round(mini,2)
    maxi1=round(maxi,2)
    v=[mini1,maxi1]
    return v


    
@app.route('/userhome1', methods=['GET', 'POST'])
def userhome1():
    msg=""
    cnt=0
    crop=[]
    s1=""
    st2=""
    crop1=""
    crop2=[]
    data2=[]
    data=[]
    result=""
    uname=""
    act = request.args.get('act')
    cat = request.args.get('cat')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where uname=%s",(uname,))
    usr = mycursor.fetchone()

    dv = pd.read_csv('dataset/soil_data.csv')
    dtt=[]
    for dd in dv.values:
        dtt.append(dd[7])
    crop2=unique(dtt)
    
                
    if request.method=='POST':        
        crop=request.form['crop']
        crop1=crop
        s1="1"
        a_n=[]
        a_p=[]
        a_k=[]
        a_t=[]
        a_h=[]
        a_ph=[]
        a_r=[]
        for dd in dv.values:
            if dd[7]==crop:
                a_n.append(int(dd[0]))
                a_p.append(int(dd[1]))
                a_k.append(int(dd[2]))
                a_t.append(float(dd[3]))
                a_h.append(float(dd[4]))
                a_ph.append(float(dd[5]))
                a_r.append(float(dd[6]))
                
        n_m=getValue(a_n)
        n_min=n_m[0]
        n_max=n_m[1]

        p_m=getValue(a_p)
        p_min=p_m[0]
        p_max=p_m[1]

        k_m=getValue(a_k)
        k_min=k_m[0]
        k_max=k_m[1]

        t_m=getValue(a_t)
        t_min=t_m[0]
        t_max=t_m[1]

        h_m=getValue(a_h)
        h_min=h_m[0]
        h_max=h_m[1]

        ph_m=getValue(a_ph)
        ph_min=ph_m[0]
        ph_max=ph_m[1]

        r_m=getValue(a_r)
        r_min=r_m[0]
        r_max=r_m[1]
        data=[n_min,n_max,p_min,p_max,k_min,k_max,t_min,t_max,h_min,h_max,ph_min,ph_max,r_min,r_max]

        mycursor.execute("SELECT count(*) FROM fert_data where crop=%s",(crop,))
        nn = mycursor.fetchone()[0]
        if nn>0:
            st2="1"
            mycursor.execute("SELECT * FROM fert_data where crop=%s",(crop,))
            data2 = mycursor.fetchall()
    


    return render_template('userhome1.html',msg=msg,usr=usr,s1=s1,result=result,crop2=crop2,data=data,st2=st2,data2=data2,crop1=crop1)

df = pd.read_csv('static/data/soil_dataset.csv')

# Columns for matching
feature_cols = ['N', 'P', 'K', 'Temperature', 'Humidity', 'pH', 'Rainfall']
X = df[feature_cols]

# Fit model
model = NearestNeighbors(n_neighbors=1)
model.fit(X)

@app.route('/userhome', methods=['GET', 'POST'])
def userhome():
    msg=""
    cnt=0
    crop=""
    st=""
    st2=""
    data=""
    result=[]
    uname=""
    llc=""
    act = request.args.get('act')
    cat = request.args.get('cat')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where uname=%s",(uname,))
    usr = mycursor.fetchone()


    x=0
    if request.method=='POST':
        v1=request.form['v1']
        v2=request.form['v2']
        v3=request.form['v3']
        temp=request.form['temp']
        hu=request.form['humidity']
        ph=request.form['ph']
        rain=request.form['rainfall']
        color=request.form['selectedValue']
        st2="1"

        if color=="Shade 1":
            llc="Light Yellowish Green"
        elif color=="Shade 2":
            llc="Pale Green"
        elif color=="Shade 3":
            llc="Green"
        elif color=="Shade 4":
            llc="Dark Green"
        elif color=="Shade 5":
            llc="Very Dark Green"
        
        '''v11=float(v1)
        v22=float(v2)
        v33=float(v3)
        t1=float(temp)
        h1=float(hu)
        p1=float(ph)
        r1=float(rain)'''

        df = pd.read_csv('static/data/soil_dataset.csv')
        #for ss2 in dv.values:
        #    s=1

        # Collect input
        user_input = {
            'N': float(v1),
            'P': float(v2),
            'K': float(v3),
            'Temperature': float(temp),
            'Humidity': float(hu),
            'pH': float(ph),
            'Rainfall': float(rain),
        }
        leaf_color = request.form['selectedValue']

        # Find closest match
        input_vals = [[user_input[col] for col in feature_cols]]
        _, indices = model.kneighbors(input_vals)
        match_row = df.iloc[indices[0][0]]

        # Filter by Leaf Color if mismatch
        if match_row['Leaf Color'] != leaf_color:
            filtered = df[df['Leaf Color'] == leaf_color]
            if not filtered.empty:
                color_model = NearestNeighbors(n_neighbors=1).fit(filtered[feature_cols])
                _, color_indices = color_model.kneighbors(input_vals)
                match_row = filtered.iloc[color_indices[0][0]]

        result = {
            'Fertility Score': match_row['Fertility Score (%)'],
            'Interpretation': match_row['Interpretation'],
            'Fertilizer Recommendation': match_row['Fertilizer Recommendation'],
            'Crop Recommendation': match_row['Crop Recommendation']
        }


        '''dv = pd.read_csv('dataset/soil_data.csv')
        
        data2=[]
        
        act="1"

        if v11<0 or v11>140:
            x+=1
        if v22<5 or v22>145:
            x+=1
        if v33<5 or v33>205:
            x+=1
        if t1<8 or t1>43:
            x+=1
        if h1<14 or h1>99:
            x+=1
        if p1<3 or p1>9:
            x+=1
        if r1<20 or r1>298:
            x+=1

        n=0
        if x==0:
            st="1"
            for ss2 in dv.values:
                            
                g1=v11-1
                g2=v11+1
                
                g11=v22-1
                g12=v22+1

                g21=v33-1
                g22=v33+1

                tt1=t1-1
                tt2=t1+1

                hh1=h1-1
                hh2=h1+1

                pp1=p1-1
                pp2=p1+1

                rr1=r1-1
                rr2=r1+1
                               
                if float(ss2[0])==float(v11) and float(ss2[1])==float(v22) and float(ss2[2])==float(v33):
                    
                    if ss2[3]>=tt1 and ss2[3]<=tt2 and ss2[4]>=hh1 and ss2[4]<=hh2 and ss2[5]>=pp1 and ss2[5]<=pp2 and ss2[6]>=rr1 and ss2[6]<=rr2:
                        n+=1
                        print(ss2[0])
                        print(ss2[1])
                        print(ss2[2])
                        result="1"
                        crop=ss2[7]
                        print("A")
                        print(ss2[0])
                        print(ss2[1])
                        print(ss2[2])
                        print(ss2[3])
                        print(ss2[4])
                        print(ss2[5])
                        print(ss2[6])
                        print(crop)

                        mycursor.execute("SELECT count(*) FROM fert_data where crop=%s",(crop,))
                        cc = mycursor.fetchone()[0]
                        if cc>0:
                            st2="1"

                            mycursor.execute("SELECT * FROM fert_data where crop=%s",(crop,))
                            data = mycursor.fetchone()
                        print("aa")
                        break
                    else:
                        if (ss2[0]>=g1 and ss2[0]<=g2 and ss2[1]>=g11 and ss2[1]<=g12 and ss2[2]>=g21 and ss2[2]<=g22):
                            n+=1
                            result="1"
                            crop=ss2[7]
                            print("B")
                            print(ss2[0])
                            print(ss2[1])
                            print(ss2[2])
                            print(ss2[3])
                            print(ss2[4])
                            print(ss2[5])
                            print(ss2[6])
                            print(crop)

                            mycursor.execute("SELECT count(*) FROM fert_data where crop=%s",(crop,))
                            cc = mycursor.fetchone()[0]
                            if cc>0:
                                st2="1"

                                mycursor.execute("SELECT * FROM fert_data where crop=%s",(crop,))
                                data = mycursor.fetchone()
                            print("bb")
                            break
                
            if n==0:
                for ss2 in dv.values:
                    if (ss2[0]>=g1 and ss2[0]<=g2):
                        result="1"
                        crop=ss2[7]
                        print("C")
                        print(ss2[0])
                        print(ss2[1])
                        print(ss2[2])
                        print(ss2[3])
                        print(ss2[4])
                        print(ss2[5])
                        print(ss2[6])
                        print(crop)
                        

                        mycursor.execute("SELECT count(*) FROM fert_data where crop=%s",(crop,))
                        cc = mycursor.fetchone()[0]
                        if cc>0:
                            st2="1"

                            mycursor.execute("SELECT * FROM fert_data where crop=%s",(crop,))
                            data = mycursor.fetchone()
                        print("cc")
                        break
                    else:
                        
                        result="2"

                
        else:
            st="2"'''

        ####
        
    
    return render_template('userhome.html',msg=msg,usr=usr,st=st,result=result,crop=crop,data=data,st2=st2)




@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""

    x = os.listdir("./dataset")
    #print(x)
    
    if request.method=='POST':
        return redirect(url_for('process1'))
        
    return render_template('admin.html',msg=msg,dfile=x)

@app.route('/process1', methods=['GET', 'POST'])
def process1():
    msg=""
    colorarr = ['#0592D0','#Cd7f32', '#E97451', '#Bdb76b', '#954535', '#C2b280', '#808000','#C2b280', '#E4d008', '#9acd32', '#Eedc82', '#E4d96f',
           '#32cd32','#39ff14','#00ff7f', '#008080', '#36454f', '#F88379', '#Ff4500', '#Ffb347', '#A94064', '#E75480', '#Ffb6c1', '#E5e4e2',
           '#Faf0e6', '#8c92ac', '#Dbd7d2','#A7a6ba', '#B38b6d']
    
    '''data1=[]
    i=0
    sd=len(homepage)
    rows=len(homepage.values)
    for ss in homepage.values:
        cnt=len(ss)
        data1.append(ss)
    cols=cnt
    #print(data1)'
    ##################
    data2=[]
    for ss2 in payment.values:
        data2.append(ss2)'''
    ##################
    cropdf = pd.read_csv("dataset/soil_data.csv")
    dat=cropdf.head()
    data=[]
    for ss in dat.values:
        data.append(ss)

    data2=cropdf.shape
    data3=cropdf.columns
    data4=cropdf.isnull().any()

    ##print("Number of various crops: ", len(cropdf['label'].unique()))
    ##print("List of crops: ", cropdf['label'].unique())

    dat3=cropdf['label'].value_counts()
    data5=[]
    ##for ss5 in dat5.values:
    ##    data5.append(ss5)
    ##print(dat5)

    dat1=len(cropdf['label'].unique())
    dat2=cropdf['label'].unique()
    i=0
    dd=[]
    while i<dat1:
        dd.append(dat2[i])
        dd.append(dat3[i])
        data5.append(dd)
        i+=1

    crop_summary = pd.pivot_table(cropdf,index=['label'],aggfunc='mean')
    dat5=crop_summary.head()
    data5=[]
    for ss5 in dat5.values:
        data5.append(ss5)
    
    return render_template('process1.html',data=data,data2=data2,data3=data3,data4=data4,data5=data5)

@app.route('/process2', methods=['GET', 'POST'])
def process2():
    msg=""
    colorarr = ['#0592D0','#Cd7f32', '#E97451', '#Bdb76b', '#954535', '#C2b280', '#808000','#C2b280', '#E4d008', '#9acd32', '#Eedc82', '#E4d96f',
           '#32cd32','#39ff14','#00ff7f', '#008080', '#36454f', '#F88379', '#Ff4500', '#Ffb347', '#A94064', '#E75480', '#Ffb6c1', '#E5e4e2',
           '#Faf0e6', '#8c92ac', '#Dbd7d2','#A7a6ba', '#B38b6d']
    
    '''data1=[]
    i=0
    sd=len(homepage)
    rows=len(homepage.values)
    for ss in homepage.values:
        cnt=len(ss)
        data1.append(ss)
    cols=cnt
    #print(data1)'
    ##################
    data2=[]
    for ss2 in payment.values:
        data2.append(ss2)'''
    ##################
    cropdf = pd.read_csv("dataset/soil_data.csv")
    dat=cropdf.head()
    data=[]
    for ss in dat.values:
        data.append(ss)

    data2=cropdf.shape
    data3=cropdf.columns
    data4=cropdf.isnull().any()

    ##print("Number of various crops: ", len(cropdf['label'].unique()))
    ##print("List of crops: ", cropdf['label'].unique())

    dat3=cropdf['label'].value_counts()
    data5=[]
    ##for ss5 in dat5.values:
    ##    data5.append(ss5)
    ##print(dat5)

    dat1=len(cropdf['label'].unique())
    dat2=cropdf['label'].unique()
    i=0
    dd=[]
    while i<dat1:
        dd.append(dat2[i])
        dd.append(dat3[i])
        data5.append(dd)
        i+=1

    crop_summary = pd.pivot_table(cropdf,index=['label'],aggfunc='mean')
    dat5=crop_summary.head()
    data5=[]
    for ss5 in dat5.values:
        data5.append(ss5)
    #####
    ##Nitrogen Analysis
    '''crop_summary_N = crop_summary.sort_values(by='N', ascending=False)
  
    fig = make_subplots(rows=1, cols=2)

    top = {
        'y' : crop_summary_N['N'][0:10].sort_values().index,
        'x' : crop_summary_N['N'][0:10].sort_values()
    }

    last = {
        'y' : crop_summary_N['N'][-10:].index,
        'x' : crop_summary_N['N'][-10:]
    }

    fig.add_trace(
        go.Bar(top,
               name="Most nitrogen required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=top['x']),
        
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(last,
               name="Least nitrogen required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=last['x']),
        row=1, col=2
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(title_text="Nitrogen (N)",
                      plot_bgcolor='white',
                      font_size=12, 
                      font_color='black',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    ##fig.show()
    ##graph1
    ##############################
    ##Phosphorus Analysis
    '''crop_summary_P = crop_summary.sort_values(by='P', ascending=False)
  
    fig = make_subplots(rows=1, cols=2)

    top = {
        'y' : crop_summary_P['P'][0:10].sort_values().index,
        'x' : crop_summary_P['P'][0:10].sort_values()
    }

    last = {
        'y' : crop_summary_P['P'][-10:].index,
        'x' : crop_summary_P['P'][-10:]
    }

    fig.add_trace(
        go.Bar(top,
               name="Most phosphorus required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=top['x']),
        
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(last,
               name="Least phosphorus required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=last['x']),
        row=1, col=2
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(title_text="Phosphorus (P)",
                      plot_bgcolor='white',
                      font_size=12, 
                      font_color='black',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    ##fig.show()
    ##graph2
    #######################
    ##Potassium analysis
    '''crop_summary_K = crop_summary.sort_values(by='K', ascending=False)
  
    fig = make_subplots(rows=1, cols=2)

    top = {
        'y' : crop_summary_K['K'][0:10].sort_values().index,
        'x' : crop_summary_K['K'][0:10].sort_values()
    }

    last = {
        'y' : crop_summary_K['K'][-10:].index,
        'x' : crop_summary_K['K'][-10:]
    }

    fig.add_trace(
        go.Bar(top,
               name="Most potassium required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=top['x']),
        
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(last,
               name="Least potassium required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=last['x']),
        row=1, col=2
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(title_text="Potassium (K)",
                      plot_bgcolor='white',
                      font_size=12, 
                      font_color='black',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    ##fig.show()
    ##graph3
    #########################
    ##N, P, K values comparision between crops
    '''fig = go.Figure()
    fig.add_trace(go.Bar(
        x=crop_summary.index,
        y=crop_summary['N'],
        name='Nitrogen',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=crop_summary.index,
        y=crop_summary['P'],
        name='Phosphorous',
        marker_color='lightsalmon'
    ))
    fig.add_trace(go.Bar(
        x=crop_summary.index,
        y=crop_summary['K'],
        name='Potash',
        marker_color='crimson'
    ))

    fig.update_layout(title="N, P, K values comparision between crops",
                      plot_bgcolor='white',
                      barmode='group',
                      xaxis_tickangle=-45)'''

    ##fig.show()
    ##graph4
    #####################
    ##NPK ratio for rice, cotton, jute, maize, lentil
    labels = ['Nitrogen(N)','Phosphorous(P)','Potash(K)']
    fig = make_subplots(rows=1, cols=5, specs=[[{'type':'domain'}, {'type':'domain'},
                                                {'type':'domain'}, {'type':'domain'}, 
                                                {'type':'domain'}]])

    rice_npk = crop_summary[crop_summary.index=='rice']
    values = [rice_npk['N'][0], rice_npk['P'][0], rice_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Rice"),1, 1)

    cotton_npk = crop_summary[crop_summary.index=='cotton']
    values = [cotton_npk['N'][0], cotton_npk['P'][0], cotton_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Cotton"),1, 2)

    jute_npk = crop_summary[crop_summary.index=='jute']
    values = [jute_npk['N'][0], jute_npk['P'][0], jute_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Jute"),1, 3)

    maize_npk = crop_summary[crop_summary.index=='maize']
    values = [maize_npk['N'][0], maize_npk['P'][0], maize_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Maize"),1, 4)

    lentil_npk = crop_summary[crop_summary.index=='lentil']
    values = [lentil_npk['N'][0], lentil_npk['P'][0], lentil_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Lentil"),1, 5)

    '''fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig.update_layout(
        title_text="NPK ratio for rice, cotton, jute, maize, lentil",
        annotations=[dict(text='Rice',x=0.06,y=0.8, font_size=15, showarrow=False),
                     dict(text='Cotton',x=0.26,y=0.8, font_size=15, showarrow=False),
                     dict(text='Jute',x=0.50,y=0.8, font_size=15, showarrow=False),
                     dict(text='Maize',x=0.74,y=0.8, font_size=15, showarrow=False),
                    dict(text='Lentil',x=0.94,y=0.8, font_size=15, showarrow=False)])'''
    #fig.show()
    #graph5
    #############
    ##NPK ratio for fruits
    labels = ['Nitrogen(N)','Phosphorous(P)','Potash(K)']
    specs = [[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}],[
             {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}]]
    fig = make_subplots(rows=2, cols=5, specs=specs)
    cafe_colors =  ['rgb(255, 128, 0)', 'rgb(0, 153, 204)', 'rgb(173, 173, 133)']

    apple_npk = crop_summary[crop_summary.index=='apple']
    values = [apple_npk['N'][0], apple_npk['P'][0], apple_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Apple", marker_colors=cafe_colors),1, 1)

    banana_npk = crop_summary[crop_summary.index=='banana']
    values = [banana_npk['N'][0], banana_npk['P'][0], banana_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Banana", marker_colors=cafe_colors),1, 2)

    grapes_npk = crop_summary[crop_summary.index=='grapes']
    values = [grapes_npk['N'][0], grapes_npk['P'][0], grapes_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Grapes", marker_colors=cafe_colors),1, 3)

    orange_npk = crop_summary[crop_summary.index=='orange']
    values = [orange_npk['N'][0], orange_npk['P'][0], orange_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Orange", marker_colors=cafe_colors),1, 4)

    mango_npk = crop_summary[crop_summary.index=='mango']
    values = [mango_npk['N'][0], mango_npk['P'][0], mango_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Mango", marker_colors=cafe_colors),1, 5)

    coconut_npk = crop_summary[crop_summary.index=='coconut']
    values = [coconut_npk['N'][0], coconut_npk['P'][0], coconut_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Coconut", marker_colors=cafe_colors),2, 1)

    papaya_npk = crop_summary[crop_summary.index=='papaya']
    values = [papaya_npk['N'][0], papaya_npk['P'][0], papaya_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Papaya", marker_colors=cafe_colors),2, 2)

    pomegranate_npk = crop_summary[crop_summary.index=='pomegranate']
    values = [pomegranate_npk['N'][0], pomegranate_npk['P'][0], pomegranate_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Pomegranate", marker_colors=cafe_colors),2, 3)

    watermelon_npk = crop_summary[crop_summary.index=='watermelon']
    values = [watermelon_npk['N'][0], watermelon_npk['P'][0], watermelon_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Watermelon", marker_colors=cafe_colors),2, 4)

    muskmelon_npk = crop_summary[crop_summary.index=='muskmelon']
    values = [muskmelon_npk['N'][0], muskmelon_npk['P'][0], muskmelon_npk['K'][0]]
    '''fig.add_trace(go.Pie(labels=labels, values=values,name="Muskmelon", marker_colors=cafe_colors),2, 5)

    fig.update_layout(
        title_text="NPK ratio for fruits",
        annotations=[dict(text='Apple',x=0.06,y=1.08, font_size=15, showarrow=False),
                     dict(text='Banana',x=0.26,y=1.08, font_size=15, showarrow=False),
                     dict(text='Grapes',x=0.50,y=1.08, font_size=15, showarrow=False),
                     dict(text='Orange',x=0.74,y=1.08, font_size=15, showarrow=False),
                    dict(text='Mango',x=0.94,y=1.08, font_size=15, showarrow=False),
                    dict(text='Coconut',x=0.06,y=0.46, font_size=15, showarrow=False),
                     dict(text='Papaya',x=0.26,y=0.46, font_size=15, showarrow=False),
                     dict(text='Pomegranate',x=0.50,y=0.46, font_size=15, showarrow=False),
                     dict(text='Watermelon',x=0.74,y=0.46, font_size=15, showarrow=False),
                    dict(text='Muskmelon',x=0.94,y=0.46, font_size=15, showarrow=False)])'''
    #fig.show()
    #graph6
    ##############
    crop_scatter = cropdf[(cropdf['label']=='rice') | 
                      (cropdf['label']=='jute') | 
                      (cropdf['label']=='cotton') |
                     (cropdf['label']=='maize') |
                     (cropdf['label']=='lentil')]

    fig = px.scatter(crop_scatter, x="temperature", y="humidity", color="label", symbol="label")
    fig.update_layout(plot_bgcolor='white')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    #fig.show()
    #graph7
    ###################
    '''fig = px.bar(crop_summary, x=crop_summary.index, y=["rainfall", "temperature", "humidity"])
    fig.update_layout(title_text="Comparision between rainfall, temerature and humidity",
                      plot_bgcolor='white',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    #fig.show()
    #graph8
    ####################
    ##Correlation between different features
    fig, ax = plt.subplots(1, 1, figsize=(15, 9))
    sns.heatmap(cropdf.corr(), annot=True,cmap='Wistia' )
    ax.set(xlabel='features')
    ax.set(ylabel='features')

    #plt.title('Correlation between different features', fontsize = 15, c='black')
    #plt.show()
    #graph9
    ###################

    
    return render_template('process2.html')

@app.route('/process3', methods=['GET', 'POST'])
def process3():
    msg=""
    st=""
    colorarr = ['#0592D0','#Cd7f32', '#E97451', '#Bdb76b', '#954535', '#C2b280', '#808000','#C2b280', '#E4d008', '#9acd32', '#Eedc82', '#E4d96f',
           '#32cd32','#39ff14','#00ff7f', '#008080', '#36454f', '#F88379', '#Ff4500', '#Ffb347', '#A94064', '#E75480', '#Ffb6c1', '#E5e4e2',
           '#Faf0e6', '#8c92ac', '#Dbd7d2','#A7a6ba', '#B38b6d']
    if request.method=='POST':
        st="1"
        files = request.files.getlist('images')
        for file in files:
            fnn=secure_filename(file.filename)
            file.save(os.path.join("static/leaf/", fnn))
        
    '''data1=[]
    i=0
    sd=len(homepage)
    rows=len(homepage.values)
    for ss in homepage.values:
        cnt=len(ss)
        data1.append(ss)
    cols=cnt
    #print(data1)'
    ##################
    data2=[]
    for ss2 in payment.values:
        data2.append(ss2)'''
    ##################
    cropdf = pd.read_csv("dataset/soil_data.csv")
    dat=cropdf.head()
    data=[]
    for ss in dat.values:
        data.append(ss)

    data2=cropdf.shape
    data3=cropdf.columns
    data4=cropdf.isnull().any()

    #print("Number of various crops: ", len(cropdf['label'].unique()))
    #print("List of crops: ", cropdf['label'].unique())

    dat3=cropdf['label'].value_counts()
    data5=[]
    #for ss5 in dat5.values:
    #    data5.append(ss5)
    #print(dat5)

    dat1=len(cropdf['label'].unique())
    dat2=cropdf['label'].unique()
    i=0
    dd=[]
    while i<dat1:
        dd.append(dat2[i])
        dd.append(dat3[i])
        data5.append(dd)
        i+=1

    crop_summary = pd.pivot_table(cropdf,index=['label'],aggfunc='mean')
    dat5=crop_summary.head()
    data5=[]
    for ss5 in dat5.values:
        data5.append(ss5)
    #####
    ##Nitrogen Analysis
    '''crop_summary_N = crop_summary.sort_values(by='N', ascending=False)
  
    fig = make_subplots(rows=1, cols=2)

    top = {
        'y' : crop_summary_N['N'][0:10].sort_values().index,
        'x' : crop_summary_N['N'][0:10].sort_values()
    }

    last = {
        'y' : crop_summary_N['N'][-10:].index,
        'x' : crop_summary_N['N'][-10:]
    }

    fig.add_trace(
        go.Bar(top,
               name="Most nitrogen required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=top['x']),
        
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(last,
               name="Least nitrogen required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=last['x']),
        row=1, col=2
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(title_text="Nitrogen (N)",
                      plot_bgcolor='white',
                      font_size=12, 
                      font_color='black',
                     height=500)'''

    #fig.update_xaxes(showgrid=False)
    #fig.update_yaxes(showgrid=False)
    #fig.show()
    #graph1
    ##############################
    ##Phosphorus Analysis
    crop_summary_P = crop_summary.sort_values(by='P', ascending=False)
  
    '''fig = make_subplots(rows=1, cols=2)

    top = {
        'y' : crop_summary_P['P'][0:10].sort_values().index,
        'x' : crop_summary_P['P'][0:10].sort_values()
    }

    last = {
        'y' : crop_summary_P['P'][-10:].index,
        'x' : crop_summary_P['P'][-10:]
    }

    fig.add_trace(
        go.Bar(top,
               name="Most phosphorus required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=top['x']),
        
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(last,
               name="Least phosphorus required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=last['x']),
        row=1, col=2
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(title_text="Phosphorus (P)",
                      plot_bgcolor='white',
                      font_size=12, 
                      font_color='black',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    #fig.show()
    #graph2
    #######################
    ##Potassium analysis
    crop_summary_K = crop_summary.sort_values(by='K', ascending=False)
  
    '''fig = make_subplots(rows=1, cols=2)

    top = {
        'y' : crop_summary_K['K'][0:10].sort_values().index,
        'x' : crop_summary_K['K'][0:10].sort_values()
    }

    last = {
        'y' : crop_summary_K['K'][-10:].index,
        'x' : crop_summary_K['K'][-10:]
    }

    fig.add_trace(
        go.Bar(top,
               name="Most potassium required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=top['x']),
        
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(last,
               name="Least potassium required",
               marker_color=random.choice(colorarr),
               orientation='h',
              text=last['x']),
        row=1, col=2
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(title_text="Potassium (K)",
                      plot_bgcolor='white',
                      font_size=12, 
                      font_color='black',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    #fig.show()
    #graph3
    #########################
    ##N, P, K values comparision between crops
    '''fig = go.Figure()
    fig.add_trace(go.Bar(
        x=crop_summary.index,
        y=crop_summary['N'],
        name='Nitrogen',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=crop_summary.index,
        y=crop_summary['P'],
        name='Phosphorous',
        marker_color='lightsalmon'
    ))
    fig.add_trace(go.Bar(
        x=crop_summary.index,
        y=crop_summary['K'],
        name='Potash',
        marker_color='crimson'
    ))

    fig.update_layout(title="N, P, K values comparision between crops",
                      plot_bgcolor='white',
                      barmode='group',
                      xaxis_tickangle=-45)'''

    #fig.show()
    #graph4
    #####################
    ##NPK ratio for rice, cotton, jute, maize, lentil
    labels = ['Nitrogen(N)','Phosphorous(P)','Potash(K)']
    '''fig = make_subplots(rows=1, cols=5, specs=[[{'type':'domain'}, {'type':'domain'},
                                                {'type':'domain'}, {'type':'domain'}, 
                                                {'type':'domain'}]])

    rice_npk = crop_summary[crop_summary.index=='rice']
    values = [rice_npk['N'][0], rice_npk['P'][0], rice_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Rice"),1, 1)

    cotton_npk = crop_summary[crop_summary.index=='cotton']
    values = [cotton_npk['N'][0], cotton_npk['P'][0], cotton_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Cotton"),1, 2)

    jute_npk = crop_summary[crop_summary.index=='jute']
    values = [jute_npk['N'][0], jute_npk['P'][0], jute_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Jute"),1, 3)

    maize_npk = crop_summary[crop_summary.index=='maize']
    values = [maize_npk['N'][0], maize_npk['P'][0], maize_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Maize"),1, 4)

    lentil_npk = crop_summary[crop_summary.index=='lentil']
    values = [lentil_npk['N'][0], lentil_npk['P'][0], lentil_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Lentil"),1, 5)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig.update_layout(
        title_text="NPK ratio for rice, cotton, jute, maize, lentil",
        annotations=[dict(text='Rice',x=0.06,y=0.8, font_size=15, showarrow=False),
                     dict(text='Cotton',x=0.26,y=0.8, font_size=15, showarrow=False),
                     dict(text='Jute',x=0.50,y=0.8, font_size=15, showarrow=False),
                     dict(text='Maize',x=0.74,y=0.8, font_size=15, showarrow=False),
                    dict(text='Lentil',x=0.94,y=0.8, font_size=15, showarrow=False)])'''
    #fig.show()
    #graph5
    #############
    ##NPK ratio for fruits
    labels = ['Nitrogen(N)','Phosphorous(P)','Potash(K)']
    specs = [[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}],[
             {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}]]
    '''fig = make_subplots(rows=2, cols=5, specs=specs)
    cafe_colors =  ['rgb(255, 128, 0)', 'rgb(0, 153, 204)', 'rgb(173, 173, 133)']

    apple_npk = crop_summary[crop_summary.index=='apple']
    values = [apple_npk['N'][0], apple_npk['P'][0], apple_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Apple", marker_colors=cafe_colors),1, 1)

    banana_npk = crop_summary[crop_summary.index=='banana']
    values = [banana_npk['N'][0], banana_npk['P'][0], banana_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Banana", marker_colors=cafe_colors),1, 2)

    grapes_npk = crop_summary[crop_summary.index=='grapes']
    values = [grapes_npk['N'][0], grapes_npk['P'][0], grapes_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Grapes", marker_colors=cafe_colors),1, 3)

    orange_npk = crop_summary[crop_summary.index=='orange']
    values = [orange_npk['N'][0], orange_npk['P'][0], orange_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Orange", marker_colors=cafe_colors),1, 4)

    mango_npk = crop_summary[crop_summary.index=='mango']
    values = [mango_npk['N'][0], mango_npk['P'][0], mango_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Mango", marker_colors=cafe_colors),1, 5)

    coconut_npk = crop_summary[crop_summary.index=='coconut']
    values = [coconut_npk['N'][0], coconut_npk['P'][0], coconut_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Coconut", marker_colors=cafe_colors),2, 1)

    papaya_npk = crop_summary[crop_summary.index=='papaya']
    values = [papaya_npk['N'][0], papaya_npk['P'][0], papaya_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Papaya", marker_colors=cafe_colors),2, 2)

    pomegranate_npk = crop_summary[crop_summary.index=='pomegranate']
    values = [pomegranate_npk['N'][0], pomegranate_npk['P'][0], pomegranate_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Pomegranate", marker_colors=cafe_colors),2, 3)

    watermelon_npk = crop_summary[crop_summary.index=='watermelon']
    values = [watermelon_npk['N'][0], watermelon_npk['P'][0], watermelon_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Watermelon", marker_colors=cafe_colors),2, 4)

    muskmelon_npk = crop_summary[crop_summary.index=='muskmelon']
    values = [muskmelon_npk['N'][0], muskmelon_npk['P'][0], muskmelon_npk['K'][0]]
    fig.add_trace(go.Pie(labels=labels, values=values,name="Muskmelon", marker_colors=cafe_colors),2, 5)

    fig.update_layout(
        title_text="NPK ratio for fruits",
        annotations=[dict(text='Apple',x=0.06,y=1.08, font_size=15, showarrow=False),
                     dict(text='Banana',x=0.26,y=1.08, font_size=15, showarrow=False),
                     dict(text='Grapes',x=0.50,y=1.08, font_size=15, showarrow=False),
                     dict(text='Orange',x=0.74,y=1.08, font_size=15, showarrow=False),
                    dict(text='Mango',x=0.94,y=1.08, font_size=15, showarrow=False),
                    dict(text='Coconut',x=0.06,y=0.46, font_size=15, showarrow=False),
                     dict(text='Papaya',x=0.26,y=0.46, font_size=15, showarrow=False),
                     dict(text='Pomegranate',x=0.50,y=0.46, font_size=15, showarrow=False),
                     dict(text='Watermelon',x=0.74,y=0.46, font_size=15, showarrow=False),
                    dict(text='Muskmelon',x=0.94,y=0.46, font_size=15, showarrow=False)])'''
    #fig.show()
    #graph6
    ##############
    crop_scatter = cropdf[(cropdf['label']=='rice') | 
                      (cropdf['label']=='jute') | 
                      (cropdf['label']=='cotton') |
                     (cropdf['label']=='maize') |
                     (cropdf['label']=='lentil')]

    '''fig = px.scatter(crop_scatter, x="temperature", y="humidity", color="label", symbol="label")
    fig.update_layout(plot_bgcolor='white')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''

    #fig.show()
    #graph7
    ###################
    '''fig = px.bar(crop_summary, x=crop_summary.index, y=["rainfall", "temperature", "humidity"])
    fig.update_layout(title_text="Comparision between rainfall, temerature and humidity",
                      plot_bgcolor='white',
                     height=500)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)'''
    #fig.show()
    #graph8
    ####################
    ##Correlation between different features
    #fig, ax = plt.subplots(1, 1, figsize=(15, 9))
    #sns.heatmap(cropdf.corr(), annot=True,cmap='Wistia' )
    #ax.set(xlabel='features')
    #ax.set(ylabel='features')

    #plt.title('Correlation between different features', fontsize = 15, c='black')
    #plt.show()
    #graph9
    ###################
    
    #plt.figure(figsize=(15,15))
    #sns.heatmap(cm, annot=True, fmt=".0f", linewidths=.5, square = True, cmap = 'Blues');
    #plt.ylabel('Actual label');
    #plt.xlabel('Predicted label');
    #all_sample_title = 'Confusion Matrix - score:'+str(accuracy_score(y_test,y_pred))
    ##plt.title(all_sample_title, size = 15);
    ##plt.show()
    
    return render_template('process3.html',st=st)
##LSTM
def load_data(stock, seq_len):
    amount_of_features = len(stock.columns)
    data = stock.as_matrix() #pd.DataFrame(stock)
    sequence_length = seq_len + 1
    result = []
    for index in range(len(data) - sequence_length):
        result.append(data[index: index + sequence_length])

    result = np.array(result)
    row = round(0.9 * result.shape[0])
    train = result[:int(row), :]
    x_train = train[:, :-1]
    y_train = train[:, -1][:,-1]
    x_test = result[int(row):, :-1]
    y_test = result[int(row):, -1][:,-1]

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))  

    return [x_train, y_train, x_test, y_test]

def build_model(layers):
    model = Sequential()

    model.add(LSTM(
        input_dim=layers[0],
        output_dim=layers[1],
        return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(
        layers[2],
        return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(
        output_dim=layers[2]))
    model.add(Activation("linear"))

    start = time.time()
    model.compile(loss="mse", optimizer="rmsprop",metrics=['accuracy'])
    print("Compilation Time : ", time.time() - start)
    return model

def build_model2(layers):
        d = 0.2
        model = Sequential()
        model.add(LSTM(128, input_shape=(layers[1], layers[0]), return_sequences=True))
        model.add(Dropout(d))
        model.add(LSTM(64, input_shape=(layers[1], layers[0]), return_sequences=False))
        model.add(Dropout(d))
        model.add(Dense(16,init='uniform',activation='relu'))        
        model.add(Dense(1,init='uniform',activation='linear'))
        model.compile(loss='mse',optimizer='adam',metrics=['accuracy'])
        return model

#LLCNet Model - EfficientNet B0
class EfficientNetB0():
    def __init__(self, blocks_args=None, global_params=None):
        super().__init__()
        assert isinstance(blocks_args, list), 'blocks_args should be a list'
        assert len(blocks_args) > 0, 'block args must be greater than 0'
        self._global_params = global_params
        self._blocks_args = blocks_args

        # Batch norm parameters
        bn_mom = 1 - self._global_params.batch_norm_momentum
        bn_eps = self._global_params.batch_norm_epsilon

        # Get stem static or dynamic convolution depending on image size
        image_size = global_params.image_size
        Conv2d = get_same_padding_conv2d(image_size=image_size)

        # Stem
        in_channels = 3  # rgb
        out_channels = round_filters(32, self._global_params)  # number of output channels
        self._conv_stem = Conv2d(in_channels, out_channels, kernel_size=3, stride=2, bias=False)
        self._bn0 = nn.BatchNorm2d(num_features=out_channels, momentum=bn_mom, eps=bn_eps)
        image_size = calculate_output_image_size(image_size, 2)

        # Build blocks
        self._blocks = nn.ModuleList([])
        for block_args in self._blocks_args:

            # Update block input and output filters based on depth multiplier.
            block_args = block_args._replace(
                input_filters=round_filters(block_args.input_filters, self._global_params),
                output_filters=round_filters(block_args.output_filters, self._global_params),
                num_repeat=round_repeats(block_args.num_repeat, self._global_params)
            )

            # The first block needs to take care of stride and filter size increase.
            self._blocks.append(MBConvBlock(block_args, self._global_params, image_size=image_size))
            image_size = calculate_output_image_size(image_size, block_args.stride)
            if block_args.num_repeat > 1:  # modify block_args to keep same output size
                block_args = block_args._replace(input_filters=block_args.output_filters, stride=1)
            for _ in range(block_args.num_repeat - 1):
                self._blocks.append(MBConvBlock(block_args, self._global_params, image_size=image_size))
                # image_size = calculate_output_image_size(image_size, block_args.stride)  # stride = 1

        # Head
        in_channels = block_args.output_filters  # output of final block
        out_channels = round_filters(1280, self._global_params)
        Conv2d = get_same_padding_conv2d(image_size=image_size)
        self._conv_head = Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self._bn1 = nn.BatchNorm2d(num_features=out_channels, momentum=bn_mom, eps=bn_eps)

        # Final linear layer
        self._avg_pooling = nn.AdaptiveAvgPool2d(1)
        if self._global_params.include_top:
            self._dropout = nn.Dropout(self._global_params.dropout_rate)
            self._fc = nn.Linear(out_channels, self._global_params.num_classes)

        # set activation to memory efficient swish by default
        self._swish = MemoryEfficientSwish()

    def set_swish(self, memory_efficient=True):

        self._swish = MemoryEfficientSwish() if memory_efficient else Swish()
        for block in self._blocks:
            block.set_swish(memory_efficient)

    def extract_endpoints(self, inputs):

        endpoints = dict()

        # Stem
        x = self._swish(self._bn0(self._conv_stem(inputs)))
        prev_x = x

        # Blocks
        for idx, block in enumerate(self._blocks):
            drop_connect_rate = self._global_params.drop_connect_rate
            if drop_connect_rate:
                drop_connect_rate *= float(idx) / len(self._blocks)  # scale drop connect_rate
            x = block(x, drop_connect_rate=drop_connect_rate)
            if prev_x.size(2) > x.size(2):
                endpoints['reduction_{}'.format(len(endpoints) + 1)] = prev_x
            elif idx == len(self._blocks) - 1:
                endpoints['reduction_{}'.format(len(endpoints) + 1)] = x
            prev_x = x

        # Head
        x = self._swish(self._bn1(self._conv_head(x)))
        endpoints['reduction_{}'.format(len(endpoints) + 1)] = x

        return endpoints

    def extract_features(self, inputs):

        # Stem
        x = self._swish(self._bn0(self._conv_stem(inputs)))

        # Blocks
        for idx, block in enumerate(self._blocks):
            drop_connect_rate = self._global_params.drop_connect_rate
            if drop_connect_rate:
                drop_connect_rate *= float(idx) / len(self._blocks)  # scale drop connect_rate
            x = block(x, drop_connect_rate=drop_connect_rate)

        # Head
        x = self._swish(self._bn1(self._conv_head(x)))

        return x

    def forward(self, inputs):

        # Convolution layers
        x = self.extract_features(inputs)
        # Pooling and final linear layer
        x = self._avg_pooling(x)
        if self._global_params.include_top:
            x = x.flatten(start_dim=1)
            x = self._dropout(x)
            x = self._fc(x)
        return x

    
    def from_name(cls, model_name, in_channels=3, **override_params):

        cls._check_model_name_is_valid(model_name)
        blocks_args, global_params = get_model_params(model_name, override_params)
        model = cls(blocks_args, global_params)
        model._change_in_channels(in_channels)
        return model

    
    def from_pretrained(cls, model_name, weights_path=None, advprop=False,
                        in_channels=3, num_classes=1000, **override_params):
        
        model = cls.from_name(model_name, num_classes=num_classes, **override_params)
        load_pretrained_weights(model, model_name, weights_path=weights_path,
                                load_fc=(num_classes == 1000), advprop=advprop)
        model._change_in_channels(in_channels)
        return model

    
    def get_image_size(cls, model_name):
        cls._check_model_name_is_valid(model_name)
        _, _, res, _ = efficientnet_params(model_name)
        return res

   
    def _check_model_name_is_valid(cls, model_name):
        if model_name not in VALID_MODELS:
            raise ValueError('model_name should be one of: ' + ', '.join(VALID_MODELS))

    def _change_in_channels(self, in_channels):
        if in_channels != 3:
            Conv2d = get_same_padding_conv2d(image_size=self._global_params.image_size)
            out_channels = round_filters(32, self._global_params)

            self._conv_stem = Conv2d(in_channels, out_channels, kernel_size=3, stride=2, bias=False)
    def model(self):
        base_model = tf.keras.applications.EfficientNetB0(
            weights="imagenet",
            include_top=False,
            input_shape=(224, 224, 3)
        )
        base_model.trainable = False

        # Add custom layers for classification
        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.3),  # Prevent overfitting
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation="sigmoid")  # Binary classification
        ])
        EPOCHS = 10

        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=EPOCHS
        )
        # Compile the model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss="binary_crossentropy",
            metrics=["accuracy"]
        )
        plt.plot(history.history['accuracy'], label='Train Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.show()

        # Evaluate on test set (if available)
        test_ds = tf.keras.preprocessing.image_dataset_from_directory(
            "path/to/test",
            image_size=IMG_SIZE,
            batch_size=BATCH_SIZE
        )
        test_ds = test_ds.map(preprocess)

        test_loss, test_acc = model.evaluate(test_ds)
        print(f"Test Accuracy: {test_acc:.2f}")
            
##########################
@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


