# récupérer l'objet GraphModifier

**Uniquement dans l'application app**

from app.clustering.GraphModifier import GraphModifier

gm = GraphModifier.get(project_id)

project_id est l'identifiant sql du projet.

# Liste des mofifications

Tous les objets doivent être passés via leur clé principale SQL. Si le type attendu d'un argument n'est pas précisé, on attend une clé principale SQL.

**create_post(database_id, noeud, tagList, author, size, parent=-1)**

A utiliser quand un nouveau post est publié. Si la publication su post créé des nouveaux tags par la même occasion, il faut ajouter les nouveaux tags **avant** d'ajouter le post (avec la fonction create_tag)
* database_id : id du post. Utiliser la clé principale de la base de donnée des posts.
* noeud : id du noeud dans lequel le post à été publié
* tag_list : liste de tous les tags.
* author : auteur du post
* author : l'id
* size : nombre de caractères du post. Il n'y a pas une unique façon de compter ça, donc je laisse benoît choisir comment il veut le compter. (Avec ou sans titre, citation, etc). Choisis une façon de compter et indique la ici.
* parent : id du post auquel celui-ci est une réponse. Mettre (-1) si le post est une publication directement dans le noeud.

**create_tag(database_id, slug)**

A utiliser quand un nouveau tag est créé. Pas besoin d'appeler cette fonction si le tag existe déjà.

**create_quote(origin_post, user)**
Utiliser quand un utilisateur clique sur le bouton "citer" et enregistre une citation
* origin_post : le post dont la citation est issue
* user : l'utilisateur qui clique sur le bouton "citer"


**forget_quote(quote)**
Utiliser quand un utilisateur supprime une citation de son répertoire. La citation ne doit surtout pas être supprimée de la BDD, elle va simplement cesser de s'afficher.

**create_recommendation_link(node1, node2, author)**

A utiliser pour signaler qu'un utilisateur a indiqué que deux posts devraient être regroupés, via l'outil prévu à cet effet.
* node1, node 2 : les deux noeud. L'arrête n'est à pas orientée pour l'instant, les deux noeud sont donc interchangeables.
* author : l'utilisateur qui à posté la recommendation

**violently_remove_post(database_id)**

Suprime toutes les données concernant ce post, a effectuer si le post à été retiré de la base de donnée. Le graphe peut refuser de supprimer le post si il est trop important. Opération assez violente, a éviter de préférence. Plutot marquer le post comme supprimé et utiliser mark_post_deleted.

**mark_post_deleted(database_id)**

Marque un post comme supprimé, mais conserve les données liées à ce post. Il est impératif que les données du post soient également conservé dans la base de données.

**add_tag_to_post(post, tag)**

Ajoute un nouveau lien entre un tag deja existant et un post deja existant. Il s'agit d'une des trois façon de modifier les tags associés à un post, et correspondrait à un bouton de type "ajouter un tag" si un tel bouton est un jour implémenté. Le tag doit avoir été créé avec create_tag avant de le rajouter au post.

* post : le post sur lequel on rajoute un tag
* tag : le tag

**remove_tag_from_post(post, tag)**
 
Retire un lien entre un tag et un post. Ne suprime ni le tag, ni le post.

**modify_post(database_id, new_size=-1, new_tags=None)**

Permet de modifier un post. Cette opération est pensée pour accompagner un bouton "EDIT". 
* new_size donne le nouveau nombre de caractères du post (compté comme pour create_post).
* new_tags indique la nouvelle liste de tags du post. Ce n'est pas une list de tags à ajouter, c'est une nouvelle liste de tags qui **remplace l'ancienne liste**. Si ces arguments sont laissé à leurs valeurs par défault (-1 et None respectivement), ils ne seront pas modifiés.


**add_vote(post, author, vote):**

A utiliser quand un utilisateur vote sur un post.

* post : le post sur lequel le vote est placé
* author : celui qui vote (pas l'auteur du post)
* vote : le vote en lui même (c.a.d. l'id dans la base de données du vote).
* vote_type : le type du vote. D'après models, cette information est représentée par un charfield de 30 charactères, avec un unique identifiant pour chaque type de vote possible. Il faudra d'ailleurs choisir et placer dans une référence le nom des divers types de vote.

**cancel_vote(vote)**

Annule un vote. Le vote en question sera supprimé du graphe, et doit également être supprimé de la BDD.
