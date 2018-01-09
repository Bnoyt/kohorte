from .models import *
from bs4 import *
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify

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
    context = {'dashboard':True}
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
		user = get_object_or_404(Utilisateur,user=request.user)
		
		posts = [[p,[[c,[r for r in Post.objects.filter(pere=c)]] for c in Post.objects.filter(pere=p)]] for p in post]

		citations = Citation.objects.filter(rapporteur=user)

		context = {
			'dashboard':True,
			'posts': posts,	
			'noeud':noeud,
			'question':noeud.question,	
			'titre_page':'Noeud : ' +  noeud.label,
			'citations':["{{" + str(i.id) + "}}" for i in citations],
			'citation' : """<blockquote>
                             <p>
                             Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam.
                             </p>
                             <small>
                             Steve Jobs, CEO Apple
                             </small>

                            </blockquote>
                            <pre class="prettyprint">class Voila {
							public:
  							// Voila
  							static const string VOILA = "Voila";

  							// will not interfere with embedded <a href="#voila2">tags</a>.
							}</pre>





                            """,

		}
		return render(request,'noeud.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))
		
def whatsup(request):
	if request.user.is_authenticated:
		user = get_object_or_404(Utilisateur,user=request.user)
		sugg = Suggestion.objects.filter(userVise=user).order_by('-pertinence')
		
		context = {
			'user':user,
			'listSugg': sugg,
			'whatsup':True,

		}
		return render(request,'whatsUp.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))

def suggestions(request):
	if request.user.is_authenticated:
		user = get_object_or_404(Utilisateur,user=request.user)
		listSugg = Suggestions.objects.filter(userVise = user).order_by(-pertinence)
		context = {
			'user':user,
			'listSugg':listSugg,
			}
		return render(request, 'suggestions.html', context)


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

def epingler(request):
	if request.user.is_authenticated:
		post = request.POST




		return JsonResponse({'texte':texte,'post':publication})
	else:
		return JsonResponse({"texte":"vafanculo",'post':'arrete gros'})

def ajouter_commentaire(request):
	if request.user.is_authenticated:
		post = request.POST

		publication="rien"

		if post['contenu'] != '':
			texte = "succes"
			question = get_object_or_404(Question,pk=int(post['id_question']))
			noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
			auteur = get_object_or_404(Utilisateur,user=request.user)
			pere= get_object_or_404(Post,pk=post['pere'].split('_')[1])
			c = Post(pere=pere,contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
			c.save()
			template = loader.get_template('commentaire.html')
			context={'c':[c,[]]
			}
			publication = template.render(context,request)
		else:
			texte = 'pasdecontenu'


		return JsonResponse({'texte':texte,'post':publication,'id_pere':post['pere']})
	else:
		return JsonResponse({"texte":"vafanculo",'post':'arrete gros','id_pere':'consternant'})

def ajouter_reponse(request):
	if request.user.is_authenticated:
		post = request.POST

		publication="rien"

		if post['contenu'] != '':
			texte = "succes"
			question = get_object_or_404(Question,pk=int(post['id_question']))
			noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
			auteur = get_object_or_404(Utilisateur,user=request.user)
			pere= get_object_or_404(Post,pk=post['pere'].split('_')[1])
			r = Post(pere=pere,contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
			r.save()
			template = loader.get_template('reponse.html')
			context={'r':[r,[]]
			}
			publication = template.render(context,request)
		else:
			texte = 'pasdecontenu'


		return JsonResponse({'texte':texte,'post':publication,'id_pere':post['pere']})
	else:
		return JsonResponse({"texte":"vafanculo",'post':'arrete gros','id_pere':'consternant'})

def sauvegarder_citation(request):
	if request.user.is_authenticated:
		post = request.POST

		contenu = post['contenu']
		publication = get_object_or_404(Post,pk = int(post['id_post']))
		rapporteur = get_object_or_404(Utilisateur,user=request.user)
		c = Citation(auteur=publication.auteur,post=publication,contenu=contenu,rapporteur=rapporteur)
		c.save()
		template = loader.get_template('citation.html')
		context={'citation':'{{' + str(c.id) + '}}'}
		contenu = template.render(context,request)

		return JsonResponse({'contenu':contenu,'id_citation':c.id})
	else:
		return JsonResponse({"contenu":"vafanculo",'id_citation':42})


def faq(request):
	context={'faq':True}

	return render(request,'faq.html',context)