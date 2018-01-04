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
			""" + a[0].post.auteur.user.username + """ le """ + (date.ctime()) + """ dans le noeud ***""" + a[0].post.noeud.label + """***
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

@register.filter(name="rendusafe",is_safe=True)
def rendusafe(texte):
	texte = str(texte)
	texte = BeautifulSoup(texte,"lxml").text
	texte = remplacer_citations(texte)
	texte = remplacer_code(texte)
	texte = markdownify(texte)
	return texte