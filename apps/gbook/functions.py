# -*- coding: utf-8 -*-
import datetime 
from random import randint 
from PIL import Image 

from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, Http404 
from django.shortcuts import render_to_response  
from django.core.context_processors import csrf 
from django.template import RequestContext 
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q  
from django.utils.html import escape 
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User 

from settings import * 
from gbook.models import GbookProfile, UsersOnline, Theme, \
                         ThemeAnswers,AnswersFromUnregistered, \
                         PrivateMessages, KarmaMessages
from gbook.forms import AuthorizationForm,Sections,ShowAnswers, \
                         SearchForm, GbookSubmitForm, GbookSubmitFormUnregistered, \
                         GbookProfileForm, ChangePasswordForm, \
                         PrivateMessagesForm, KarmaMessagesForm, \
                         RegistrationForm, AdminGbookProfileForm, FormErrorList

def gbook_authorization(request):

    user = request.user
    
    if user.is_anonymous(): 
        profile = None
    else:
        try:
            profile = user.gbookprofile          
        except:
            profile = GbookProfile()
            profile.user = user
            profile.save()
            
    if profile != None:
        if profile.banned:  
            logout(request) 
            return HttpResponseRedirect(reverse('gbook_view'))
            
    return user, profile

def gbook_online_users(user,client_address,datetime_now):
    
    if user.is_authenticated():      
        try:
            UsersOnline.objects.get(username=user)
            UsersOnline.objects.filter(username=user).update(time=datetime_now)
        except:
            UsersOnline(username=user, ip_adress = client_address, time=datetime_now).save()
    else: 
        try:
            UsersOnline.objects.get(username=user,ip_adress = client_address)
            UsersOnline.objects.filter(username=user, ip_adress = client_address).update(time=datetime_now)           
        except:
            UsersOnline(username=user, ip_adress = client_address,time=datetime_now).save() 
    
    online_users = UsersOnline.objects.all()

    for user in online_users:

        dt = datetime_now - user.time
        if (dt >= datetime.timedelta(minutes=3)): 
            user.delete() 
            
    return online_users            
      
                         
def gbook_save_avatar(name,image):

    img = Image.open(image)     
    image_name = str(randint(100,999)) + '-' + str(name)         
    resize_to_width = 200 
    resize_to_height = 250 
    if img.mode not in ('L', 'RGB'): 
        img = img.convert('RGB')
    image_width = float(img.size[0]) 
    image_height = float(img.size[1])                 
    if image_width > image_height:
        if image_width > resize_to_width:
            resize_percent = float(resize_to_width / image_width) 
            resize_to_height = int(image_height * resize_percent)
            img = img.resize((resize_to_width, resize_to_height),Image.ANTIALIAS) 
            img.save('%s/gbook/avatar/%s' % (MEDIA_ROOT, image_name), "JPEG") 
        if image_width <= resize_to_width: 
            img.save('%s/gbook/avatar/%s' % (MEDIA_ROOT, image_name), "JPEG") 
    elif image_width < image_height: 
        if image_height > resize_to_height:
            resize_percent = float(resize_to_height / image_height) 
            resize_to_width = int(image_width * resize_percent) 
            img = img.resize((resize_to_width, resize_to_height),Image.ANTIALIAS) 
            img.save('%s/gbook/avatar/%s' % (MEDIA_ROOT, image_name), "JPEG") 
        if image_height <= resize_to_height: 
            img.save('%s/gbook/avatar/%s' % (MEDIA_ROOT, image_name), "JPEG") 
    elif image_width == image_height: 
        if image_width > resize_to_width: 
            img = img.resize((resize_to_width, 200),Image.ANTIALIAS) 
            img.save('%s/gbook/avatar/%s' % (MEDIA_ROOT, image_name), "JPEG") 
        if image_width <= resize_to_width:
            img.save('%s/gbook/avatar/%s' % (MEDIA_ROOT, image_name), "JPEG")  
    
    return image_name                               