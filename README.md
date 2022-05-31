# IAProject

## Ce que l'IA peut faire 

Notre IA est implémentée dans le fichier myPlayer.py et possède divers fonctionnalités :
 - minimax qui renvoie la valeur ainsi que le coup
 - alphabeta qui renvoie la valeut ainsi que le coup
 - monteCarlo qui est une approximation de MonteCarlo, en fonction d'une pronfondeur donnée, l'algorithme va évaluer un certain nombre de parties jusqu'à la fin, et faire la moyenne sur le nombre de victoires afin de savoir quel coup prendre
 - gestion des ouvertures, qui tente de reproduire une partie déjà existante si tous les coups coincident, ou pas
 - gestion du temps, si notre joueur a utilisé plus de 810 secondes (variable _self.\_dangerTime_ modifiable), alors il joue un coup aléatoire, mais il y a tout de même une vérification rapide que ce coup ne mène pas à la défaite

## Notre heuristique

Pour l'heuristique, nous avons eu différentes idées :
 - utiliser simplement compute_score() renvoyant le score pour les Noirs et les Blans (fonction _getScore()_) (heuristique actuellement utilisée)
 - utiliser implement la différence de pières (fonction _getScore2()_)
 - utiliser la différence de pières et le nombre de pières capturés avec un certain facteur pour chacun de ces paramètres (fonction _heuristique()_ et _getScore3()_)


## La gestion des ouvertures

Pour la gestion des ouvertures, nous avons une variable _self.\_exactOuverture_ qui vaut soit True ou soit False.
 - Si jamais la variable vaut True, alors on va chercher une ouverture qui correspond exactement aux coups joués
 - Si jamais la variable vaut False, alors on choisit une ouverture initialement et on joue tous les coups présent dans l'ouverture selon notre couleur jusqu'à qu'un coup qu'on souhaite jouer n'est pas légal

## Notre stratégie finale

 Notre stratégie est la suivante :
 1. Au début de la partie, notre jouer va tenter de reproduire une partie déjà existante (gestion des ouvertures), elles sont toutes stockées dans _self.\_gameWinner_ ou  _self.\_newGameWinner_  (en fonction de si on a passé _self.\_exactOuverture_ à True ou False)
 2. Dès que cela n'est plus possible, notre joueur va réaliser alphabeta avec une profondeur de 2 (variable _self.\_normalDepth_ modifiable)
 3. Dès que le nombre de coups possibles passe en dessous de 50 (_self.\_numberOfMovesForMiddleDepth_), la profondeur passe à 3, et dès que le nombre de coups possibles passe en dessous de 30 (_self.\_numberOfMovesForAdvancedDepth_), la profondeur passe à 4 (_self.\_advancedDepth_)
 4. Ensuite, dès que le nombre de coups possibles est inférieur à 15 (_self.\_beginMonteCarlo_), c'est la technique MonteCarlo avec une profondeur de 1 (variable _self.\_depthMonteCarlo_ modifiable) qui est mise en place, en dessous de 7, avec une profondeur de 2
 5. Enfin, dès que le nombre de coups possibles est inférieur à 5 (_self.\_numberOfMovesForExtraDepth_) on refait l'algorithme alphabeta avec une profondeur de 5 (_self.\_extraDepth_)

# Auteurs

DEPLANNE Coralie

PAUWELS Quentin