# Étape 4, seconde partie : tout le jaune lu et certifié, dix-sept incohérences déclarées, les cas types année par année, le stock pesé comme la page

**La demande.** Le propriétaire, le 13 octobre 2026 : « fais la seconde partie
de l'étape 4 », avec trois décisions prises sur les questions de la session :
les référents restent une série certifiée de `data/reference/macro/`, non le
registre des modèles ; tout se lit et se certifie, les annexes A et B et les
tableaux 60 à 108 du corps, et se confronte au modèle là où il se peut ; la
case fausse du tableau 50 reste telle qu'imprimée, le B-22 à côté d'elle.

Le document est celui de l'étape 1 (`sre_jaune_pensions_2027`), son empreinte
vérifiée. Les pages citées sont celles qu'il imprime.

## Le lecteur PDF perdait cinq pages

Le B-20 et le B-21 n'étaient sur aucune page que le lecteur du dépôt rendait.
`lecture_pdf._flux` ôtait les retours à la ligne des deux bouts d'un flux avant
de le décompresser : quand les données compressées finissent elles-mêmes par
cet octet, il les tronquait, zlib refusait le flux, et la page disparaissait
sans bruit. Sept flux du jaune échouaient ainsi, cinq portant du texte : une
page de la partie I sur le programme 741, celle des tableaux 95 et 96, une
page de la partie V sur le minimum garanti, celle des B-20 et B-21. Le flux se
relit désormais tel quel quand le premier essai échoue, pourvu qu'il finisse ;
deux tests le tiennent (`tests/test_lecture_pdf.py`). Les lectures écrites
avant, le tableau 50, l'A-7, le B-1 et les taux employeurs, rendent les mêmes
1 703 valeurs, et les six tableaux de la première partie les mêmes 1 371.

## La lecture

Le lecteur des référents a son module, `scripts/fetch/sre_jaune_referents.py`,
que `sre_jaune_pensions.py` appelle. Chaque tableau a son gabarit ; la clé d'une
valeur a gagné une dimension, la modalité (l'année d'une série, l'âge, le
sexe, la catégorie, le grade). Ce que les cinquante-trois tableaux lui ont
appris :

- *Un tableau finit à ses sources, au titre du suivant, ou avec sa page* : le
  jaune pose le corps des A-3 et A-4 sur des pages à eux, leurs titres et
  leurs sources sur une autre ; au tableau 69, une note en marge porte ses
  sources au milieu des lignes. Une ligne de cases que le gabarit n'attend
  pas, sur la page de sa dernière ligne, est une erreur : c'est ainsi que le
  bloc « Ensemble CNRACL » et la valeur du point, oubliés au B-14, se sont
  vus.
- *Un âge en années et en mois* (« 62 ans et 5 mois ») est une case, lue en
  mois ; *une année en tête de ligne* (tableaux 60, 69, 75, 76, 78) en est
  l'intitulé ; *le signe posé sur la ligne du dessus* (les montants de la
  décote du tableau 104, en trois lignes : le signe, les chiffres, le
  symbole) se recompose ; *des pourcentages sans leur signe* (tableau 107) se
  lisent en fraction.

Chaque tableau passe le banc d'essai de la session : les nombres que
pdftotext lit dans sa région, et ceux du lecteur, sont les mêmes, à
l'exception des en-têtes et des renvois.

## Ce qui est certifié

`caracteristiques_fonction_publique.csv`, clé (tableau, population, champ,
modalite, indicateur) : 8 166 valeurs, 7 082 des annexes, 1 084 du corps.

- *Le stock* : au 31 décembre 2025 (A-1), par tranche d'âge (A-2), ses
  effectifs et sa pension de 2016 à 2025 (A-3, A-4), par sexe en 2024 et 2025
  (A-5), au minimum garanti depuis 2010 (A-6), ses déciles (A-8) ; depuis 1990
  (tableau 60), sa pension depuis 2000 (75).
- *Le flux* : de 2025 par motif, catégorie, grade, âge, administration et
  sexe (B-1 à B-10, B-16 à B-19, 70, 108) ; les réversions et les décès de 2025
  (B-11, B-13) ; les entrées depuis 2016 (B-12, 66) ; la pension, l'indice et
  le taux depuis 2016 (B-14, B-15) ; ses déciles (B-20) ; le minimum garanti
  (B-21, 80, 83 à 85) ; les âges de départ (67 à 69, 101, 102), la surcote et
  la décote (103 à 106), le taux de liquidation (107) depuis 2004 ; la
  pension depuis 2000 (76, 78), la durée validée (79), la part encore
  rémunérée (73), la décristallisation (86).

Le B-22, les bonifications du flux de 2025 (59 valeurs), va à
`bonifications_jaune.csv`, avec le tableau 50 : chacune de ses parts y est
celle du tableau 50 à un millième près, et chaque durée à un dixième de
trimestre, sauf la case fausse — 20 736 bénéficiaires de la bonification pour
enfant parmi 47 104 civils, 44,0 %, quand le tableau 50 imprime 4,0 %.

Les graphiques du corps (61 à 65, 71, 72, 74, 77, 81, 82, 98) n'ont pas de
nombres à lire.

## Ce que le document dit contre lui-même

Les tableaux se recoupent : 599 recoupements exacts — les sexes font
l'effectif, les régimes leur total, les âges, les catégories et les grades
leur ensemble, chaque case imprimée deux fois l'est à l'identique —, 45
concordances à l'arrondi près entre tableaux qui impriment la même grandeur à
des précisions différentes, 26 moyennes pesées de leurs parts, et chaque
moyenne entre celles des hommes et des femmes. Sauf en dix-sept points,
déclarés un à un (`INCOHERENCES_DU_DOCUMENT`) ; un test exige que rien d'autre
ne se contredise, et que chacun se voie encore :

- les âges des B-8 et B-9 ne font que les neuf dixièmes de leurs totaux
  (42 018 pour 46 897, 19 986 pour 22 753) ;
- le B-2 compte 13 237 départs de la CNRACL en catégorie active, quand sa
  territoriale et son hospitalière en comptent 10 597, comme le B-1 ;
- au tableau 108, les taux de liquidation des catégories de la territoriale
  sont ceux de l'hospitalière à la décimale près, et ne font pas, pesés de
  leurs départs, le taux du versant (49,5 % pour 50,7) ; ceux des grades des
  militaires font 63,7 % pour 65,3 ;
- le B-1 compte 102 départs de la territoriale et 16 de l'hospitalière que
  leurs tableaux par motif ne classent nulle part ; le B-3 bis et le B-16, le
  B-20 et le B-16, le tableau 70 et le B-1 ne comptent pas les mêmes départs
  de la CNRACL, à quelques dizaines près ;
- le tableau 69 fait liquider les civils de l'État à 62 ans et 6 mois en 2025,
  le tableau 67 à 62 ans et 10 mois, comme le B-1 ; le 67 fait liquider la
  territoriale à 62 ans et 1 mois, le B-1 à 62,3 ans ;
- au tableau 101, l'âge de l'ensemble des civils sort quatre fois de ceux de
  leurs hommes et de leurs femmes, de deux ans en 2010 ;
- et cinq écarts de quelques unités, ou de deux dixièmes de point (B-6,
  B-11, B-13, B-17, et le taux des ouvriers de l'État entre le B-1 et le
  B-14).

Hors de ces recoupements, la valeur « annuelle moyenne » du point du B-14 reste
à 58,64 € en 2024 et en 2025, la moyenne de 2023, quand il vaut 59,07 € toute
l'année depuis le 1er juillet 2023 ; un test le dit, contre
`point_indice_fonction_publique.csv`.

## Les cas types, année par année

L'étape 5 a recalé les deux civils le 14 octobre, pendant cette session :
les mesures ci-dessous sont celles de ses cas types, sur le simulateur de la
page Coût, comme celles du flux de 2025. `scripts/flux_fonction_publique.py`
fait partir chaque cas type chaque année de 2016 à 2025 où le droit fait
partir l'une de ses générations, face à la série de son groupe (`SERIES`) :

| cas type | série | 2016 | 2025 |
|---|---|---|---|
| sédentaire, âge | sédentaires de l'État (101) | +0,65 an | −0,40 an |
| sédentaire, taux | civils pour ancienneté, hors minimum garanti (107) | −4,1 % | −5,1 % |
| sédentaire, pension | flux des civils (B-14) | −0,7 % | −3,3 % |
| actif, âge | actifs de la CNRACL (102) | +1,00 an | +1,00 an |
| actif, taux | flux de la CNRACL (B-14) | +4,2 % | +18,4 % |
| actif, pension | flux de la CNRACL (B-14) | −8,6 % | +4,6 % |
| militaire, taux | flux des militaires (B-14) | −5,9 % | −9,5 % |
| militaire, pension | flux des militaires (B-14) | +2,8 % | +5,2 % |

Le sédentaire suit le taux de son groupe, deux à quatre points en dessous,
mais non son âge : il monte de trois trimestres en neuf ans, les sédentaires
d'un an et neuf mois. L'actif part d'un à deux ans après les actifs — un an
en 2016, deux en 2020, un en 2025 —, et son taux monte quand celui de sa caisse
baisse. Le militaire perd six points de taux, le flux réel quatre. Les
vingt-deux écarts sont déclarés, chacun dans sa fourchette
(`tests/test_flux_fonction_publique.py`).

## Le stock, pesé comme la page

`stock_pese_comme_la_page` reprend la grille de la page Coût
(`cout._pensionnes`) et ses poids (`cout._masses_regimes`) : chaque cohorte à
l'effectif de son âge et à sa complétude, la seule part du régime statutaire.
En 2025, la page sert 2 364 € aux civils de l'État pour 2 386 € au jaune
(avantage principal, A-5), 1 443 € à la CNRACL pour 1 481, 1 798 € aux
militaires pour 1 832 : de 1 à 3 % de moins. En 2016, 10, 13 et 16 % de moins
que le stock accessoires compris (A-4) : le stock de la page monte plus vite.
Il suit les prix, quand le droit a revalorisé les pensions de 16,1 % de 2016 à
2025 pour 20,7 % de hausse des prix, et avec un an de retard en 2023 : l'écart
des civils passe de −4,2 à −0,4 % cette année-là, et revient à −3,5 en 2024.
Les neuf écarts sont déclarés ; le paragraphe daté des limites
(`docs/limites/5-bis-cout-agrege.md`) le dit.

## Le registre des modèles

*Oscar* (SRE) : les agrégats du flux de 2025, ses séries de 2016 à 2025 et le
stock depuis 2016 sont au dépôt ; les trois cas types statutaires s'y
confrontent chaque année, et le stock que la page leur sert. La validation
pension par pension reste au chantier 138.14.

## Ce qui va aux autres étapes

- **Les cas types (étape 5, close)** : les tableaux 95 et 96 — la durée des
  services et des bonifications par sexe et par motif, les pensions
  militaires par durée de référence — se lisent désormais, et ne sont pas lus.
  L'âge du sédentaire monte moins vite que celui des sédentaires, ce que le
  pilote du taux plein que l'étape 5 a déclaré explique peut-être.
- **Une question au propriétaire** : la page indexe le stock du scénario 1 sur
  les prix, comme le droit le dit en moyenne ; le faire suivre des
  revalorisations effectives (`revalorisation_pensions.csv`) rapprocherait
  ses années observées du jaune, et toucherait au modèle.

*Ce qui reste.* Rien pour l'étape 4. GitHub refera le paquet, que les
nouvelles valeurs certifiées déplacent, et les fichiers fabriqués.
