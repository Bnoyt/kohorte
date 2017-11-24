# -*- coding: utf-8 -*-
#a deplacer dans le dossier idouane
from __future__ import unicode_literals
from django.db import models
# Create your models here.

class User(models.Model):
    """FIXME Ce n'est qu'un classe creuse. Django est
    censé gérer les utilisateurs d'une manière ou d'une 
    autre (2017-11-22)"""
    
class PostVersionne(models.Model):
    """Le post versionné est présent dans chaque fil de discussion
    /noeud. Il doit pouvoir etre modifié par les utilisateurs,
    tout en gardant une trace des résultats précédents
    XXX : s'appuyer sur un système type git pour le versionner
    en backend ?"""
    contenu = models.TextField()
    contributeurs = models.ManyToManyField(User)
    
class Noeud(models.Model):
    """Classe générique dont héritent NoeudIdee et NoeudPb
    Ne contient pour l'instant que le label et une méthode
    TODO détailler les attentes de la classe Noeud (2017-11-22)
    """
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement
    postVersionne = models.OneToOneField(PostVersionne)
    
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
        existence ? (2017-11-22)"""
        pass

class NoeudIdee(Noeud):
    """Pour les éventuelles spécificités des noeuds idée"""
    pass

class NoeudPb(Noeud):
    """Pour les éventuelles spécificités des noeuds idée"""
    pass

    
class TypeArrete(models.Model):
    """TypeArrete permet d'englober les types d'arrete du
    graphe de reflexion, dont on ne sait pas encore grand 
    chose (2017-11-22)"""
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement

class ArreteReflexion(models.Model):
    """Ce sont les arretes du graphe de reflexion, 
    celles qui sont visibles par les utilisateurs"""
    ideeSource = models.ForeignKey(Noeud, related_name='source')
    ideeDest = models.ForeignKey(Noeud, related_name='dest')
    typeArrete = models.ForeignKey(TypeArrete)
    


class Tag(models.Model):
    """Element qui relie des posts entre eux.
    Important car joue sur les arretes du grand graphe
    et/ou sur sa métrique"""
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement
    
    def postTagues():
        """renvoie une collection (quelque soit son
        implementation) de posts tagués par un tag 
        particulier."""
        pass

class Citation(models.Model):
    """Element qui relie des utilisateurs, et un post entre
    eux. Important car joue sur les arretes du grand graphe
    et/ou sur sa métrique"""
    auteur = models.ForeignKey(User, related_name='userAuteur')#TODO user comme nom ?
    post = models.ForeignKey('Post', related_name='postSource') 
    #j'utilise le nom de la classe car elle est définie après,
    #comme indiqué dans la documentation
    rapporteur = models.ForeignKey(User, related_name='userRapporteur')

class Post(models.Model):
    """Le post qui sera écrit et lu par des utilisateurs
    TODO choisir un langage de formatage du texte : 
    html ? bbCode ? autre ?. Il devra en outre traiter des 
    citations (2017-11-22)"""
    pere = models.ForeignKey('self', on_delete=models.CASCADE)
    auteur = models.ForeignKey(User)
    tag = models.ManyToManyField(Tag)
    contenu = models.TextField()
    citations = models.ManyToManyField(Citation, related_name='postsCites')
    date = models.DateTimeField(auto_now_add = True, auto_now = False)
    
    def insererCitation():
        """Transforme l'information qu'on a de l'user
        dans le contenu du post pour garder l'info de
        la citation"""
        pass



class TypeVote(models.Model):
    """Permet de garder toute la généralité des types de
    votes.
    XXX j'ai choisi  de rajouter impact en pensant 
    qu'il aurait un intéret (A;2017-11-22)"""
    label = models.CharField(max_length = 30)
    #valeur de max_length choisie arbitrairement
    impact = models.IntegerField()

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

class Reputation(models.Model):
    """est ensuite associée à chaque utilisateur
    TODO mettre en place une association 
    * avec les utilisateurs
    * avec les votes
    * avec les citation ?(2017-11-22)
    Pour l'instant très mal définie"""
    user = models.OneToOneField(User)

class Suggestion(models.Model):
    """La suggestion est un outil très orienté utilisateur
    Il s'agit de relier un user et un noeud du graphe de 
    reflexion pour l'inciter, dans son interface, à aller
    voir ce dont il s'agit.
    Une suggestion sera le résultat du traitement du grand
    graphe."""
    userVise = models.ForeignKey(User)
    objet = models.ForeignKey(Noeud)
    pertinence = models.IntegerField()


class Log(models.Model):
    """on sait qu'on doit en faire un donc le voilà.
    Il permettra des traitements par la suite.
    """
    user = models.ForeignKey(User)
    action = models.CharField(max_length = 100)
    #valeur de max_length choisie arbitrairement

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
    
