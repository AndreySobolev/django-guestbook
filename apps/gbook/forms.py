# -*- coding: utf-8 -*-
import datetime 

from django import forms
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django.forms.util import ErrorList
from gbook.models import GbookProfile
from settings import GBOOK_SECTIONS

SHOW_ANSWERS = (
    (u'yes', _(u'Show')),
    (u'no', _(u'Do not show')),
)
  
class AuthorizationForm(forms.Form):  
    user = forms.CharField( label=_('User'),error_messages={'required': _(u'Enter login')} )
    password = forms.CharField( widget=forms.PasswordInput, label=_(u'Password'),error_messages={'required': _(u'Enter password')} ) 
    def clean_user(self):
        user = self.cleaned_data['user']

        try:
            user = User.objects.get(username = user)
            if not user.is_active:
                raise forms.ValidationError("Wait email confirmation")              
            profile = user.gbookprofile
  
        except:
            raise forms.ValidationError("No such user")
        
        if profile.banned:
            raise forms.ValidationError("You banned")    
                                  
        return user
        
class Sections(forms.Form):    
    section = forms.ChoiceField(label=_(u'Section'),choices=GBOOK_SECTIONS,required=False)
 
    
class ShowAnswers(forms.Form):     
    show_answers = forms.ChoiceField(label=_(u'Show answers to themes'),choices=SHOW_ANSWERS,required=False)


class SearchForm(forms.Form):
    search_text = forms.CharField(label=_(u'Search text'),widget=forms.TextInput(attrs={'size':'54'}),error_messages={'required' : _(u'Specify your search')},required=True )
    show_section = forms.ChoiceField(label=_(u'Section'),choices=((u'all', u'*'),) + GBOOK_SECTIONS,required=False)
    #captcha = CaptchaField(label=_(u'Captcha'),error_messages={'required' : _(u'Input digits from picture'),'invalid': _(u'Error captcha code')}) 
    def clean_search_text(self):
        search_text = self.cleaned_data['search_text'] 
        if len(search_text) > 70:
            raise forms.ValidationError("No more 70 symbols") 
        return search_text


class GbookSubmitForm(forms.Form):    
    message = forms.CharField(label = _(u'Message'), widget=forms.Textarea(attrs={'cols': 84, 'rows': 10}),error_messages={'required' : _(u'Write something')}) 
    section = forms.ChoiceField(label=_(u'Section'),choices=GBOOK_SECTIONS,required=False) 
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) > 2000:
            raise forms.ValidationError(_(u'The maximum size of the message - 2000 symbols'))
        return message           
    #captcha = CaptchaField(label=_(u'Captcha'),error_messages={'required' : _(u'Input digits from picture'),'invalid': _(u'Error captcha code')})  
 
 
NEED_REGISTRATION = (
    (u'no', _(u'Don\'t need registration')),
    (u'yes', _(u'Need registration')),
)
    
class GbookSubmitFormUnregistered(forms.Form): 
    unregistered_user = forms.CharField(max_length=30,required=True,error_messages={'required' : _(u'Specify name')})   
    unregistered_user_send_message = forms.CharField(label = _(u'Message'), widget=forms.Textarea(attrs={'cols': 38, 'rows': 10}),required=True,error_messages={'required' : _(u'Write something')}) 
    section = forms.ChoiceField(label=_(u'Section'),choices=GBOOK_SECTIONS,required=False) 
    captcha = CaptchaField(label=_(u'Captcha'),error_messages={'required' : _(u'Enter characters from picture'),'invalid': _(u'Error captcha code')}) 
    unregistered_user_need_registration = forms.ChoiceField(choices=NEED_REGISTRATION,required=False) 
    unregistered_user_email = forms.EmailField(label=u'email',required=False)            
    def clean_unregistered_user(self):
        user = self.cleaned_data['unregistered_user'] 
        u_check = 1 
        try:     
            User.objects.get(username = user) 
        except:
            u_check = 0 
        if u_check == 1: 
            raise forms.ValidationError(_(u'That user already exist')) 
        return user 
    def clean_unregistered_user_send_message(self):
        message = self.cleaned_data['unregistered_user_send_message']
        if len(message) > 4000:
            raise forms.ValidationError(_(u'The maximum size of the message - 4000 symbols'))
        return message          
    def clean_unregistered_user_email(self):
        email = self.cleaned_data['unregistered_user_email'] 
        if len(email) > 40:
            raise forms.ValidationError(_(u'No more than 40 characters'))         
        e_check = 1        
        try:     
            User.objects.get(email = email)
        except:
            e_check = 0
        if e_check == 1:
            raise forms.ValidationError(_(u'Such mail box already is'))
        need_red = self.cleaned_data['unregistered_user_need_registration']
        if need_red == 'yes':                 
            if email == None or email == '':
                raise forms.ValidationError(_(u'For registration fill the field \"email \"'))              
        return email  


class GbookProfileForm(ModelForm): 
    class Meta:
        model = GbookProfile   
        fields = ('avatar', 'gender', 'city', 'about',) 
        widgets = {'about': Textarea(attrs={'cols': 33, 'rows': 5}),}  


class ChangePasswordForm(forms.Form):
    password = forms.CharField(required=True, widget=forms.PasswordInput,label=_(u'Current password'),error_messages={'required' : _(u'Enter current password')} )
    password_new = forms.CharField(required=True, widget=forms.PasswordInput, label=_(u'New password'),error_messages={'required' : _(u'Enter new password')} )    
    password_confirm = forms.CharField(required=True, widget=forms.PasswordInput,label=_(u'Repeat new password'),error_messages={'required' : _(u'Repeat new password')})     
    class ChangePasswordForm(ErrorList):
        def __unicode__(self):
            return self.as_divs()
        def as_divs(self):
            if not self: return u''
            error = u'<div class="errorlist_registration">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])
            return error 


class PrivateMessagesForm(forms.Form):
    message_text = forms.CharField(label=_(u'Message'), widget=forms.Textarea(attrs={'cols': 84, 'rows': 10}),error_messages={'required' : _(u'Write something')})
    def clean_message_text(self):
        message = self.cleaned_data['message_text']
        if len(message) > 1400:
            raise forms.ValidationError(_(u'The maximum size of the message of 1400 characters'))
        return message  
                             
                             
class KarmaMessagesForm(forms.Form):
    karma_text = forms.CharField(label=_(u'Message'), widget=forms.Textarea(attrs={'cols': 84, 'rows': 10}),error_messages={'required' : u'Напишите что нибудь'})
    def clean_karma_text(self):
        message = self.cleaned_data['karma_text']
        if len(message) > 1400:
            raise forms.ValidationError(_(u'The maximum size of the message of 1400 characters'))
        return message 


class RegistrationForm(forms.Form):
    user = forms.CharField(label=_(u'User'),error_messages={'required' : _(u'Enter login')} )
    password = forms.CharField( widget=forms.PasswordInput, label=_(u'Password'),error_messages={'required' : _(u'Enter password')} )    
    email = forms.EmailField(required=True, label=_(u'Email'),error_messages={'invalid': _(u'Enter correct e-mail'),'required' : _(u'Enter e-mail')})
    captcha = CaptchaField( label=_(u'Captcha'),error_messages={'required' : _(u'Enter characters from picture'),'invalid': _(u'Invalid captcha code')} )
    def clean_user(self):
        user = self.cleaned_data['user'] 
        if len(user) > 30:
            raise forms.ValidationError(_(u'No more 30 characters'))        
        u_check = 1 
        try:     
            User.objects.get(username = user) 
        except:
            u_check = 0 
        if u_check == 1: 
            raise forms.ValidationError(_(u'That user already exist'))
        return user      
    def clean_email(self):
        email = self.cleaned_data['email'] 
        if len(email) > 40:
            raise forms.ValidationError(_(u'No more than 40 characters'))         
        e_check = 1        
        try:     
            User.objects.get(email = email)
        except:
            e_check = 0
        if e_check == 1:
            raise forms.ValidationError(_(u'Such mail box already is'))
        return email  
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.error_class = self.RegistrationFormErrorList 
    class RegistrationFormErrorList(ErrorList):
        def __unicode__(self):
            return self.as_divs()
        def as_divs(self):
            if not self: return u''
            error = u'<div class="errorlist_registration">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])
            return error  


class AdminGbookProfileForm(ModelForm): 
    class Meta:
        model = GbookProfile   
        fields = ('avatar', 'gender', 'city', 'about','personal_status','karma','karma_points') 
        widgets = {'about': Textarea(attrs={'cols': 33, 'rows': 5}),}          
        

class FormErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        error = u'<div class="errorlist_gbook">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])
        return error                                                   
       
           