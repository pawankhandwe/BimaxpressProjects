from typing import final
from django.core.mail import message
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import http
from django.urls import path
from django.shortcuts import redirect, render, HttpResponse
from django.http import HttpResponse, request
from django.core.paginator import Paginator
from fireo.queries import filter_query
# from .decoration import adminuser
from django.core.paginator import Paginator
from .models import *
import os
from .settings import BASE_DIR, EMAIL_BACKEND,EMAIL_PORT, EMAIL_USE_SSL
import fireo

from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
import smtplib
from django.contrib.auth.forms import UserCreationForm
from django.core.mail.message import MIMEMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import get_connection

import urllib
import imaplib
import email
import json
# from .sendemail_form import EmailForm
from django.core.mail import send_mail, send_mass_mail, EmailMessage
import re
import datetime
import os
from datetime import date, datetime
from django.http import HttpResponse, HttpResponseRedirect
# from background_task import background
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from email.mime.message import MIMEMessage
from textwrap import dedent
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
import time
from html import escape, unescape
import requests
import rpa as r

# database stuff
import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate(
    os.path.join(BASE_DIR, "serviceAccountKey.json"))
firebase_admin.initialize_app(cred)
db = firestore.client()
databunny = {}
firebaseConfig = {
    "apiKey": "AIzaSyDlZMu8lypZDEhRpMVKlD3JcTuvItFaG2A",
    "authDomain": "bimaxpress-cashless.firebaseapp.com",
    "projectId": "bimaxpress-cashless",
    "storageBucket": "bimaxpress-cashless.appspot.com",
    "messagingSenderId": "577257002368",
    "databaseURL": "https://accounts.google.com/o/oauth2/auth",
    "appId": "1:577257002368:web:489252768c47b398465d65",
    "measurementId": "G-Y8B68GW5YX"
}
mth = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

week = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
allpage=0

firebase = pyrebase.initialize_app(firebaseConfig)
authe = firebase.auth()



def new_data(request):
    login_id='HEGIC-HS-138249'
    password='HEGIC-HS-138249'
    health_idc='10007116980'
    admon="6"
    adyear='2021'
    addate='13'
    transno='7'
    DOA=addate+'/'+admon+'/+adyear'
    DOBd='3'
    DOBy='2000'
    doc_name='Amrita Mohanty'
    reg_no='OR11864'
    docQ='Ophthalmologist'
    docno='8093028088'
    clino='809328088'
    diagnosis='fever'
    clm_amt='20000'
    file='PREAUTH ID.pdf'
    Dtype='Bills'
    r.init(visual_automation = True)
    r.url('https://heapp5.hdfcergo.com/ProviderPortal')
    r.type('txtUserName',login_id)
    r.type('Password',password)
    r.wait(10)
    r.click('btnDirectLogin')
    r.click('Online Preauth')
    r.click('rdbRetail')
    r.type('txtHdfcergo_id',health_idc)
    r.wait(10)
    r.click('txtAdmissionDate')
    r.select('ui-datepicker-month',admon)
    r.select('ui-datepicker-year',adyear)
    r.click(addate)
    r.click('btnSearch')
    r.url('https://heapp5.hdfcergo.com/ProviderPortal/GeneratePreauth/GeneratePreauthClaim?HegicCardNo='+health_idc+'&TransNo='+transno+'&PolicyNo=4848100245872606000&DOADate=21/07/2021')
    r.click('dvDOBEntered')
    r.select('ui-datepicker-month',DOBd)
    r.select('ui-datepicker-year',DOBy)
    r.click('ui-state-default')
    r.click('ShowDocPanel1')
    r.type('txtSearchDrName',doc_name)
    r.type('txtSearchDrRegNo',reg_no)
    r.click('btnSearchQualification')
    r.click('ddlSearchPhysicianQualification')
    r.select('ddlSearchPhysicianQualification',docQ)
    r.type('txtSearchDrMobileNo',docno) 
    r.type('txtSearchDrTelClinic',clino)
    r.click('Save')
    r.keyboard('safari[enter]')
    r.click('Diagnosis Details')
    r.type('txtUserAilment',diagnosis)
    r.click('click Other Details and Document Upload')
    r.type('txtClaimedAmount',clm_amt)
    r.upload('#fileInput', file)
    r.click('ddlDocument_Type')
    r.select('ddlDocument_Type',Dtype)
    r.click('Upload')
    r.wait(10)
    r.close()
    
def postsignIn(request):
    try:
        context={}
        cases_data={}
        values={}
        mydoctor={}
        list_status = ['draft',  'Unprocessed', 'query', 'Approved', 'Reject',
                    'Enhance', 'Discharge_Approved', 'Settled']
        
        if request.method == "POST":
            email = request.POST.get('email')
            pasw = request.POST.get('pass')
            try:
                user = authe.sign_in_with_email_and_password(email, pasw)
                request.session['email'] = user['email']

            except:
                message = "Invalid Credentials!!Please ChecK your Data"
                return render(request, "login.html", {"message": message})

            docs = db.collection(u'backend_users').where(
                    u'email', u'==', user['email']).stream()
            print("Executing")
            for doc in docs:
                Role = doc.to_dict()
                request.session['role'] = Role['Role']

            if Role['Role'] != 'admin':
                request.session['hospital_email'] = Role['hospital']
                doc_ref = db.collection(u'counter').document(request.session['hospital_email'])

                doc_counter = doc_ref.get()
                if doc_counter.exists:
                    values = doc_counter.to_dict()
                else:
                    print(u'No such document!')
                    
                cases_draft = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , "draft").get()

 
                cases = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , "draft").stream()
                for i in cases:
                    cases_data[i.id] = i.to_dict()
                    
                print(values)
                context["cases_data"] = cases_data
                context["draft"] = len(cases_draft)
                context['list_status'] = list_status
                context['values'] = values
                context['hospital_email'] = request.session['hospital_email']
                context['role'] = request.session['role']
                return render(request, "index.html", context)
            
            else:
                request.session['hospital_email'] = user['email']
                print("this is session",request.session['hospital_email'])
                return redirect("mainpage")
        else:
            return redirect("login")
    except:
        return redirect("login")

     
def newcase(request):
    context={}
    doc_ref_two = db.collection(u'backend_users').document(request.session['email'])
    docs = doc_ref_two.get()
    if docs.exists:
        print(f'Document data: {docs.to_dict()}')
        
        context["role"] = docs.to_dict()['Role']
        
    docs = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').get()
    casenumber = len(docs)+1
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
    doc = doc_ref.get()
    datamy=[]
    mydoctor={}
    if doc.exists:
        datamy = doc.to_dict()['Empanelled_companies']
    else:
        print(u'No such document!')
    print(datamy)
    docs = db.collection(u'backend_users').where(u'hospitals', "array_contains", request.session['hospital_email']).stream()
    for doc in docs:
        mydoctor[doc.id] = doc.to_dict()
            
       
            

    context ['doctor'] = mydoctor
    
    context['company'] = datamy
    context['akey'] = "case"+str(casenumber)
    context['email'] = request.session['hospital_email']
    system = request.session['hospital_email']+"+"+"case"+str(casenumber)
    
    print(system)
    context['system'] = system
    return render(request, "pageAccordian.html", context)


def mainpage(request):
    print("got it")
    context = {}
    cases_data = {}
    list_status = ['draft',  'Unprocessed', 'query', 'Approved', 'Reject',
                   'Enhance', 'Discharge_Approved', 'Settled']

    print("this is role ", request.session['role'])
    print("hospooiiiiiiiiiiiii",request.session['hospital_email'])
    
    cases_draft = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , "draft").get()
    
    
    doc_ref = db.collection(u'counter').document(request.session['hospital_email'])

    doc_counter = doc_ref.get()
    if doc_counter.exists:
        values = doc_counter.to_dict()
    else:
        print(u'No such document!')
 

    if request.session['role'] != 'admin':
        
        cases = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , "draft").stream()
        
        for i in cases:
            cases_data[i.id] = i.to_dict()
        
        
       
        print(values)
        context['draft'] = len(cases_draft)
        context["cases_data"] = cases_data
        context['list_status'] = list_status
        context['values'] = values
        context['hospital_email'] = request.session['hospital_email']
        context['role'] = request.session['role']
        return render(request, "index.html", context)
            
    else:
        print("this is session",request.session['hospital_email'])
        
        cases = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , "draft").stream()

        for i in cases:
            cases_data[i.id] = i.to_dict()

        print(values)
        context['draft'] = len(cases_draft)
        context["cases_data"] = cases_data
        context['list_status'] = list_status
        context['values'] = values
        context['hospital_email'] = request.session['hospital_email']
        context['role'] = request.session['role']
        return render(request, "index.html", context)
        


def hospital(request):
    context = {}
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
    doc = doc_ref.get()
    if doc.exists:
        print(f'Document data: {doc.to_dict()}')
        
        context["hospitals"] = doc.to_dict()
    else:
        print(u'No such document!')

    context["role"] = request.session['role']
    return render(request, 'hospital.html', context)

def hospitalEdit(request):
    context = {}
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
    doc = doc_ref.get()
    if doc.exists:
        print(f'Document data: {doc.to_dict()}')
        print(type(doc.to_dict()))
        context["hospitals"] = doc.to_dict()
    else:
        print(u'No such document!')

    if request.method == "POST":
        data = request.POST.dict()
        print(data)
        db.collection(u'hospitals').document(request.session['email']).update(data)

    context["role"] = request.session['role']
    return render(request, 'hospitalEdit.html', context)

def plandetails(request):
    context = {}
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
    doc = doc_ref.get()
    if doc.exists:
        print(f'Document data: {doc.to_dict()}')
        context["hospitals"] = doc.to_dict()
    else:
        print(u'No such document!')
    
    context["role"] = request.session['role']
    return render(request, 'plandetails.html', context)

def sendData(request):
    context ={}
    if request.method == "POST":
        data = request.POST.dict()
        mystr = str(data['mybtn'])
        context['perticulerAnalyst'] = mystr.split(",")
        print(context)
    context["role"] = request.session['role']
    return render(request , 'analistEdit.html',context)


def analist(request):
    context= {}
    mylist = []
    docs = db.collection(u'backend_users').where(u'hospital', u'==', request.session['hospital_email']).stream()

    for doc in docs:
        mylist.append(doc.to_dict())
        context ['claimAnalyst'] = mylist
        
    print("list of analyst",mylist)

    context["role"] = request.session['role']
    return render(request, 'analist.html', context)

def analistAdd(request):
    context={}
    if request.method == "POST":
        data = request.POST.dict()
        email = request.POST.get('email')
        pasw = request.POST.get('password')
        try:
            authe.create_user_with_email_and_password(email, pasw)

        except:
            return HttpResponse("Please Recreate Doctor Inconvinience Regretted")
        
        print("this is data", data)
        db.collection(u'backend_users').document(data['email']).set({
            "email":data['email'],
            "employeeId":data['employeeId'],
            "hospital":request.session['email'],
            "name":data['name'],
            "phone":data['phone'],
            "Role":"claim_analyst"
        })
        context['role'] = request.session['role']
        return redirect('analist')
    
    
        
    context['role'] = request.session['role']
    return render(request, 'analistAdd.html',context)

def analistEdit(request):
    context={}
    if request.method == "POST":
        data = request.POST.dict()
        print(data)
        data.pop('csrfmiddlewaretoken')
        print(request.session['email'])
        db.collection(u'backend_users').document(data['email']).update(data)
    return redirect('analist')
    


def doctor(request):
    context= {}
    mylist = []
    docs = db.collection(u'backend_users').where(u'hospitals', "array_contains", request.session['hospital_email']).stream()
    for doc in docs:
        mylist.append(doc.to_dict())
        
    context ['doctor'] = mylist
    print(context)
    context['role'] = request.session['role']
    return render(request, 'doctor.html',context)

def sendDataDoctors(request):
    context= {}
    if request.method == "POST":
        data = request.POST.dict()
        print("last ", data)
        mystr = str(data['mybtn'])
        context['perticulerdoctor'] = mystr.split(",")

    doc_ref_two = db.collection(u'backend_users').document(request.session['email'])
    docs = doc_ref_two.get()
    if docs.exists:
        print(f'Document data: {docs.to_dict()}')
        
        context["role"] = docs.to_dict()['Role']
    return render(request , "doctorEdit.html",context)

def doctorEdit(request):
    context={}
    if request.method == "POST":
        data = request.POST.dict()
        print(data)
        data.pop('csrfmiddlewaretoken')
        db.collection(u'backend_users').document(data['email']).update(data)

    return redirect('doctor')

def doctorAdd(request):
    context={}
    print("thssssssssssssssssssss")
    print("yes")
    if request.method == "POST":
        
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        print("Last",data)
        doc_ref = db.collection(u'backend_users').document(data['email'])
        doc = doc_ref.get()
        if doc.exists:
            db.collection(u'backend_users').document(data['email']).update({"hospitals": firestore.ArrayUnion([request.session['email']])})
        else:
            email = request.POST.get('email')
            pasw = request.POST.get('password')
            try:
                authe.create_user_with_email_and_password(email, pasw)
            except:
                return HttpResponse("Please Recreate Doctor Inconvinience Regretted")

            db.collection(u'backend_users').document(data['email']).set({
                "doctorRegistrationNo":data['doctorRegistrationNo'],
                "email":data['email'],
                "name":data['name'],
                "phone":data['phone'],
                "qualification":data['qualification'],
                "speciality":data['speciality'],
                "Role":"doctor",
            })
            db.collection(u'backend_users').document(data['email']).update({"hospitals": firestore.ArrayUnion([request.session['email']])})
            return redirect("doctor")
            
            
        
    context["role"] = request.session['role']    
    return render(request, 'doctorAdd.html',context)



def EmpanelledCompanies(request):
    context={}
    temp = {}
    empanneled =[]
    res=[]
    print(request.session['hospital_email'])
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
    doc = doc_ref.get()
    if doc.exists:
        temp = doc.to_dict()
        companies = temp['Empanelled_companies']
        empanneled = list(companies.keys())
        for i in empanneled:
            res.append(i.strip())
        print(res)
        
        images={}
        
        for i in res:
            print("val of i",i)
            doc_ref = db.collection(u'InsuranceCompany_or_TPA').document(f"{i}")
            doc = doc_ref.get()
            if doc.exists:
                img_value = doc.to_dict()
                print(img_value)
                images[doc.id]=(img_value['image'])
        context['images'] = images
    else:
        print(u'No such document!')
        
    print(images)

    context["role"] = request.session['role']
    return render(request, 'empanelledCompanies.html',context)


def sendcompany(request , p):
    context={}
    print("value of P",p)
    # doc_ref = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
    #     u'cases').document(f'{casenumber}').collection("patient_details").document("patient_details")

    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
    doc = doc_ref.get()
    if doc.exists:
        temp = doc.to_dict()
        temp1 = temp['Empanelled_companies']
        gotvalue = {x.replace(' ', ''): v for x, v in temp1.items()}
        print("gotvalue ki value",gotvalue)
        companydata = gotvalue[p]
    print(companydata)
    context['companydata'] = companydata
    context['companyname'] = p
    context['role'] = request.session['role']
    
    return render(request, "companyDetails.html" ,context)

def saveinsurancedata(request):
    context={}
    doc_ref_two = db.collection(u'backend_users').document(request.session['email'])
    docs = doc_ref_two.get()
    if docs.exists:
        print(f'Document data: {docs.to_dict()}')
        
        context["role"] = docs.to_dict()['Role']
    if request.method == "POST":
        data = request.POST.dict()

    ref = db.collection(u'hospitals').document(request.session['email'])
    
    data=  {
            "Empanelled_companies":{
                data['companyname']:{
                    "Discount":data.get("Discount",""),
                    "Exclusion":data.get("Exclusion",""),
                    "Expiry":data.get("Expiry","")
                }
            }
        }
    
    ref.set(data,merge=True)
    
    return redirect("EmpanelledCompanies")

def listData(request, p):
    context = {}
    cases_data={}
    context['role'] = request.session['role']
    if request.session['role'] != None:
        list_status = ['draft',  'Unprocessed', 'query', 'Approved', 'Reject',
                       'Enhance', 'Discharge_Approved', 'Settled']
        
        doc_ref = db.collection(u'counter').document(request.session['hospital_email'])

        doc_counter = doc_ref.get()
        if doc_counter.exists:
            values = doc_counter.to_dict()
        else:
            print(u'No such document!') 
            
        
        print("Runnign")
        
        cases_draft = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , "draft").get()
    

        cases = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').where(u'status', u'==', "done").where("formstatus", "==" , f"{p}").stream()
        for i in cases:
            cases_data[i.id] = i.to_dict()
        print(values)
        print(cases_data)
        
        print("yes2")
    
        context["cases_data"] = cases_data
        context['draft'] = len(cases_draft)
        context['list_status'] = list_status
        context['hospital_email'] = request.session['hospital_email']
        context['role'] = request.session['role']
        context["values"] = values
        context['p'] = p
        
        print("P is here",p)
        

        if p.upper() == "DRAFT":
            context['isdraft'] = True
        else:
            context['isdraft'] = False
                
        if p.upper() == "UNPROCESSED":
            context['isunprocessed'] = True
        else:
            context['isunprocessed'] = False
                

        if p.upper() == "ISSUBMITTED_QUERY":
            context['issubmitted_query'] = True
        else:
            context['issubmitted_query'] = False

        if p.upper() == "QUERY":
            context['isquery'] = True
        else:
            context['isquery'] = False

        if p.upper() == "APPROVED":
            context['isapproved'] = True
        else:
            print("runnnniiiiiiiiiing")
            context['isapproved'] = False

        if p.upper() == "REJECT":
            context['isreject'] = True
        else:
            context['isreject'] = False

        if p.upper() == "ENHANCE":
            context['isenhance'] = True
        else:
            context['isenhance'] = False

        if p.upper() == "DISCHARGE APPROVE":
            context['isdischargeapprove'] = True
        else:
            context['isdischargeapprove'] = False

        if p.upper() == "SETTLED":
            context['issettled'] = True
        else:
            context['issettled'] = False

        return render(request, 'renderCards.html', context)
    else:
        return redirect('mainpage')    


def updateunprocess(request):
    context = {}
    casenumber = request.GET.get('data', None)
    flag = 0
    email = ""
    case = ""
    for char in casenumber:
        if char == " ":
            flag = 1
        if flag == 0 and char != ' ':
            email = email+char
        if flag == 1 and char != ' ':
            case = case+char
    try:
        db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(case).update({
            'formstatus': "Unprocessed",
        })
    except:
        db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(case).add({
            'formstatus': "Unprocessed",
        })

    return redirect("mainpage")

def getcasedetail(request):
    context = {}
    list_status = ['Unprocessed', 'query', 'Approved', 'Reject',
                       'Enhance', 'Discharge_Approved', 'Settled']
    casenumber = request.GET.get('data')
    print("hosital email",request.session['hospital_email'])
    print(casenumber)
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}')
    doc = doc_ref.get()

    if doc.exists:
        a = doc.to_dict()
        
        convert = a['patient_details']['Insurance_Company']
        convert = convert.replace("_", " ")
        context['insurance_company'] = convert
        context['real_insurance'] = a['patient_details']['Insurance_Company']
        context['patient_name'] = a['patient_details']['Name']
        context['caseid'] = casenumber                      
        context['contact_Number'] = a['patient_details']['Phone']
        context['doctor_natureOfLiness'] = a['patient_details']['Nature_Of_Illness']
        context['city'] = a['patient_details']['city']
        context['healthid'] = a['patient_details']['Health_Id']
        
    else:
        print("no data found")

    doc_ref_new = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}')
    doc_new = doc_ref_new.get()

    if doc_new.exists:
        b = doc_new.to_dict()
        print("bhhhhhhhhhhhhhhhhhh",b)
        context['admissiondate'] = b['hospital_details']['Date_of_Admission']
        context['treating_doctor'] = b['hospital_details']['Treating_Doctor_Name']
        context['list_status'] = list_status

    else:
        print("no data found")

    status = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}')

    formstatus = status.get()
    if formstatus.exists:
        b = formstatus.to_dict()
        print(b)
        context['formstatus'] = b['formstatus']

    else:
        print("no data found o")
    audit = []

    audit_trail = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}')
    audit_value = audit_trail.get()

    if audit_value.exists:
        b = audit_value.to_dict()
        print(b)
        if len(b) > 3:
            values = b['audit_trail']
            for i in values:    
                x = i.split("+")
                audit.append(x)
            print(audit)
            context['audit'] = audit
            context['hospital_email'] = request.session['hospital_email']
            context['casenumber'] = casenumber
        else:
            print("no data found")
            context['hospital_email'] = request.session['hospital_email']
            context['casenumber'] = casenumber
    else:
        context['hospital_email'] = request.session['hospital_email']
        context['casenumber'] = casenumber
    context['role'] = request.session['role']

    return render(request, 'caseDetails.html', context)
    
def updateFormstatus(request, new):
    new_status = ''
    email = ''
    old_status = ''
    case = ''
    flag = 1
    print("update form status", new)
    for char in new:
        if char == '+':
            flag = 0
        if flag == 1:
            new_status = new_status+char
        if char == '*':
            flag = 2
        if char == '&':
            flag = 3
        if flag == 0 and char != '+':
            email = email+char
        if flag == 2 and char != '*':
            old_status = old_status+char
        if flag == 3 and char != '&':
            case = case+char
            
    return HttpResponse("success")


def claimpage1(request):
    if request.session.get('role') != None:
        context = {}
        system = request.GET.get('system', None)
        flag = 0
        email = ''
        case = ''
        for char in system:
            if char == "+":
                flag = 1
            if flag == 0 and char != '+':
                email = email+char
            if flag == 1 and char != '+':
                case = case+char
        print(email)
        print(case)
        bunny = {}
        
        singlecasedata = db.collection('hospitals').document(
                request.session['hospital_email']).collection(u'cases').document(case).get()
        if singlecasedata.exists:
            bunny=singlecasedata.to_dict()
        else:
            print(u'No such document!')
            
        # //doctor Dropown
        mydoctor={}
        
        docs = db.collection(u'backend_users').where(u'hospitals', "array_contains", request.session['hospital_email']).stream()
        for doc in docs:
            mydoctor[doc.id] = doc.to_dict()
            
       
            

        context ['doctor'] = mydoctor
        
        
        
                    
        print("this is bunnny dictonary",bunny)
        
        doc_ref = db.collection(u'hospitals').document(request.session['hospital_email'])
        doc = doc_ref.get()
        datamy=[]
        if doc.exists:
            datamy = doc.to_dict()['Empanelled_companies']

        else:
            print(u'No such document!')
       
        print(datamy)
    
        context['company'] = datamy
        
        context['casenumber'] = case
        context['email'] = email
        context['bunny'] = bunny
        context['data'] = databunny
        context['system'] = system
        context['role'] = request.session['role']
        
        context['existForm'] ="Yes"

        print("cool dude", system)
        
        doc = db.collection('hospitals').document(email).collection('cases').document(case).get()
        if doc.exists:
            print(f'Document data: {doc.to_dict()}')
            data = doc.to_dict()
        else:
            print(u'No such document!')	

        

        try: 
            context['Aadhar_Card_Back'] = data['patient_details']['Aadhar_Card_Back']

        except:
            context['Aadhar_Card_Back'] = "https://thumbs.dreamstime.com/z/no-image-available-icon-photo-camera-flat-vector-illustration-132483296.jpg"

        try:
            context['Aadhar_card_Front'] = data['patient_details']['Aadhar_card_Front']
        
        except:
            context['Aadhar_card_Front'] = "https://thumbs.dreamstime.com/z/no-image-available-icon-photo-camera-flat-vector-illustration-132483296.jpg"
        
        try:
            context['Health_card'] = data['patient_details']['Health_card']
        except:
            context['Health_card']= "https://thumbs.dreamstime.com/z/no-image-available-icon-photo-camera-flat-vector-illustration-132483296.jpg"

        return render(request, 'pageAccordian.html', context)
    else:
        return redirect('login')



def logout(request):
    request.session.flush()
    return redirect('login')


def adduser(request):
    context = {}
    context['role'] = request.session.get('role')
    return render(request, 'addaccount.html', context)


def index(request):

    return render(request, 'index.html')


def about(request):
    return HttpResponse("About page bolte")

def addcompany(request):
    data=[]
    context={}
    if request.method == "POST":
        data = request.POST.dict()
    data.pop('csrfmiddlewaretoken')
    context['randomCompany'] = data['insurance_company']
    context['email'] = request.session['hospital_email']
       
    context['role'] = request.session['role']    
    return render(request, 'randomCompany.html',context)

def empanelledCompaniesAdd(request):
    context={}
    insurance_company = {}
    doc_ref_two = db.collection(u'backend_users').document(request.session['hospital_email'])
    docs = doc_ref_two.get()
    if docs.exists:
        print(f'Document data: {docs.to_dict()}')
        
        context["role"] = docs.to_dict()['Role']
    message = "Provide Email password to singnIn"
    docs = db.collection(u'InsuranceCompany_or_TPA').stream()
    for doc in docs:
        insurance_company[f'{doc.id}'] = f'{doc.to_dict()}'
    print(insurance_company)
    context['company'] = insurance_company
    return render(request, 'empanelledCompaniesAdd.html',context)

def login(request):
    # context = {}
    # message = "Provide Email password"
    # context['message'] = message
    # client = razorpay.Client(auth=("rzp_test_b3CpaCEQMBm0qq", "q33pGrbne9OBFCdpWTwFsk00"))
    # data = {
    #     "email":"grvshrivastava45655@gmail.com",
    #     "contact":"7247020941",
    #     "name" : "Gourav",
    #     "fail_existing": "0",
        
    # }
    # print(client.customer.create(data=data))
    
    return render(request, 'login.html')

def sendmail(request):
    try:
        emailId = request.session['hospital_email']
        data = db.collection(u'hospitals').document(emailId).get()
        user = data.to_dict()['Emailer']
        emailId = user['email']
        # emailId = 'anishshende001@gmail.com'
        smtpVal = user['smtp']
        imapVal = user['imap']
        password = user['password']
        if request.method == 'POST':
            sub = request.POST.get('email_title',"")
            body = request.POST.get('email_content',"")
            print("body",body)
            check = request.POST.get('cc',"")
            Cc = check.split(" ")
            print("cc value is ",Cc)
            consultPapers = request.FILES.getlist('uploadConsultation')
            healthCard = request.FILES.getlist("uploadPatientsHealth")
            aadharCard  = request.FILES.getlist("idproofid")
            preauth = request.FILES.getlist("uploadSigned")
            otherDocument = request.FILES.getlist("otherDocumentsg")
            print(healthCard,consultPapers,preauth,consultPapers,otherDocument)
            
            print('*****')
            files = healthCard+consultPapers+aadharCard+preauth+otherDocument
            print(sub)
            print(body)
            
            list = request.POST.get('sendbtn')
            Bcc =""
            
            data = list.split('+')
            companyName = data[0]
            
            
            case = data[2]

            db.collection(u'hospitals').document(data[1]).collection('cases').document(case).update({
                "formstatus":"Unprocessed",
            })
            
            db.collection(u'counter').document(request.session['hospital_email']).update({
                            'draft': firestore.Increment(-1),
                            'Unprocessed': firestore.Increment(1),
            })

            print(companyName)
            print(case)
            companyName = companyName.replace(" ","_")
            companyDetails = db.collection(u'InsuranceCompany_or_TPA').document(companyName).get().to_dict()
            print(companyDetails)
            to = companyDetails['email']
            # to = 'cse180001006@iiti.ac.in'
            try:
                print("emailid",emailId)
                print("emailid",to)
                
                print("password",)
                
                sendemail(emailId,to,sub,body,Bcc,Cc,files,smtpVal,imapVal,password)
            except:
                context={}
                message="Emailer has some issue please send mail Manually"
                context['message'] = message
                return render(request,"404.html",context)
            
            return redirect('mainpage')
    except Exception as e:
        return HttpResponse("Exception")

def resendemail(request):
    if request.method == "POST":
        data = request.POST.dict()
    if data['email'] != "":
        authe.send_password_reset_email(data['email'])
    else:
        return redirect("login")
    
    return redirect("login")
   
   
def get_name(email):
    try:
        name = ''
        for char in email:
            if char == '@':
                return name
            name = name+char
    except:
        return None


def savestatus(request):
    if request.method == "POST":
        data = request.POST.dict()

    print(data)
    # city_ref = db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(data['save'])
    print('********************')
    list = data['save'].split(',')
    
    if len(list) == 3:
        caseNumber = list[0]
        data['save'] = caseNumber
        insuranceCompany = list[1]
        currentformstatus = list[2]
        print("length of list",len(list))
        newformstatus=data['status']
        # print(city_ref)
        files = request.FILES.getlist('files')
        check = request.POST.get('cc',"")
        Cc = check.split(" ")
        sub = data['email_title']
        msg = data['email_content']
        toEmail = db.collection(u'InsuranceCompany_or_TPA').document(insuranceCompany).get().to_dict()['email']

        print('********************')

        try:
            db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(f'{caseNumber}').update({"audit_trail": firestore.ArrayUnion([data.get(
                f'{newformstatus}', f'{newformstatus}')+'+'+datetime.today().strftime('%Y-%m-%d')+'+'+data['email_title']])})

            db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(f'{caseNumber}').update({
                'formstatus': data['status'],
                'settledate': data.get('date', ""),
                'settleamount': data.get('amount', ""),
                'status': "done"
            })

            if(currentformstatus != newformstatus):
                db.collection(u'counter').document(request.session['hospital_email']).update({
                                f'{currentformstatus}': firestore.Increment(-1),
                                f'{newformstatus}': firestore.Increment(1),              
                })
            
                
        except:
            print("Exception aarh h ")
            return HttpResponse("Exception")

        fromEmail = request.session['hospital_email'] 
        
        details = db.collection(u'hospitals').document(fromEmail).get().to_dict()['Emailer']	
        fromEmail = details['email']
        smtpVal = details['smtp']
        imapVal = details['imap']
        password = details['password']
        Bcc = ""
        
        
        sendemail(fromEmail,toEmail,sub,msg,Bcc,Cc,files,smtpVal,imapVal,password)
            
        return redirect("mainpage")
    else:
        caseNumber = list[0]
        data['save'] = caseNumber
        insuranceCompany = list[1]
        currentformstatus = list[2]
        print("length of list",len(list))
        newformstatus=data['status']
        
        
        print("check statement",caseNumber,newformstatus,currentformstatus)
        try:
            db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(f'{caseNumber}').update({"audit_trail": firestore.ArrayUnion([data.get(
                f'{newformstatus}', f'{newformstatus}')+'+'+datetime.today().strftime('%Y-%m-%d')+'+'+'Status Changed'])})
            
            db.collection(u'hospitals').document(request.session['hospital_email']).collection(u'cases').document(f'{caseNumber}').update({
                'formstatus': data['status'],
                'settledate': data.get('valuedate', ""),
                'settleamount': data.get('valueamount', ""),
                'status': "done"
            })
            
            if(currentformstatus != newformstatus):
                db.collection(u'counter').document(request.session['hospital_email']).update({
                                f'{currentformstatus}': firestore.Increment(-1),
                                f'{newformstatus}': firestore.Increment(1),              
                })
        except:
            print("Exception aarh h")
            return redirect("error_404")        
        return redirect("mainpage")

def generateform(request):
    request.session['counter'] = 0
    context = {}
    form = ""
    form_data = ""
    flag=0
    email=""
    case=""
    bunny=[]
    if request.method == "POST":
        data = request.POST.dict()
        system = request.POST.get('finalvalue', None)
        print(system)
        for char in system:
            if char == "+":
                flag = 1
            if flag == 0 and char != '+':
                email = email+char
            if flag == 1 and char != '+':
                case = case+char
        print("this is case value",case)
        print(email)
        doc_ref = db.collection(u'hospitals').document(email)

        doc = doc_ref.get()
        if doc.exists:
            hospitaldata = doc.to_dict()
        else:
            print(u'No such document!')
            
        bunny = {}
        
        singlecasedata = db.collection('hospitals').document(
                request.session['hospital_email']).collection(u'cases').document(case).get()
        if singlecasedata.exists:
            bunny=singlecasedata.to_dict()
            doctor_email = singlecasedata.to_dict()['hospital_details']['Treating_Doctor']
        else:
            print(u'No such document!')
        
        doctor_details = db.collection("backend_users").document(f"{doctor_email}").get()
        if doctor_details.exists:
            values_doctor=doctor_details.to_dict()            
        else:
            print(u'No such document!')
            
        context['doctor_details'] = values_doctor
           
        try:
            if request.session['counter'] == 0:
                request.session['counter'] = request.session['counter']+1
            print(request.session['counter'])
            if(bunny["patient_details"]["Insurance_Company"]) == "HDFC_ERGO_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "hdfc.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Paramount_Health_Services_&_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "paramount.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Medi_Assist_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Medi_assist.html", context)
            
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Bajaj_Allianz_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "bajaj_allianz.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Star_Health_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "star.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Cholamandalam_MS_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "chola.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Aditya_Birla_Health_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "AdityaBirla.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Family_Health_Plan_Insurance_TPA_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "fhpl.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "MDIndia_Health_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "md_india_real.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Religare_Health_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Religare.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "Max_Bupa_Health_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Reliance.html", context)
            
            if(bunny["patient_details"]["Insurance_Company"]) == "IFFCO_Tokio_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "IFFCKO.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Vidal_Health_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "vidal.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "ICICI_Lombard_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "ICICI.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Vipul_Medcorp_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Vipul.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Universal_Sompo_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Sompo.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Ericson_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Ericson.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Medsave_Health_Insurance_TPA_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "MedSave.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Liberty_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Liberty.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Health_Insurance_TPA_of_India_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "HealthInsurance.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Heritage_Health_Insurance_TPA_Private_Limited":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Heritage.html", context)

            if(bunny["patient_details"]["Insurance_Company"]) == "Future_Generali_General_Insurance":
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "Future_Generali.html", context)
            else:
                context['hospitaldata'] = hospitaldata
                context['bunny'] = bunny
                return render(request, "irda.html", context)
                return HttpResponse(bunny["patient_details"]["Insurance_Company"])
                
        except Exception as e:
            return HttpResponse(e,"Somthing Went Wrong Contact 9406928294")
            
def error_404(request,exception):
    return render(request,"404.html");

def error_500(request):
        return render(request,"404.html")

def error_403(request,  exception):
        return render(request,"404.html")

def error_400(request,  exception):
        return render(request,"404.html")


def newdb(request):
    docs = db.collection(u'discountMaster').stream()

    for doc in docs:
        print(f'{doc.id} : {doc.to_dict()}')
        
        
    return HttpResponse("bro")
    
    
def saveData(request):
    context = {}
    form = ""
    form_data = ""
   
    if request.method == "POST":
        data = request.POST.dict()
        system = request.POST.get('save', None)
        form = request.POST.get('last', None)
        if(form != None):
            form_data = form[-4:]
        print("system = ", system)
        flag = 0
        email = ''
        case = ''
        print(" System value when in last"+f"{system}")
        print(system)
        
        
        # if system == None:
        #     context['data'] = data
        #     print(data["insurance_company"])
        #     if data["insurance_company"] == "HDFC ERGO General Insurance":
        #         print("None called")
        #         return render(request, "hdfc.html", context)
        #     else:
        #         return render(request, "hdfc.html", context)

        # if system == "":
            
        #     context['data'] = data
        #     print(data["insurance_company"])
        #     if data["insurance_company"] == "HDFC ERGO General Insurance":
        #         print("None called")
        #         return render(request, "hdfc.html", context)
        #     else:
        #         return render(request, "hdfc.html", context)

        # if system == " ":
        #     sys = request.POST.get('save', None)
        #     print("value of system",sys)
        #     context['data'] = data
        #     print(data["insurance_company"])
        #     if data["insurance_company"] == "HDFC ERGO General Insurance":
        #         print("None called")
        #         return render(request, "hdfc.html", context)
        #     else:
        #         return render(request, "hdfc.html", context)



        if system != None:
            print("running inside")
            for char in system:
                if char == "+":
                    flag = 1
                if flag == 0 and char != '+':
                    email = email+char
                if flag == 1 and char != '+':
                    case = case+char
            print("email = ", email)
            print("case = ", case)
            context["data"] = data
            datetoday = date.today()
            Proposed_Line_Of_Treat=[]
            # return render(request,"test.html",context)
            try:
                    if data.get("doctor_proposedLineOfTreatment_Medical_Managment", "") == 'Yes':
                        Proposed_Line_Of_Treat.append("Medical Management")
                    if data.get("doctor_proposedLineOfTreatment_Surgical_Managment", "") == 'Yes':
                        Proposed_Line_Of_Treat.append("Surgical Managment")
                    if data.get("doctor_proposedLineOfTreatment_Intensive_Care", "") == 'Yes':
                        Proposed_Line_Of_Treat.append("Intensive Care")
                    if  data.get("doctor_proposedLineOfTreatment_Investigation", "") == 'Yes':
                        Proposed_Line_Of_Treat.append("Investigation")
                    if data.get("doctor_proposedLineOfTreatment_Allopathic_Treatment", "") == 'Yes':
                        Proposed_Line_Of_Treat.append("Non Allopathic Treatment")
                    
                    print("final submission Taking Place")
                    ref = db.collection(u'hospitals').document(request.session['hospital_email']).collection('cases').document(case)
                    a =  data.get("doctor_email","")
                    x = a.split("+")
                    try:
                                doctor_name_email = x[0]
                                doctor_name = x[1]
                                
                    except:
                                doctor_name_email = "test"
                                doctor_name = "test"
                       
                                
                    newdata = {
                            "patient_details": {
                                "city":data.get("city"," "),
                                "Insurance_Company": data.get("insurance_company", ""),
                                "Name": data.get("patient_details_name",""),
                                "Gender": data["patient_details_gender"],
                                "AgeYear": data["patient_details_ageYear"],
                                "AgeMonth": data["patient_details_ageMonth"],
                                "DOB": data["patient_details_date"],
                                "Phone": data["patient_details_contact_number"],
                                "Attending_Relative_Number": data["patient_details_numberOfAttendingRelative"],
                                "Health_Id": data["patient_details_insuredMemberIdCardNo"],
                                "Policy_Id": data["patient_details_policyNumberorCorporateName"],
                                "EmployeeId": data["patient_details_EmployeeId"],
                                "Other_Insurance_Details": data.get("patient_details_Give_details",""),
                                "Address": data["patient_details_currentAddress"],
                                "Occupation": data["patient_details_occupation"],
                                "Nature_Of_Illness": data["doctor_natureOfLiness"],
                                "Physician": data.get("patient_details_familyPhysician", ""),
                                "Nature_Of_Illness": data["doctor_natureOfLiness"],
                                "Duration_Of_Present_Ailments": data["doctor_durationOfPresentAliment"],
                                "Date_Of_First_Consultation": data["doctor_dateOfFirstConsultation"],
                                "Past_History_Of_Present_Ailments": data["doctor_PastHistoryOfPresentAlignment"],
                                "Provision_Diagnosis": data["doctor_provisionalDiagnosis"],
                                "ICD_Code": data["doctor_icdCode"],
                                'If_Investigation_Or_Medical_Management_Provide_Details' :data['If_Investigation_Or_Medical_Management_Provide_Details'],
                                'Route_Of_Drug_Administration': data['Route_Of_Drug_Administration'],
                                'If_Surgical_Name_of_Surgery':data['If_Surgical_Name_of_Surgery'],
                                'ICD_Code_10_PCS':data['ICD_Code_10_PCS'],
                                "If_Other_Treatment_Provide_Details": data["doctor_ifOtherTratmentProvideDetails"],
                                "How_Did_Injury_Occur": data["doctor_howDidInjuryOccure"],
                                "Date_Of_Injury":data.get("doctor_dateOfInjury",""),
                                "Relevant_Critical_Findings":data.get("doctor_releventClinicFindings",""),
                                "MandatoryPastHistoryMonth": data["admission_mandatoryPastHistoryMonth"],
                                "MandatoryPastHistoryYear": data["admission_mandatoryPastHistoryYear"],
                                "HeartDiseaseMonth": data["admission_heartDiseaseMonth"],
                                "HeartDiseaseYear": data["admission_heartDiseaseYear"],
                                "HypertensionMonth": data["admission_hypertensionMonth"],
                                "HypertensionYear": data["admission_hypertensionYear"],
                                "HyperlipidemiasMonth": data["admission_HyperlipidemiasMonth"],
                                "HyperlipidemiasYear": data["admission_HyperlipidemiasYear"],
                                "OsteoarthritisMonth": data["admission_osteoarthritisMonth"],
                                "OsteoarthritisYear": data["admission_osteoarthritisYear"],
                                "AsthmaOrCOPDOrBronchitisMonth": data["admission_asthmaOrCOPDOrBronchitisMonth"],
                                "AsthmaOrCOPDOrBronchitisYear": data["admission_asthmaOrCOPDOrBronchitisYear"],
                                "CancerMonth": data["admission_cancerMonth"],
                                "CancerYear": data["admission_cancerYear"],
                                "AlcoholOrDrugAbuseMonth": data["admission_alcoholOrDrugAbuseMonth"],
                                "AlcoholOrDrugAbuseYear": data["admission_alcoholOrDrugAbuseYear"],
                                "RelatedAlimentsMonth": data["admission_anyHIVOrSTDOrRelatedAlimentsMonth"],
                                "RelatedAlimentsYear": data["admission_anyHIVOrSTDOrRelatedAlimentsYear"],
                                "OtherAliments": data["admission_anyOtherAliments"],
                                "Reported_To_Police": data.get("doctor_reportedToPolice", ""),
                                "patient_details_HealthInsurance": data.get("patient_details_HealthInsurance", ""),
                                "doctor_proposedLineOfTreatment_Medical_Managment": data.get("doctor_proposedLineOfTreatment_Medical_Managment", ""),
                                "doctor_proposedLineOfTreatment_Surgical_Managment": data.get("doctor_proposedLineOfTreatment_Surgical_Managment", ""),
                                "doctor_proposedLineOfTreatment_Intensive_Care": data.get("doctor_proposedLineOfTreatment_Intensive_Care", ""),
                                "doctor_proposedLineOfTreatment_Investigation": data.get("doctor_proposedLineOfTreatment_Investigation", ""),
                                "doctor_proposedLineOfTreatment_Allopathic_Treatment": data.get("doctor_proposedLineOfTreatment_Allopathic_Treatment", ""),
                                "In_Case_Of_Accident": data.get("doctor_inCaseOfAccident", ""),
                                "Injury_Disease_Caused_Due_To_Substance_Abuse_Alcohol_Consumption_": data.get("doctor_injuryorDiseaseCausedDueToSubstance", ""),
                                "doctor_testAlcohol": data.get("doctor_testAlcohol", ""),
                                "isThisAEmergencyPlannedHospitalization": data.get("admission_isThisAEmergencyPlannedHospitalization", ""),
                                "HealthInsuranceYesCompanyName": data.get("HealthInsuranceYesCompanyName", ""),
                                "Give_Company_details": data.get("Give_Company_details", ""),
                                "PhysicianYesPhysicianName": data.get("PhysicianYesPhysicianName", ""),
                                "PhysicianYesPhysicianContactNum": data.get("PhysicianYesPhysicianContactNum", ""),
                                'Proposed_Line_Of_Treat':Proposed_Line_Of_Treat,
                                "FIR_Number": data.get("doctor_firNo", ""),
                                "G": data.get("doctor_inCaseMaternityG", ""),
                                "P": data.get("doctor_inCaseMaternityP", ""),
                                "L": data.get("doctor_inCaseMaternityL", ""),
                                "A": data.get("doctor_inCaseMaternityA", ""),              
                            }
                    }

                    
                    hospital = {
                            "hospital_details": {
                                "Contact_number": data["Contact_number"],
                                "Date_of_Admission": data["admission_date"],
                                "ExpectedDateOfDelivery": data["doctor_expectedDateOfDelivery"],
                                "Days_In_ICU": data["admission_daysInICU"],
                                "Room_Type": data["admission_roomType"],
                                "DateofInjury": data["doctor_dateOfInjury"],
                                "Treating_Doctor_Name": doctor_name,
                                "Treating_Doctor":doctor_name_email,
                                "Days_In_Hospital":data["admission_expectedNoOfDays"],
                                "Per_Day_Room_Rent": data["admission_perDayRoomRent"],
                                "Cost_Of_Investigation": data["admission_expectedCostForInvestigation"],
                                "ICU_Charges": data["admission_icuCharge"],
                                "OT_Charges": data["admission_otCharge"],
                                "ProfessionalFeesSurgeon": data["admission_professionalFeesSurgeon"],
                                "cost_Of_Implant": data["admission_madicineConsumablesCostOfImplats"],
                                "OtherHospitalIfAny": data["admission_otherHospitalIfAny"],
                                "All_Including_Package": data["admission_allIncludePackageCharge"],
                                "total": data["admission_sumTotalExpected"], 
                                "admission_time":data["admission_time"],
                                "datasaved":'true',
                            }
                    }
                     
                    ref.set(newdata,merge=True)
                    ref.set(hospital,merge=True)
                    
                    db.collection(u'hospitals').document(f'{email}').collection(u'cases').document(
                        case).update({"audit_trail": firestore.ArrayUnion([data.get('status', "FormCreation")+'+'+datetime.today().strftime('%Y-%m-%d')+'+'+data.get('email_title', "FormCreation")])}),
                    
                    db.collection(u'hospitals').document(f'{email}').collection(u'cases').document(case).update({
                        'formstatus': u'draft',
                        'status': "done",
                        'Type': data.get("admission_isThisAEmergencyPlannedHospitalization", ""),
                        "date":f"{datetoday}",
                    })
                    
                    print("Increment Rinning")
                
                
            except:
                return redirect(f"/claimpage1?system={email}%2B{case}")
            return redirect(f"/claimpage1?system={email}%2B{case}")
    return redirect(f"/claimpage1?system={email}%2B{case}")

def formData(request, text):
    flag = 0
    email = ''
    case = ''
    print("thisssss")
    for char in text:
        if char == "+":
            flag = 1
        if flag == 0 and char != '+':
            email = email + char
        if flag == 1 and char != '+':
            case = case+char
            
            
    context = {}
    doc_ref = db.collection(u'users').document(f'{email}').collection(
        u'case').document(f'{case}').collection(u'forms').document(u'form_data')
    doc = doc_ref.get()
    if doc.exists:
        a = doc.to_dict()
    else:
        print("no data found")
    print(a)
    context['formContents'] = a
    return render(request, 'formData.html', context)

def addQuery(request, que):
    email = ""
    case = ''
    query = ''
    flag = 0
    for char in que:
        if char == '+':
            flag = 1
        if char == '&':
            flag = 2
        if flag == 0:
            query = query+char
        if flag == 1 and char != '+':
            email = email+char
        if flag == 2 and char != '&':
            case = case+char

    print("email = ", email)
    print("case = ", case)
    print("query = ", query)

    db.collection(u'hospitals').document(f'{email}').collection(u'cases').document(
        case).update({
            'formstatus': 'query',
            'Query': query,
            "status": "filled"
        })
        
    return HttpResponse("success")


def rateList(request):
    return render(request, 'rateList.html')


def rateListDetails(request):
    return render(request, 'ratelistDetails.html')


def caseDetails(request):
    context = {}
    casenumber = request.GET.get('data')
    doc_ref = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}').collection("patient_details").document("patient_details")
    doc = doc_ref.get()

    if doc.exists:
        a = doc.to_dict()
        context['insurance_company'] = a['Insurance_Company']
        context['patient_name'] = a['Name']
        context['caseid'] = casenumber
        context['contact_Number'] = a['Number']
        context['doctor_natureOfLiness'] = a['Nature_Of_Illness']
    else:
        print("no data found")

    doc_ref_new = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}').collection("hospital_details").document("hospital_details")
    doc_new = doc_ref_new.get()

    if doc_new.exists:
        b = doc_new.to_dict()
        print(b)
        context['admissiondate'] = b['Date_of_Admission']
        context['treating_doctor'] = b['Treating_Doctor']

    else:
        print("no data found")

    status = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}')

    formstatus = status.get()
    if formstatus.exists:
        b = formstatus.to_dict()
        print(b)
        context['formstatus'] = b['formstatus']

    else:
        print("no data found o")
    audit = []

    audit_trail = db.collection(u'hospitals').document(request.session['hospital_email']).collection(
        u'cases').document(f'{casenumber}')
    audit_value = audit_trail.get()

    if audit_value.exists:
        b = audit_value.to_dict()
        print(b)
        if len(b) > 3:
            values = b['audit_trail']
            for i in values:
                x = i.split("+")
                audit.append(x)
            print(audit)
            context['audit'] = audit
        else:
            print("no data found")
    else:
        print("no data found of ")

        # this is hospital email also accessible in caseDetails page
        
        context['hospital_email'] = request.session['hospital_email']
    context['role'] = request.session['role']
    return render(request, 'caseDetails.html')

def newAction(request):
    return render(request, 'newAction.html')


def loginPage(request):
    return render(request, 'loginPage.html')


def companyDetails(request):
    return render(request, 'companyDetails.html')
























# Emailer Anish
def optimiser(s):
    if(s[0] == '"' and s[len(s)-1] == '"'):
        return s[1:-1]
    else:
        return s


def helper(s):
    s = str(s)
    if(s[0] == '0'):
        return s[1:]
    else:
        return s


def spliteremail(s):
    if(s == None):
        return "", ""
    idx = s.find('<')
    if(idx == -1):
        return s, s
    lgth = len(s)
    # print(s)
    x_name = s[:idx-1]
    if s[:-1].isalpha():
        y_email = s[idx+1:]

    else:
        y_email = s[idx+1:-1]
    # print (y_email)
    # print("-"*50)
    return x_name, y_email


def func(s):
    if(s[:2].isdigit()):
        x = s[:2]
        y = s[2:]
    else:
        x = s[:1]
        y = s[1:]

    # print(x)
    # print(y)
    return x, y


def spliterdate(s):
    if s == None:
        return "0"
    if(s[0:3] in week):
        day = s[5:11]
    else:
        day = s[0:6]
    # print(day)
    # print("xxxxxx")

    final = day
    monthdate = day.replace(" ", "")
    curr = datetime.today()

    date, day = func(monthdate)

    date = helper(date)
    day = mth.index(day) + 1
    tdate = helper(curr.day)
    tmonth = helper(curr.month)

    if(date == tdate and day == tmonth):
        return "today"
    else:
        s = date + " " + mth[day-1]
        return s
    
    

def bunny(request):
    context = {}
    # sender = "anish@bimaxpress.com"

    sender = request.session['hospital_email']
    # sender = "harshyadav24@yahoo.com"
    print(sender)
        # sender = 'newuser@gmail.com'

    data = db.collection(u'hospitals').document(sender).get()
        
    user = data.to_dict()['Emailer']

    imapVal = user['imap']
    smtpVal = user['smtp']
    emailID = user['email']
    password = user['password']
    # print(emailID)
    # print(password)


    

    if request.method == "POST":
        
        file = request.FILES.getlist("filenameupload")
       
        sender_msg = request.POST.get('smsg')
        reciever = request.POST.get('recv')
        Bcc = request.POST.get('recvBcc')
        Cc = request.POST.get('recvCc')
        sub = request.POST.get('ssub')
        # att = request.POST.get('filenameupload')
        
        print('_'*50)
        print(os.environ)
        print('_'*50)
        # print(len(file))

        sendemail(emailID, reciever, sub, sender_msg, Bcc, Cc,file,smtpVal,imapVal,password)
        

    # print(data)

    imap_server = imaplib.IMAP4_SSL(host=imapVal)
    print("this is imap",imap_server)
    
    imap_server.login(emailID, password)
    
    imap_server.select()  # Default is `INBOX`

    # status, resp = imap_server.status('INBOX')
    # print(status)
    # print(resp)

    count = 0
    # Find all emails in inbox
    _, message_numbers_raw = imap_server.search(None, 'ALL')
    # search_criteria = 'REVERSE DATE'
    # _, message_numbers_raw = imap_server.sort(search_criteria, 'UTF-8', 'ALL')
    message = []
    count = 1
    flag = 0

    arr = list(reversed(message_numbers_raw[0].split()))
    # print(arr)
    totalmsgs = int(len(arr)/10) + 1
    page_id = 8
    n = 10
    leftind = (page_id-1)*n
    rightind = min((page_id*n),len(arr))
    searchArr = arr[leftind:rightind]

    # for message_number in reversed(message_numbers_raw[0].split()):
    for message_number in searchArr:
    # for ct in range(count, count+10):
    #     if(count == 11):
    #         break
        # message_number = "b'"+str(ct)+"'"
        
        print(message_number)
        print('_____________________')
        _, msg = imap_server.fetch(message_number, '(RFC822)')

        # Parse the raw email message in to a convenient object
        x = email.message_from_bytes(msg[0][1])
        nameid, emailid = spliteremail(x['from'])
        print(x['from'])
        print(x['date'])
        print('_' * 50)
        time = spliterdate(x['date'])
        if (x['to'] == None):
            continue;
        


        # nameid = emailID = time = ""

        # print("========email start===========")
        # print(x)
        # print("========email end===========")
        print("to message",x["to"])
        
        newtext = ""
        for part in x.walk():
            if (part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment")):

                part.set_type("text/plain")
                part.set_payload('Attachment removed: %s (%s, %d bytes)'
                                 % (part.get_filename(),
                                    part.get_content_type(),
                                    len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]
            # print("part print")
            # print(part)
            if part.get_content_type().startswith("text/plain"):
                newtext += "\n"
                newtext += part.get_payload(decode=False)

        msg_json = {
            # "from" : x['from'],
            "from": escape(emailid),
            "name": escape(optimiser(nameid)),
            "to": escape(x['to']),
            "subject": escape(x['subject']),
            
            "message": escape(newtext),
            "date": escape(time),
            "id": count,
        }
        # print(newtext)
        count += 1
        message.append(msg_json)

    email_message = json.dumps(message)
    # print(email_message)s
    a = eval(email_message)
    # print(a)
    from_list = []
    to_list = []
    sub_list = []
    date_list = []
    l = []
    totalmsgList = []
    time_list = []

    # for i in reversed(range(len(a))):
    for i in range(1,totalmsgs+1):
        totalmsgList.append(str(i))

    for i in range(len(a)):
        print("+++++++++++")
        l.append(a[i])
        from_list.append(a[i]['from'])
        to_list.append(a[i]['to'])
        sub_list.append(a[i]['subject'])
        date_list.append(a[i]['date'])

    # print(l)
    context['data_from'] = from_list
    context['data_to'] = to_list
    context['data_sub'] = sub_list
    context['data_date'] = date_list
    context['data'] = l
    context['pageidlist'] = totalmsgList
    context['pagecount'] = len(totalmsgList)
    
    return render(request, "baseemail.html", context)

def replymail(request):
    context = {}
    # print(request.method)
    if request.method == "POST":
        file = request.FILES.getlist("filenameupload")
        sender = request.session['hospital_email']
        data = db.collection(u'hospitals').document(sender).get()
        user = data.to_dict()['Emailer']
        imapVal = user['imap']
        emailID = user['email']
        password = user['password']

        # file = request.FILES['filenameupload']

        sender_msg = request.POST.get('rep_smsg')
        reciever = request.POST.get('rep_recv')

        Bcc = request.POST.get('rep_recvBcc')
        Cc = request.POST.get('rep_recvCc')
        sub = request.POST.get('rep_ssub')
        m_id = request.POST.get('rep_id')
        # att = request.POST.get('filenameupload')
        # sender = "anish@bimaxpress.com"

        imap_server = imaplib.IMAP4_SSL(host=imapVal)
        imap_server.login(emailID, password)
        imap_server.select()

        _, msg = imap_server.fetch(m_id, '(RFC822)')
        email_msg = email.message_from_bytes(msg[0][1])

        newtext = ""

        new = EmailMultiAlternatives("Re: "+email_msg["Subject"],
                                     sender_msg,
                                     sender,  # from
                                     [email_msg["Reply-To"]
                                         or email_msg["From"]],  # to
                                     headers={'Reply-To': sender,
                                              "In-Reply-To": email_msg["Message-ID"],
                                              "References": email_msg["Message-ID"]})
        # new.attach_alternative(sender_msg, "text/plain")
        new.attach(MIMEMessage(email_msg))
        # print(new.body) # attach original message
        for f in file:
            new.attach(f.name, f.read(),f.content_type)

        new.send()
        next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)
    # return render(request,"baseemail.html",context)





def sentmail(request):
    context = {}

    sender = request.session['hospital_email']
    data = db.collection(u'hospitals').document(sender).get()
    user = data.to_dict()['Emailer']
    imapVal = user['imap']
    smtpVal = user['smtp']
    emailID = user['email']
    password = user['password']

    # emailID = sender = 'anishshende001@gmail.com'
    # password = 'Anish@123'

    if request.method == "POST":
        file = request.FILES.getlist("filenameupload")
        # file = request.FILES['filenameupload']
        sender_msg = request.POST.get('smsg')
        reciever = request.POST.get('recv')
        Bcc = request.POST.get('recvBcc')
        Cc = request.POST.get('recvCc')
        sub = request.POST.get('ssub')
        # att = request.POST.get('filenameupload')
        # sender = "anish@bimaxpress.com"
        # print(len(file))
        sendemail(sender, reciever, sub, sender_msg, Bcc, Cc,file,smtpVal,imapVal,password)
    # print(data)

    imap_server = imaplib.IMAP4_SSL(host=imapVal)
    imap_server.login(emailID, password)
    print(imap_server.list())

    # sent folder selected
    if imapVal == 'imap.gmail.com':
        imap_server.select('"[Gmail]/Sent Mail"')
        
    else:
        imap_server.select('Sent')

    count = 0
    # Find all emails in inbox
    _, message_numbers_raw = imap_server.search('',None, 'ALL')

    message = []
    count = 0
    for message_number in message_numbers_raw[0].split():
        _, msg = imap_server.fetch(message_number, '(RFC822)')

        # Parse the raw email message in to a convenient object
        x = email.message_from_bytes(msg[0][1])
        # print(x['from'])
        nameid, emailid = spliteremail(x['from'])
        time = spliterdate(x['date'])
        to = ""
        ssub = ""
        mssg = ""
        if(x['to'] != None):
            to = x['to']

        if(x['subject'] != None):
            ssub = x['subject']

        if(x['message'] != None):
            mssg = x['message']

        newtext = ""
        for part in x.walk():
            if (part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment")):

                part.set_type("text/plain")
                part.set_payload('Attachment removed: %s (%s, %d bytes)'
                                 % (part.get_filename(),
                                    part.get_content_type(),
                                    len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]

            if part.get_content_type().startswith("text/plain"):
                newtext += "\n"
                newtext += part.get_payload(decode=False)

        msg_json = {
            "from": emailid,
            "name": nameid,
            "to": to,
            "subject": ssub,
            "date": time,
            "id": count,
            "message": newtext,
        }

        if(emailid):
            count += 1
            message.append(msg_json)

    imap_server.close()
    imap_server.logout()

    email_message = json.dumps(message)
    print(email_message)

    a = eval(email_message)
    from_list = []
    to_list = []
    sub_list = []
    date_list = []
    l = []
    time_list = []

    for i in reversed(range(len(a))):
        # print(a[i]['from'])
        # print(a[i]['message'])
        l.append(a[i])
        from_list.append(a[i]['from'])
        to_list.append(a[i]['to'])
        sub_list.append(a[i]['subject'])
        date_list.append(a[i]['date'])

    # print(l)
    context['data_from'] = from_list
    context['data_to'] = to_list
    context['data_sub'] = sub_list
    context['data_date'] = date_list
    context['data'] = l

    return render(request, "sentemail.html", context)


# TRASH Folder



# def trashmail(request):
#     context = {}
#     if request.method == "POST":
#         file = request.FILES.getlist("filenameupload")
#         sender = request.session['hospital_email']
#         data = db.collection(u'hospitals').document(sender).get()
#         user = data.to_dict()['Emailer']
#         imapVal = user['imap']
#         smtpVal = user['smtp']
#         emailID = user['email']
#         password = user['password']
#         # file = request.FILES['filenameupload']
#         sender_msg = request.POST.get('smsg')
#         reciever = request.POST.get('recv')
#         Bcc = request.POST.get('recvBcc')
#         Cc = request.POST.get('recvCc')
#         sub = request.POST.get('ssub')
#         # att = request.POST.get('filenameupload')
#         # sender = "anish@bimaxpress.com"
#         # print(len(file))
#         sendemail(sender, reciever, sub, sender_msg, Bcc, Cc,file,smtpVal,imapVal,password)
#     # print(data)

#     imap_server = imaplib.IMAP4_SSL(host=imapVal)
#     imap_server.login(emailID, password)
#     imap_server.select('INBOX.Trash')  # Default is `INBOX`
#     count = 0
#     # Find all emails in inbox
#     _, message_numbers_raw = imap_server.search(None, 'ALL')

#     message = []
#     count = 0
#     for message_number in message_numbers_raw[0].split():
#         _, msg = imap_server.fetch(message_number, '(RFC822)')

#         # Parse the raw email message in to a convenient object
#         x = email.message_from_bytes(msg[0][1])
#         nameid, emailid = spliteremail(x['from'])
#         time = spliterdate(x['date'])

#         newtext = ""
#         for part in x.walk():
#             if (part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment")):

#                 part.set_type("text/plain")
#                 part.set_payload('Attachment removed: %s (%s, %d bytes)'
#                                  % (part.get_filename(),
#                                     part.get_content_type(),
#                                     len(part.get_payload(decode=True))))
#                 del part["Content-Disposition"]
#                 del part["Content-Transfer-Encoding"]

#             if part.get_content_type().startswith("text/plain"):
#                 newtext += "\n"
#                 newtext += part.get_payload(decode=False)

#         msg_json = {
#             "from": emailid,
#             "name": nameid,
#             "to": x['to'],
#             "subject": x['subject'],
#             "date": time,
#             "id": count,
#             "message": newtext,
#         }
#         count += 1
#         message.append(msg_json)

#     email_message = json.dumps(message)
#     # print(email_message)s
#     a = eval(email_message)
#     from_list = []
#     to_list = []
#     sub_list = []
#     date_list = []
#     l = []
#     time_list = []

#     for i in reversed(range(len(a))):
#         # print(a[i]['from'])
#         l.append(a[i])
#         from_list.append(a[i]['from'])
#         to_list.append(a[i]['to'])
#         sub_list.append(a[i]['subject'])
#         date_list.append(a[i]['date'])

#     # print(l)
#     context['data_from'] = from_list
#     context['data_to'] = to_list
#     context['data_sub'] = sub_list
#     context['data_date'] = date_list
#     context['data'] = l

#     return render(request, "trash.html", context)

# # DRAFTS Folder



def draftmail(request):
    context = {}
    if request.method == "POST":
        file = request.FILES.getlist("filenameupload")
        sender = request.session['hospital_email']
        data = db.collection(u'hospitals').document(sender).get()
        user = data.to_dict()['Emailer']
        imapVal = user['imap']
        smtpVal = user['smtp']
        emailID = user['email']
        password = user['password']

        # file = request.FILES['filenameupload']
        sender_msg = request.POST.get('smsg')
        reciever = request.POST.get('recv')
        Bcc = request.POST.get('recvBcc')
        Cc = request.POST.get('recvCc')
        sub = request.POST.get('ssub')
        # att = request.POST.get('filenameupload')
        # sender = "anish@bimaxpress.com"
        # print(len(file))
        sendemail(sender, reciever, sub, sender_msg, Bcc, Cc,file,smtpVal,imapVal,password)
    # print(data)

    imap_server = imaplib.IMAP4_SSL(host=imapVal)
    imap_server.login(emailID, password)
    imap_server.select('INBOX.Sent')  # Default is `INBOX`
    count = 0
    # Find all emails in inbox
    _, message_numbers_raw = imap_server.search(None, 'ALL')

    message = []
    count = 0
    for message_number in message_numbers_raw[0].split():
        _, msg = imap_server.fetch(message_number, '(RFC822)')

        # Parse the raw email message in to a convenient object
        x = email.message_from_bytes(msg[0][1])
        nameid, emailid = spliteremail(x['from'])
        time = spliterdate(x['date'])

        newtext = ""
        for part in x.walk():
            if (part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment")):

                part.set_type("text/plain")
                part.set_payload('Attachment removed: %s (%s, %d bytes)'
                                 % (part.get_filename(),
                                    part.get_content_type(),
                                    len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]

            if part.get_content_type().startswith("text/plain"):
                newtext += "\n"
                newtext += part.get_payload(decode=False)

        msg_json = {
            "from": emailid,
            "name": nameid,
            "to": x['to'],
            "subject": x['subject'],
            "date": time,
            "id": count,
            "message": newtext,
        }
        count += 1
        message.append(msg_json)

    email_message = json.dumps(message)
    # print(email_message)s
    a = eval(email_message)
    from_list = []
    to_list = []
    sub_list = []
    date_list = []
    l = []
    time_list = []

    for i in reversed(range(len(a))):
        # print(a[i]['from'])
        l.append(a[i])
        from_list.append(a[i]['from'])
        to_list.append(a[i]['to'])
        sub_list.append(a[i]['subject'])
        date_list.append(a[i]['date'])

    # print(l)
    context['data_from'] = from_list
    context['data_to'] = to_list
    context['data_sub'] = sub_list
    context['data_date'] = date_list
    context['data'] = l

    return render(request, "drafts.html", context)

# Starred Folder

def starredemail(request):
    context = {}
    if request.method == "POST":
        file = request.FILES.getlist("filenameupload")
        sender = request.session['hospital_email']
        data = db.collection(u'hospitals').document(sender).get()
        user = data.to_dict()['Emailer']
        imapVal = user['imap']
        smtpVal = user['smtp']
        emailID = user['email']
        password = user['password']
        # file = request.FILES['filenameupload']
        sender_msg = request.POST.get('smsg')
        reciever = request.POST.get('recv')
        Bcc = request.POST.get('recvBcc')
        Cc = request.POST.get('recvCc')
        sub = request.POST.get('ssub')
        # att = request.POST.get('filenameupload')
        # sender = "anish@bimaxpress.com"
        # print(len(file))
        sendemail(sender, reciever, sub, sender_msg, Bcc, Cc,file,smtpVal,imapVal,password)
    # print(data)

    imap_server = imaplib.IMAP4_SSL(host=imapVal)
    imap_server.login(emailID, password)
    imap_server.select('INBOX')  # Default is `INBOX`
    count = 0
    # Find all emails in inbox
    _, message_numbers_raw = imap_server.search(None, 'ALL')

    message = []
    count = 0
    for message_number in message_numbers_raw[0].split():
        _, msg = imap_server.fetch(message_number, '(RFC822)')

        # Parse the raw email message in to a convenient object
        x = email.message_from_bytes(msg[0][1])
        nameid, emailid = spliteremail(x['from'])
        time = spliterdate(x['date'])

        newtext = ""
        for part in x.walk():
            if (part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment")):

                part.set_type("text/plain")
                part.set_payload('Attachment removed: %s (%s, %d bytes)'
                                 % (part.get_filename(),
                                    part.get_content_type(),
                                    len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]

            if part.get_content_type().startswith("text/plain"):
                newtext += "\n"
                newtext += part.get_payload(decode=False)

        msg_json = {
            "from": emailid,
            "name": nameid,
            "to": x['to'],
            "subject": x['subject'],
            "date": time,
            "id": count,
            "message": newtext,
        }
        count += 1
        message.append(msg_json)

    email_message = json.dumps(message)
    # print(email_message)s
    a = eval(email_message)
    from_list = []
    to_list = []
    sub_list = []
    date_list = []
    l = []
    time_list = []

    for i in reversed(range(len(a))):
        # print(a[i]['from'])
        l.append(a[i])
        from_list.append(a[i]['from'])
        to_list.append(a[i]['to'])
        sub_list.append(a[i]['subject'])
        date_list.append(a[i]['date'])

    # print(l)
    context['data_from'] = from_list
    context['data_to'] = to_list
    context['data_sub'] = sub_list
    context['data_date'] = date_list
    context['data'] = l
    
    return render(request, "starred.html", context)



def sendemail(sender, reciever, sub, sender_msg, Bcc, Cc,files,smtpVal,imapVal,password):

    connection = get_connection(
        host = smtpVal,
        port = EMAIL_PORT,
        username = sender,
        password = password ,
        use_ssl = EMAIL_USE_SSL,
        backend=EMAIL_BACKEND
    )
    
    if(len(Cc)>=5):
        email = EmailMultiAlternatives(sub, body = "%s \r\n" % sender_msg,from_email= sender, to=[reciever, ], bcc=[
                                   Bcc, ], cc=[Cc[0],Cc[1],Cc[2],Cc[3],Cc[4],],connection=connection)
    if(len(Cc)==4):
        email = EmailMultiAlternatives(sub, body = "%s \r\n" % sender_msg,from_email= sender, to=[reciever, ], bcc=[
                                   Bcc, ], cc=[Cc[0],Cc[1],Cc[2],Cc[3],],connection=connection)
    if(len(Cc)==3):
        email = EmailMultiAlternatives(sub, body = "%s \r\n" % sender_msg,from_email= sender, to=[reciever, ], bcc=[
                                   Bcc, ], cc=[Cc[0],Cc[1],Cc[2],],connection=connection)
    if(len(Cc)==2):
        email = EmailMultiAlternatives(sub, body = "%s \r\n" % sender_msg,from_email= sender, to=[reciever, ], bcc=[
                                   Bcc, ], cc=[Cc[0],Cc[1],],connection=connection)
    if(len(Cc)==1):
        email = EmailMultiAlternatives(sub, body = "%s \r\n" % sender_msg,from_email= sender, to=[reciever, ], bcc=[
                                   Bcc, ], cc=[Cc[0],],connection=connection)
    if(len(Cc)<1):
        email = EmailMultiAlternatives(sub, body = "%s \r\n" % sender_msg,from_email= sender, to=[reciever, ], bcc=[
                                   Bcc, ], cc=["",],connection=connection)
    
    
    # print(email.message())
    text = str(email.message())
    imap_server = imaplib.IMAP4_SSL(host=imapVal, port=993)

    
    imap_server.login(sender, password)
    imap_server.append('Sent', '\\Seen', imaplib.Time2Internaldate(
        time.time()), text.encode('utf8'))

    for f in files:
        email.attach(f.name, f.read(), f.content_type)

    email.send()
    connection.close()

def pageload(request):
    page_id = int(request.GET.get('data'))
    context = {}
    sender = request.session['hospital_email']
    print(sender)
    data = db.collection(u'hospitals').document(sender).get()
    user = data.to_dict()['Emailer']
    imapVal = user['imap']
    smtpVal = user['smtp']
    emailID = user['email']
    password = user['password']
# print(emailID)
# print(password)
    if request.method == "POST":
        page_id = request.POST.get("pageid")
        page_id = int(page_id)
# print(data)
    imap_server = imaplib.IMAP4_SSL(host=imapVal)
    print("this is imap", imap_server)
    imap_server.login(emailID, password)
    imap_server.select()  # Default is `INBOX`
# status, resp = imap_server.status('INBOX')
# print(status)
# print(resp)
    count = 0
# Find all emails in inbox
    _, message_numbers_raw = imap_server.search(None, 'ALL')
# search_criteria = 'REVERSE DATE'
# _, message_numbers_raw = imap_server.sort(search_criteria, 'UTF-8', 'ALL')
    message = []
    count = 1
    flag = 0
    arr = list(reversed(message_numbers_raw[0].split()))
    # print(arr)
    totalmsgs = int(len(arr) / 10) + 1
    n = 10
    leftind = (page_id - 1) * n
    rightind = min((page_id * n), len(arr))
    searchArr = arr[leftind:rightind]
# for message_number in reversed(message_numbers_raw[0].split()):
    for message_number in searchArr:
    # for ct in range(count, count+10):
    #     if(count == 11):
    #         break
    # message_number = "b'"+str(ct)+"'"
        print(message_number)
        print('_____________________')
        _, msg = imap_server.fetch(message_number, '(RFC822)')
    # Parse the raw email message in to a convenient object
        x = email.message_from_bytes(msg[0][1])
        nameid, emailid = spliteremail(x['from'])
        print(x['from'])
        print(x['date'])
        print('_' * 50)
        time = spliterdate(x['date'])
    # nameid = emailID = time = ""
    # print("========email start===========")
    # print(x)
    # print("========email end===========")
        newtext = ""
        for part in x.walk():
            if (part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment")):
                part.set_type("text/plain")
                part.set_payload('Attachment removed: %s (%s, %d bytes)'
                             % (part.get_filename(),
                                part.get_content_type(),
                                len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]
        # print("part print")
        # print(part)
            if part.get_content_type().startswith("text/plain"):
                newtext += "\n"
                newtext += part.get_payload(decode=False)
        msg_json = {
        # "from" : x['from'],
        "from": escape(emailid),
        "name": escape(optimiser(nameid)),
        "to": escape(x['to']),
        "subject": escape(x['subject']),
        "message": escape(newtext),
        "date": escape(time),
        "id": count,
        }
    # print(newtext)
        count += 1
        print(msg_json)
        message.append(msg_json)
    email_message = json.dumps(message)
    # print(email_message)s
    a = eval(email_message)
    # print(a)
    from_list = []
    to_list = []
    sub_list = []
    date_list = []
    l = []
    totalmsgList = []
    time_list = []
    print(len(a))
    # for i in reversed(range(len(a))):
    for k in range(1, totalmsgs + 1):
        totalmsgList.append(str(k))
    for i in range(len(a)):
        print("+++++++++++")
        l.append(a[i])
        from_list.append(a[i]['from'])
        to_list.append(a[i]['to'])
        sub_list.append(a[i]['subject'])
        date_list.append(a[i]['date'])
    # print(l)
    context['data_from'] = from_list
    context['data_to'] = to_list
    context['data_sub'] = sub_list
    context['data_date'] = date_list
    context['data'] = l
    context['pageidlist'] = totalmsgList
    context['pagecount'] = len(totalmsgList)
    context["role"] = request.session['role'] 
    return render(request, "baseemail.html", context)
