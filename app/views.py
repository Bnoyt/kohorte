from .models import *

from django.shortcuts import render, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.core.urlresolvers import reverse

from django.template import loader

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
		context['etat_connexion'] = True
		context['titre_page'] = 'Se connecter'
		# Return an 'invalid login' error message.
		return render(request,'login.html',context)


def page_login(request):
	if request.user.is_authenticated:
		logout(request)
	if 'username' in request.POST:
		return authentification(request)
	else:
		context={'titre_page': 'Se connecter'}
		context['etat_connexion'] = False
		return render(request, 'login.html',context)

def page_register(request):
	context = {}
	if request.user.is_authenticated:
		return render(request, 'content_index.html', context)
	post = request.POST
	if 'username' in post and 'email' in post and 'prenom' in post and 'nom' in post and 'mdp' in post:
		if User.objects.filter(email=post['email']).exists() or User.objects.filter(username=post['username']).exists():

			context['message'] = "L'email ou le pseudo spécifié existe déjà"
			return render(request, 'register.html', context)
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
		return render(request, 'register.html', context)

def index(request):
    #call database
    context = {}
    if request.user.is_authenticated:
        user = get_object_or_404(Utilisateur, user=request.user)
        context['user'] = user
    else:
        #TODO: handle unlogged user
        pass

    return render(request, 'index.html', context)


def noeud(request,noeud_id):
	if request.user.is_authenticated:
		noeud = get_object_or_404(Noeud,pk=noeud_id)
		post = Post.objects.filter(noeud=noeud,pere=None)
		

		posts = [[p,[[c,[r for r in Post.objects.filter(pere=c)]] for c in Post.objects.filter(pere=p)]] for p in post]

		context = {
			'posts': posts,	
			'noeud':noeud,
			'question':noeud.question,		
		}
		return render(request,'noeud.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))


def parametres(request):
	if request.user.is_authenticated:
		context={
		'titre_page':'Paramètres',
		}
		return render(request,'parametres.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))


def ajouter_post(request):
	if request.user.is_authenticated:
		post = request.POST

		publication="rien"

		if post['titre'] != '' and post['contenu'] != '':
			texte = "succes"
			question = get_object_or_404(Question,pk=int(post['id_question']))
			noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
			auteur = get_object_or_404(Utilisateur,user=request.user)
			p = Post(titre=post['titre'],contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
			p.save()
			template = loader.get_template('post.html')
			context={'p':[p,[]]
			}
			publication = template.render(context,request)
		elif post['titre'] == '' and post['contenu'] == '':
			texte ="riendutout"
		elif post['titre'] == '':
			texte ='titre'
		else:
			texte = 'pasdecontenu'


		return JsonResponse({'texte':texte,'post':publication})
	else:
		return JsonResponse({"texte":"vafanculo",'post':'arrete gros'})