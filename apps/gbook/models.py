# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User 
from django.forms import ModelForm, Textarea
from django.db.models.signals import post_init, post_save
from django.utils.translation import ugettext_lazy as _


GENDER_CHOICES = (
(_(u'M'), _(u'Male')),
(_(u'F'), _(u'Female')),
)
 
class GbookProfile(models.Model): 
    user = models.OneToOneField(User) 
    avatar = models.ImageField(blank=True, null=True, upload_to='gbook/avatar/') 
    gender = models.CharField(blank=True, null=True, max_length=1,choices=GENDER_CHOICES) 
    city = models.CharField(blank=True, null=True, max_length=30) 
    about = models.CharField(blank=True, null=True, max_length=200) 
    personal_status = models.CharField(blank=True, null=True, max_length=500) 
    karma = models.IntegerField(default=1) 
    karma_points = models.IntegerField(default=1)  
    karma_points_last_add = models.DateTimeField(blank=True, null=True, default=datetime.datetime.now)     
    auth_key = models.CharField(blank=True, max_length=50) 
    banned = models.BooleanField(default=False) 
    banned_by = models.CharField(blank=True, null=True, max_length=50) 
    banned_to = models.DateTimeField(blank=True, null=True)


# create first profile (when install)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        GbookProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

# manage profile karma and ban time
def manage_profile(sender, **kwargs):

    profile = kwargs['instance']

    datetime_now = datetime.datetime.now() 
    
    # if user banned
    if profile.banned and profile.banned_to:
        if profile.banned_to <= datetime_now: # after exit from ban           
            profile.banned = False
            profile.banned_to = None
            profile.banned_by = None
            
            if profile.karma < 1:
                profile.karma = 1 

            profile.save()      
                                  
    # every 3 days activity user get 3 karma points
    add_karma_period = datetime.timedelta(days=3)
    if (datetime_now - profile.karma_points_last_add) > add_karma_period:
        karma_points = profile.karma_points + 3 # increase karma points to 3             
        profile.karma_points = karma_points
        profile.karma_points_last_add = datetime_now
        profile.save()
    
post_init.connect(manage_profile, sender=GbookProfile)
                            


class UsersOnline(models.Model): 
    username = models.CharField(max_length=30) 
    time = models.DateTimeField() # time last request to gbook 
    ip_adress = models.IPAddressField(blank=True, null=True) # current ip               
    
                                                   
class Theme(models.Model):
    theme_start_user = models.CharField(max_length=30)
    theme_start_datetime = models.DateTimeField() 
    theme_start_message_text = models.CharField(max_length=4000)  
    theme_changetime = models.DateTimeField() 
    section = models.CharField(max_length=30,default='',blank=True)    
    private = models.BooleanField(default=False, blank=True)   
    fk_to_profile = models.ForeignKey(GbookProfile,blank=True, null=True)            
    def __unicode__(self):
            return '%s %s %s' % (self.theme_start_user, self.theme_start_datetime, self.theme_start_message_text, self.theme_changetime)               
    class Meta:
        ordering = ('-theme_changetime',) 
                          
class ThemeAnswers(models.Model):
    theme_answer_user = models.CharField(max_length=30)
    theme_answer_datetime = models.DateTimeField()
    theme_answer_message_text = models.CharField(max_length=4000)
    fk_to_theme = models.ForeignKey(Theme, blank=True, null=True)  
    fk_to_profile = models.ForeignKey(GbookProfile,blank=True, null=True)  
    def __unicode__(self):
            return '%s %s %s %s' % (self.theme_answer_user, self.theme_answer_datetime, self.theme_answer_message_text)    

class AnswersFromUnregistered(models.Model):
    unregistered_user = models.CharField(max_length=30)   
    unregistered_user_has_password = models.CharField(max_length=30,blank=True, null=True)                         
    unregistered_user_send_message = models.CharField(max_length=4000)
    unregistered_message_to_theme = models.CharField(max_length=30)
    unregistered_message_section = models.CharField(max_length=30,default='',blank=True)   
    unregistered_user_need_registration = models.CharField(max_length=8,blank=True, null=True)
    unregistered_user_email = models.CharField(max_length=48,blank=True, null=True)    
    unregistered_message_send_time = models.DateTimeField() 
    class Meta:
        ordering = ('-unregistered_message_send_time',)        
      
class PrivateMessages(models.Model):
    current_profile = models.ForeignKey(GbookProfile)  
    message_from_user = models.CharField(blank=True,max_length=30)
    message_to_user = models.CharField(blank=True,max_length=30)
    message_text = models.CharField(blank=True, null=True, max_length=2000)
    message_status = models.CharField(blank=True,max_length=30)
    message_send_time = models.DateTimeField()
    def __unicode__(self):
            return '%s %s %s %s' % (self.message_from_user, self.message_to_user, self.message_text, self.message_status)
     
class KarmaMessages(models.Model): 
    current_profile = models.ForeignKey(GbookProfile)    
    karma_from_user = models.CharField(blank=True, max_length=30)
    karma_to_user = models.CharField(blank=True, max_length=30)    
    karma_text = models.CharField(blank=True, null=True, max_length=2000)
    karma_delta = models.IntegerField(blank=True)
    karma_send_time = models.DateTimeField() 
    def __unicode__(self):
            return '%s %s %s %s' % (self.karma_from_user, karma_to_user, self.karma_text, self.karma_send_time)
            

          
                   

                 
              




       
                    
