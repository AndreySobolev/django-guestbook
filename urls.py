# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
import settings 


urlpatterns = patterns('',
    url(r'^$', 'gbook.views.index'),
    # etc
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),    
)

# gbook
urlpatterns += patterns('',
    (r'^gbook/', include('gbook.urls')),) 

#captcha    
urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),)


         