from .models import *
from .forms import *
from bs4 import *
from django.utils.safestring import mark_safe
from django.utils.encoding import uri_to_iri
from markdownx.utils import markdownify
from notify.signals import notify

from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import loader
from django.contrib.auth.models import User
from django.core.mail import send_mail

from app.backend.api import GraphModifier as GraphModifier


MAIL_DEV = ['alice.andres+django@polytechnique.edu']


def tri_anatole(votes,importance,vieillesse):
    return vieillesse


def trouver_hashtags(texte):
    #utiliser regex
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
        user = User.objects.get(username = request.POST['username']).utilisateur
        if not user.ban:
            return authentification(request)
        else:
            context={'titre_page': 'Se connecter', 'etat_connexion' : False, 'notif':"Votre compte a été désactivé par un modérateur"}
            return render(request, 'login.html',context)
    else:
        context={'titre_page': 'Se connecter', 'etat_connexion' : False}
        return render(request, 'login.html',context)

def page_register(request):
    context = {}
    if request.user.is_authenticated:
        return redirect(index)
    post = request.POST
    if 'username' in post and 'email' in post and 'mdp' and 'mdp2' in post:
        if User.objects.filter(email=post['email']).exists() or User.objects.filter(username=post['username']).exists():

            context['message'] = "L'email ou le pseudo spécifié existe déjà"

            return render(request, 'register.html', context)
        else:
            if post["mdp"] != post["mdp2"]:
                context['message'] = "Inscrivez vous gratuitement sur Agorado et participez à la première plateforme d'intelligence collective en France"
                context["notif"] = "Les deux mots de passe ne correspondent pas"
                return render(request, 'register.html', context)

            user = User.objects.create_user(post['username'],post['email'],post['mdp'])
            personne = Utilisateur(user=user)
            personne.save()
            login(request,user)
            return HttpResponseRedirect(reverse('index'))
    else:
        context['message'] = "Inscrivez vous gratuitement sur Agorado et participez à la première plateforme d'intelligence collective en France"
        if "csrfmiddlewaretoken" in post:
            context["notif"] = "Vous avez oublié de remplir un champ !"
        return render(request, 'register.html', context)

def index(request):
    #call database
    context = {'whatsUpId':-1}
    if request.user.is_authenticated:
        user = get_object_or_404(Utilisateur, user=request.user)
        types_suivi_reel = TypeSuivi.objects.filter(actif=True)
        
        projSuivis = [r.noeud.question for r in RelationUserSuivi.objects.filter(user=user,type_suivi__in=types_suivi_reel)]        
        printRecap = [recapProjet(q, user.user) for q in list(set(projSuivis))]
        
        context['user'] = user
        context['printRecap'] = printRecap
        
        if len(projSuivis)==1:
            context['whatsUpId'] = projSuivis[0]
            return redirect(whatsup, projSuivis[0].id)
        else:
            return render(request, 'index.html', context)
        
    else:
        return redirect(page_login)
    pass

def recapProjet(question, user):
    nbPosts = Post.objects.filter(question=question).count()
    nbNewPosts = Post.objects.filter(question=question).filter(date__gt=user.last_login).count()
    nbNoeuds = Noeud.objects.filter(question=question).count()
    nbNewNoeuds = Noeud.objects.filter(question=question).filter(date__gt=user.last_login).count()
    return (question, nbPosts, nbNewPosts, nbNoeuds, nbNewNoeuds)
    

def ancetres(noeud):
    l = [parente.ideeSource for parente in AreteReflexion.objects.filter(ideeDest = noeud)]
    res = []
    while len(l) > 0:
        n = l[0]
        res = [n] + res
        l = [parente.ideeSource for parente in AreteReflexion.objects.filter(ideeDest = n)]
    return res


def tripost(p):
    """p est de type (Post; enfants, votes)"""
    votes = len(Vote.objects.filter(post=p[0]))
    importance = p[0].importance
    vieillesse = p[0].date.timestamp()
    return tri_anatole (votes,importance,vieillesse)

def postsDescendants(postPere, node, user):
    return sorted([(p, postsDescendants(p, node, user), aVote(user, p)) for p in Post.objects.filter(pere=postPere).filter(noeud=node)], key=tripost)

def aVote(user, p):
  """renvoie les infos de vote pour un user et un post donné, pour tous les types de votes."""
  return {tVote.label:Vote.objects.filter(voteur=user.user).filter(post=p).filter(typeVote=tVote).exists() for tVote in TypeVote.objects.all()}


def noeud(request,noeud_id):
    if request.user.is_authenticated:
        #elements de contexte
        noeud = get_object_or_404(Noeud,pk=noeud_id)
        postPeres = Post.objects.filter(noeud=noeud,pere=None)
        user = get_object_or_404(Utilisateur,user=request.user)
        
        context = {}
        
        #ajouter_post
        form = PostForm(request.POST or None)
        if form.is_valid():
            texte = "succes"
            p = form.save(commit = False)
            p.question = noeud.question
            p.noeud = noeud
            p.auteur = get_object_or_404(Utilisateur,user=request.user)
            p.save()
            form = PostForm(None)
            
            include_tags(request.POST, p)

            context['notif'] = "Votre message a été publié"
            context['notifType'] = "success"
            
            #on passe à l'affichage
            request.POST = {}
            #template = loader.get_template('post.html')
            #contextPost={'p':[p,[]]}
            #publication = template.render(contextPost,request)
        
        else:
            texte = 'pasdecontenu'
        context['form'] = form
        #fin ajouter_post
        
        #calcul de l'affichage
        posts = [(p, postsDescendants(p, noeud, user), aVote(user, p)) for p in postPeres] #les descendants des postsPere encore dans le noeud.

        #pour la navigation entre les noeuds dans l'alpha
        noeudsFamille = [(parente.ideeSource, [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = parente.ideeSource)]) for parente in AreteReflexion.objects.filter(ideeDest = noeud)]
        noeudsFils = [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = noeud)]
        noeudsAncetres = ancetres(noeud)

        citations = [c for c in Citation.objects.filter(rapporteur=user) if c.post.question==noeud.question]

        suivi = TypeSuivi.objects.filter(actif=True)
        suivi=RelationUserSuivi.objects.filter(noeud_id=noeud_id,user = user,type_suivi__in=suivi).exists()
        
        ideesTag = Tag.objects.filter(question=noeud.question)[:5]
        
        estModo = noeud.question in user.projetModo.all()


        
        context.update({
            'suivi':suivi,
            'dashboard':True,
            'posts': posts,    
            'noeud':noeud,
            'question':noeud.question,    
            'titre_page':'Noeud : ' +  noeud.label,
            'citations':["{{" + str(i.id) + "}}" for i in citations],
            'vraiCitation':citations,
            'noeudsFamille':noeudsFamille,
            'noeudsFils':noeudsFils,
            'noeudsAncetres': noeudsAncetres,
            'whatsUpId': noeud.question.id,
            'nouveau_nom':True,
            'utilisateur':user,
            'ideesTag':ideesTag,
            'estModo':estModo,
        })
        
               
        #ajouter_post(request)
        
        return render(request,'noeud.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))
        
def whatsup(request, project_id):
    if request.user.is_authenticated:
        user = get_object_or_404(Utilisateur,user=request.user)
        question = get_object_or_404(Question, id=project_id)
    
        sugg = Suggestion.objects.filter(userVise=user).order_by('-pertinence')    #.filter(objet.question=project_id)
        suggPrint = [recapNoeud(s.objet, user.user) for s in sugg]
    
        types_suivi_reel = TypeSuivi.objects.filter(actif=True)
        noeudsSuivis = [r.noeud for r in RelationUserSuivi.objects.filter(user=user,type_suivi__in=types_suivi_reel) if r.noeud.question == question]
        posts = [(p, [], aVote(user, p)) for p in Post.objects.filter(noeud__in=noeudsSuivis, question=project_id)]
        
        printRecap = [recapNoeud(n, user.user) for n in noeudsSuivis]
        
        
        context = {
            'user':user,
            'listSugg': sugg,
            'whatsup':True,
            'printSugg':suggPrint,
            'printRecap':printRecap,
            'titre_page': question.label,
            'posts': posts,
            'whatsUpId':question.id

        }
        


        return render(request,'whatsUp.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))

def recapNoeud(noeud, user):
    nbPosts = Post.objects.filter(noeud=noeud).count()
    nbNewPosts = Post.objects.filter(noeud=noeud).filter(date__gt=user.last_login).count()
    fils = [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = noeud)]
    return (noeud, nbPosts, nbNewPosts, fils)

def suggestions(request):
    if request.user.is_authenticated:
        user = get_object_or_404(Utilisateur,user=request.user)
        listSugg = Suggestions.objects.filter(userVise = user).order_by(-pertinence)
        context = {
            'user':user,
            'listSugg':listSugg,
            }
        return render(request, 'suggestions.html', context)
    else:
        return redirect(index)


def parametres(request):
    if request.user.is_authenticated:
        context={
        'titre_page':'Paramètres',
        }
        return render(request,'parametres.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))
        
def include_tags(postHTTP, post):
  tags_list_texts = trouver_hashtags(postHTTP['contenu'])
  
  for tag_text in tags_list_texts:
      tags_query = Tag.objects.filter(label=tag_text).filter(question=post.question)
      if len(tags_query) == 0:
          tag_object = Tag(label = tag_text, question=post.question)
          tag_object.save()
      else:
          tag_object = tags_query[0]
      if tag_object not in post.tags.all():
          post.tags.add(tag_object)
  pass


def ajouter_post(request):
    
    if request.user.is_authenticated:
        post = request.POST

        publication="rien"
        
        form = PostForm(post)
        if form.is_valid():
            texte = "succes"
            p = form.save(commit = False)
            p.question = get_object_or_404(Question,pk=int(post['id_question']))
            p.noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
            p.auteur = get_object_or_404(Utilisateur,user=request.user)
            p.save()
            
            include_tags(post, p)

            #on passe à l'affichage
            template = loader.get_template('post.html')
            context={'p':[p,[]]
            }
            publication = template.render(context,request)
        
        else:
            texte = 'pasdecontenu'

        '''
        if post['titre'] != '' and post['contenu'] != '':
            texte = "succes"
            question = get_object_or_404(Question,pk=int(post['id_question']))
            noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
            auteur = get_object_or_404(Utilisateur,user=request.user)

            p = Post(titre=post['titre'],contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
            p.save()
            
            include_tags(post, p)
            
            

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
            '''


        return JsonResponse({'texte':texte,'post':publication})
    else:
        return JsonResponse({"texte":"vafanculo",'post':'arrete gros'})

def epingler(request):
    if request.user.is_authenticated:
        post = request.POST




        return JsonResponse({'texte':texte,'post':publication})
    else:
        return JsonResponse({"texte":"vafanculo",'post':'arrete gros'})

def delete_message(request):
    if request.user.is_authenticated:
        post = request.POST

        publication="rien"

        texte = "succes"
        postToDelete = get_object_or_404(Post,pk=post['idPostToDelete'])
        question = postToDelete.question
        noeud = postToDelete.noeud
        auteur = postToDelete.auteur
        if request.user == auteur.user or question in request.user.all():
            postToDelete.disabled = True
            postToDelete.save()
					
            if request.user != postToDelete.auteur.user:
                #dans ce cas c'est un modérateur qui a effectué la modification
                notify.send(request.user, recipient=postToEdit.auteur.user, actor=request.user, verb='supprimé', target=postToEdit, nf_type='modo')

            #gm : modifier post
            template = loader.get_template('commentaire.html')
            context={'c':(postToDelete,[], {})}
            publication = template.render(context,request)


        return JsonResponse({'texte':texte,'post':publication,'id_postDeleted':postToDelete.id})
    else:
        return JsonResponse({"texte":"vafanculo",'post':'arrete gros','id_pere':'consternant'})
        
def edit_message(request):
    if request.user.is_authenticated:
        post = request.POST

        publication="rien"

        texte = "succes"
        question = get_object_or_404(Question,pk=int(post['id_question']))
        noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
        auteur = get_object_or_404(Utilisateur,user=request.user)
        if request.user == auteur.user or question in request.user.all():
                postToEdit = get_object_or_404(Post,pk=post['postToEdit'].split('_')[1])
                postToEdit.contenu = post['contenu']
                postToEdit.save()
				        
                if request.user != postToEdit.auteur.user:
                    #dans ce cas c'est un modérateur qui a effectué la modification
                    notify.send(request.user, recipient=postToEdit.auteur.user, actor=request.user, verb='édité', target=postToEdit, nf_type='modo')
			        
                    include_tags(post, postToEdit)
                    #gm : modifier post
                    template = loader.get_template('commentaire.html')
                    context={'c':(postToEdit,[], {})}
                    publication = template.render(context,request)
        else:
            texte = 'pasdecontenu'


        return JsonResponse({'texte':texte,'post':publication})
    else:
        return JsonResponse({"texte":"vafanculo",'post':'arrete gros','id_pere':'consternant'})


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
            
            include_tags(post, c)
            template = loader.get_template('commentaire.html')
            context={'p':(c,[], {})}
            publication = template.render(context,request)
            notify.send(request.user, recipient=pere.auteur.user, actor=request.user, target=pere, verb="répondu", nf_type='answer')
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
            
            include_tags(post, r)
            template = loader.get_template('reponse.html')
            context={'r':[r,[]] }
            publication = template.render(context,request)
            notify.send(request.user, recipient=pere.auteur.user, actor=request.user, verb="répondu", target=pere, nf_type='answer')
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
        question=publication.question
        template = loader.get_template('citation.html')
        context={'citation':'{{' + str(c.id) + '}}',"question":question}
        contenu = template.render(context,request)

        return JsonResponse({'contenu':contenu,'id_citation':c.id})
    else:
        return JsonResponse({"contenu":"vafanculo",'id_citation':42})


def faq(request):
    context={'faq':True, 'whatsUpId':-1}
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur,user=request.user)
        user = utilisateur.user
        projSuivis = [r.noeud.question for r in RelationUserSuivi.objects.filter(user=user)]
        if len(projSuivis)==1:
            context['whatsUpId'] = projSuivis[0].id
     
    return render(request,'faq.html',context)


def profil(request) :
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur,user=request.user)
        user = utilisateur.user
            
        noeudsSuivis = [r.noeud for r in RelationUserSuivi.objects.filter(user=utilisateur)]
        printRecap = [recapNoeud(n, user) for n in noeudsSuivis]
        
        projets=list(set([n.question for n in noeudsSuivis]))
        whatsUpId = (-1 if len(projets)!=1 else projets[0].id)
        
        posts = [(p, [], aVote(utilisateur, p)) for p in Post.objects.filter(auteur=utilisateur)]
            # a completer pour creer la liste des noeuds suivis aprs modification de la class "utilisateur" dans models.py
            #type_suivi=get_object_or_404(TypeSuivi,pk=1)
    
        context = {
                'user':utilisateur,
                'printRecap': printRecap,
                'profil':True,
                'posts':posts,
                'noeudsSuivis':noeudsSuivis,
                'titre_page':'Profil',
                'whatsUpId':whatsUpId,
                'GENRES':Utilisateur.GENRES,
            }
            
        post = request.POST
        
        if ('username' in post and user.username != post['username']) or \
        ('email' in post and  user.email != post['email']) or \
        ('mdp' in post or 'mdp2' in post and len(post['mdp']) > 0):
                if 'mdpOld' in post and user.check_password(post['mdpOld']):
                    if 'username' in post and user.username != post['username']:
                        if User.objects.filter(username=post['username']).exists():
                            context['notif'] = "Ce nom d'utilisateur est déjà pris"
                        else:
                            user.username = post['username']
                            user.save()
                    if 'email' in post and user.email != post['email']:
                        if User.objects.filter(email=post['email']).exists():
                            context['notif'] = "Cette adresse mail est déjà prise"
                        else:
                            user.email = post['email']
                            user.save()
                    if 'mdp' in post and post['mdp'] != "":
                        if 'mdp2' in post and post['mdp2']==post['mdp']:
                            user.set_password(post['mdp'])
                            user.save()
                        else:
                            context['notif'] = "Veuillez confirmer votre nouveau mot de passe"
                else:
                    context['notif']="Veuillez entrer votre mot de passe actuel pour valider la modification"
    

        return render(request,'profil.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))    
    
    
def hashtags(request,project_id,hashtag):
    #hashtag = uri_to_iri(hashtag) #les caracteres speciaux etaient transformes
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur, user=request.user)
        q = get_object_or_404(Question, id=project_id)
        t = get_object_or_404(Tag,label=hashtag,question=q)
        
        posts = [(p, [], aVote(utilisateur, p)) for p in  t.postTagues()]

        context = {
        'posts':posts,
        'titre_page' : "#" + t.label,
        }


        
        return render(request,'hashtags.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))

def suivi_noeud(request):
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur,user = request.user)
        post = request.POST
        type_suivi_simple = get_object_or_404(TypeSuivi, label="suivi simple")
        type_suivi_unactivated = get_object_or_404(TypeSuivi, label="post puis unfollow")
        types_suivi_reel = TypeSuivi.objects.filter(actif=True)
        noeud = get_object_or_404(Noeud,pk = int(post["id_noeud"]))
        if post["type"] == "suivre" and not (RelationUserSuivi.objects.filter(user=utilisateur,noeud=noeud,type_suivi__in=types_suivi_reel).exists()):
            if (RelationUserSuivi.objects.filter(user=utilisateur,noeud=noeud).exclude(type_suivi__in= types_suivi_reel).exists()):
                relation_suivi = get_object_or_404(RelationUserSuivi,user=utilisateur, noeud=noeud, type_suivi = type_suivi_unactivated)
                relation_suivi.type_suivi = type_suivi_simple
                relation_suivi.save()
            else:
                relation_suivi = RelationUserSuivi(noeud=noeud,type_suivi=type_suivi_simple,user=utilisateur)
                relation_suivi.save()
        elif post["type"] == "desuivre" and (RelationUserSuivi.objects.filter(user=utilisateur,noeud=noeud).exists()):
            relation_suivi = get_object_or_404(RelationUserSuivi,noeud=noeud,user=utilisateur)
            relation_suivi.type_suivi = type_suivi_unactivated
            relation_suivi.save()
        return JsonResponse({})
    else:
        return JsonResponse({})

def vote(request):
    if request.user.is_authenticated:
        utilisateur = get_object_or_404(Utilisateur,user = request.user)
        user = utilisateur.user
        post = request.POST
        type_vote = get_object_or_404(TypeVote, label=post['typeVote'])
        idPostVote = post["post"]#.split("-")[1] #post['post'] de la forme "id-%n"
        postVote = get_object_or_404(Post,pk = idPostVote)
        if post["type"] == "vote" and not(Vote.objects.filter(typeVote=type_vote, post=postVote, voteur=user).exists()):
            vote = Vote(typeVote=type_vote, post=postVote, voteur=user)
            vote.save()
        elif post["type"] == "unvote":
            vote = get_object_or_404(Vote,typeVote=type_vote, post=postVote, voteur=user)
            vote.delete()
        return JsonResponse({})
    else:
        return JsonResponse({})

def posts_signales(request, project_id):
    if request.user.is_authenticated: #plus tard il faudra que l'utilisateur soit modo ou admin
        utilisateur = get_object_or_404(Utilisateur,user = request.user)
        user = utilisateur.user
        question = get_object_or_404(Question,pk=int(project_id))
        if question in utilisateur.projetModo.all():
            type_signal = get_object_or_404(TypeVote, label='signal')
            signalements = Vote.objects.filter(typeVote = type_signal).select_related('post')
            posts = [v.post for v in signalements if v.post.question == question]
            postsToPrint = [(p, [], aVote(utilisateur, p)) for p in posts]
                
            context = {
                    'user':utilisateur,
                    'posts': postsToPrint,
                    'titre_page':'Posts signalés',
                    'whatsUpId':question.id,
                }
            return render(request, 'modo/posts_signales.html', context)
        else:
            return HttpResponseRedirect(reverse('index'))

def inconstruct(request):
    #call database
    context = {'page_propos':True}

    return render(request, 'inconstruct.html', context)

def signaler_bug(request):
    form = BugForm(request.POST or None)
    if form.is_valid():
        sujet = form.cleaned_data['sujet']
        message = form.cleaned_data['message']
        #TODO envoyer mail aux dev
        send_mail(
          '[BUG_REPORT]' + sujet,
          message,
          'alice.andres@m4x.org',
          MAIL_DEV,
          fail_silently=False)
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'signaler_bug.html', locals())

def modo_ban_user(request, project_id):
	projet = Question.objects.get(pk=project_id)
	listeNoeuds = Noeud.objects.filter(question=projet)
	listeRel = RelationUserSuivi.objects.filter(noeud__in=listeNoeuds)
	listeUser = [r.user for r in listeRel]
	context = {
		'titre_page' : "Liste d'utilisateurs",
		'listeUser' : listeUser,
		}
	return render(request, 'modo_ban_user.html')
		
