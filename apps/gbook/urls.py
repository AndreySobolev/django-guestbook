# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
import settings 


urlpatterns = patterns('gbook.views',     
    # gbook & user authorization 
    url(r'^$', 'gbook_view', name='gbook_view'), 
    url(ur'^section/(?P<section>.+)/$', 'gbook_view', name='gbook_view_section'),            
    url(r'^theme/(?P<theme>[a-z,_,0-9]+)/$', 'gbook_view', name='gbook_view_theme'),       
    url(r'^submit/(?P<theme>[a-z,_,0-9]+)/$', 'gbook_submit', name='gbook_submit'), 
    url(r'^submit/answer/(?P<theme>[a-z,_,0-9]+)/$', 'gbook_submit_answer', name='gbook_submit_answer'),     
    url(r'^unregistered/submit/(?P<theme>[a-z,_,0-9]+)/$', 'gbook_submit_unregistered', name='gbook_submit_unregistered'),  
    url(r'^unregistered/submit/answer/(?P<theme>[a-z,_,0-9]+)/$', 'gbook_submit_unregistered_answer', name='gbook_submit_unregistered_answer'),        
    url(r'^edit-theme/(?P<theme_id>\d+)$', 'gbook_edit_theme', name='gbook_edit_theme'),
    url(r'^edit-answer/(?P<answer>[a-z,_,-,-,0-9]+)$', 'gbook_edit_answer', name='gbook_edit_answer'),
    url(r'^delete-theme/(?P<theme>[a-z,_,-,-,0-9]+)$', 'gbook_delete_theme', name='gbook_delete_theme'), 
    url(r'^delete-answer/(?P<answer>[a-z,_,-,-,0-9]+)$', 'gbook_delete_answer', name='gbook_delete_answer'),
    url(r'^search/$', 'gbook_search', name='gbook_search'),         
     # user profile
    url(r'^manage-profile/$', 'gbook_manage_profile', name='gbook_manage_profile'),     
    url(ur'^view-profile/(?P<view_profile>.+)/$', 'gbook_view_profile', name='gbook_view_profile'),
    url(ur'^сhange-password/$','gbook_change_password', name='gbook_change_password'),     
     # private messages 
    url(ur'^send-message/to/(?P<message_to_profile>.+)/$', 'gbook_send_message', name='gbook_send_message'),     
    url(r'^my-private-messages/$', 'gbook_private_messages', name='gbook_private_messages'),
    url(ur'^show-chat/with/(?P<with_profile>.+)/$', 'gbook_show_chat', name='gbook_show_chat'),
     # karma
    url(r'^my-karma/$', 'gbook_my_karma', name='gbook_my_karma'),     
    url(ur'^(?P<karma_delta>[a-z,_,-,-,0-9]+)/to/(?P<to_profile>.+)/$', 'gbook_change_karma', name='gbook_change_karma'),                
     # registration
    url(r'^registration/$', 'gbook_registration', name='gbook_registration'),     
    url(r'^registration/success/$', 'gbook_registration_success', name='gbook_registration_success'), 
    url(r'^registration/confirm/(?P<auth_key>[a-z,0-9]+)/$', 'gbook_registration_confirm', name='gbook_registration_confirm'), 
      # logout
    url(r'^logout/$', 'gbook_log_out', name='gbook_log_out'),     
     # administration
    url(r'^admin/edit-theme/(?P<theme>[a-z,_,-,-,0-9]+)$', 'gbook_admin_edit_theme', name='gbook_admin_edit_theme'),
    url(r'^admin/edit-answer/(?P<answer>[a-z,_,-,-,0-9]+)$', 'gbook_admin_edit_answer', name='gbook_admin_edit_answer'),
    url(r'^admin/delete-theme/(?P<theme>[a-z,_,-,-,0-9]+)$', 'gbook_admin_delete_theme', name='gbook_admin_delete_theme'), 
    url(r'^admin/delete-answer/(?P<answer>[a-z,_,-,-,0-9]+)$', 'gbook_admin_delete_answer', name='gbook_admin_delete_answer'),
    url(r'^admin/up-theme/(?P<theme>[a-z,_,-,-,0-9]+)$', 'gbook_admin_up_theme', name='gbook_admin_up_theme'),
    url(r'^admin/make-private/(?P<theme>[a-z,_,-,-,0-9]+)$', 'gbook_admin_make_private_theme', name='gbook_admin_make_private_theme'), 
    url(r'^admin/make-public/(?P<theme>[a-z,_,-,-,0-9]+)$', 'gbook_admin_make_public_theme', name='gbook_admin_make_public_theme'),       
    url(ur'^admin/manage-profile/(?P<manage_profile>.+)$', 'gbook_admin_manage_profile', name='gbook_admin_manage_profile'), 
    url(ur'^admin/delete-profile/(?P<delete_profile>.+)$', 'gbook_admin_delete_profile', name='gbook_admin_delete_profile'), 
    url(ur'^admin/add-ban/(?P<to_profile>.+)$', 'gbook_admin_add_ban', name='gbook_admin_add_ban'), 
    url(ur'^admin/remove-ban/(?P<to_profile>.+)$', 'gbook_admin_remove_ban', name='gbook_admin_remove_ban'),   
    url(r'^admin/answers-from-unregistered/$', 'gbook_admin_answers_from_unregistered', name='gbook_admin_answers_from_unregistered'), 
    url(r'^admin/manage-users/$', 'gbook_admin_manage_users',name='gbook_admin_manage_users'),      
)
         