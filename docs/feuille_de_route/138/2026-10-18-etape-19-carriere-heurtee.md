# Étape 19, deuxième partie : la carrière heurtée d'Osiris, écrite et éprouvée sur le droit ; son poids dans la grille, au propriétaire

**La demande.** Vague du 18 octobre 2026, lancée par la session
d'orchestration sur la demande du propriétaire, « toutes les actions de la
feuille de route qui n'ont pas besoin de lui » : à l'étape 19, le premier
point du bloc « Reprise » qui ne dépende pas de sa décision, une carrière
heurtée dans la grille des cas types (« Reste du moyen »,
`2026-10-14-la-coupe.md`) ou la part de la solidarité confrontée aux masses
de la Cnav. La seconde est coupée depuis le 14 octobre (registre, `prisme`,
`etat: coupe` : « une confrontation ou un indicateur, qui ne change aucun
chiffre ») ; le bloc « Reprise » du 14 la comptait encore. Reste la première,
seul point du chantier 138.19 qui ne soit ni repris ni coupé (`osiris`).

**Ce qui est fait.** `CARRIERE_HEURTEE` (`castypes.py`), le cas type de la
maquette Osiris de la DSS tel que l'étude d'impact du projet de loi instituant
un système universel de retraite le définit (2020, p. 202 du PDF) : un
non-cadre du privé au salaire moyen du tiers inférieur à chaque âge, « environ
30 000 € par an » quand le salaire moyen en fait 38 000 (niveau 0,79), entré à
22 ans, qui perd son emploi à 42 ans ; l'ARE deux ans, l'ASS deux ans, un an
et demi de chômage non indemnisé, que deux années portent, puis l'inactivité
jusqu'au départ. Le modèle avait tout : les motifs `chomage_indemnise`,
`chomage_solidarite` et `chomage_non_indemnise`, l'inactivité lue en
`sans_activite` (`periodes_non_travaillees.csv`), la limite des trimestres du
chômage non indemnisé (`limiter_chomage_non_indemnise`). Le test
(`test_moteur.py`) tient ce que le droit lui valide : quatre trimestres par
année d'ARE et d'ASS (R. 351-12, 4°, c) ; six au plus pour la première période
de chômage non indemnisé si elle suit 2010, quatre avant (4°, d ; décret
n° 2011-934, art. 2) ; rien pour l'inactivité ; parti au taux plein par
l'âge, 65 ans né en 1950, 67 ans né depuis 1955 (L. 351-8, 1°, fiche
`age_annulation_decote`).

**Ce qu'elle donne.** L'écart de pension au système actuel, pilier capitalisé
compris, comme la page Cas types le montre ; entre parenthèses, le salarié au
salaire moyen de la grille :

| Génération | Départ | Trimestres | 2. Rétroactif, part salariale | 4. Rétroactif, part patronale | 6. La proposition |
|---|---:|---:|---:|---:|---:|
| 1950 | 65 ans | 100 | −78 % (−77 %) | −43 % (−41 %) | +7 % (−41 %) |
| 1960 | 67 ans | 100 | −71 % (−73 %) | −28 % (−33 %) | +1 % (−33 %) |
| 1980 | 67 ans | 102 | −69 % (−72 %) | −23 % (−32 %) | +1 % (−24 %) |
| 2000 | 67 ans | 102 | −73 % (−76 %) | −33 % (−40 %) | −6 % (−26 %) |

Aux scénarios 2 et 4, il perd autant que le salarié moyen, ou un peu moins :
le compte ne porte de ses années de chômage que ce que l'Unédic et l'État
versent aux complémentaires, quand le système actuel lui en valide vingt ou
vingt-deux trimestres, mais il part tard, à 65 ou 67 ans, sur un diviseur plus
court. La proposition
lui rend sa pension d'aujourd'hui, à six points près, quand le salarié moyen y
perd un quart à un tiers : sa pension contributive, 71 % du plancher de la
garantie vieillesse pour la génération 1960 (800 € par mois, plus 250
d'isolement pour qui vit seul), est complétée jusqu'à lui.

**Pourquoi elle reste hors de la grille.** Ajoutée à `CAS_TYPES`, elle entre
dans les agrégats par la Cnav, que le dépôt partage également entre les cas
types du privé faute de part publiée (`poids_effectifs`). Elle y part au taux
plein par l'âge, 65 puis 67 ans, et fait partir la grille plus tard que la
France réelle (`tests/test_age_conjoncturel.py`, DREES, 2004 à 2022) :

| Sa part de la Cnav | Écart moyen à l'âge conjoncturel | En 2022 |
|---|---:|---:|
| aucune, la grille du jour | +0,27 an | −0,02 an |
| 12 %, entre les 14,4 % des nés en 1950 et les 9,9 % des nés en 1953 partis au taux plein par l'âge (EIR, `departs_generations.csv`) | +0,56 an | +0,32 an |
| un cinquième, le partage égal | +0,75 an | +0,56 an |

À l'une ou l'autre part, trois tests de l'âge conjoncturel rougissent : l'écart
moyen passe sa borne de 0,4 an, et la grille ne part plus plus tôt que la
France des dernières années. La cause n'est pas la carrière heurtée, mais ce
qui manque en face : la grille n'a aucun des départs anticipés du privé, ni
carrière longue (11,5 % des nés en 1950, 20,3 % des nés en 1953), ni
inaptitude (7,7 et 7,0 %), ni invalidité (6,8 et 7,9 %), que le droit sert à
l'âge légal ou avant ; elle recevrait les départs tardifs des carrières
courtes sans eux. Sur la page Coût, l'effet est petit : à 12 % de la
Cnav, la dépense de la proposition passe de 0,692 à 0,698 de celle du système
actuel en 2030, de 0,739 à 0,745 en 2050, et sa recette de 0,660 à 0,655.

**Au propriétaire.** Le poids de la carrière heurtée, et donc son entrée dans
la grille :

1. *Maintenant, à une part mesurée* — les départs au taux plein par l'âge de
   l'EIR, 14,4 % ou 9,9 % —, en acceptant une grille qui part une demi-année
   trop tard et en récrivant les trois tests de l'âge conjoncturel, jusqu'à ce
   que les départs anticipés la compensent.
2. *Après les départs anticipés* : une carrière longue et une inaptitude dans
   la grille, chacune à sa part de l'EIR, puis la carrière heurtée ; l'âge de
   la grille reste tenu à chaque pas.
3. *Sur la page Cas types seulement*, hors des agrégats, ce qui demande une
   grille de la page distincte de celle du coût, et une retouche des pages.

Quel que soit le choix, la page dit « treize carrières » en dur (`pages.js`,
« Qui sont ces treize carrières », « Voir treize carrières types »), et
`tests/test_web_revues.py` le fige : à une session des pages, avec
`test_age_conjoncturel.py`, qui compte treize cas types, et la docstring de
`avantages.py` (« aucun ne connaît le chômage »).

**Ce qui reste**, outre ce choix : le biais des cotisants de moins de 50 ans
de `cout.py`, au propriétaire depuis le 14 octobre ; le bilan du compte dans
la table du paquet et sur la page Coût, à une session des pages.
