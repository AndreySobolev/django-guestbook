# -*- coding: utf-8 -*-
import datetime 
import random 
from PIL import Image 

from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, Http404 
from django.shortcuts import render_to_response  
from django.core.context_processors import csrf 
from django.template import RequestContext 
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q  

from django.core.urlresolvers import reverse
from settings import *
from settings import GBOOK_SECTIONS
 
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User 
from gbook.models import GbookProfile, UsersOnline, Theme, \
                         ThemeAnswers,AnswersFromUnregistered, \
                         PrivateMessages, KarmaMessages
from gbook.forms import AuthorizationForm,Sections,ShowAnswers, \
                         SearchForm, GbookSubmitForm, GbookSubmitFormUnregistered, \
                         GbookProfileForm, ChangePasswordForm, \
                         PrivateMessagesForm, KarmaMessagesForm, \
                         RegistrationForm, AdminGbookProfileForm, FormErrorList

from gbook.functions import gbook_authorization, gbook_online_users, gbook_save_avatar
                          
# index     
def index(request):
    return render_to_response('gbook/index.html', 
                              locals(),
                              context_instance=RequestContext(request))    

# gbook & user authorization 
def gbook_view(request, section = '', theme = '',**kwargs):
    
    user, profile = gbook_authorization(request) 
      
    if user.is_authenticated() and profile:
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')
             
    datetime_now = datetime.datetime.now() 
    registation_via_email = GBOOK_REGISTRATION_VIA_EMAIL 
    time_to_delete_or_edit = datetime.timedelta(hours=1) 
    time_to_delete_or_edit = datetime_now - time_to_delete_or_edit
    
    # if unregistered adding new theme or answer  
    if 'show_notice_to_ungregistered' in request.GET: 
        show_notice_to_ungregistered = True
    else:
        show_notice_to_ungregistered = False        
     
    if user.is_superuser == True: 
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()  
     
    section_text = section[:]
    if user.is_authenticated() and user.is_active:
        if theme != '':
            themes = Theme.objects.filter(id=theme)
            if len(themes) == 0:
                themes = Theme.objects.all()  
        elif section != '':
            themes = Theme.objects.filter(section=section)
            if len(themes) == 0:
                themes = []
                section_text = _(u'No themes in this section') 
            else:
                section_text = [item[1] for item in GBOOK_SECTIONS if item[0] == section_text][0]                           
        else:
            themes = Theme.objects.all()   
    else:
        if theme != '':
            themes = Theme.objects.filter(id=theme, private = False)
            if len(themes) == 0:
                themes = Theme.objects.all()  
        elif section != '':
            themes = Theme.objects.filter(section=section, private = False)
            if len(themes) == 0:
                themes = []
                section_text = _(u'No themes in this section')
            else:
                section_text = [item[1] for item in GBOOK_SECTIONS if item[0] == section_text][0]                                       
        else:
            themes = Theme.objects.filter(private = False)           
    
    sections = Sections(initial = {'section': section,})

    search_form = SearchForm() 
    
    # online users
    try:
        client_address = request.META['HTTP_X_FORWARDED_FOR']
    except:
        client_address = request.META['REMOTE_ADDR']      
    
    online_users = gbook_online_users(user,client_address,datetime_now)
                                      
    if request.method == 'POST':
        form = AuthorizationForm(request.POST, error_class=FormErrorList)
        if form.is_valid():            
            send_data = form.cleaned_data
            user = authenticate(username = send_data['user'], password = send_data['password'])
            if user is not None:                 
                login(request, user)                       
                return HttpResponseRedirect('')                                  
            else:
                auth_error = _(u'Incorrect login or password') 
    else:
        form = AuthorizationForm()  
        
    # work with show answers option

    if 'show_answers' in request.GET:
        session_show_answers = request.GET['show_answers']
        request.session['show_answers'] = request.GET['show_answers']
    elif 'show_answers' in request.session:  
        session_show_answers = request.session['show_answers'] 
    else:
        request.session['show_answers'] = 'yes'
        session_show_answers = 'yes'
                                      
    show_answers = ShowAnswers(initial = {'show_answers': session_show_answers})       
    
    if session_show_answers == 'yes' or theme != '': 
        
        return render_to_response('gbook/gbook.html', locals(),context_instance=RequestContext(request))            
    
    if session_show_answers == 'no':
        
        return render_to_response('gbook/gbook_themes_only.html', 
                                      locals(),
                                      context_instance=RequestContext(request))   
                    

                                
def gbook_submit(request, theme):

    user, profile = gbook_authorization(request)    
    
    online_users = UsersOnline.objects.all()
    if user.is_authenticated() and user.gbookprofile.banned == False:    
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')         
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()  
        if request.method == 'POST':
            form = GbookSubmitForm(request.POST,error_class=FormErrorList)
            if form.is_valid():           
                send_data = form.cleaned_data
                datetime_now = datetime.datetime.now()        
                if theme == 'new_theme':
                    Theme(theme_start_user = user, 
                              theme_start_datetime = datetime_now, 
                              theme_start_message_text = send_data['message'], 
                              theme_changetime = datetime_now,
                              section = send_data['section'],
                              fk_to_profile_id = profile.id).save()
                    return HttpResponseRedirect(reverse('gbook_view'))
                else:
                    return HttpResponseRedirect(reverse('gbook_view'))    
        else:          
            form = GbookSubmitForm()   
        return render_to_response('gbook/gbook_submit.html', locals(),context_instance=RequestContext(request))
    else:
        logout(request)    
    return HttpResponseRedirect(reverse('gbook_view'))
 
    
def gbook_submit_answer(request, theme):

    user, profile = gbook_authorization(request)
         
    online_users = UsersOnline.objects.all()
    if user.is_authenticated() and user.gbookprofile.banned == False:    
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')    
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        
        try:    
            to_theme = Theme.objects.get(id = theme) 
        except:
            raise Http404 
                  
        if request.method == 'POST':
            form = GbookSubmitForm(request.POST,error_class=FormErrorList)
            if form.is_valid():           
                send_data = form.cleaned_data
                datetime_now = datetime.datetime.now()        
                ThemeAnswers(theme_answer_user = user, 
                             theme_answer_datetime = datetime_now, 
                             theme_answer_message_text = send_data['message'],
                             fk_to_theme_id = theme,
                             fk_to_profile_id = profile.id).save() 
                Theme.objects.filter(id = theme).update(theme_changetime = datetime_now)
                return HttpResponseRedirect(reverse('gbook_view'))    
        else:          
            form = GbookSubmitForm()   
        return render_to_response('gbook/gbook_submit_answer.html', locals(),context_instance=RequestContext(request))
    else:
        logout(request)    
    return HttpResponseRedirect(reverse('gbook_view'))    

                                 
def gbook_submit_unregistered(request, theme): 

    user, profile = gbook_authorization(request) 
    
    unregistred_send_message = _(u'The message is sent and will be published after check by the administrator')
    online_users = UsersOnline.objects.all()
    if request.method == 'POST':
        form = GbookSubmitFormUnregistered(request.POST, error_class=FormErrorList)         
        if form.is_valid():                      
            send_data = form.cleaned_data  
            datetime_now = datetime.datetime.now() 
            custom_password = random.randint(100000, 999999)              
            if theme == 'new_theme':
                AnswersFromUnregistered(unregistered_user = send_data['unregistered_user'],
                          unregistered_user_has_password = custom_password,                          
                          unregistered_user_send_message = send_data['unregistered_user_send_message'],
                          unregistered_message_to_theme = 'new_theme',
                          unregistered_message_section = send_data['section'],
                          unregistered_user_need_registration = send_data['unregistered_user_need_registration'],
                          unregistered_user_email = send_data['unregistered_user_email'],
                          unregistered_message_send_time = datetime_now).save()                         
                return HttpResponseRedirect('%s?show_notice_to_ungregistered=yes' % (reverse('gbook_view')))  
            else:
                raise Http404  
    else:          
        form = GbookSubmitFormUnregistered()   
    return render_to_response('gbook/gbook_submit_unregistered.html', locals(),context_instance=RequestContext(request))  

    
def gbook_submit_unregistered_answer(request, theme): 

    user, profile = gbook_authorization(request)
         
    unregistred_send_message = _(u'The message is sent and will be published after check by the administrator')
    online_users = UsersOnline.objects.all()
    
    try:
        to_theme = Theme.objects.get(id = theme)
    except:
        raise Http404
        
    if request.method == 'POST':
        form = GbookSubmitFormUnregistered(request.POST, error_class=FormErrorList)        
        if form.is_valid(): 
                     
            send_data = form.cleaned_data  
            datetime_now = datetime.datetime.now()
            custom_password = random.randint(100000, 999999)
            AnswersFromUnregistered(unregistered_user = send_data['unregistered_user'],
                      unregistered_user_has_password = custom_password,                            
                      unregistered_user_send_message = send_data['unregistered_user_send_message'],
                      unregistered_message_to_theme = theme,
                      unregistered_user_need_registration = send_data['unregistered_user_need_registration'],
                      unregistered_user_email = send_data['unregistered_user_email'],                      
                      unregistered_message_send_time = datetime_now).save()
            return HttpResponseRedirect('%s?show_notice_to_ungregistered=yes' % (reverse('gbook_view')))
    else:          
        form = GbookSubmitFormUnregistered()   
    return render_to_response('gbook/gbook_submit_answer_unregistered.html', locals(),context_instance=RequestContext(request))      

 
def gbook_edit_theme(request, edit_theme):
    
    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now()
    if user.is_authenticated() and user.gbookprofile.banned == False:  
        new_private_messages = new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        
        try:
            edit_theme = Theme.objects.get(id = edit_theme)
        except:
            raise Http404
             
        if datetime_now < edit_theme.theme_start_datetime + datetime.timedelta(hours=1) and user.username == edit_theme.theme_start_user:                      
            if request.method == 'POST':
                form = GbookSubmitForm(request.POST,error_class=FormErrorList)
                if form.is_valid():          
                    send_data = form.cleaned_data        
                    Theme.objects.filter(id = edit_theme.id).update(theme_start_message_text = send_data['message'],section = send_data['section'])
                    return HttpResponseRedirect(reverse('gbook_view'))    
            else:          
                form = GbookSubmitForm(initial = {'message': edit_theme.theme_start_message_text})   
            return render_to_response('gbook/gbook_edit_theme.html', locals(),context_instance=RequestContext(request))      
        return HttpResponseRedirect('/gbook/404.html')     
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))    


def gbook_edit_answer(request, answer):

    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now()
    if user.is_authenticated() and user.gbookprofile.banned == False:  
        new_private_messages = new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        try:
            edit_answer = ThemeAnswers.objects.get(id = answer)
        except:
            raise Http404    
        if datetime_now < edit_answer.theme_answer_datetime + datetime.timedelta(hours=1) and user.username == edit_answer.theme_answer_user:       
            if request.method == 'POST':
                form = GbookSubmitForm(request.POST,error_class=FormErrorList)
                if form.is_valid():          
                    send_data = form.cleaned_data        
                    ThemeAnswers.objects.filter(id = edit_answer.id).update(theme_answer_message_text = send_data['message'])
                    return HttpResponseRedirect(reverse('gbook_view'))    
            else:          
                form = GbookSubmitForm(initial = {'message': edit_answer.theme_answer_message_text})   
            return render_to_response('gbook/gbook_edit_answer.html', 
                                      locals(),
                                      context_instance=RequestContext(request))
        else:
            raise Http404     
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))    


def gbook_delete_theme(request, theme):

    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now() 
    if user.is_authenticated() and user.gbookprofile.banned == False: 
       
        try:
            delete_theme = Theme.objects.get(id = theme,fk_to_profile = profile)
        except:
            raise Http404 
            
        if datetime_now < delete_theme.theme_start_datetime + datetime.timedelta(hours=1) and user.username == delete_theme.theme_start_user:
            delete_theme.delete()
            return HttpResponseRedirect(reverse('gbook_view'))                
        else:
            raise Http404
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))
          
                
def gbook_delete_answer(request,answer):

    user, profile = gbook_authorization(request) 
        
    if user.is_authenticated() and user.gbookprofile.banned == False:  
    
        try:
            delete_answer = ThemeAnswers.objects.get(id = answer)
        except:
            raise Http404 
            
        datetime_now = datetime.datetime.now()                 
        if datetime_now < delete_answer.theme_answer_datetime + datetime.timedelta(hours=1) and user.username == delete_answer.theme_answer_user:
            delete_answer.delete()                
            return HttpResponseRedirect(reverse('gbook_view'))                
        else:
            raise Http404
    else:
        logout(request)                         
    return HttpResponseRedirect(reverse('gbook_view'))
        

def gbook_search(request):

    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now() 
    registation_via_email = GBOOK_REGISTRATION_VIA_EMAIL 
    time_to_delete_or_edit = datetime.timedelta(hours=1) 
    time_to_delete_or_edit = datetime_now - time_to_delete_or_edit 
    show_wait_message = request.GET.get('show_wait_message') 
    new_private_messages = new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
    if user.is_superuser == True: 
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()  
    show_section = ''    
    if request.method == 'POST' and 'search_text' in request.POST:
        search_form = SearchForm(request.POST,error_class=FormErrorList)
        if search_form.is_valid():
            send_data = search_form.cleaned_data
            search_text = send_data["search_text"]
            show_section = send_data["show_section"]
            form = AuthorizationForm()
            if user.is_authenticated() and user.is_active:
                if show_section == 'all':
                    sections = Sections()
                    themes = Theme.objects.filter( Q(theme_start_message_text__icontains=search_text) | Q(themeanswers__theme_answer_message_text__icontains=search_text))
                    themes = themes.all().distinct()                                                                                                                                     
                    if len(themes) == 0:
                        themes = []   
                        section_text = _(u'No result')
                                                
                else:             
                    sections = Sections(initial = {'section': show_section,})
                    themes = Theme.objects.filter( Q(theme_start_message_text__icontains=search_text) | Q(themeanswers__theme_answer_message_text__icontains=search_text)).filter(section=show_section)
                    themes = themes.all().distinct()
                    section_text = show_section
                    if len(themes) == 0:
                        themes = []
                        section_text = _(u'No result')
        
            else:
                if show_section == 'all':
                    sections = Sections()
                    themes = Theme.objects.filter( Q(theme_start_message_text__icontains=search_text) | Q(themeanswers__theme_answer_message_text__icontains=search_text)).filter(private = False)
                    themes = themes.all().distinct()
                    if len(themes) == 0:
                        themes = []   
                        section_text = _(u'No result')
                                                
                else:             
                    sections = Sections(initial = {'section': show_section,})
                    themes = Theme.objects.filter( Q(theme_start_message_text__icontains=search_text) | Q(themeanswers__theme_answer_message_text__icontains=search_text)).filter(section=show_section, private = False)
                    themes = themes.all().distinct()
                    section_text = show_section
                    if len(themes) == 0:
                        themes = []
                        section_text = _(u'No result')
                          
         
        else:   
            section_text = _(u'Invalid request')          
            themes = []  
            form = AuthorizationForm()
  
    elif request.method == 'POST' and 'user' in request.POST:
        form = AuthorizationForm(request.POST, error_class=FormErrorList)
        if form.is_valid():            
            send_data = form.cleaned_data
            user = authenticate(username = send_data['user'], password = send_data['password'])
            if user is not None:                 
                login(request, user)                       
                return HttpResponseRedirect('')                                  
            else:
                auth_error = _(u'Incorrect login or password')                                                                                  
    else: 
        section_text = ''
        themes = [] 
        form = AuthorizationForm()
        search_form = SearchForm()
     
                                    
    client_address = request.META['HTTP_X_FORWARDED_FOR']
    if user.is_authenticated():      
        try:
            UsersOnline.objects.get(username=user)
            UsersOnline.objects.filter(username=user).update(time=datetime_now)
        except:
            UsersOnline(username=user, time=datetime_now).save()
    else:  
        try:
            UsersOnline.objects.get(username=user,ip_adress = client_address)
            UsersOnline.objects.filter(username=user, ip_adress = client_address).update(time=datetime_now)         
        except:
            UsersOnline(username=user, ip_adress = client_address,time=datetime_now).save() 
    
    online_users = UsersOnline.objects.all()

    for users in online_users:
        dt = datetime_now - users.time
        if (dt > datetime.timedelta(minutes=3)): 
            users.delete() 
            
                                   
    # work with show answers option

    if 'show_answers' in request.GET:
        session_show_answers = request.GET['show_answers']
        request.session['show_answers'] = request.GET['show_answers']
    elif 'show_answers' in request.session:  
        session_show_answers = request.session['show_answers'] 
    else:
        request.session['show_answers'] = 'yes'
        session_show_answers = 'yes'
                                      
    show_answers = ShowAnswers(initial = {'show_answers': session_show_answers})       
    
    if session_show_answers == 'yes': 
        
        return render_to_response('gbook/gbook.html', locals(),context_instance=RequestContext(request))            
    
    if session_show_answers == 'no':
        
        return render_to_response('gbook/gbook_themes_only.html', 
                                      locals(),
                                      context_instance=RequestContext(request))  
                     
                          
# user profile   

def gbook_manage_profile(request):

    user, profile = gbook_authorization(request)     
        
    if user.is_authenticated() and user.gbookprofile.banned == False:
        datetime_now = datetime.datetime.now()
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        manage_profile = profile   
        post_count = Theme.objects.filter(theme_start_user = user).count() + ThemeAnswers.objects.filter(theme_answer_user = user).count()
        next_datetime_add_karma = manage_profile.karma_points_last_add + datetime.timedelta(days=3)
        if request.method == 'POST':
            form = GbookProfileForm(request.POST,request.FILES,error_class=FormErrorList)
            if form.is_valid():
                send_data = form.cleaned_data  
                
                if 'avatar' in request.FILES:
                    manage_profile.avatar = gbook_save_avatar(name = send_data['avatar'],
                                                              image = request.FILES['avatar'])    
                                         
                manage_profile.gender=send_data['gender'] 
                manage_profile.city=send_data['city'] 
                manage_profile.about=send_data['about']
                                                            
                manage_profile.save()
                    
                return HttpResponseRedirect(reverse('gbook_manage_profile'))
        else:
            form = GbookProfileForm(initial = {'gender':manage_profile.gender,
                                               'city': manage_profile.city,
                                               'about':manage_profile.about})  
        return render_to_response('gbook/manage_profile.html', 
                                  locals(), 
                                  context_instance=RequestContext(request))
    else:
        raise Http404

 
def gbook_view_profile(request, view_profile):

    user, profile = gbook_authorization(request) 
                 
    datetime_now = datetime.datetime.now() 
    if user.is_authenticated() and user.gbookprofile.banned == False:
        new_private_messages = new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
    if user.is_superuser == True: 
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
    
    post_count = Theme.objects.filter(theme_start_user = view_profile).count() + ThemeAnswers.objects.filter(theme_answer_user = view_profile).count()

    try:    
        view_profile = User.objects.get(username = view_profile).gbookprofile
    except:
        raise Http404
        
    next_datetime_add_karma = view_profile.karma_points_last_add + datetime.timedelta(days=3)
    return render_to_response('gbook/view_profile.html', 
                              locals(),
                              context_instance=RequestContext(request))  
 
       
def gbook_change_password(request): 
 
    user, profile = gbook_authorization(request) 
             
    if user.is_authenticated() and user.gbookprofile.banned == False: 
        new_private_messages = new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')          
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()      
        post_count = Theme.objects.filter(theme_start_user = user).count() + ThemeAnswers.objects.filter(theme_answer_user = user).count() 
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST,error_class=FormErrorList)
            if form.is_valid():
                send_data = form.cleaned_data
                password = send_data['password']
                if user.check_password(password) == False:
                    pass_change_message = _(u'Current password is invalid') 
                else:       
                    password_new = send_data['password_new'] 
                    password_confirm = send_data['password_confirm']
                    if password_new == password_confirm:
                        user.set_password(password_new) 
                        user.save()
                        pass_change_message = _(u'Your password is successfully changed') 
                    else:
                        pass_change_message = _(u'The entered passwords do not match') 
                return render_to_response('gbook/change_password.html', locals(), context_instance=RequestContext(request))                            
        else:   
            form = ChangePasswordForm()  
        return render_to_response('gbook/change_password.html', locals(), context_instance=RequestContext(request))
    else:
        logout(request)    
    return HttpResponseRedirect(reverse('gbook_view'))     
      


# private messages 
def gbook_send_message(request, message_to_profile):

    user, profile = gbook_authorization(request) 
        
    if user.is_authenticated() and user.gbookprofile.banned == False:
        datetime_now = datetime.datetime.now() 
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        if request.method == 'POST':
            form = PrivateMessagesForm(request.POST, error_class=FormErrorList)
            if form.is_valid():       
                send_data = form.cleaned_data
                to_user = User.objects.get(username = message_to_profile)
                # send message to user
                PrivateMessages(message_to_user = message_to_profile,
                                message_from_user = user,
                                current_profile = to_user.gbookprofile,
                                message_text = send_data['message_text'], 
                                message_send_time = datetime_now, 
                                message_status = 'unread').save()
                # dublicate message for yourself               
                PrivateMessages(message_to_user = message_to_profile,
                                message_from_user = user,
                                current_profile = profile,
                                message_text = send_data['message_text'], 
                                message_send_time = datetime_now, 
                                message_status = 'send').save()                            
                return HttpResponseRedirect(reverse('gbook_private_messages'))
        else:
            form = PrivateMessagesForm()
        return render_to_response('gbook/send_message.html', 
                                   locals(),
                                   context_instance=RequestContext(request))
    else:
        logout(request)    
    return HttpResponseRedirect(reverse('gbook_view'))
 
    
def gbook_private_messages(request):
  
    user, profile = gbook_authorization(request) 
         
    if user.is_authenticated() and user.gbookprofile.banned == False:
        get_message = 14 # how many incoming messages show by default
        send_message = 14 # how many outcoming messages show by default
        if request.method == 'GET':
            show_what = request.GET.get('all')
            if show_what == 'get_message':
                get_message = None
            if show_what == 'send_message': 
                send_message = None  
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        messages_from = PrivateMessages.objects.filter(Q(current_profile = profile) & ~Q(message_status = 'send')).order_by('-message_send_time')[:get_message]
        messages_to = PrivateMessages.objects.filter(Q(current_profile = profile) & Q(message_status = 'send')).order_by('-message_send_time')[:send_message]
        return render_to_response('gbook/private_messages.html', 
                                   locals(),
                                   context_instance=RequestContext(request))   
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))
 
    
def gbook_show_chat(request, with_profile): 
 
    user, profile = gbook_authorization(request) 
        
    if user.is_authenticated() and user.gbookprofile.banned == False:
        datetime_now = datetime.datetime.now() 
        with_user = User.objects.get(username = with_profile)
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')    
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        messages = PrivateMessages.objects.filter(Q(current_profile = profile)) \
                                          .filter(Q(message_from_user = with_profile) | Q(message_to_user = with_profile)) \
                                          .order_by('-message_send_time')                                      
        PrivateMessages.objects.filter(Q(current_profile = profile) & Q(message_from_user = with_profile)) \
                               .update(message_status = 'read')                                                                           
        if request.method == 'POST':
            form = PrivateMessagesForm(request.POST,error_class=FormErrorList)
            if form.is_valid():       
                send_data = form.cleaned_data 
                with_profile_obj = User.objects.get(username = with_profile).gbookprofile
                # send message to user            
                PrivateMessages(message_to_user = with_profile,
                                message_from_user = user,
                                current_profile = with_profile_obj,
                                message_text = send_data['message_text'], 
                                message_send_time = datetime_now, 
                                message_status = 'unread').save()
                # dublicate message for yourself               
                PrivateMessages(message_to_user = with_profile,
                                message_from_user = user, 
                                current_profile = profile,
                                message_text = send_data['message_text'], 
                                message_send_time = datetime_now, 
                                message_status = 'send').save() 
                return HttpResponseRedirect('')
        else:
            form = PrivateMessagesForm()    
        return render_to_response('gbook/show_chat.html', 
                                  locals(),
                                  context_instance=RequestContext(request))      
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))


# karma       
def gbook_my_karma(request):
 
    user, profile = gbook_authorization(request) 
        
    if user.is_authenticated() and user.gbookprofile.banned == False: 
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')  
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        get_karma = 14 
        send_karma = 14 
        if request.method == 'GET':
            show_what = request.GET.get('all')
            if show_what == 'get_karma':
                get_karma = None
            if show_what == 'send_karma': 
                send_karma = None  
        karma_from_user = KarmaMessages.objects.filter(Q(current_profile = profile) & Q(karma_to_user = user)).order_by('-karma_send_time')[:get_karma]
        karma_to_user = KarmaMessages.objects.filter(Q(current_profile = profile) & ~Q(karma_to_user = user)).order_by('-karma_send_time')[:send_karma]
        return render_to_response('gbook/my_karma.html', locals(),context_instance=RequestContext(request))   
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))
 
     
def gbook_change_karma(request, karma_delta, to_profile):

    user, profile = gbook_authorization(request) 
        
    if user.is_authenticated() and user.gbookprofile.banned == False: 
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')  
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()    
        datetime_now = datetime.datetime.now() 
        karma_points = profile.karma_points          
        if karma_points > 0:
            
            if karma_delta == 'add-karma':
                karma_delta = 1
            elif karma_delta == 'remove-karma':
                karma_delta = -1  
            else:
                raise Http404
                     
            if request.method == 'POST':
                form = KarmaMessagesForm(request.POST, error_class=FormErrorList)
                if form.is_valid():
                    datetime_now = datetime.datetime.now()        
                    send_data = form.cleaned_data
                    to_profile_obj = User.objects.get(username = to_profile).gbookprofile
                    
                    # get karma points to current user                
                    karma_points = karma_points - 1
                    GbookProfile.objects.filter(user = profile.id).update(karma_points = karma_points)  

                    KarmaMessages(karma_to_user = to_profile,
                                  karma_from_user = user,
                                  current_profile = to_profile_obj,
                                  karma_text = send_data['karma_text'], 
                                  karma_delta = karma_delta,
                                  karma_send_time = datetime_now).save() 
           
                    KarmaMessages(karma_to_user = to_profile,
                                  karma_from_user = user,
                                  current_profile = profile,
                                  karma_text = send_data['karma_text'], 
                                  karma_delta = karma_delta,
                                  karma_send_time = datetime_now).save()                           
                                          
                    current_karma = to_profile_obj.karma            
                    
                    new_karma = current_karma + karma_delta
                    if to_profile_obj.user.is_superuser == False:
                        if new_karma <= -10 and to_profile_obj.banned == False:
                            to_profile_obj.banned = True
                            to_profile_obj.banned_by = 'Users'
                            to_profile_obj.banned_to = datetime_now + datetime.timedelta(days=3)
                            to_profile_obj.karma = new_karma
                            to_profile_obj.save()
                        elif new_karma >= 1 and to_profile_obj.banned:
                            to_profile_obj.banned = False
                            to_profile_obj.banned_by = None
                            to_profile_obj.karma = new_karma
                            to_profile_obj.save()                                                                                                                         
                        else:
                            to_profile_obj.karma = new_karma  
                            to_profile_obj.save()  
                             
                    elif to_profile_obj.user.is_superuser == True:    
                            to_profile_obj.karma = new_karma  
                            to_profile_obj.save() 
                                                     
                    return HttpResponseRedirect(reverse('gbook_my_karma'))
            else:
                form = KarmaMessagesForm()
        else: 
            karma_message = _(u'Your karma points have ended')        
        return render_to_response('gbook/change_karma.html', locals(),context_instance=RequestContext(request))
    else:
        logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))

    
# registration                          
def gbook_registration(request): 
    if GBOOK_REGISTRATION_VIA_EMAIL == 'yes':  
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                from md5 import md5 
                from django.core.mail import send_mail
                datetime_now = datetime.datetime.now()
                auth_key = md5(str(datetime_now)).hexdigest()              
                send_data = form.cleaned_data    
                host = request.META['HTTP_HOST']           
                subject = u'DjangoGuestbook registration'
                email_from = GBOOK_EMAIL_FROM    
                email = send_data['email']
                message = u'%s %s \n\n %s %s \n %s \n http://%s%s' % (_(u'Welcome'),
                                                               send_data['user'],
                                                               _(u'Your password:'),
                                                               send_data['password'],
                                                               _(u'For authorization use next link:'),
                                                               host,
                                                               reverse('gbook_registration_confirm',kwargs = {'auth_key':auth_key}))

                send_mail(subject, message, email_from, [email])
                new_user = User.objects.create_user(username = send_data['user'], 
                                                email = send_data['email'], 
                                                password = send_data['password'])                                    
                new_user.is_active = False
                new_user.save()
                GbookProfile.objects.filter(user = new_user.id).update(auth_key = auth_key)
                success_string  = u'%s %s <br /> %s <b>%s</b> <br /> %s<br /><a href="%s">Back to the guestbook</a>' % (_(u'Thank you'),
                                                                                                               send_data['user'],
                                                                                                               _(u'To your еmail:'),
                                                                                                               email,
                                                                                                               _(u'send message with authorization code.'),
                                                                                                               reverse('gbook_view'))
                request.session['success'] = success_string 
                return HttpResponseRedirect(reverse('gbook_registration_success'))
        else:
            form = RegistrationForm()
        return render_to_response('gbook/registration_form.html', locals(),context_instance=RequestContext(request))     
    else:
        logout(request)  
    return HttpResponseRedirect(reverse('gbook_view'))          
  
  
def gbook_registration_success(request):
    try:
        success = request.session['success']
        del request.session['success']
    except:
        return HttpResponseRedirect(reverse('gbook_registration'))
    return HttpResponse(success)
 
    
def gbook_registration_confirm(request, auth_key):
    
    try:
        user = GbookProfile.objects.get(auth_key = auth_key).user 
        if user.is_active == True:
            return HttpResponseRedirect(reverse('gbook_registration'))
        else: 
            user.is_active = True
            user.save()    
            success_string = u'%s <a href="%s">%s</a>' % (_(u'Your account is active'), reverse('gbook_view'), _(u'Back to gbook'))                 
            return HttpResponse(success_string) 
    except exception, e:
        return HttpResponseRedirect(reverse('gbook_registration'))     
  
        
# logout
def gbook_log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('gbook_view'))
    
    
# administration                               
def gbook_admin_edit_theme(request, theme):

    user = request.user 
    if user.is_anonymous(): 
        profile = None
    else:
        profile = user.gbookprofile 
                
    if user.is_superuser == True and user.gbookprofile.banned == False: 
        profile = user.gbookprofile 
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        edit_theme = Theme.objects.get(id = theme)       
        if request.method == 'POST':
            form = GbookSubmitForm(request.POST,error_class=FormErrorList)
            if form.is_valid():         
                send_data = form.cleaned_data        
                Theme.objects.filter(id = edit_theme.id).update(theme_start_message_text = send_data['message'],section = send_data['section'])
                return HttpResponseRedirect(reverse('gbook_view'))    
        else:          
            form = GbookSubmitForm(initial = {'message': edit_theme.theme_start_message_text,'section':edit_theme.section })   
        return render_to_response('gbook/gbook_edit_theme.html', locals(),context_instance=RequestContext(request)) 
    else:
        raise Http404


def gbook_admin_edit_answer(request, answer):

    user, profile = gbook_authorization(request)  
        
    if user.is_superuser == True and user.gbookprofile.banned == False: 
        profile = user.gbookprofile 
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        if user.is_superuser == True: 
            new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        try:
            edit_answer = ThemeAnswers.objects.get(id = answer) 
        except:
            raise Http404                 
        if request.method == 'POST':
            form = GbookSubmitForm(request.POST,error_class=FormErrorList)
            if form.is_valid():          
                send_data = form.cleaned_data        
                ThemeAnswers.objects.filter(id = edit_answer.id).update(theme_answer_message_text = send_data['message'])
                return HttpResponseRedirect('/gbook/')    
        else:          
            form = GbookSubmitForm(initial = {'message': edit_answer.theme_answer_message_text})   
        return render_to_response('gbook/gbook_edit_answer.html', 
                                  locals(),
                                  context_instance=RequestContext(request)) 
    else:
        raise Http404    


def gbook_admin_delete_theme(request, theme):

    user, profile = gbook_authorization(request)  
        
    if user.is_superuser == True and user.gbookprofile.banned == False:    
        theme = Theme.objects.get(id = theme)
        theme.delete()                
        return HttpResponseRedirect(reverse('gbook_view'))
    else:
        raise Http404
 
            
def gbook_admin_delete_answer(request,answer):

    user, profile = gbook_authorization(request) 
               
    if user.is_superuser == True and user.gbookprofile.banned == False:    
        theme_answer = ThemeAnswers.objects.get(id = answer)
        theme_answer.delete()                
        return HttpResponseRedirect(reverse('gbook_view')) 
    else:
        raise Http404


def gbook_admin_up_theme(request,theme):

    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now()
    if user.is_superuser == True and user.gbookprofile.banned == False:    
        theme = Theme.objects.filter(id = theme).update(theme_changetime = datetime_now)              
        return HttpResponseRedirect(reverse('gbook_view')) 
    else:
        raise Http404   


def gbook_admin_make_private_theme(request,theme):

    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now()
    if user.is_superuser == True and user.gbookprofile.banned == False:    
        theme = Theme.objects.filter(id = theme).update(private = True)              
        return HttpResponseRedirect(reverse('gbook_view')) 
    else:
        raise Http404


def gbook_admin_make_public_theme(request,theme):

    user, profile = gbook_authorization(request) 
        
    datetime_now = datetime.datetime.now()
    if user.is_superuser == True and user.gbookprofile.banned == False:    
        theme = Theme.objects.filter(id = theme).update(private = False)              
        return HttpResponseRedirect(reverse('gbook_view')) 
    else:
        raise Http404          

       
def gbook_admin_manage_profile(request,manage_profile):

    user, profile = gbook_authorization(request)     
        
    if user.is_superuser == True and user.gbookprofile.banned == False:
        datetime_now = datetime.datetime.now()
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        manage_profile = User.objects.get(username = manage_profile).gbookprofile   
        post_count = Theme.objects.filter(theme_start_user = manage_profile).count() + ThemeAnswers.objects.filter(theme_answer_user = manage_profile).count()
        next_datetime_add_karma = manage_profile.karma_points_last_add + datetime.timedelta(days=3)
        if request.method == 'POST':
            form = AdminGbookProfileForm(request.POST,request.FILES,error_class=FormErrorList)
            if form.is_valid():
                send_data = form.cleaned_data  
                
                if 'avatar' in request.FILES:
                    manage_profile.avatar = gbook_save_avatar(name = send_data['avatar'],
                                                              image = request.FILES['avatar'])    
                                         
                manage_profile.gender=send_data['gender'] 
                manage_profile.city=send_data['city'] 
                manage_profile.about=send_data['about']
                manage_profile.personal_status=send_data['personal_status']
                manage_profile.karma=send_data['karma']
                manage_profile.karma_points=send_data['karma_points']
                                                            
                if manage_profile.karma <= -10 and manage_profile.banned_by != 'Administrator':
                    manage_profile.banned = True, 
                    manage_profile.banned_by = 'Users'
                    manage_profile.banned_to = datetime_now + datetime.timedelta(days=3)                                      
                elif manage_profile.karma >= 1 and manage_profile.banned_by != 'Administrator':
                    manage_profile.banned = False  

                manage_profile.save()
                    
                return HttpResponseRedirect(reverse('gbook_admin_manage_profile',kwargs={'manage_profile':manage_profile.user.username}))
        else:
            form = AdminGbookProfileForm(initial = {'city': manage_profile.city,
                                                    'gender':manage_profile.gender,
                                                    'about':manage_profile.about,
                                                    'personal_status':manage_profile.personal_status,
                                                    'karma':manage_profile.karma,
                                                    'karma_points':manage_profile.karma_points})  
        return render_to_response('gbook/admin_manage_profile.html', 
                                  locals(), 
                                  context_instance=RequestContext(request))
    else:
        raise Http404

def gbook_admin_delete_profile(request,delete_profile):

    user, profile = gbook_authorization(request) 
        
    if user.is_superuser == True:    
        delete_profile = User.objects.get(username = delete_profile).gbookprofile
        Theme.objects.filter(fk_to_profile = delete_profile.id).update(fk_to_profile = None)
        ThemeAnswers.objects.filter(fk_to_profile = delete_profile.id).update(fk_to_profile = None)  
        delete_profile.delete()                
        return HttpResponseRedirect(reverse('gbook_admin_manage_users'))                      
    else:
        raise Http404 

def gbook_admin_add_ban(request,to_profile):

    user, profile = gbook_authorization(request) 
        
    if user.is_superuser == True and user.gbookprofile.banned == False: 
        datetime_now = datetime.datetime.now()   
        timedelta = datetime.timedelta(days=3) 
        profile = User.objects.get(username = to_profile).gbookprofile
        profile.banned = True
        profile.banned_by = 'Administrator'
        profile.banned_to = datetime_now + timedelta
        profile.save()                  
        return HttpResponseRedirect(request.META["HTTP_REFERER"])                    
    else:
        raise Http404 
  
  
def gbook_admin_remove_ban(request,to_profile):

    user, profile = gbook_authorization(request) 
        
    if user.is_superuser == True:    
        datetime_now = datetime.datetime.now()
        remove_ban_to_user = User.objects.get(username = to_profile).gbookprofile                                                   
        
        remove_ban_to_user.banned = False   
        remove_ban_to_user.banned_by = None          
        remove_ban_to_user.banned_to = None
        
        if remove_ban_to_user.karma <= -10: 
            remove_ban_to_user.karma = 1  
                  
        remove_ban_to_user.save()   
 
        return HttpResponseRedirect(request.META["HTTP_REFERER"])                    
    else:
        raise Http404 
                  

    
def gbook_admin_answers_from_unregistered(request):

    user, profile = gbook_authorization(request) 
      
    if user.is_superuser == True:
        datetime_now = datetime.datetime.now() 
        profile = user.gbookprofile  
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread') 
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        answers = AnswersFromUnregistered.objects.all() 
        if request.GET.get('publish'):
            publish = request.GET.get('publish')
            answer = AnswersFromUnregistered.objects.get(id = publish)
            if request.GET.get('confirm_reg'):
                
                # check for exist
                go_to_reg = False
                try:
                    User.objects.get(username = answer.unregistered_user)
                except:
                    go_to_reg = True
                
                # if user doesnt exist
                if go_to_reg:                                                                            
                    new_user = User.objects.create_user(username = answer.unregistered_user, 
                                email = answer.unregistered_user_email, 
                                password = answer.unregistered_user_has_password)  
                    fk_to_profile = new_user.gbookprofile 
                    
                    
                    from md5 import md5 
                    from django.core.mail import send_mail           
                    
                    host = request.META['HTTP_HOST']           
                    subject = _(u'Django Guestbook Registration')
                    email_from = GBOOK_EMAIL_FROM    
                    email = answer.unregistered_user_email
                    
                    message = u'%s %s\n\n%s\n%s %s\n%s %s\n%s%s' % (_(u'Welcome'), 
                                                                     answer.unregistered_user,
                                                                     _(u'For authorization use:'),
                                                                     _(u'Login:'),
                                                                     answer.unregistered_user,
                                                                     _(u'Password:'),
                                                                     answer.unregistered_user_has_password,
                                                                     _(u'Guestbook adress: http://'),
                                                                     host,                                                                         
                                                                     )
    
                    send_mail(subject, message, email_from, [email])                 
                             
            else:
                fk_to_profile = None 
                   
            if answer.unregistered_message_to_theme == 'new_theme':
                Theme(theme_start_user = answer.unregistered_user, 
                      theme_start_datetime = datetime_now, 
                      theme_start_message_text = answer.unregistered_user_send_message,
                      section = answer.unregistered_message_section,
                      theme_changetime = datetime_now,
                      fk_to_profile = fk_to_profile).save()             
                answer.delete()            
            else:
                ThemeAnswers(theme_answer_user = answer.unregistered_user, 
                      theme_answer_datetime = datetime_now, 
                      theme_answer_message_text = answer.unregistered_user_send_message, 
                      fk_to_theme_id = answer.unregistered_message_to_theme,
                      fk_to_profile = fk_to_profile).save() 
                Theme.objects.filter(id = answer.unregistered_message_to_theme).update(theme_changetime = datetime_now)                 
                answer.delete()
                                  
            return HttpResponseRedirect(reverse('gbook_admin_answers_from_unregistered'))   
            
        if request.GET.get('delete'):
            delete = request.GET.get('delete')
            answer = AnswersFromUnregistered.objects.get(id = delete)
            answer.delete()                
            return HttpResponseRedirect(reverse('gbook_admin_answers_from_unregistered'))                   
        return render_to_response('gbook/admin_answers_from_unregistered.html', 
                                  locals(),
                                  context_instance=RequestContext(request))
    else:
        raise Http404        
 
    
def gbook_admin_manage_users(request):

    user, profile = gbook_authorization(request)   
         
    if user.is_superuser == True: 
        datetime_now = datetime.datetime.now() 
        new_private_messages = PrivateMessages.objects.filter(current_profile = profile).filter(message_status = 'unread')        
        new_messages_from_unregistered = AnswersFromUnregistered.objects.all()
        gbook_profiles = GbookProfile.objects.all()
        gbook_profiles_count = GbookProfile.objects.count()
        return render_to_response('gbook/admin_manage_users.html', 
                                  locals(), 
                                  context_instance=RequestContext(request))
    else:
        raise Http404           