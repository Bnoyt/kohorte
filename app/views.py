from .models import *
from bs4 import *
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify
from notify.signals import notify

from django.shortcuts import render, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.core.urlresolvers import reverse

from django.template import loader

from django.contrib.auth.models import User

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
        
        projSuivis = [r.noeud.question for r in RelationUserSuivi.objects.filter(user=user)]        
        printRecap = [recapProjet(q, user.user) for q in list(set(projSuivis))]
        
        context['user'] = user
        context['printRecap'] = printRecap
        projSuivis = [r.noeud.question for r in RelationUserSuivi.objects.filter(user=user)]
        if len(projSuivis)==1:
            context['whatsUpId'] = projSuivis[0]
        
    else:
        #TODO: handle unlogged user
        pass

    return render(request, 'index.html', context)

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

def postsDescendants(postPere, node, user):
    return [(p, postsDescendants(p, node, user), aVote(user, p)) for p in Post.objects.filter(pere=postPere).filter(noeud=node)]

def aVote(user, p):
  """renvoie les infos de vote pour un user et un post donné, pour tous les types de votes."""
  return {tVote.label:Vote.objects.filter(voteur=user.user).filter(post=p).filter(typeVote=tVote).exists() for tVote in TypeVote.objects.all()}


def noeud(request,noeud_id):
    if request.user.is_authenticated:
        noeud = get_object_or_404(Noeud,pk=noeud_id)
        postPeres = Post.objects.filter(noeud=noeud,pere=None)
        user = get_object_or_404(Utilisateur,user=request.user)
        
        posts = [(p, postsDescendants(p, noeud, user), aVote(user, p)) for p in postPeres] #les descendants des postsPere encore dans le noeud.


        #pour la navigation entre les noeuds dans l'alpha
        noeudsFamille = [(parente.ideeSource, [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = parente.ideeSource)]) for parente in AreteReflexion.objects.filter(ideeDest = noeud)]
        noeudsFils = [a.ideeDest for a in AreteReflexion.objects.filter(ideeSource = noeud)]
        noeudsAncetres = ancetres(noeud)

        citations = [c for c in Citation.objects.filter(rapporteur=user) if c.post.question==noeud.question]

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
            'noeudsAncetres': noeudsAncetres,
            'whatsUpId': noeud.question.id,
            
        }
        return render(request,'noeud.html',context)
    else:
        return HttpResponseRedirect(reverse('index'))
        
def whatsup(request, project_id):
    if request.user.is_authenticated:
        user = get_object_or_404(Utilisateur,user=request.user)
        question = get_object_or_404(Question, id=project_id)
    
        sugg = Suggestion.objects.filter(userVise=user).order_by('-pertinence')    #.filter(objet.question=project_id)
        suggPrint = [recapNoeud(s.objet, user.user) for s in sugg]
    
        noeudsSuivis = [r.noeud for r in RelationUserSuivi.objects.filter(user=user) if r.noeud.question == question]
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
            tags = trouver_hashtags(post['contenu'])

            p = Post(titre=post['titre'],contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
            p.save()
            
            for tag in tags:
                t = Tag.objects.filter(label=tag).filter(question=question)
                if len(t) == 0:
                    t = Tag(label = tag, question=question)
                    t.save()
                else:
                    t = t[0]
                p.tags.add(t)
            
            

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
            #gm = GraphModifier.GraphModifier.get(question.id) #TODO gm
            noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
            auteur = get_object_or_404(Utilisateur,user=request.user)
            pere= get_object_or_404(Post,pk=post['pere'].split('_')[1])
            c = Post(pere=pere,contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
            c.save()
            #gm.create_post(p.id, noeud.id, [t.id for t in p.tags], author.id, p.contenu.len(), p.pere.id)
            template = loader.get_template('commentaire.html')
            context={'c':[c,[]]
            }
            publication = template.render(context,request)
            notify.send(request.user, recipient=pere.auteur.user, actor=request.user, verb='a commenté votre message.', nf_type='answer')
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
            #gm = GraphModifier.GraphModifier.get(question.id) #TODO gm
            noeud = get_object_or_404(Noeud,pk=int(post['id_noeud']))
            auteur = get_object_or_404(Utilisateur,user=request.user)
            pere= get_object_or_404(Post,pk=post['pere'].split('_')[1])
            r = Post(pere=pere,contenu=post['contenu'],question=question,noeud=noeud,auteur=auteur)
            r.save()
            #gm.create_post(p.id, noeud.id, [t.id for t in p.tags], author.id, p.contenu.len(), p.pere.id)
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
        #gm = GraphModifier.get(publication.question.id) TODO gm
        rapporteur = get_object_or_404(Utilisateur,user=request.user)
        c = Citation(auteur=publication.auteur,post=publication,contenu=contenu,rapporteur=rapporteur)
        #create_quote(publication.id, rapporteur.id) TODO gm
        c.save()
        template = loader.get_template('citation.html')
        context={'citation':'{{' + str(c.id) + '}}'}
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
                'titre_page_':'Profil',
                'whatsUpId':whatsUpId
    
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
    if request.user.is_authenticated:
        q = get_object_or_404(Question, id=project_id)
        t = get_object_or_404(Tag,label=hashtag,question=q)
        
        posts = t.postTagues()

        context = {'posts':posts}


        
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
