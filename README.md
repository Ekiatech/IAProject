# IAProject

Notre IA est implémentée dans le fichier myPlayer.py et possède divers fonctionnalités :
 - minimax qui renvoie la valeur ainsi que le coup
 - alphabeta qui renvoie la valeut ainsi que le coup
 - monteCarlo qui est une approximation de MonteCarlo, en fonction d'une pronfondeur donnée, l'algorithme va évaluer un certain nombre de parties jusqu'à la fin, et faire la moyenne sur le nombre de victoires afin de savoir quel coup prendre
 - gestion des ouvertures, qui tente de reproduire une partie déjà existante si tous les coups coincident
 - gestion du temps, si notre joueur a utilisé plus de 810 secondes (variable self._dangerTime modifiable), alors il joue un coup aléatoire, mais il y a tout de même une vérification que ce coup ne mène pas à la défaite

 Notre stratégie est la suivante :
 1. Au début de la partie, notre jouer va tenter de reproduire une partie déjà existante (gestion des ouvertures), elles sont toutes stockées dans _self.\_gameWinner_
 2. Dès que cela n'est plus possible, notre joueur va réaliser alphabeta avec une profondeur de 2 (variable _self.\_normalDepth_ modifiable)
 3. Dès que le nombre de coups possibles passe en dessous de 50 (_self.\_numberOfMovesForMiddleDepth_), la profondeur passe à 3, et dès que le nombre de coups possibles passe en dessous de 30 (_self.\_numberOfMovesForAdvancedDepth_), la profondeur passe à 4 (_self.\_advancedDepth_)
 4. Enfin, dès que le nombre de coups possibles est inférieur à 15 (_self.\_beginMonteCarlo_), c'est la technique MonteCarlo avec une profondeur de 2 (variable _self.\_depthMonteCarlo_ modifiable) qui est mise en place

# Auteurs

DEPLANNE Coralie

PAUWELS Quentin