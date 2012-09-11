# -*- coding: utf-8 -*-
# statuses on russian, for correct translate to russian language

from django import template 
from django.utils.translation import ugettext_lazy as _
from settings import MEDIA_URL
register = template.Library()


# standart by Sobolev Andrey
@register.filter(name='show_status')
def show_status(karma):
    print karma
    if karma is None or karma is '':
        return ''     
    if karma <= -10:
        return ''     
    elif karma == -9:
        points_to_ban = 1
        return u'<img src=%s/gbook/img/standart_theme_status_pics/0.png id="status-pic"><span class="status" style="background:#f68989">%s %s</span>' % (MEDIA_URL, points_to_ban, _(u'одно очко до бана'))          
    elif karma > -9 and karma < -5:
        points_to_ban = 10 + int(karma) 
        return u'<img src=%s/gbook/img/standart_theme_status_pics/1.png id="status-pic"><span class="status" style="background:#ffdada">%s %s</span>' % (MEDIA_URL, points_to_ban, _(u'очка до бана'))    
    elif karma >= -5 and karma < 1:
        points_to_ban = 10 + int(karma) 
        return u'<img src=%s/gbook/img/standart_theme_status_pics/2.png id="status-pic"><span class="status" style="background:#ffdada">%s %s</span>' % (MEDIA_URL, points_to_ban, _(u'очков до бана')) 
    elif karma >= 1 and karma <= 5:
        return u'<img src=%s/gbook/img/standart_theme_status_pics/3.png id="status-pic"><span class="status" style="background:#e8eaea">%s</span>' % (MEDIA_URL,_(u'Новичок'))
    elif karma > 5 and karma <= 20:
        return u'<img src=%s/gbook/img/standart_theme_status_pics/3.png id="status-pic"><span class="status" style="background:#f7f7f7">%s</span>' % (MEDIA_URL,_(u'Хорошая репутация'))       
    elif karma > 20 and karma <= 100:
        return u'<img src=%s/gbook/img/standart_theme_status_pics/4.png id="status-pic"><span class="status" style="background:#bbdaa6">%s</span>' % (MEDIA_URL,_(u'Прекрасная репутация'))
    elif karma > 100 and karma <= 777:
        return u'<img src=%s/gbook/img/standart_theme_status_pics/5.png id="status-pic"><span class="status" style="background:#b5df26">%s</span>' % (MEDIA_URL,_(u'Легенда'))                     
    elif karma > 777:
        return u'<span class="status" style="background:#dfdfdf;font-size:12px;">%s</span>' % (_(u'Администратор'))                                  
    else:
        return '' 


       
        
        
            

       
        