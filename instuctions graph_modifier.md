# récupérer l'objet GraphModifier

**Uniquement dans l'application app**

from app.clustering.GraphModifier import GraphModifier
gm = GraphModifier.get(project_id)

project_id est l'identifiant sql du projet.

# Liste des mofifications

Tous les objets doivent être passés via leur clé principale SQL.

*create_post(database_id, noeud, tagList, author, size, parent=-1, value=-1)*

A utiliser quand un nouveau post est publié. Si la publication su post créé des nouveaux tags par la même occasion, il faut ajouter les nouveaux tags **avant** d'ajouter le post (avec la fonction create_tag)

* database_id : id du post. Utiliser la clé principale de la base de donnée des posts.
* noeud : id du noeud dans lequel le post à été publié
* tag_list : liste de tous les tags.
* author : auteur du post
* author : l'id
* size : nombre de caractères du post **avec ou sans le titre ?**
* parent : id du post auquel celui-ci est une réponse. Mettre (-1) si le post est une publication directement dans le noeud.

*create_recommendation_link(node1, node2, author)*

A utiliser pour signaler qu'un utilisateur a indiqué que deux posts devraient être regroupés, via l'outil prévu à cet effet.

* node1
