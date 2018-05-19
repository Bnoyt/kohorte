#Conventions

##Notify-x

* notification de Branch
target est le noeud père
object est le noeud qui se fait créer

#Clés

## notify-x

* nf_type
branch d'un noeud : "branch"
réponse à un post : "answer"
action de modération (édition, suppression) : "modo"
message privé : "mp"

## labels django

* TypeArete

* TypeSuivi
l'utilisateur a cliqué sur suivre : "suivi simple"
l'utilisateur a posté : "auto apres post"
branch :  "auto pendant branch"
l'utilisateur a posté puis s'est désabonné : "post puis unfollow"

* TypeVote
upvote : "upvote"
signalement de posts : "signal"
