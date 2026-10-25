# Étape 10, cinquième partie : le solveur inverse, les leviers qui portent l'année à un solde visé

**La demande.** Le reste 4 de la note du 16 octobre
(`2026-10-16-etape-10-ages-de-depart-au-site.md`, « Ce qui reste »), le
dernier point de son bloc : le solveur inverse. Le registre le tient du
simulateur de dépense publique de S. Aurain (`simulateur_aurain`, chantier
138.10) : « Son interface résout un problème budgétaire à l'envers, par
dichotomie » ; le site avait un solveur individuel, la saisie par la pension,
et aucun solveur budgétaire. Relu à son commit `59b7985`, l'outil fixe une
somme à dégager et une année, puis dose par quarante bissections chacun de six
profils de leviers (`app/retraites.html:1548-1554`). Ni la comparaison A/B, ni
le rapport du même point. Session du 25 octobre, la seule sur les pages.

**La forme.** Elle ne revenait pas au propriétaire : le registre dit le geste,
le COR et la page Coût le reste. La page chiffrait déjà, sous le coefficient
d'équilibre, les trois leviers du COR — la pension, le taux de prélèvement,
l'âge —, chacun seul, pour l'équilibre (étape 3). Le solveur en change la
cible : un solde, en part du PIB, plutôt qu'une somme, qui ne dirait pas la
même chose en 2050 et en 2070, et que la page convertirait de toute façon au
PIB de 2025. Le coût ne se calcule qu'en Python (`moteur/CLAUDE.md`) : la
fabrique cherche les leviers de sept soldes, de deux points de déficit à un
d'excédent, aux deux années que la page montre, et la page choisit lequel
montrer par un regard de son adresse, comme l'année de la cascade. Pas de
champ de saisie.

**La veille.** Aucune règle du scénario 1 ne change, et le journal de veille
n'a pas d'entrée.

**Ce qui est fait.**

- Le modèle (`leviers.py`) : `leviers(…, solde_vise=0.0)` et
  `releve_age(…, visee=0.0)`. La pension égale les ressources moins le solde
  visé — le coefficient, moins un, moins le solde visé sur la dépense — ; le
  taux comble l'écart du solde au solde visé, sur les revenus d'activité ;
  l'âge recule, par la même bissection, jusqu'à ce que les ressources, qui
  suivent les cotisants, moins la dépense, qui suit les retraités, tombent sur
  le solde visé. Le terme ajouté s'annule à l'équilibre : ses leviers ne
  changent pas d'un bit, et aucun chiffre de la table ne bouge.
  `leviers_du_modele(…, soldes_vises, annees_visees)` rend les autres dans
  `vises`.
- La table du paquet, en version 34 des deux côtés : `figer_leviers` y ajoute
  `soldes_vises`, `annees_visees` et, par système, les leviers de chaque solde ;
  `LeviersFiges.vise` et son jumeau de `agregats.js` les lisent. La fabrique lit
  dans `pages.js` `SOLDES_VISES` et `ANNEES_LEVIERS`, que l'empreinte du paquet
  suit désormais (`fabrique._LU_DE_PAGES`) : `test_fabrique.py` l'a exigé.
- La page Coût, dans le dépliant du coefficient d'équilibre : un paragraphe qui
  pose la question à l'envers, puis un sélecteur « Solde visé » (`g.bascule`),
  au-dessus du tableau des leviers, qui vise le solde choisi. L'adresse le porte
  (`solde=-1`, `VUES_DE_PAGE`), chacun des trois sélecteurs de la page garde
  les deux autres, et un solde que la liste n'a pas revient à l'équilibre. À
  l'équilibre, le tableau et la phrase du COR sont ceux d'hier ; à un autre
  solde, une phrase dit que le COR ne chiffre que l'équilibre, et comment les
  autres soldes se résolvent.
- Les tests. `test_le_solveur_dose_chaque_levier_pour_le_solde_vise`
  (`tests/test_leviers.py`, rapide) pose le cas à la main : 14 % de PIB de
  dépense, 12,6 de ressources, 40 % de revenus d'activité, 20 millions de
  retraités, 30 de cotisants, 800 000 personnes par âge. Un déficit visé de
  0,7 point rend −5 % de pension, +1,75 point de taux, 25/26 d'an de recul ;
  un excédent de 0,7 point, −15 %, +5,25 points, 75/26 d'an ; l'année juste,
  viser le même déficit rend +5 %, −1,75 point, et avance l'âge de 15/16 d'an ;
  viser l'équilibre redonne ses leviers, au bit près. `tests/test_agregats.py` :
  les leviers figés sont ceux du modèle, solde par solde, et les deux lecteurs
  lisent les mêmes. `tests/test_web.py` : le sélecteur et ses liens, le tableau
  d'un déficit d'un point, l'équilibre sans regard ou pour un solde inconnu ; une
  page qui ignore le regard le fait rougir. Le contrôle des cellules est
  partagé avec le test de l'équilibre (`_cellules_des_leviers`). Un témoin de
  page de plus, `cout_solde_vise`. Au registre, le point de `simulateur_aurain`
  passe à `repris`, pour le solveur.

**Ce que montrent les mesures.** Viser un déficit d'un point de PIB plutôt que
l'équilibre ramène, pour le système actuel en 2070, le rognage de 16 à 9 %, le
relèvement du taux de 5,6 à 3,3 points, le recul de 3,0 à 1,8 an ; pour la
proposition en 2050, de 17 à 6 %, de 3,8 à 1,5 point, de 3,2 à 1,2 an. La
table des leviers passe de 20,7 à 26,6 Ko, le paquet de 5 860 à 5 866 Ko ; les
leviers des sept soldes coûtent 3 ms de plus par système à la fabrique. Aucun
des 909 témoins de simulation ne bouge de mon fait : le seul qui bouge,
`reversion_au_maximum`, prend la majoration forfaitaire que l'étape 4 a
poussée sans refaire les témoins (c56843d). Cinq rendus de page sur 82
changent : les quatre de la page Coût gagnent le paragraphe et le sélecteur,
sans rien d'autre, et le neuf. Au navigateur, `tests/test_ecrans.py` ne trouve
ni débordement, ni grand vide, ni erreur aux cinq largeurs ; à 320 points, le
sélecteur se replie sur trois lignes. Tout déplié, Coût compte 33 237 mots pour
un budget de 33 250 (`test_une_page_depliee_tient_son_budget`) : la première
rédaction du paragraphe, qui redisait la légende du tableau, le dépassait de
neuf, et a été resserrée (3ae0c57, puis le commit suivant).

**Ce qui reste.**

1. Du point du registre, la comparaison A/B de deux jeux d'hypothèses et le
   rapport avec ses repères budgétaires. La page Coût ne montre que la
   référence, à côté de ses variantes démographiques : comparer deux jeux de
   réglages y demanderait de figer le coût sous chacun.
2. Le solveur ne vise qu'un solde, une année. Ni un solde moyen sur un horizon
   — le tax gap d'une autre cible que l'équilibre —, ni les leviers dosés
   ensemble (le profil « Équilibré entre les trois » de l'outil), ni ses
   leviers propres : la sous-indexation, l'écrêtement par décile, le plafond.
3. L'étape n'a plus que des restes « s'il le faut » : le point 5 de la note du
   16 octobre ; le contrôle d'un relevé des autres régimes, et ce que les
   trimestres manquants changeraient (note du 19 octobre) ; le gain de la
   suspension génération par génération (note des droits contrefactuels) ; et,
   au registre, cinq points du chantier 138.10 encore `a_reprendre` — Marel,
   Oscar, Osiris, Nos retraites et ce gain —, à relire avant de clore l'étape.
   L'indice dans le relevé et le barème attendent l'action 158. Le retrait de
   `cycle_de_vie.py`, que le bloc plaçait après ce point, est fait (action 161,
   étape 5).
