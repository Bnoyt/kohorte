from django import template
from ..models import *
from bs4 import BeautifulSoup
from markdownx.utils import markdownify
from django.utils.safestring import mark_safe
import re

register = template.Library()


def remplacer_citations(texte):
	citations = re.findall(r"\{\{[0-9]+\}\}",texte)
	for c in citations:
		a = Citation.objects.filter(pk=int(c[2:][:-2]))
		if len(a) > 0:
			date = a[0].post.date
			k = """<blockquote>
			<p>""" + BeautifulSoup(a[0].contenu).text + """
			</p>
			<small> 
			""" + a[0].post.auteur.user.username + """ le """ + (date.ctime()) + """ dans le noeud <strong>""" + a[0].post.noeud.label + """</strong>
			</small>
			</blockquote>"""
			texte = texte.replace(c,k)
	return texte

def remplacer_code(texte):
	codes = re.findall(r"\{%c%(.+)%c%\}",texte,re.S)
	for c in codes:
		k =  '<pre class="prettyprint">' + c + '</pre>'
		texte = texte.replace("{%c%" + c + "%c%}",k)



	return texte

def remplacer_hashtag(texte):
	new_texte = ""
	for i in range(len(texte)-1):
		if texte[i] == "#" and texte[i+1] != " ":
			new_texte += "\#"
		else:
			new_texte += texte[i]
	try: 
		new_texte += texte[-1]
	except:
		pass


	hashtags = re.findall(r"\\#[A-Za-z1-9]+",new_texte,re.S)
	for h in hashtags:
		t = """<a href = '/hashtags/""" + h[2:] + """/'> """ + h + """ </a> """
		new_texte = new_texte.replace(h,t)
	return new_texte


@register.filter(name="rendusafe",is_safe=True)
def rendusafe(texte):
	texte = str(texte)
	texte = BeautifulSoup(texte,"lxml").text
	texte = remplacer_citations(texte)
	texte = remplacer_code(texte)
	texte = remplacer_hashtag(texte)
	texte = markdownify(texte)
	return texte

@register.filter(name="menumessagerie")
def menumessagerie(path):
	a = path.split("/")
	if a[1] == "messages":
		return 'class="active"'
	else:
		return ""