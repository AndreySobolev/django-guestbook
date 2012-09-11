# -*- coding: utf-8 -*-
import re
from django.conf import settings
from django.utils.html import escape
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe 
from django.utils.translation import ugettext_lazy as _
from settings import MEDIA_URL
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext 

__all__ = ('BBCODE_RULES', 'bbcode')

#regexp for url validation from django URLField + added ftp:// and allowing spaces around
URL_RE = r'\s*(http:\/\/|https:\/\/)(www.|)((?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'\
    'localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+))\s*'

IMG_RE = r'\s*((ftp|https?)://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'\
    'localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+))\s*'
    
#regexp for email from django + allowing spaces around
EMAIL_RE = r"""\s*(([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^"""\
        """([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")"""\
        """@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?)\s*"""


def code_parser(matchobj):
    """
    Escaping bbcode and html tags between [code] tags.
    """

    value = matchobj.group(1)
    value = value.replace('[', '&#91;')
    value = value.replace(']', '&#93;')
    value = value.replace('<br />', '\n')
    return "<pre><code>%s</code></pre>" % value

"""
BBcode rule format:
    'pattern' and 'repl'' - params for re.sub(); 'repl' can be function
    'sortkey' - used to sort rules from highest to lowest; default value: 0
    'nested' - show how many time tag can be nested to itself; only for [quote] now
"""

PATH_TO_SMILES = MEDIA_URL + '/gbook/smiles/'

thisUser = '' 
  
def private(matchobj):
    value = matchobj.group(1)
    global thisUser
    if str(thisUser) == 'AnonymousUser':
        new_val = u'<span class="jQtooltip private-registred" title="%s">%s</span>' % (_(u'Private text. Only for registered users.'),_(u'private text'))   
        return new_val
    else:  
        new_val = u'<span class="jQtooltip private-registred" title="%s">%s</span>' % (_(u'Private text. Only for registered users.'),value)                 
        return new_val
   
BBCODE_RULES = [
        {'pattern': r'\[code\](.*?)\[/code\]', 'repl': code_parser, 'sortkey': 100},
        {'pattern': r'\[url\]%s\[/url\]' % URL_RE, 'repl': r'<a href="http://\3" target="_blank">http://\3</a>'},
        #{'pattern': r'\[url=%s\](.*?)\[/url\]' % URL_RE, 'repl': r'<a href="\1">\3</a>'},
        #{'pattern': r'\[link\]%s\[/link\]' % URL_RE, 'repl': r'<a href="\1">\1</a>'},
        #{'pattern': r'\[link=%s\](.*?)\[/link\]' % URL_RE, 'repl': r'<a href="\1">\3</a>'},
        #{'pattern': r'\[email\]%s\[/email\]' % EMAIL_RE, 'repl': r'<a href="mailto:\1">\1</a>'},
        #{'pattern': r'\[email=%s\](.*?)\[/email\]' % EMAIL_RE, 'repl': r'<a href="mailto:\1">\5</a>'},
        {'pattern': r'\[img\]%s\[/img\]' % IMG_RE, 'repl': r'<img src="\1">'},
        #{'pattern': r'\[img=%s\](.*?)\[/img\]' % URL_RE, 'repl': r'<img src="\1" alt="\3">'},
        {'pattern': r'\[color=([a-zA-Z]*|\#?[0-9a-fA-F]{6})\](.*?)\[/color=([a-zA-Z]*|\#?[0-9a-fA-F]{6})\]', 'repl': r'<span style="color:\1">\2</span>'},
        {'pattern': r'\[b\](.*?)\[/b\]', 'repl': r'<strong>\1</strong>'},
        {'pattern': r'\[i\](.*?)\[/i\]', 'repl': r'<em>\1</em>'},
        {'pattern': r'\[u\](.*?)\[/u\]', 'repl': r'<u>\1</u>'},
        {'pattern': r'\[s\](.*?)\[/s\]', 'repl': r'<strike>\1</strike>'},
        {'pattern': r'\[quote\](.*?)\[/quote\]', 'repl': r'<blockquote>\1</blockquote>', 'nested': 5},
        {'pattern': r'\[quote=(.*?)\](.*?)\[/quote\]', 'repl': r'<blockquote><em>\1</em> <br /> \2</blockquote>', 'nested': 5},         
        {'pattern': r'\[h2\](.*?)\[/h2\]', 'repl': r'<h2>\1</h2>'}, 
        {'pattern': r'\[h3\](.*?)\[/h3\]', 'repl': r'<h3>\1</h3>'}, 
        {'pattern': r'\[more\](.*?)\[/more\]', 'repl': '<span><a href=\'#\' onclick="obj=this.parentNode.childNodes[1].style;tmp=(obj.display!=\'block\')?\'block\':\'none\';obj.display=tmp;return false;">' + ur'Скрытый текст' + r'</a>' + r'<div class="subblock" style="display:none">\1</div></span>'},     
        {'pattern': r'\[youtube\](http:\/\/|)(www.|)youtube.com\/watch\?v\=(\w+)(&.*?)?(?=[^-\w&=%])\[/youtube\]', 'repl': r'<object width="425" height="350"><param name="movie" value="http://www.youtube.com/v/\3"></param><param name="wmode" value="transparent"></param><embed src="http://www.youtube.com/v/\3" type="application/x-shockwave-flash" width="425" height="350"></embed></object>'},
        #{'pattern': r'\[center\](.*?)\[/center\]', 'repl': r'<div style="text-align: center;">\1</div>'},
        #{'pattern': r'\[big\](.*?)\[/big\]', 'repl': r'<big>\1</big>'},      
        #{'pattern': r'\[small\](.*?)\[/small\]', 'repl': r'<small>\1</small>'},
        #{'pattern': r'\[list\](.*?)\[/list\]', 'repl': r'<ul>\1</ul>'},
        #{'pattern': r'\[list\=(\d+)\](.*?)\[/list\]', 'repl': r'<ol start="\1">\2</ol>'},
        {'pattern': r'\[\*\](.*?)<br./>', 'repl': r'<li>\1</li>'},
        {'pattern': r'\[br\]', 'repl': r'<br />'},
        # private message
        {'pattern': r'\[private\](.*?)\[/private\]', 'repl': private},
        # smiles
        {'pattern': r'\[aaaa\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'aaaa.gif">'},
        {'pattern': r'\[good\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'good.gif">'},     
        {'pattern': r'\[wink\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'wink.gif">'},
        {'pattern': r'\[bubble\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'bubble.gif">'},
        {'pattern': r'\[angel\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'angel.gif">'},
        {'pattern': r'\[gigi\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'gigi.gif">'},
        {'pattern': r'\[kissmebaby\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'kissmebaby.gif">'},
        {'pattern': r'\[emo\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'emo.gif">'},
        {'pattern': r'\[heart\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'heart.gif">'},
        {'pattern': r'\[hate\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'hate.gif">'},
        {'pattern': r'\[haughty\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'haughty.gif">'},
        {'pattern': r'\[applauds\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'applauds.gif">'},
        {'pattern': r'\[kissgirl\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'kissgirl.gif">'},
        {'pattern': r'\[take-a-rose\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'take-a-rose.gif">'},
        {'pattern': r'\[cool\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'cool.gif">'},
        {'pattern': r'\[accordion\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'accordion.gif">'},
        {'pattern': r'\[wakeup\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'wakeup.gif">'},
        {'pattern': r'\[birthday\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'birthday.gif">'},
        {'pattern': r'\[aaaaa\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'aaaaa.gif">'},
        {'pattern': r'\[drink2\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'drink2.gif">'},
        {'pattern': r'\[drink3\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'drink3.gif">'},
        {'pattern': r'\[bluff\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'bluff.gif">'},
        {'pattern': r'\[byebye\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'byebye.gif">'},
        {'pattern': r'\[killyourself\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'killyourself.gif">'},
        {'pattern': r'\[dance\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'dance.gif">'},
        {'pattern': r'\[devil\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'devil.gif">'},
        {'pattern': r'\[disco\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'disco.gif">'},
        {'pattern': r'\[tease\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'tease.gif">'},
        {'pattern': r'\[emo\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'emo.gif">'},
        {'pattern': r'\[evil\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'evil.gif">'},
        {'pattern': r'\[gandja\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'gandja.gif">'},   
        {'pattern': r'\[girlcry\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'girlcry.gif">'},
        {'pattern': r'\[gnas\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'gnas.gif">'},
        {'pattern': r'\[gnas2\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'gnas2.gif">'},
        {'pattern': r'\[gbo\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'gbo.gif">'},
        {'pattern': r'\[haha\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'haha.gif">'},
        {'pattern': r'\[holiday\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'holiday.gif">'},
        {'pattern': r'\[go-out\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'go-out.gif">'},
        {'pattern': r'\[inlove\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'inlove.gif">'},
        {'pattern': r'\[inlove2\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'inlove2.gif">'},
        {'pattern': r'\[koncert\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'koncert.gif">'}, 
        {'pattern': r'\[listen\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'listen.gif">'},
        {'pattern': r'\[magic\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'magic.gif">'},
        {'pattern': r'\[on-horse\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'on-horse.gif">'},
        {'pattern': r'\[reglament\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'reglament.gif">'},
        {'pattern': r'\[drink\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'drink.gif">'},
        {'pattern': r'\[sex\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'sex.gif">'},  
        {'pattern': r'\[shoot\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'shoot.gif">'},
        {'pattern': r'\[not-me\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'not-me.gif">'},
        {'pattern': r'\[zig\]', 'repl': r'<img src="'+ PATH_TO_SMILES + 'zig.gif">'},                       
]

BBCODE_RULES += getattr(settings, 'BBMARKUP_EXTRA_RULES', [])
BBCODE_RULES.sort(key=lambda r: r.get('sortkey', 0), reverse=True)

BBCODE_RULES_COMPILED = []
for bbset in (getattr(settings, 'BBMARKUP_CUSTOM_RULES', []) or BBCODE_RULES):
    bbset['pattern'] = re.compile(bbset['pattern'], re.DOTALL | re.IGNORECASE)
    bbset.setdefault('sortkey', 0)
    bbset.setdefault('nested', 0)
    BBCODE_RULES_COMPILED.append(bbset)

from django import template 
from django.template import loader,RequestContext     
register = template.Library()


@register.filter(name='bbcode') 
def bbcode(value, user=''):
    global thisUser
    thisUser = str(user)
    value = escape(value)
    value = linebreaksbr(value)
    for bbset in BBCODE_RULES_COMPILED:
        for _ in xrange(bbset['nested'] + 1):
            value = bbset['pattern'].sub(bbset['repl'], value)
    return mark_safe(value)
    
   

