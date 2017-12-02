from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Utilisateur
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
		# Return an 'invalid login' error message.
		return render(request,'app/login.html',context)


def page_login(request):
	if request.user.is_authenticated:
		logout(request)
	if 'username' in request.POST:
		return authentification(request)
	else:
		context={}
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
