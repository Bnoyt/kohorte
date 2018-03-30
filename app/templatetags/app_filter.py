from django import template
from ..models import *
from bs4 import BeautifulSoup
from markdownx.utils import markdownify
from django.utils.safestring import mark_safe
from django.utils.http import urlquote_plus
import re

register = template.Library()


def remplacer_citations(texte, limit=0):
	citations = re.findall(r"\{\{[0-9]+\}\}",texte)
	for c in citations:
		a = Citation.objects.filter(pk=int(c[2:][:-2]))
		if len(a) > 0:
			date = a[0].post.date
			if a[0].post.disabled:
				k = """<blockquote>
				<p>Post source supprimé</p>
				<small> 
				le """ + (date.ctime()) + """ dans le noeud <strong>""" + a[0].post.noeud.label + """</strong>
				</small>
				</blockquote>"""
				pass
			else:
				k = """<blockquote>
				<p>""" + BeautifulSoup(a[0].contenu, "lxml").text + """
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

def remplacer_hashtag(texte, question):
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

	q = question
	hashtags = re.findall(r"\\#\w+",new_texte,re.S)
	for h in hashtags:
		t = "<a href = '/{question}/hashtags/{hashtag}/'> {display} </a>".format(question = str(q), hashtag = urlquote_plus(h[2:]), display = h)
		new_texte = new_texte.replace(h,t)
	return new_texte


@register.filter(name="rendusafe")
def rendusafe(texte, id_question, limit=0):
	texte = str(texte)
	texte = BeautifulSoup(texte,"lxml").text
	texte = remplacer_citations(texte, limit)
	texte = remplacer_code(texte)
	texte = remplacer_hashtag(texte, id_question)
	texte = markdownify(texte)
	return texte

@register.filter(name="markdownify")
def markdownifyFilter(texte):
	texte = str(texte)
	texte = BeautifulSoup(texte,"lxml").text
	texte = markdownify(texte)
	return texte

@register.filter(name="menumessagerie")
def menumessagerie(path):
	a = path.split("/")
	if a[1] == "messages":
		return 'class="active"'
	else:
		return ""
