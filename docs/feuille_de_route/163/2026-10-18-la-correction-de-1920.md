# Le rouge de la correction de 1920

**Le 18 octobre 2026, vers 8 h 10.** La suite complète rougit sur fd63f3d,
publiée par GitHub : `test_la_correction_des_trois_generations_se_retrouve`
— la page Méthode annonce +5,4 points pour la génération 1920, le modèle en
donne +5,5. La cause est en amont, à c30fa45 (action 131) : l'ASF au
1er avril 1983 et le protocole de 1976 à l'Arrco touchent le non-cadre né en
1920 parti en 1982 ; sa correction passe à 5,459, et l'arrondi bascule. La
session de l'action 131 avait lancé la suite rapide et ses tests, non ceux du
site, et les envois suivants ont caché le rouge jusqu'à fd63f3d.

**La réparation.** Le test attend +5,5, vu rouge sur la page ; la page dit
+5,5 ; le témoin des pages est refait. 1945 (+0,04) et 1958 (−0,50) ne
bougent pas.

**La classe.** Un chiffre du site écrit à la main, que tout changement du
modèle peut déplacer : le seul qui reste, par choix, ses six simulations
coûtant plus d'une seconde à l'affichage. Le produire comme les mesures de
l'accueil (`scripts/mesures_accueil.py`, étape de `regenerer.py`) le
tiendrait juste sans session ; à faire quand le propriétaire relancera les
sessions.
