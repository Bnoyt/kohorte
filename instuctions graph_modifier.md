# récupérer l'objet GraphModifier

import clustering.GraphModifier
gm = GraphModifier.GraphModifier.get(project_id)

project_id est l'identifiant sql du projet.

# Liste des moficications

*create_post(database_id, noeud, tagList, size, parent=-1, value=-1)*

A utiliser quand un nouveau post est publié.

database_id : id du post. Utiliser la clé principale de la base de donnée des posts.
noeud : id du noeud dans lequel le post à été publié
tag_list : liste de tous les tags, donnés sous formes de strings passés sous wordsoup.
size : nombre de caractères du post
parent : id du post auquel celui-ci est une réponse. Mettre (-1) si le post est une publication directement dans le noeud.