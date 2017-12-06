from .models import *

from django.shortcuts import render, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

def authentification(request):
	username = request.POST['username']
	password = request.POST['password']
	context = {}
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		# Redirect to a success page.
		return HttpResponseRedirect(reverse('index'))
	else:
		context['etat_connexion'] = 'pas_reussi'
		context['titre_page': 'Se connecter']
		# Return an 'invalid login' error message.
		return render(request,'app/login.html',context)


def page_login(request):
	if request.user.is_authenticated:
		logout(request)
	if 'username' in request.POST:
		return authentification(request)
	else:
		context={'titre_page': 'Se connecter'}
		context['etat_connexion'] = 'pasessaye'
		return render(request, 'app/login.html',context)

def page_register(request):
	context = {}
	if request.user.is_authenticated:
		return render(request, 'app/content_index.html', context)
	post = request.POST
	if 'username' in post and 'email' in post and 'prenom' in post and 'nom' in post and 'mdp' in post:
		if User.objects.filter(email=post['email']).exists() or User.objects.filter(username=post['username']).exists():
			
			context['message'] = "L'email ou le pseudo spécifié existe déjà"
			return render(request, 'app/register.html', context)
		else:
			user = User.objects.create_user(post['username'],post['email'],post['mdp'])
			user.first_name = post['prenom']
			user.last_name = post['nom']
			personne = Utilisateur(user=user)
			personne.save()
			login(request,user)
			return HttpResponseRedirect(reverse('index'))
	else:
		context['message'] = "Inscrivez vous gratuitement sur Kohorte et participez à la première plateforme d'intelligence collective en France"
		return render(request, 'app/register.html', context)

def index(request):
    context = {}
    return render(request, 'app/content_index.html', context)


def noeud(request,noeud_id):
	if request.user.is_authenticated:
		noeud = get_object_or_404(Noeud,pk=noeud_id)
		context = {
			'noeud': noeud,
			'titre_page': noeud.label + ' - ' + noeud.question.label,
		}
		return render(request,'app/noeud.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))


def parametres(request):
	if request.user.is_authenticated:
		context={
		'titre_page':'Paramètres',
		}
		return render(request,'app/parametres.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))