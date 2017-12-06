


#######################

# -*- coding: utf-8 -*-
#a deplacer dans le dossier idouane
from django.db import models
import datetime

from django.contrib.auth.models import User



# Create your models here.

class Utilisateur(models.Model):

    """
    Classe de définition d'un utilisateur. J'ai défini 3 types de droits. Admin est le plus haut niveau (le notre)
    Questionneur ce sera pour les gens qui veulent poser des questions par exemple (Pourquoi pas leur donner un tableau de bord de leurs questions)
    Contributeur ce sera pour toutes les autres personnes, celles qui répondent aux questions

    """


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DROITS = (
        ('0', 'admin'),
        ('1', 'questionneur'),
        ('2', 'contributeur'),
    )
    profil = models.CharField(max_length=1, choices=DROITS, default='2')

    def __unicode__(self):
        return self.user.__unicode__() + u' -> ' + self.profil


class Question(models.Model):
    label = models.CharField(max_length=300)
    auteur = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.label + u' => ' + self.auteur.__unicode__() + u' => ' + self.date.__unicode__()

class Noeud(models.Model):
    """Classe qui contient à la fois les noeuds pb et les noeuds idee (c'est plus simple)
    Ne contient pour l'instant que le label et une méthode
    TODO détailler les attentes de la classe Noeud (2017-11-22)
    """
    TYPE_NOEUD =  (
        ('0', 'idee'),
        ('1', 'probleme'),
    )
    type_noeud = models.CharField(max_length=1, choices=TYPE_NOEUD)
    label = models.CharField(max_length = 30)
    question = models.ForeignKey(Question,related_name="Questiondebase")
    #valeur de max_length choisie arbitrairement
    
    def recupPosts():
        """Permet d'accéder rapidement à l'ensemble des 
        posts de cette discussion. 
        TODO La relation entre Noeud et Post n'a pas 
        encore ete etablie (2017-11-22)
        TODO aux posts de cette discussion et de ses noeuds
        fils récursivement ou uniquement de celle-là ?
        (2017-11-22)
        TODO Qu'est-ce qui est différent entre les sous-classes
        NoeudIdee et NoeudPb qui justifie leur (prudente)
        existence ? (2017-11-22)
        Je suis d'accord ça n'est pas vraiment justifié

        """
        pass

    def __unicode__(self):
        return self.type_noeud + u' => ' + self.label + u' => ' + self.question

    
class PostVersionne(models.Model):
    """Le post versionné est présent dans chaque fil de discussion
    /noeud. Il doit pouvoir etre modifié par les utilisateurs,
    tout en gardant une trace des résultats précédents
    XXX : s'appuyer sur un système type git pour le versionner
    en backend ?"""
    contenu = models.TextField()
    contributeurs = models.ManyToManyField(User, )
    noeud = models.ForeignKey(Noeud)

    def __unicode__(self):
        return self.noeud.__unicode__() + u' => Post versioné'
    


    
class TypeArete(models.Model):
    """TypeArrete permet d'englober les types d'arrete du
    graphe de reflexion, dont on ne sait pas encore grand 
    chose (2017-11-22)"""
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement

    def __unicode__(self):
        return self.label


class AreteReflexion(models.Model):
    """Ce sont les arretes du graphe de reflexion, 
    celles qui sont visibles par les utilisateurs"""
    ideeSource = models.ForeignKey(Noeud, related_name='source')
    ideeDest = models.ForeignKey(Noeud, related_name='dest')
    typeArete = models.ForeignKey(TypeArete,related_name="TypeArete")
    
    def __unicode__(self):
        return self.ideeSource.label + ' => ' +  self.ideeDest.label  + u' : ' + self.typeArete.label


class Tag(models.Model):
    """Element qui relie des posts entre eux.
    Important car joue sur les arretes du grand graphe
    et/ou sur sa métrique"""
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement
    
    def postTagues(self):
        """renvoie un querySet (quelque soit son
        implementation) de posts tagués par un tag 
        particulier."""
        return self.posts_lies.all()

    def __unicode__(self):
        return self.label




class Citation(models.Model):
    """Element qui relie des utilisateurs, et un post entre
    eux. Important car joue sur les arretes du grand graphe
    et/ou sur sa métrique"""
    auteur = models.ForeignKey(User, related_name='userAuteur')#TODO user comme nom ?
    post = models.ForeignKey('Post', related_name='postSource') 
    #j'utilise le nom de la classe car elle est définie après,
    #comme indiqué dans la documentation
    rapporteur = models.ForeignKey(User, related_name='userRapporteur')

    def __unicode__(self):
        return self.rapporteur.user.__unicode__() + u' cite ' + self.auteur.user.__unicode__() + u' dans ' + self.post.label

class Post(models.Model):
    """Le post qui sera écrit et lu par des utilisateurs
    TODO choisir un langage de formatage du texte : 
    html ? bbCode ? autre ?. Il devra en outre traiter des 
    citations (2017-11-22)"""
    pere = models.ForeignKey('self', on_delete=models.CASCADE)
    titre = models.CharField(max_length=100)
    auteur = models.ForeignKey(Utilisateur)
    tag = models.ManyToManyField(Tag)
    contenu = models.TextField()
    citations = models.ManyToManyField(Citation, related_name='postsCites')
    date = models.DateTimeField(auto_now_add = True, auto_now = False)
    question = models.ForeignKey(Question,related_name="Question_de_base")
    noeud = models.ForeignKey(Noeud,related_name="Noeud")
    
    def insererCitation():
        """Transforme l'information qu'on a de l'user
        dans le contenu du post pour garder l'info de
        la citation"""
        pass

    def __unicode__(self):
        return self.titre + u' de ' + self.auteur.user.__unicode__()




class TypeVote(models.Model):
    """Permet de garder toute la généralité des types de
    votes.
    XXX j'ai choisi  de rajouter impact en pensant 
    qu'il aurait un intéret (A;2017-11-22)"""
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement
    impact = models.IntegerField()

    def __unicode__(self):
        return self.label + u' - ' + str(self.impact)

class Vote(models.Model):
    """Un vote permet est donné par un utilisateur à
    un post qui n'est pas de lui.
    TODO typeVote est ici une instance de la classe TypeVote
    pour permettre le plus de généralité possible, vérifier
    que c'est une solution pertinente et corriger sinon. 
    (2017-11-22)"""
    typeVote = models.ForeignKey(TypeVote)
    post = models.ForeignKey(Post)
    voteur = models.ForeignKey(User)

    def __unicode__(self):
        return self.typeVote.__unicode__() + u' sur ' + self.post.label + u' de ' + self.voteur.user.__unicode__()

class Reputation(models.Model):
    """est ensuite associée à chaque utilisateur
    TODO mettre en place une association 
    * avec les utilisateurs
    * avec les votes
    * avec les citation ?(2017-11-22)
    Pour l'instant très mal définie"""
    user = models.OneToOneField(Utilisateur)
    puissance = models.IntegerField()

    def __unicode__(self):
        return self.user.user.__unicode__() + u' : ' + str(self.puissance)

class Suggestion(models.Model):
    """La suggestion est un outil très orienté utilisateur
    Il s'agit de relier un user et un noeud du graphe de 
    reflexion pour l'inciter, dans son interface, à aller
    voir ce dont il s'agit.
    Une suggestion sera le résultat du traitement du grand
    graphe."""
    userVise = models.ForeignKey(Utilisateur)
    objet = models.ForeignKey(Noeud)
    pertinence = models.IntegerField()

    def __unicode__(self):
        return self.userVise.user.__unicode__() + self.objet.label + str(self.pertinence)


class Log(models.Model):
    """on sait qu'on doit en faire un donc le voilà.
    Il permettra des traitements par la suite.
    """
    user = models.ForeignKey(Utilisateur)
    action = models.CharField(max_length = 100)
    date = models.DateTimeField(auto_now_add=True)
    #valeur de max_length choisie arbitrairement

    def __unicode__(self):
        return self.user.user.__unicode__() + self.action + u' - ' + self.date.__unicode__()

class TypeLienSg(models.Model):
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement

class lienPostsSgraphe(models.Model):
    """Sg pour supergraphe
    a pour objectif de faire le lien avec le supergraphe
    TODO definir le type de noeudSg1 et noeudSg2"""
    #noeudSg1
    #noeudSg2
    typeLien = models.ForeignKey(TypeLienSg)
    poids = models.IntegerField()






    
    
