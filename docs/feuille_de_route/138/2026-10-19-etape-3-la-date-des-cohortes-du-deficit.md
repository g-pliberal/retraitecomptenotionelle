# Étape 3, quinzième partie : la date de chaque cohorte dans `mortalite_population.py`, ce que le diviseur commun coûte au régime

**La demande.** Vague B du 19 octobre 2026, session 2 de la première salve :
« Action 138, étape 3 : `mortalite_population.py` porte la même erreur de date
des cohortes » — le point 1 de « Ce qui reste » de la note « le coût des
avantages ». Le script relisait la grille du coût à la date de la grille
(`annee_liquidation + decalage`), quand `cout.py` date chaque cohorte au droit
de sa génération depuis le 18 octobre. En Python seul : le script n'a pas de
jumeau (`python scripts/jumeaux.py`). Ni les 0,19 point, ni le taux effectif.

**Ce que fait le script, désormais.** `--deficit` mesure, sur les têtes de la
page Coût, ce que le diviseur commun coûte au régime. Chaque cohorte des
couples de la grille y compte à partir de l'année que le droit de sa
génération lui donne (`Pensionne.liquidation`), sa survie depuis ce départ ;
ses deux courbes, la commune et celle de son vingtile, et le rapport de ses
diviseurs se prennent à son âge et à son année de départ (`_cohortes`), comme
la page date sa survie (`cout._survies`) ; le flux de `--depuis` se choisit
sur son départ à elle (`_masses`). Avant, le rapport et les courbes se
prenaient une fois par couple, à l'âge et à l'année de la génération simulée.
La pension reste celle de la génération simulée. Seul `--deficit` lisait la
grille : `mesurer` et `--niveau-de-vie`, dont `docs/methodologie.md` ancre les
chiffres, simulent chaque cas type à sa génération, et ne bougent pas ; aucun
fichier fabriqué ne lit le déficit. Ni `flux_fonction_publique.py` ni
`grille_large.py`, qui relisent aussi la grille, ne gardent la même erreur.

Au passage, la dernière ligne du déficit lisait le PIB du solde, en millions
d'euros, comme un point : « Un point de PIB vaut 2 991 Md€ » ; il en vaut 30
(`_point_de_pib`).

**La mesure.** `python scripts/mortalite_population.py --deficit`, puis avec
`--depuis 2026`, sur `main` au 19 octobre (4a668a8), avant et après. Tout le
monde recalculé, stock compris, presque rien ne bouge au dixième : la baisse
de la dépense du scénario 4 en 2050 passe de 3,5 à 3,6 %, le solde du
scénario 6 la même année de −1,65 à −1,64 % du PIB, et ce que la survie du
vingtile ajoute à la masse du système actuel en 2030, de 2,3 à 2,4 % ; aucun
solde moyen ne bouge au centième. Le flux seul, celui des pensions liquidées
depuis 2026, est atteint plus tôt : il compte désormais les cohortes que le
droit de leur génération fait partir en 2026 et non en 2025, telles celles de
1961 de six cas types (note « la date de chaque cohorte »).

| Baisse de la dépense, le flux depuis 2026 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| 2030, à la date de la grille | 0,8 % | 0,6 % | 0,8 % | 0,6 % | 0,8 % |
| 2030, chacune à sa génération | 0,9 % | 0,7 % | 1,0 % | 0,7 % | 0,9 % |
| 2050, à la date de la grille | 2,8 % | 2,5 % | 3,0 % | 2,7 % | 2,8 % |
| 2050, chacune à sa génération | 2,9 % | 2,6 % | 3,1 % | 2,8 % | 2,8 % |

Le solde moyen de 2026 à 2070 sous le diviseur par vingtile, dans ce flux,
bouge d'un centième de point au plus : +7,91 % du PIB au lieu de +7,90 pour le
scénario 2, +1,74 au lieu de +1,73 pour le 3, −1,20 au lieu de −1,21 pour le 6 ;
le 4 et le 5 ne bougent pas. Rien en 2070.

**Les tests.** En suite rapide, un fichier neuf,
`tests/test_mortalite_population.py` :
`test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation`,
le salarié au salaire moyen de 1965 de `test_cout.py`, parti en 2028, ses
cohortes en 2026, 2027, 2030 et 2031 (L. 161-17-3), sous une mortalité et une
population posées à la main — en 2030, la cohorte de 1967 n'est pas partie,
celle de 1966 part l'année même, chacune a ses courbes à son âge et à son
départ, et le flux de 2030 est la seule cohorte de 1966 ; sans dates, celles
de la grille — et `test_un_point_de_pib_en_vaut_le_centieme`. Chacun vu rouge
sur le comportement : `_cohortes` et `_masses` d'abord extraites à
l'identique, la sortie du script refaite au caractère près dans ses deux
lectures, puis corrigées.

**Ce qui reste**, de cette partie ; les points 1 et 3 de la note « la date de
chaque cohorte » et le point 2 de la note « le coût des avantages » demeurent.

1. *Pour une session de l'étape 7 : la prémisse du déficit.* Le script dit
   encore la page Coût à la mortalité générale — sa documentation (« ce que la
   page ne fait pas ») et son premier tableau (« Ce que la page sous-compte ») —,
   quand, depuis le 17 octobre, chaque cas type y survit au rythme de son
   vingtile, à nombre de décès égal (`cout._survies`, `_survies_alignees` ;
   note « la mortalité différentielle »). Ses colonnes « page » mesurent la page
   d'avant le 17 octobre : à relire sur la survie alignée, avec la limite que
   le point 4 de cette note renvoie à la fin de l'étape. Le récit de
   `docs/limites/5-hors-du-modele.md`, vrai à sa date, donne une baisse de 3,5
   à 4,4 % et un solde moyen meilleur de deux à cinq dixièmes de point ; le
   script donne aujourd'hui de 3,0 à 3,6 % et de 0,14 à 0,41 point.
