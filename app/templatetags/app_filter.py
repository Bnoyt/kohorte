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
		print(a)
		if len(a) > 0:
			k = """<blockquote>
			<p>""" + BeautifulSoup(a[0].contenu).text + """
			</p>
			<small> 
			""" + a[0].auteur.user.username + """
			</small>
			</blockquote>"""
			texte = texte.replace(c,k)
	return texte



@register.filter(name="rendusafe",is_safe=True)
def rendusafe(texte):
	texte = BeautifulSoup(texte).text
	texte = remplacer_citations(texte)

	return markdownify(texte)