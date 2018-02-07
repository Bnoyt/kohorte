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

#import clustering.GraphModifier TODO l'import ne fonctionne pas

def trouver_hashtags(texte):
	n = len(texte)
	a = 0
	tags = []
	while a < n:
		if texte[a] == "#":
			tag = ""
			a += 1
			while a < n and texte[a] != " " and texte[a] !="#":
				tag += texte[a]
				a += 1
			tags.append(tag)
		else:
			a += 1
	return tags


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
	if 'username' in post and 'email' in post and 'mdp' and 'mdp2' in post:
		if User.objects.filter(email=post['email']).exists() or User.objects.filter(username=post['username']).exists():

			context['message'] = "L'email ou le pseudo spécifié existe déjà"

			return render(request, 'register.html', context)
		else:
			if post["mdp"] != post["mdp2"]:
				context['message'] = "Inscrivez vous gratuitement sur Kohorte et participez à la première plateforme d'intelligence collective en France"
				context["notif"] = "Les deux mots de passe ne correspondent pas"
				return render(request, 'register.html', context)

			user = User.objects.create_user(post['username'],post['email'],post['mdp'])
			personne = Utilisateur(user=user)
			personne.save()
			login(request,user)
			return HttpResponseRedirect(reverse('index'))
	else:
		context['message'] = "Inscrivez vous gratuitement sur Kohorte et participez à la première plateforme d'intelligence collective en France"
		if "csrfmiddlewaretoken" in post:
			context["notif"] = "Vous avez oublié de remplir un champ !"
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

		#pour la navigation entre les noeuds dans l'alpha
		noeudsFamille = [(parente.ideeSource, [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = parente.ideeSource)]) for parente in AreteReflexion.objects.filter(ideeDest = noeud)]
		noeudsFils = [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = noeud)]

		citations = Citation.objects.filter(rapporteur=user)

		suivi_simple = TypeSuivi.objects.filter(pk=1)
		suivi=RelationUserSuivi.objects.filter(noeud_id=noeud_id,user = user,type_suivi=suivi_simple).exists()

		context = {
			'suivi':suivi,
			'dashboard':True,
			'posts': posts,	
			'noeud':noeud,
			'question':noeud.question,	
			'titre_page':'Noeud : ' +  noeud.label,
			'citations':["{{" + str(i.id) + "}}" for i in citations],
			'noeudsFamille':noeudsFamille,
			'noeudsFils':noeudsFils,
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
	#gm = GraphModifier.GraphModifier.get(project_id)#TODO ou est project_id ?
	if request.user.is_authenticated:
		post = request.POST

		publication="rien"

		if post['titre'] != '' and post['contenu'] != '':
			texte = "succes"
			question = get_object_or_404(Question,pk=int(post['id_question']))
			noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
			auteur = get_object_or_404(Utilisateur,user=request.user)
			tags = trouver_hashtags(post['contenu'])

			p = Post(titre=post['titre'],contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
			p.save()
			for tag in tags:
				t = Tag.objects.filter(label=tag)
				if len(t) == 0:
					t = Tag(label = tag)
					#TODO gm.create_tag
					t.save()
				else:
					t = t[0]
				p.tags.add(t)
			
			#gm.create_post(p.id, noeud.id, [t.id for t in p.tags],  author.id, p.contenu.len(), p.pere)

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


def profil(request) :
    if request.user.is_authenticated:
        user = get_object_or_404(Utilisateur,user=request.user)
        sugg = Suggestion.objects.filter(userVise=user).order_by('-pertinence')
        posts = Post.objects.filter(auteur=user)
        # a completer pour creer la liste des noeuds suivis aprs modification de la class "utilisateur" dans models.py
        type_suivi=get_object_or_404(TypeSuivi,pk=1)

        noeudsSuivis = [r.noeud for r in RelationUserSuivi.objects.filter(user=user,type_suivi=type_suivi)]
        

        context = {
            'user':user,
            'listSugg': sugg,
            'profil':True,
            'posts':posts,
            'noeudsSuivis':noeudsSuivis

        }
        return render(request,'profil.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))
    
    
    
def hashtags(request,hashtag):
	if request.user.is_authenticated:

		context = {}


		
		return render(request,'hashtags.html',context)
	else:
		return HttpResponseRedirect(reverse('index'))

def suivi_noeud(request):
	if request.user.is_authenticated:
		utilisateur = get_object_or_404(Utilisateur,user = request.user)
		post = request.POST
		type_suivi = get_object_or_404(TypeSuivi, pk=1)
		noeud = get_object_or_404(Noeud,pk = int(post["id_noeud"]))
		if post["type"] == "suivre" and not(RelationUserSuivi.objects.filter(noeud=noeud,type_suivi=type_suivi,user=utilisateur).exists()):
			relation_suivi = RelationUserSuivi(noeud=noeud,type_suivi=type_suivi,user=utilisateur)
			relation_suivi.save()
		elif post["type"] == "desuivre":
			relation_suivi = get_object_or_404(RelationUserSuivi,noeud=noeud,type_suivi=type_suivi,user=utilisateur)
			relation_suivi.delete()
		return JsonResponse({})
	else:
		return JsonResponse({})