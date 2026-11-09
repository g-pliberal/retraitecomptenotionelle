# Qui finance quoi, milliard par milliard : les recettes de la retraite en 2026, et ce que la proposition en fait

**Reprise, au 9 novembre 2026.** La table des recettes de 2026 est posée
(« 1. » à « 4. »), sans toucher au modèle ni au site, et le propriétaire en a
tranché toutes les lignes le jour même (décisions 91 à 99, 103 et 104). La table
finale, impôt par impôt, est sous « La table, impôt par impôt » : chaque
impôt retiré aux retraites baisse de moitié sur sa part retraite, l'autre
moitié va au budget général de l'État. Plus aucune question ne l'attend.
Par quoi commencer : une session du modèle porte ces décisions au
scénario 6 (« Ce que les réponses changent au modèle »), la hausse des
fonctionnaires restant hors de la page Coût (décision 98).

*Le 9 novembre 2026, le propriétaire demande, pour le chantier 4 de
l'action 186 : qui finance quoi, milliard par milliard. Le chiffrage
(`docs/chiffrage_plf.md`, hypothèse fragile n° 1) écrit que « le programme ne
dit pas ce que deviennent » les impôts et taxes affectés, 66 Md€ en 2026 ; il
ne le dit qu'en partie pour les versements de l'État et de la branche
famille, 69 Md€. La session a lu trois sources : le rapport à la Commission
des comptes de la sécurité sociale d'octobre 2026, qui donne la prévision de
2026 des régimes de base ; le rapport annuel du COR de juin 2026, qui donne le
système entier en 2025 ; le modèle du dépôt, tel qu'il est, pour 2026. Ses
deux scripts sont restés dans son brouillon, hors du dépôt ; chaque calcul
est posé en « 5. ». La note propose, le propriétaire tranche.*

*Lire les chiffres.* **(publié)** : lu à sa source, citée. **(dépôt)** : sorti
du modèle ou d'un fichier du dépôt, au commit `1c32439`. **(calcul)** : fait
par la session, posé en « 5. ». Les montants sont en milliards d'euros
courants de 2026, sauf mention ; « (p) » marque une prévision.

## L'essentiel

- **La retraite reçoit 428 Md€ en 2026** (dépôt) : 281 de cotisations, 50 de
  contribution d'équilibre de l'État employeur, 66 d'impôts et taxes
  affectés, 17 de transferts, 8 de subventions, 7 d'autres produits. La
  proposition lui en laisse 248 : 236 de cotisations à 18 %, 5 de transferts,
  7 d'autres produits.
- **Sur les 180 Md€ retirés, les décisions en règlent 83** : la baisse des
  cotisations (45), les subventions que l'État garde (8), la taxe sur les
  salaires et le forfait social supprimés (17), la CTA supprimée (1,7), la
  branche famille (11,5, à sa prestation près). Elles en gardent 11 que le
  modèle retire à tort, la TVA de l'Agirc-Arrco, et 5 de plus dans la ligne de
  la branche famille, l'AVPF.
- **Quatre lignes restent ouvertes**, et deux d'entre elles ne sont dans
  aucun chiffrage. La contribution de l'État (50) : le chantier 1 dit que
  l'État la garde, la règle du 20 septembre en rend la moitié aux traitements
  des fonctionnaires, 23,6 Md€ (calcul). Les allègements de cotisations que la
  décision 47 garde (24 à 31) : le modèle encaisse 18 % comme s'ils
  n'existaient plus. Le reste des impôts affectés (36 à 43), dont la règle
  « moitié-moitié » ne dit pas lesquels restent. Et, parmi eux, la CSG de
  l'ancien fonds de solidarité (22), qui paie aujourd'hui les droits du
  chômage et de la maladie que la décision 7 garde.
- **Le solde public consolidé de 2026 n'est pas le solde de la retraite.**
  La retraite, garantie comprise, perd 76 Md€ par rapport au droit en
  vigueur. Toutes administrations ensemble, l'écart va de + 2 Md€, si tout
  impôt affecté est supprimé, à + 67, si l'État les garde tous (calcul). Sous
  les décisions telles qu'elles sont écrites, il est de + 39 ; de − 15 à − 9
  une fois comptés les traitements et les allègements ; et, tout compté, de
  + 4 à + 24 avec la taxe sur la valeur du terrain.
- **Trois faits nouveaux, lus aux sources.** La Cnav ne reçoit aucune TVA :
  la « part de TVA des retraites » de la décision 79 est celle de
  l'Agirc-Arrco, 7,4 Md€ en 2025 et 11 en 2026 (calcul sur publié). La CTA
  rapporte 1,67 Md€ en 2026 (publié), ce que la note du 9 novembre cherchait.
  La CSG sur les revenus de remplacement affectée à la retraite, celle des
  pensions pour l'essentiel, vaut 9,7 Md€ (publié) : la supprimer rendrait
  560 € par an à chaque retraité, la « petite baisse » de la décision 89.

## 1. La table des recettes de 2026

### 1.1 Les totaux : le modèle, et les deux sources

| Poste | Modèle, 2026 (dépôt) | COR, 2025 (publié) | CCSS, régimes de base, 2026 (p) (publié) |
|---|---:|---:|---:|
| Cotisations | 280,9 | 277,0 | 170,1 |
| Contribution d'équilibre de l'État employeur | 50,0 | 49,3 | 50,0 |
| Impôts et taxes affectés, CSG comprise | 65,6 | 64,7 | 54,3, et 5,9 de cotisations prises en charge par l'État |
| Subventions d'équilibre | 7,8 | 7,7 | 7,6 |
| Transferts d'organismes extérieurs | 16,7 | 16,5 | 14,0, transferts entre régimes compris |
| dont branche famille | 11,5 | 11,2 | 10,8 à la seule Cnav |
| dont Unédic | 4,2 | 3,9 | — (aux complémentaires) |
| Autres produits, produits financiers compris | 7,1 | 7,0 | 1,6 |
| **Total** | **428,1** | **422,2** | **302,5** |
| Dépenses | 433,0 | — | 310,5 |
| Solde | − 5,0 | — | − 8,0 |

Sources : `SoldeAnnuel.postes_ressources("actuel")` du modèle ; COR, rapport
annuel de juin 2026, tableau 2.2, p. 87 ; CCSS d'octobre 2026, tableau 13,
p. 33. Le champ du COR est le système entier, complémentaires comprises ;
celui de la CCSS, les seuls régimes de base, qui font 71 % du total.

### 1.2 Ligne par ligne

Les montants des régimes de base sont ceux de 2026 (p) de la CCSS (publié) :
fiche 4.5 pour la Cnav, 4.8 à 4.15 pour les autres régimes, 5.3 pour les
subventions. La colonne « Décision » renvoie aux décisions de
`docs/feuille_de_route_programme.md`.

**Les cotisations : 281 Md€ (dépôt)**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Cnav, indépendants compris | 110,4 | remplacée par le taux unique de 18 % | réglée : programme |
| Salariés agricoles ; exploitants agricoles | 3,5 ; 1,3 | idem | réglée |
| Fonction publique de l'État : agents ; employeurs hors budget général (établissements, La Poste, Orange) | 7,5 ; 7,5 | idem | réglée |
| CNRACL : agents ; collectivités et hôpitaux | 6,6 ; 22,3 | idem ; la caisse est absorbée à la bascule | réglée : 62, 69 |
| SNCF ; IEG ; professions libérales (base) ; autres régimes | 2,0 ; 3,4 ; 3,2 ; 2,6 | idem | réglée |
| **Régimes de base** | **170,1** | | |
| Complémentaires (Agirc-Arrco, Ircantec, indépendants, libéraux, navigants…) | 110,8 (calcul : 280,9 − 170,1) ; 105,4 en 2025 (calcul : 277,0 − 171,6, publiés) | gardent leurs cotisations jusqu'à leur intégration, CEG et CET en moins dès maintenant (près de 18 Md€) ; puis 18 % | réglée : 12, 36, 37, 40, 48 ; le coût les fond encore à la bascule |
| **Ensemble, au taux unique** | **235,8 (dépôt)** | 18 % de 1 310 Md€ d'assiette ; 45,0 de moins | réglée, **sauf les allègements (4.3)** |

Qui gagne : les salariés, la part patronale ne bougeant pas (règle du
20 septembre). C'est 1 500 € par ménage et par an (calcul, sur 30 millions de
ménages). Mais les cinq points du pilier obligatoire, 65,5 Md€ (dépôt), sont
prélevés sur la même assiette : cotisation et pilier ensemble font 301,3 Md€,
soit 20,5 de plus qu'aujourd'hui (calcul). Le salarié type du privé passe
bien de 27,98 % à 23 %, mais le droit en vigueur n'encaisse en moyenne que
21,4 % de l'assiette (dépôt) : allègements, primes des fonctionnaires,
indépendants.

**L'État employeur et les subventions : 58 Md€ (dépôt)**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Contribution d'équilibre du budget général (fonctionnaires civils et militaires) | 49,7 | n'est plus versée ; l'État cotise 18 % comme tout employeur | **ouverte (4.1)** : gardée par l'État selon le chantier 1, rendue pour moitié aux traitements selon la règle du 20 septembre |
| Contribution d'équilibre d'autres employeurs (autres régimes) | 0,2 | n'est plus versée | suit la ligne précédente |
| Dotation de l'État à la Cnav pour les régimes fermés (SNCF, RATP, mines, SEITA) | 5,0 | n'est plus versée ; le régime unique porte ces pensions, recalculées | réglée : l'État la garde (chantier 1, 7 novembre) |
| Subventions directes (ouvriers de l'État 1,7 ; marins 0,8 ; Assemblée nationale 0,1 ; autres 0,1) | 2,7 | idem | réglée : idem |

**La CSG : 22,1 Md€**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| CSG sur les revenus de remplacement (2,94 points sur les pensions) | 9,7 | retirée à la retraite | **ouverte (4.2, 4.4)** |
| CSG sur les revenus du capital | 12,5 | retirée à la retraite | **ouverte (4.2, 4.4)** |

Cette CSG était celle du fonds de solidarité vieillesse, que la Cnav a
absorbé le 1er janvier 2026 (loi de financement pour 2025, article 24). Elle
payait en 2025 les cotisations des périodes de chômage (13,1), de maladie
(2,3) et d'autres périodes (0,3), et le minimum vieillesse (4,2) (publié,
fiche 4.5). Aucune CSG sur les salaires ne va à la retraite
(`restitution.py`, article L. 131-8 du code de la sécurité sociale).

**Les impôts assis sur une rémunération : 17,2 Md€**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Taxe sur les salaires (58,35 % de son produit) | 10,6 | supprimée | réglée : 20 septembre, 29 |
| Forfait social | 6,6 | supprimé | réglée : idem |

C'est une baisse d'impôt des employeurs qui les paient : hôpitaux, banques,
assurances, associations pour la première ; entreprises qui versent
intéressement et participation pour le second. 570 € par ménage si elle
passe entière aux salaires (calcul). Le modèle les compte pour 18,3 Md€ en
2026 (dépôt), 28 % du poste.

**Les autres contributions et impôts de la Cnav : 11,4 Md€**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Contribution sociale de solidarité des sociétés (C3S) | 5,4 | retirée à la retraite | **ouverte (4.2)** |
| Prélèvements sur les stock-options et les actions gratuites | 1,6 | idem | **ouverte (4.2)** |
| Contributions sur les avantages de retraite et de préretraite | 1,4 | idem | **ouverte (4.2)** |
| Taxe spéciale sur les conventions d'assurance et autres taxes | 1,4 | idem | **ouverte (4.2)** |
| Taxes sur les émissions de CO₂ et de polluants des véhicules de société | 0,9 | idem | **ouverte (4.2)** |
| Autres contributions, majorations et pénalités | 0,8 | idem | **ouverte (4.2)** |

Trois de ces lignes, 3,8 Md€, viennent d'être prises à la branche famille
par la loi de financement pour 2026, pour compenser à la Cnav la réduction
générale dégressive unique (publié, p. 32).

**Les taxes des autres régimes : 5,0 Md€**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Droits sur les alcools, base des exploitants agricoles | 2,6 | retirés au régime | **ouverte (4.2)** |
| Droits sur les alcools, complémentaire agricole | 0,6 (2024, note des complémentaires) | la caisse les perd et rejoint le régime général | réglée pour la caisse : 67 ; **la taxe, ouverte (4.2)** |
| Contribution tarifaire d'acheminement (CTA) | 1,67 ; 2,16 en 2025 | supprimée : la facture baisse | réglée : 88 |
| Autres (clercs de notaires, avocats…) | 0,1 | retirées | **ouverte (4.2)** |

La CTA supprimée rend environ 23 € par an sur l'électricité d'un ménage
(note du 9 novembre), 56 € par ménage si l'on y compte le gaz et ce que
paient les entreprises (calcul). La CNIEG dégage encore 0,45 Md€ d'excédent
en 2026 (publié).

**La TVA, et les exonérations que l'État rembourse : 17 Md€, hors des régimes de base pour l'essentiel**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Fraction de TVA versée par l'Urssaf à l'Agirc-Arrco, pour la réduction générale | 11,1 (calcul sur publié) ; 7,4 en 2025 | gardée, affectée en titre | réglée : 47, 79 ; **le modèle la retire encore** |
| Fraction de TVA de la Cnav | 0 (publié) | — | sans objet : voir 1.3 |
| Cotisations prises en charge par l'État (exonérations ciblées compensées), régimes de base | 5,9 | les allègements restent ceux de la loi | **ouverte (4.3)** |

**Les transferts : 16,7 Md€ (dépôt)**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Branche famille : cotisations de l'AVPF | 5,3 | gardées, la branche famille continue de cotiser | réglée : 57 ; **le modèle les retire encore** |
| Branche famille : majorations de pension pour enfants | 5,5 | droit supprimé ; la branche famille garde la somme, et la moitié de ce que coûtaient les droits retirés va aux parents d'aujourd'hui | réglée : 50, 54 ; la prestation, à étudier (51) |
| Unédic : points de retraite complémentaire des chômeurs | 4,2 (dépôt) | gardés : l'assureur du risque paie | réglée : 7, 27 |
| Autres (branche accidents du travail 0,3 ; divers) | 1,0 (dépôt) | gardés | réglée : 7 |

**Les autres produits : 7,1 Md€ (dépôt)**

| Ligne | 2026 | Sous la proposition | Décision |
|---|---:|---|---|
| Produits financiers des réserves ; autres produits | 5,6 ; 1,4 en 2025 (publié) | gardés ; les réserves paient les recettes perdues | réglée : 38 |

**Les recettes nouvelles, que le modèle n'a pas**

| Ligne | Par an | Sous la proposition | Décision |
|---|---:|---|---|
| Taxe sur la valeur du terrain, le point des retraites | 36 à 43 (note du 7 novembre, valeurs de 2025) | recette nouvelle ; 30 à 43 de plus que la taxe foncière, soit 1 000 à 1 400 € par ménage (calcul) | réglée : 80, 81 ; abattement et plafonnement remis |

### 1.3 Trois écarts entre le modèle et les sources

1. **La Cnav ne reçoit aucune TVA.** Son compte n'en porte aucune ligne, et
   toute la TVA de la sécurité sociale va à l'assurance maladie : 49,6 Md€ en
   2025, 45,0 en 2026 (publié, fiches 1.4 et 4.3). La décision 79 attendait
   « la part de la Cnav dans la fraction de la sécurité sociale, qui reste à
   chiffrer » : elle est nulle. La part de TVA des retraites est la seule
   compensation de l'Agirc-Arrco, 11,1 Md€ en 2026, 0,36 point de PIB, et non
   0,23 comme le compte `scripts/lectures_decision_29.py`.
2. **Les lignes publiées de 2026 somment à 73 Md€ d'impôts affectés, le
   modèle en lit 65,6.** La réduction générale dégressive unique, entrée en
   vigueur le 1er janvier 2026, fait passer une dizaine de milliards des
   cotisations aux impôts de compensation : 6,8 à la Cnav, 3,8 à
   l'Agirc-Arrco (publié, p. 67). Le modèle reconduit la structure de 2025 du
   COR, qui ne le voit pas. Le total des recettes ne bouge pas ; le partage
   entre « cotisations » et « impôts affectés », si.
3. **Le modèle étale 417 Md€ sur une structure de 422.** Les parts du
   tableau 2.2 du COR comptent les produits financiers (422,2 Md€ en 2025) ;
   le dépôt les applique au total qui les exclut (417,2). Chaque poste est
   minoré de 1,3 % — 273,7 Md€ de cotisations en 2025 au lieu de 277,0 — et
   les « autres produits » portent 5,6 Md€ de produits financiers qui n'y
   sont pas (calcul).

## 2. Ce que les décisions règlent déjà

Sur les 428,1 Md€ du modèle, en 2026 :

| | Md€ | Décisions |
|---|---:|---|
| Gardé par la retraite, et déjà au modèle : cotisations à 18 %, Unédic, autres transferts, autres produits | 248,2 | programme, 7, 27, 38 |
| Gardé par la retraite, pas encore au modèle : TVA de l'Agirc-Arrco, AVPF | 16,4 | 47, 79 ; 57 |
| Rendu aux cotisants : baisse des cotisations | 45,0 | programme, 20 septembre |
| Supprimé : taxe sur les salaires, forfait social, CTA | 18,9 | 20 septembre, 29, 88 |
| Gardé par son payeur : subventions de l'État ; majorations pour enfants de la branche famille | 14,0 | chantier 1 ; 50, 54 |
| **Ouvert : contribution d'équilibre de l'État** | **50,0** | 4.1 |
| **Ouvert : le reste des impôts affectés, selon qu'on lit le modèle ou les lignes publiées** | **35,6 à 42,7** | 4.2, 4.4 |

Les cinq premières lignes et la contribution font 392,5 ; le reste, 35,6,
est ce que le modèle laisse d'impôts affectés une fois ôtées la TVA, la taxe
sur les salaires, le forfait social et la CTA (65,6 − 11,1 − 17,2 − 1,7).
Les lignes publiées en donnent 42,7 : 22,1 de CSG, 11,4 à la Cnav, 3,3 de
droits sur les alcools et de petites taxes, 5,9 de cotisations prises en
charge par l'État. Et une ligne ouverte n'apparaît dans aucune colonne : les
allègements, 24 à 31 Md€, que le modèle compte comme encaissés (4.3).

## 3. Le solde public consolidé

Le solde de la retraite perd ce que d'autres administrations cessent de lui
verser ; elles le gardent, et le solde de toutes les administrations
ensemble n'en bouge pas. Le pont part de l'écart du fait central et ajoute,
ligne à ligne, ce qui reste dans une autre caisse publique. Variante
rétroactive, 2026, par rapport au droit en vigueur ; « + » améliore le
solde public.

| | Md€ | Cumul |
|---|---:|---:|
| Écart de solde de la retraite, garantie comprise (dépôt) | − 76,1 | − 76,1 |
| L'État garde sa contribution (50,0) et ses subventions (7,8) ; la branche famille, ses transferts (11,5) (dépôt) | + 69,2 | − 6,9 |
| Les employeurs publics de titulaires versent 13,05 % du traitement au lieu de 29,8 Md€ (calcul) | + 13,3 | + 6,4 |
| Ils versent la part patronale du pilier, 3,62 % (calcul) | − 4,6 | **+ 1,8** |

**+ 1,8 Md€ : le plancher.** C'est le solde consolidé si tous les impôts
affectés sont supprimés, les traitements inchangés et les allègements
abolis, comme le coût le compte. La retraite y perd 76 Md€ ; les
administrations ensemble, rien. Chaque euro d'impôt affecté que l'État
continue de lever s'y ajoute :

| Ce que deviennent les 65,6 Md€ d'impôts affectés | Encore levé | Solde consolidé |
|---|---:|---:|
| Tous supprimés | 0 | + 1,8 |
| La règle du 20 septembre sur le poste entier, CTA supprimée en plus | 31,1 | + 32,9 |
| **Les décisions telles qu'elles sont écrites** : TVA gardée à la retraite (79), CTA supprimée (88), le reste partagé par moitié | 37,5 | **+ 39,3** |
| Tous gardés par l'État, sauf la CTA | 63,9 | + 65,7 |

Puis ce que les décisions engagent et qu'aucun chiffrage ne compte :

| | Md€ | Cumul |
|---|---:|---:|
| Les décisions telles qu'elles sont écrites | | + 39,3 |
| La moitié de la contribution d'équilibre rendue aux traitements (règle du 20 septembre, calcul) | − 23,6 | + 15,7 |
| Les allègements gardés (décision 47) : les employeurs du privé versent moins que 18 % (calcul) | − 24,3 à − 30,9 | − 15,2 à − 8,6 |
| La prestation aux parents, moitié des droits familiaux retirés (décision 50 ; note des enfants, à côté) | − 2,7 | − 17,9 à − 11,3 |
| Les prélèvements sociaux sur les pensions qui ne sont plus servies, 6,9 % de 117,6 (calcul sur dépôt) | − 8,1 | − 26,0 à − 19,4 |
| La taxe sur la valeur du terrain, nette de la taxe foncière (décisions 80 et 81 ; note du 7 novembre) | + 30 à + 43 | **+ 4,0 à + 23,6** |

Si l'État garde toute sa contribution, comme l'écrit le chantier 1, chaque
cumul remonte de 23,6 : + 27,6 à + 47,2 en bout de table.

Ce que le pont ne compte pas : l'impôt sur le revenu que les pensions non
servies ne paient plus ; ce qui revient en cotisations, en CSG et en impôt
sur les traitements relevés ; les cotisations des employeurs publics de
contractuels, à peu près neutres ; la part de La Poste et d'Orange, qui ne
sont pas des administrations, dans les 7,5 Md€ des employeurs hors budget
général ; le comportement. La variante prospective part de − 172 au lieu de
− 76 (fait central) ; les autres lignes sont les mêmes.

## 4. Les lignes ouvertes, et leurs options

### 4.1 La contribution d'équilibre de l'État : 50,0 Md€

Deux règles du dépôt se contredisent. Le chantier 1, le 7 novembre :
« l'État garde les 58 Md€ qu'il ne verse plus ». La règle du 20 septembre,
que le simulateur applique à chaque fiche de paie (`remuneration.py`,
`Incidence.PARTAGEE`) : la moitié de ce que l'employeur public cesse de
verser remonte dans le traitement, sauf ce qui payait des départs anticipés.
Le coût, lui, ne compte aucune hausse de traitement.

| Option | Pour les fonctionnaires | Coût public, 2026 | Solde consolidé (depuis + 39,3) |
|---|---|---:|---:|
| A. L'État garde tout (chantier 1) | traitement inchangé ; le simulateur est à corriger | 0 | + 39,3 |
| B. La moitié rendue, État, hôpitaux et collectivités (règle du 20 septembre) | + 27,5 % pour un civil de l'État, + 32,4 % pour un militaire, + 9,0 % à la CNRACL, hors primes | 23,6 | + 15,7 |
| C. La moitié rendue par le seul État | les mêmes, sans la CNRACL | 18,3 | + 21,0 |

B fait 790 € par ménage et par an, mais pour les seuls agents titulaires ;
elle vaut 1,8 point de taux unique (calcul). Le site montre déjà
B dans le simulateur ; la page Coût montre A.

### 4.2 Les impôts affectés qui ne sont assis sur aucun salaire : 36 à 43 Md€

La règle du 20 septembre partage le poste par moitié : la taxe sur les
salaires et le forfait social supprimés, le solde de la moitié rendu par une
baisse de la CSG sur les salaires, l'autre moitié « éteint de la dette ».
Les décisions 79 et 88 l'ont entamée sans dire si la moitié se compte avant
ou après elles, et aucune ne dit quels impôts l'État garde.

| Option, 2026 | Baisse d'impôt | dont CSG sur les salaires | L'État garde |
|---|---:|---:|---:|
| A. La moitié du poste entier (le modèle) ; TVA et CTA prises sur la moitié gardée | 32,8, et 1,7 de CTA | − 1,12 point, 14,5 Md€ | 20,0, et 11,1 de TVA à la retraite |
| B. La moitié de ce qui reste après la TVA et la CTA | 26,4, et 1,7 de CTA | − 0,62 point, 8,1 Md€ | 26,4, et 11,1 de TVA à la retraite |
| C. La baisse va aussi aux retraités : la taxe sur les salaires et le forfait social supprimés, et la CSG sur les pensions affectée à la retraite à la place de la baisse de CSG sur les salaires | 28,0, et 1,7 de CTA | aucune ; − 2,94 points sur les pensions, 9,7 Md€ | 24,8, et 11,1 de TVA à la retraite |

Par ménage et par an (calcul, 30 millions de ménages) : A rend 1 090 €,
dont 485 € par la CSG, soit 11 € par mois pour 1 000 € de salaire brut ; B
rend 880 €, 6 € par mois pour 1 000 € de brut. C rend 560 € par an à chacun
des 17,3 millions de retraités (dépôt), 47 € par mois : c'est la « petite
baisse » de la décision 89, face à une pension de 1 500 € qui perd 420 € par
mois (note de la CTA). Les salariés y perdent la baisse de CSG de B,
8,1 Md€ ; l'État y garde 1,6 Md€ de moins.

Sous B, les 26,4 Md€ gardés sont du même ordre que ce qui n'est assis ni
sur un salaire ni sur une pension, 26,2 Md€ : CSG du capital 12,5, C3S 5,4,
alcools 3,2, stock-options 1,6, avantages de retraite 1,4, assurances et
véhicules 2,3 (publié). Ce serait une façon de le dire : la proposition supprime ce
que paient le travail et, sous C, les retraités ; l'État garde ce que paient
le capital et la consommation.

### 4.3 Les allègements que la décision 47 garde : 24 à 31 Md€

En 2026, la réduction générale efface 19,8 Md€ de cotisations de la branche
vieillesse et 11,1 de l'Agirc-Arrco ; l'État rembourse en outre 5,9 Md€
d'exonérations ciblées (publié, fiche 1.6). Les impôts affectés compensent
les premières, la TVA les secondes. La décision 47 garde ces allègements, la
79 garde la TVA de l'Agirc-Arrco, et rien n'est dit de la compensation de la
base. Le modèle prélève 18 % sur toute l'assiette, comme s'il n'y avait plus
d'allègement, alors que la fiche de paie du simulateur les applique encore.
Sur la part patronale de la proposition, 13,05 points au lieu de 16,58, ils
vaudraient 24,3 Md€ ; 30,9 s'ils restent ce qu'ils sont (calcul).

| Option | La retraite | L'État | Le coût du travail au SMIC |
|---|---|---|---|
| A. Gardés et compensés à la retraite, « en titre », comme la TVA de la décision 79 | encaisse ses 18 % : le coût ne change pas | paie 24 à 31 Md€ ; il ne lui reste rien, ou presque, de la moitié gardée sous 4.2 B | inchangé |
| B. Gardés, non compensés | perd 24 à 31 Md€, 1,9 à 2,4 points de taux unique | garde sa moitié | inchangé |
| C. Supprimés sur la cotisation de retraite | encaisse ses 18 % | garde sa moitié | monte de 13 points de salaire brut ; la décision 47 est défaite |

Sous A comme sous B, le solde consolidé est de 24 à 31 Md€ sous celui du
pont : seul change qui porte le manque, l'État ou la retraite. Sous C, il
est celui du pont, et ce sont les employeurs de salariés proches du SMIC
qui paient.

### 4.4 La CSG de l'ancien fonds de solidarité : 22,1 Md€

Elle payait les cotisations de retraite des chômeurs et des malades, 15,7 Md€
en 2025, et le minimum vieillesse, 5,3 Md€ en 2026 avec les autres régimes
(publié). La décision 7 garde les droits des accidents de la vie, « l'assureur
du risque » les payant (chantier 3, décision 27) ; le modèle, lui, retire ces
droits et leur recette. La garantie vieillesse, payée par l'impôt, remplace
le minimum vieillesse et coûte 13,9 Md€ nets en 2026 (dépôt).

| Option | Qui paie les cotisations du chômage et de la maladie | La CSG (22,1) |
|---|---|---|
| A. La CSG reste affectée, en titre, aux droits des accidents de la vie et à la garantie | la CSG, comme aujourd'hui : 15,7 aux comptes, le reste à la garantie | gardée à la retraite |
| B. L'assureur du risque paie | l'Unédic, de l'ordre de 13 Md€ de plus ; l'assurance maladie, 2,3 | suit 4.2 : gardée par l'État ou rendue |
| C. Les droits ne sont plus portés au compte (le modèle) | personne | suit 4.2 |

B déplace un déficit de 15 Md€ vers l'Unédic et l'assurance maladie sans
changer le solde consolidé ; C défait la décision 7. Sous A, si la moitié
rendue de 4.2 B ne change pas, l'État ne garde plus que 4,3 Md€
(26,4 − 22,1).

### 4.5 Les petites lignes

- **Les droits sur les alcools**, 3,2 Md€ : la décision 67 les retire à la
  complémentaire agricole sans dire si la taxe baisse. Gardés par l'État
  (dans la moitié de 4.2), ou supprimés avec la CTA au titre des « petites
  baisses » : 105 € par ménage et par an (calcul).
- **La branche famille**, 6,2 Md€ qu'elle ne verse plus : la prestation aux
  parents (décision 51) est à étudier ; la note des enfants en chiffre la
  moitié à 2,7 Md€ en 2026.
- **L'excédent de la CNIEG**, 0,45 Md€ en 2026 après 0,93 en 2025 (publié) :
  la CTA rapportait plus que ce qu'elle payait ; la décision 88 le règle.

## 5. Les calculs, posés

Le PIB de 2026 est celui du modèle, 3 065 Md€ ; l'assiette des cotisations,
1 310 Md€ (235,8 ÷ 18 %), si bien qu'un point de taux unique vaut 13,1 Md€.

- **L'écart de solde de la retraite.** Droit en vigueur : 428,1 − 433,0 =
  − 5,0. Proposition : 248,2 − 315,4 = − 67,2 ; moins la garantie nette,
  14,1 − 0,2 = 13,9 : − 81,1. Écart : − 81,1 + 5,0 = − 76,1. Recettes
  retirées : 428,1 − 248,2 = 179,9 ; dépense retirée : 433,0 − 315,4 − 13,9
  = 103,7.
- **La TVA de l'Agirc-Arrco.** Les allègements généraux hors régimes de base
  (Unédic, Agirc-Arrco, FNAL) valent 12,587 Md€ en 2025 et 18,910 en 2026
  (publié). La part de l'Agirc-Arrco dans le coefficient est de 6,01 points
  sur 10,2 (note des complémentaires) : 0,589 × 12,587 = 7,4 ; 0,589 ×
  18,910 = 11,1. Recoupement : 7,4 + 3,8 d'effet de la réduction dégressive
  unique (publié) = 11,2.
- **Les traitements.** La retenue des agents est de 11,10 % : 7,464 ÷ 0,111
  = 67,2 Md€ de traitements à l'État, 6,584 ÷ 0,111 = 59,3 à la CNRACL,
  126,6 en tout. Les employeurs versent aujourd'hui 7,5 + 22,3 = 29,8 de
  cotisations réelles, hors contribution d'équilibre ; à 13,05 %, 16,5 :
  13,3 de moins. Le pilier : 3,62 % × 126,6 = 4,6.
- **La moitié rendue aux traitements.** La formule de `brut_partage`, sans
  primes : le traitement devient [1 + t − g − ½ × (t − p − g)] ÷ (1 + p),
  où t est le taux d'équilibre, p = 16,67 % la part patronale de la
  proposition, pilier compris, et g ce qui payait des départs anticipés.
  Civils : t = 82,28 %, g = 1,5 point : 1,4873 ÷ 1,1667 = + 27,5 %.
  Militaires : t = 126,07 %, g = 33,8 points : 1,5447 ÷ 1,1667 = + 32,4 %.
  CNRACL : t = 37,65 %, g = 0 : 1,2716 ÷ 1,1667 = + 9,0 %. Les militaires
  font 10,8 des 50,4 Md€ de la contribution de 2023 (COR, p. 85) : 10,7 Md€
  en 2026, soit 8,5 de solde ; les civils, 39,1 ÷ 0,8228 = 47,5 de
  traitement, et 9,1 chez les employeurs hors budget général. D'où
  56,6 × 0,275 + 8,5 × 0,324 + 59,3 × 0,090 = 15,6 + 2,7 + 5,3 = 23,6.
- **La restitution**, par `Restitution(...).annuelle(2026)`, la part rendue
  changée en mémoire : à 0,5, 32,8 rendus, dont 18,3 de taxe sur les
  salaires et de forfait social et 14,5 par 1,12 point de CSG ; à 1, 65,6
  rendus et 3,64 points de CSG. Sous 4.2 B : 65,6 − 11,1 − 1,7 = 52,8, dont
  la moitié, 26,4 ; (26,4 − 18,3) ÷ 13,1 = 0,62 point.
- **Les allègements.** 19,8 + 11,1 = 30,9 ; × 13,05 ÷ 16,58 = 24,3, où
  16,58 points sont la part patronale de retraite que la réduction efface
  aujourd'hui (10,57 à la Cnav, 6,01 à l'Agirc-Arrco).
- **Par ménage** : le montant divisé par 30 millions de ménages, un ordre de
  grandeur à relire à l'Insee. La CSG sur les pensions : 9,66 Md€ ÷ 17,3
  millions de retraités = 560 € par an.

## Ce qui reste à faire

- Une session du modèle, après les réponses : la TVA de l'Agirc-Arrco et
  l'AVPF gardées au scénario 6 ; la CTA ôtée ; la LVT versée ; les trois
  écarts de 1.3 ; la table E de `docs/chiffrage_plf.md` et son hypothèse
  n° 1, qui pourra dire ce que devient chaque ligne.
- Refaire au modèle la hausse des traitements, primes comprises, sur les
  effectifs par statut, et la part des allègements qui survit à 18 %.
- Lire les comptes de 2025 de l'Agirc-Arrco, de l'Ircantec et des autres
  complémentaires, dont aucune source lue ne donne les recettes ligne à
  ligne : le communiqué de l'Agirc-Arrco ne publie son tableau qu'en image.
- Relire à l'Insee le nombre de ménages.

## Sources

- Commission des comptes de la sécurité sociale, *Les comptes de la sécurité
  sociale, résultats 2025, prévisions 2026 et 2027*, octobre 2026 : tableau
  13, p. 33 ; fiches 1.4 et 1.6, p. 58 à 67 ; fiche 4.5, p. 174 à 177 ;
  fiches 4.8 à 4.15 ; fiche 5.3.
  https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf
- COR, rapport annuel de juin 2026, partie 2, chapitre 2, p. 79 à 89, dont
  le tableau 2.2.
  https://www.cor-retraites.fr/sites/default/files/2026-06/RA_Part2_Chap2.pdf
- Agirc-Arrco, communiqué du 31 mars 2026 sur les résultats de 2025.
  https://www.agirc-arrco.fr/storage/20260331_CP_Resultats-Agirc-Arrco-2025.pdf
- Dépôt : `src/retraite_notionnelle/cout.py` (`postes_ressources`),
  `restitution.py`, `remuneration.py` (`brut_partage`), `config.py`
  (`part_rendue_aux_salaires`, `part_salariale_taux_unique`) ;
  `data/reference/regimes/effectifs_retraites.csv` ;
  `data/reference/macro/pensions_brutes_nettes.csv` ; les notes
  `2026-11-07-recettes-tva-lvt.md`, `2026-11-07-deux-lectures-au-modele.md`,
  `2026-11-07-complementaires-etude.md`, `2026-11-07-enfants-regle-par-regle.md`
  et `2026-11-09-cta.md`.

## Les six questions, telles qu'elles ont d'abord été posées

1. **La contribution d'équilibre de l'État, 50 Md€ (4.1).** L'État la garde
   en entier, comme l'écrit le chantier 1, ou en rend la moitié aux
   traitements, comme le fait le simulateur depuis le 20 septembre :
   23,6 Md€, + 27,5 % pour un fonctionnaire civil de l'État. La session
   propose A, l'État garde tout : c'est ce que la page Coût compte, et une
   hausse d'un quart des traitements ne se défend pas à côté d'une baisse des
   pensions.
2. **La moitié des impôts affectés, avant ou après la TVA et la CTA (4.2).**
   La session propose B : la moitié de ce qui reste, 26,4 Md€ rendus et
   autant gardés.
3. **À qui va la baisse (4.2).** Aux salariés, par la CSG sur les salaires,
   ou aux retraités, par la CSG sur les pensions : 560 € par an et par
   retraité, de quoi chiffrer la décision 89. La session propose C.
4. **Les allègements, 24 à 31 Md€ (4.3).** Compensés à la retraite par
   l'État, comme la TVA de la décision 79 ; gardés sans compensation ; ou
   supprimés sur la cotisation de retraite. La session propose A, en
   sachant qu'elle prend à l'État toute la moitié qu'il gardait.
5. **La CSG de l'ancien fonds de solidarité, 22 Md€ (4.4).** Affectée en
   titre aux droits du chômage et de la maladie et à la garantie ; ou ces
   droits payés par l'Unédic et l'assurance maladie ; ou plus portés au
   compte. La session propose A.
6. **Les droits sur les alcools, 3,2 Md€ (4.5).** Gardés par l'État, ou
   supprimés avec la CTA.

Les propositions 2, 4 et 5 ne tiennent pas ensemble sans arbitrage : les
allègements compensés (24 à 31) et la CSG gardée à la retraite (22)
dépassent ce que la moitié gardée laisse à l'État (26,4). C'est le vrai
choix de ce chantier : ce que la proposition rend en baisses d'impôt, elle
ne l'a plus pour payer les allègements et les droits des accidents de la
vie qu'elle garde.

## Le même jour : ce que le propriétaire a répondu, et les limites corrigées

Le propriétaire, à la lecture des six questions : « Il faut poser des
questions plus claires. C'est vraiment compliqué. Je suis un humain, je ne
comprends pas les choses implicites. » Et, une par une :

1. « Pourquoi le chantier 1 la garde ? C'est bizarre. »
2. « Précise la question. »
3. « À tous. »
4. « Les allègements de cotisations existent toujours. Il faudrait peut-être
   aller dans le détail. »
5. « Je ne comprends pas la question. »
6. « On garde pour l'État mais on ne dirige plus vers les retraites. »

**Ce qui est tranché.** La baisse d'impôt va à tous, salariés et retraités
(décision 91) ; reste à dire comment elle se partage, question 3 ci-dessous.
Les droits sur les alcools, 3,2 Md€, restent à l'État et ne vont plus aux
retraites (décision 92) : ils entrent dans la moitié que l'État garde. Les
allègements restent (décision 47, confirmée) ; leur détail est ci-dessous.

**Pourquoi « le chantier 1 la garde » : une erreur de rédaction, pas une
décision.** Le propriétaire n'a jamais décidé que l'État garderait sa
contribution. Sa décision est celle du 20 septembre 2026 (action 59,
archivée) : « on a enlevé les impôts et taxes affectées ainsi que les
contributions de l'État. Il ne faut pas que ces baisses d'impôts servent
uniquement à combler le déficit. Il faut aussi que les salaires soient
augmentés. » Le dépôt l'a traduite ainsi : la moitié de ce que l'État cesse
de verser pour les pensions de ses fonctionnaires augmente leur traitement.
Le simulateur le fait. La page Coût ne compte pas cette hausse. La note du
chantier 1, le 7 novembre, a décrit ce que compte la page Coût par la phrase
« l'État garde les 58 Md€ », et la note du chantier 4 l'a reprise comme une
réponse du propriétaire. La proposition A de la question 1 du matin, « l'État
garde tout », allait donc contre une décision prise : elle est retirée.

**Les allègements, dans le détail.** Un salarié au SMIC gagne 1 823 € brut
par mois en 2026 (dépôt). Sous la proposition, la retraite doit recevoir
18 % de ce salaire, 328 € par mois, et son compte est crédité de ces 328 €
(modèle, `scripts/partage_taux_unique.py`) :

| Au SMIC, par mois | Doit | Paie |
|---|---:|---:|
| Le salarié, 4,95 points | 90 € | 90 € |
| L'employeur, 13,05 points | 238 € | 0 € : l'allègement les efface |
| **La retraite** | **328 €** | **90 €** |

Il manque 238 € par mois. Aujourd'hui, c'est pareil : l'employeur d'un
salarié au SMIC ne paie rien de sa cotisation de retraite, et l'État verse
la somme à sa place, avec les impôts affectés aux retraites — ceux-là mêmes
que la proposition leur retire. L'allègement diminue quand le salaire monte
et s'éteint à 3 SMIC. Sur tous les salaires, les 238 € du SMIC deviennent
24 à 31 Md€ par an (calcul, « 4.3 »). Le modèle compte les 328 € comme
encaissés, sans dire qui les verse.

**Les limites, corrigées.**

- *Le nombre de ménages* est lu à l'Insee : 30 907 289 ménages, France hors
  Mayotte, au recensement de 2022 (publié). Les montants par ménage de la
  note, calculés sur 30 millions, baissent de 3 % : 1 460 € au lieu de 1 500
  pour la baisse des cotisations, 560 € au lieu de 570 pour la taxe sur les
  salaires et le forfait social, 54 € pour la CTA, 970 à 1 390 € pour la
  taxe sur la valeur du terrain, 760 € pour la hausse des traitements,
  1 060 € et 850 € pour les options A et B de « 4.2 », dont 470 € par la CSG
  sous A (calcul).
- *Les recettes de l'Agirc-Arrco* sont lues à son communiqué du 31 mars
  2026, dont le tableau n'est publié qu'en image : 103,3 Md€ de ressources
  en 2025, 103,0 de charges, un résultat technique de 0,3 et un résultat
  financier de 1,1 (publié). En ôtant la TVA (7,4), les points des chômeurs
  payés par l'Unédic (3,8) et les cotisations que lui verse la CNIEG (1,4),
  il reste 90,7 Md€ de cotisations (calcul). Les autres complémentaires font
  donc 105,4 − 90,7 = 14,7 Md€ de cotisations (calcul) ; le dépôt leur
  donne, sur la projection du COR de 2024, 16,6 Md€ de ressources en 2025,
  produits financiers compris : libéraux 6,0, Ircantec 4,9, indépendants
  3,1, exploitants agricoles 1,1, avocats 0,9, navigants 0,6 (dépôt). Leurs
  comptes de 2025, caisse par caisse, restent à lire.
- *Les trois écarts entre le modèle et les sources* (« 1.3 ») ne sont pas
  corrigés ici : les corriger, c'est changer les données du modèle, ce que
  cette session n'a pas à faire. Ils attendent la session du modèle.

## Les cinq questions, reposées en clair

Cinq questions. Pour chacune : ce qui se passe aujourd'hui, la question, et
ce que change chaque réponse. Les montants sont ceux de 2026, par an.

**Question 1. Les fonctionnaires sont-ils augmentés ?**

- *Aujourd'hui.* L'État verse 50 Md€ par an pour payer les pensions de ses
  anciens fonctionnaires ; les hôpitaux et les collectivités, 22 Md€. Sous
  la proposition, ils cotisent 18 % comme tout employeur, et gardent la
  différence.
- *Votre décision du 20 septembre* rend la moitié de cette différence aux
  fonctionnaires en activité, en salaire.
- *La question.* Confirmez-vous cette hausse ?
- *Si oui* : un fonctionnaire civil de l'État gagne 27,5 % de plus, un
  militaire 32,4 %, un agent d'hôpital ou de mairie 9 %. Cela coûte
  23,6 Md€, que la page Coût ne compte pas encore.
- *Si non* : les traitements ne bougent pas, l'État et les autres employeurs
  publics gardent tout, et le simulateur est corrigé.
- *Entre les deux* : oui pour l'État seul, 18,3 Md€ ; ou une part plus
  petite que la moitié.

**Question 2. La moitié des impôts rendue : la moitié de quoi ?**

- *Aujourd'hui.* 66 Md€ d'impôts vont aux retraites. Votre règle du
  20 septembre : la moitié est rendue en baisses d'impôt, l'autre moitié
  reste à l'État.
- *Depuis, deux exceptions décidées.* 11 Md€ de TVA restent aux retraites
  (décision 79). La CTA, 1,7 Md€, est supprimée (décision 88).
- *La question.* La moitié se compte-t-elle sur les 66 Md€ du départ, ou sur
  les 53 Md€ qui restent une fois ces deux exceptions mises de côté ?
- *Sur 66* : 33 Md€ de baisses d'impôt ; il reste 20 Md€ à l'État.
- *Sur 53* : 26 Md€ de baisses d'impôt ; il reste 26 Md€ à l'État.

**Question 3. « À tous » : combien pour les salariés, combien pour les retraités ?**

- *Ce qui est acquis.* Dans la baisse, 18 Md€ suppriment deux impôts que
  paient les employeurs sur les salaires (taxe sur les salaires, forfait
  social). Il reste à rendre 8 Md€ (si la question 2 donne 26) ou 14,5 Md€
  (si elle donne 33).
- *La question.* Comment partager ce reste entre salariés et retraités ?
- *Le même nombre de points de CSG pour tous* : la CSG baisse de 0,5 point
  sur les salaires et sur les pensions (0,9 point si le reste est de
  14,5 Md€). Un salarié gagne 5 € par mois pour 1 000 € de salaire brut ;
  un retraité, 7 € par mois pour 1 500 € de pension (9 € et 13 € à 0,9
  point) (calcul).
- *Tout aux retraités* : la CSG sur les pensions baisse de 2,94 points,
  9,7 Md€, soit 47 € par mois en moyenne par retraité ; rien de plus pour
  les salariés. C'est 1,6 Md€ de plus que la moitié de 26.
- *Tout aux salariés* : la CSG sur les salaires baisse de 0,6 point (1,1 si
  le reste est de 14,5 Md€) ; rien pour les retraités, sauf la CTA.

**Question 4. Qui verse la cotisation de retraite que l'allègement efface ?**

- *Aujourd'hui.* L'employeur d'un salarié au SMIC ne paie pas sa cotisation
  de retraite, 238 € par mois. L'État la verse à sa place, avec les impôts
  affectés aux retraites. En tout : 24 à 31 Md€.
- *Ce qui est décidé.* Les allègements restent. Les impôts qui les payaient
  sont retirés aux retraites.
- *La question.* Qui verse ces 238 € par mois à la retraite ?
- *L'État, sur les impôts qu'il garde* : le compte du salarié est plein, la
  retraite reçoit ses 18 %. Mais cela prend à l'État 24 à 31 Md€, à peu
  près tout ce que la question 2 lui laisse.
- *Personne* : le compte du salarié est crédité quand même, et la retraite a
  24 à 31 Md€ de déficit en plus, que les autres cotisants paient.
- *Personne, et le compte n'est crédité que de ce qui est versé* : le
  salarié au SMIC n'acquiert que 90 € de droits par mois au lieu de 328 ; sa
  pension sera plus de trois fois plus basse, et la garantie vieillesse la
  complétera.

**Question 5. Qui paie la retraite des chômeurs et des malades ?**

- *Aujourd'hui.* Une personne au chômage ou en arrêt maladie continue
  d'acquérir des droits à la retraite sans cotiser. Quelqu'un cotise pour
  elle : 15,7 Md€ par an. L'argent vient d'une CSG de 22 Md€, prélevée sur
  les pensions et sur les revenus du capital, qui paie aussi le minimum
  vieillesse.
- *Ce qui est décidé.* Ces droits sont gardés (décision 7). Mais cette CSG
  fait partie des impôts retirés aux retraites.
- *La question.* Qui cotise pour les chômeurs et les malades ?
- *La même CSG, comme aujourd'hui* : elle reste aux retraites, 16 Md€ pour
  ces cotisations et le reste pour la garantie vieillesse. L'État garde
  22 Md€ de moins.
- *L'assurance chômage et l'assurance maladie* : l'Unédic paie 13 Md€ de
  plus par an, l'assurance maladie 2,3. La CSG suit la règle de la
  question 2.
- *Personne* : les chômeurs et les malades n'acquièrent plus de droits
  pendant ces périodes. C'est ce que le modèle fait aujourd'hui, et c'est
  contraire à la décision 7.

**Ce qu'il faut savoir avant de répondre.** Les questions 2, 4 et 5 puisent
dans la même somme : ce que l'État garde des impôts retirés aux retraites,
20 ou 26 Md€. Payer les allègements (24 à 31) et garder la CSG pour les
chômeurs et les malades (22) en demande 46 à 53. Les deux ne tiennent pas
dans la somme : il faut soit rendre moins en baisses d'impôt, soit faire
payer l'un des deux par quelqu'un d'autre.

## Le même jour, ensuite : les cinq réponses

Le propriétaire, aux cinq questions :

1. « Les fonctionnaires sont augmentés du montant qui a été économisé. »
2. « Il faut faire impôt par impôt. On ne redonne la moitié que sur les
   impôts enlevés. »
3. « On ne fait pas de macro comme ça. On fait au cas par cas avec les
   règles existantes. On ne redonne pas de l'argent, on enlève des charges. »
4. « L'État. »
5. « L'assurance maladie et l'assurance chômage. »

Ce sont les décisions 93 à 97 de `docs/feuille_de_route_programme.md`.

### Ce que la session en comprend

- **Les fonctionnaires sont augmentés** (décision 93). La hausse du
  simulateur est confirmée, et la page Coût doit la compter. La phrase se
  lit de deux façons, que la première confirmation ci-dessous départage.
- **Chaque impôt se traite à part** (décisions 94 et 95). Un impôt que les
  retraites gardent ne rend rien. Un impôt retiré aux retraites baisse de
  moitié, pour ceux qui le paient, par son propre taux ; l'État garde
  l'autre moitié. Il n'y a plus de baisse générale de la CSG sur les
  salaires, que la règle du 20 septembre prévoyait (1,12 point).
- **L'État verse la cotisation que les allègements effacent** (décision
  96) : 238 € par mois pour un salarié au SMIC, 24 à 31 Md€ en tout. La
  retraite reçoit bien ses 18 %, comme le modèle le compte.
- **L'assurance chômage et l'assurance maladie cotisent pour les chômeurs et
  les malades** (décision 97) : 13,1 et 2,3 Md€ au tarif de 2025 (publié).

### La table, impôt par impôt

Montants de 2026 (publié, CCSS d'octobre 2026), en Md€. « Retiré » veut
dire : ne va plus aux retraites.

| Impôt | Aux retraites aujourd'hui | Retiré ? | Baisse pour ceux qui le paient | L'État garde | Comment, par sa règle |
|---|---:|---|---:|---:|---|
| TVA versée à l'Agirc-Arrco | 11,1 (calcul) | non (décision 79) | 0 | 0 | rien ne change |
| CTA, sur les factures d'énergie | 1,7 | oui, supprimée en entier (décision 88) | 1,7 | 0 | taux à zéro |
| Droits sur les alcools | 3,2 | oui, gardés en entier par l'État (décision 92) | 0 | 3,2 | rien ne change pour le buveur |
| Taxe sur les salaires, part des retraites | 10,6 | oui | 5,3 | 5,3 | ses taux baissent de 29 % |
| Forfait social | 6,6 | oui | 3,3 | 3,3 | son taux passe de 20 % à 10 % |
| CSG sur les pensions, 2,94 points | 9,7 | oui | 4,8 | 4,8 | 1,47 point de moins sur les pensions |
| CSG sur les revenus du capital, 6,67 points | 12,5 | oui | 6,2 | 6,2 | 3,3 points de moins sur le capital |
| C3S, sur le chiffre d'affaires des sociétés | 5,4 | oui | 2,7 | 2,7 | son taux baisse de moitié |
| Stock-options et actions gratuites | 1,6 | oui | 0,8 | 0,8 | idem |
| Contributions sur les retraites d'entreprise et les préretraites | 1,4 | oui | 0,7 | 0,7 | idem |
| Taxe sur les contrats d'assurance et autres | 1,4 | oui | 0,7 | 0,7 | idem |
| Taxes sur les véhicules de société | 0,9 | oui | 0,45 | 0,45 | idem |
| Autres contributions et petites taxes | 1,0 | oui | 0,5 | 0,5 | idem |
| **Ensemble** | **66,8** | | **27,1** | **28,6** | |

Les exonérations que l'État rembourse déjà aux caisses, 5,9 Md€, ne sont
pas un impôt : il continue de les payer (décision 96).

Ce que cela donne pour une personne (calcul) :

- *Un retraité* : la CSG sur sa pension baisse de 1,47 point, soit 23 € par
  mois en moyenne, 22 € pour 1 500 € de pension au taux plein.
- *Un salarié du privé* : sa cotisation de retraite baisse (de 11,31 à 6,33
  points de son salaire brut) ; sa CSG ne bouge plus. Ce que son employeur
  gagne sur la taxe sur les salaires ou le forfait social ne lui revient
  que si l'employeur le lui rend.
- *Un épargnant* : la CSG sur ses revenus du capital baisse de 3,3 points.
  C'est la plus grosse baisse de la table, 6,2 Md€.

### Les comptes, après ces réponses

| En 2026, Md€ | |
|---|---:|
| L'État garde, des impôts retirés aux retraites | 28,6 |
| L'État verse pour les allègements (décision 96) | − 24,3 à − 30,9 |
| **Il lui reste** | **+ 4,3 à − 2,3** |
| Baisses de charges, tous impôts | 27,1 |
| Hausse des fonctionnaires, de la moitié ; du tout | 23,6 ; 47,3 |
| Charge nouvelle de l'assurance chômage ; de l'assurance maladie | 13,1 ; 2,3 |

Deux choses à voir en face :

- **L'assurance chômage et l'assurance maladie n'ont aucune recette
  nouvelle** pour ces 15,4 Md€. Leur déficit augmente d'autant, ou leurs
  cotisations montent, ou l'État les aide ; mais il ne lui reste rien.
- **La hausse des fonctionnaires n'est payée par aucune recette nouvelle** :
  l'État rend ce qu'il économisait.

Le solde public consolidé (« 3. », refait avec ces réponses, calcul) : il
part de + 40,3 Md€ (le plancher de + 1,8 et les 38,5 Md€ d'impôts encore
levés). La hausse des fonctionnaires de la moitié le ramène à + 16,7 ; les
allègements, à − 14,2 à − 7,6 ; la prestation aux parents et les
prélèvements sur les pensions non servies, à − 25,0 à − 18,4 ; la taxe sur
la valeur du terrain, à **+ 5,0 à + 24,6**. Si les fonctionnaires
reçoivent tout ce qui est économisé, 23,7 Md€ de moins : **− 18,7 à + 0,9**.
Ce que l'assurance chômage et l'assurance maladie versent à la retraite ne
change pas ce total : c'est d'une caisse publique à une autre.

### Ce que les réponses changent au modèle

Pour la session du modèle, rien n'étant fait ici :

- la page Coût compte la hausse des traitements, et les cotisations qu'elle
  rapporte ;
- `restitution.py` et la fiche de paie : la baisse de CSG sur les salaires
  s'en va ; la taxe sur les salaires et le forfait social baissent de
  moitié au lieu de disparaître ; la CSG sur les pensions baisse de 1,47
  point ;
- le scénario 6 garde la TVA de l'Agirc-Arrco et l'AVPF, ôte la CTA, verse
  la LVT ; il crédite les périodes de chômage et de maladie, payées par
  leurs assurances, au prix à fixer : 18 % de l'allocation ou le forfait
  d'aujourd'hui ;
- les trois écarts de « 1.3 ».

## Les deux confirmations demandées

Deux confirmations, chacune en un mot.

**Confirmation 1. Les fonctionnaires : la moitié, ou tout ?**

- *Ce que l'État économise* : il versait 82 % du traitement d'un
  fonctionnaire civil pour payer les pensions ; il n'en versera plus que
  17 %, comme un employeur privé.
- *La règle du 20 septembre* : la moitié de cette économie augmente le
  traitement ; l'autre moitié reste à l'État.
- *Votre phrase d'aujourd'hui* : « augmentés du montant qui a été
  économisé ».
- *La question.* Est-ce la moitié, comme le 20 septembre, ou tout ?
- *La moitié* : + 27,5 % pour un fonctionnaire civil de l'État, + 32,4 %
  pour un militaire, + 9 % pour un agent d'hôpital ou de mairie. Coût :
  23,6 Md€ par an.
- *Tout* : + 55 %, + 65 % et + 18 %. Coût : 47,3 Md€ par an ; l'État ne
  garde rien.

**Confirmation 2. La table impôt par impôt est-elle la bonne lecture ?**

- *Ce que j'ai compris de vos réponses 2 et 3* : chaque impôt retiré aux
  retraites baisse de moitié, pour ceux qui le paient ; l'État garde l'autre
  moitié ; aucune baisse générale de la CSG sur les salaires.
- *Trois conséquences à valider, parce qu'elles changent ce qui était
  prévu* :
  1. la taxe sur les salaires et le forfait social baissent de moitié ; le
     20 septembre, ils étaient supprimés en entier ;
  2. la CSG sur les revenus du capital baisse de 3,3 points, 6,2 Md€ : c'est
     la plus grosse baisse, et elle va aux épargnants ;
  3. la CSG sur les salaires ne baisse plus : le salarié ne gagne que la
     baisse de sa cotisation de retraite.
- *La question.* Oui à la table entière ? Sinon, dites la ligne à changer :
  un impôt peut être supprimé en entier, comme la CTA, ou gardé en entier
  par l'État, comme les alcools.

## Le même jour, enfin : les confirmations, et trois explications

Le propriétaire :

- « Confirmation 1 : la moitié. Cela ne doit pas être dans la page coût car
  c'est le budget général de l'État et non le périmètre des retraites. »
- « Confirmation 2 : pourquoi la taxe sur le salaire et le forfait social ne
  baissent que de moitié ? Quelles différences entre les différentes CSG ? »
- Sur le solde de toutes les administrations : « Tu peux expliquer le
  calcul ? C'est bizarre. »
- « On augmente les cotisations chômage et maladie. »

**Ce qui est tranché** (décisions 98 et 99). Les fonctionnaires reçoivent la
moitié de l'économie, 23,6 Md€ ; cette hausse est une dépense du budget
général de l'État, hors de la page Coût, qui ne compte que les retraites. Les
cotisations chômage et maladie montent pour payer les cotisations de retraite
des chômeurs et des malades : 13,1 et 2,3 Md€ au tarif de 2025. Rapportés aux
salaires du privé (756 Md€ en 2024, note des complémentaires) et à tous les
revenus d'activité (1 310 Md€), c'est de l'ordre de 1,7 point de cotisation
chômage et 0,2 point de cotisation maladie (calcul). Un salarié du privé
gagnait 5 points de cotisation de retraite (de 27,98 à 23) ; il en garde
environ 3.

### Pourquoi la taxe sur les salaires et le forfait social ne baissaient que de moitié

Parce que la session a appliqué la phrase « on ne redonne la moitié que sur
les impôts enlevés » à chaque impôt, un par un, ces deux-là compris. Ce
n'est pas ce que le 20 septembre avait fait : ce jour-là, la moitié se
comptait sur l'ensemble, et ces deux impôts, les seuls que paie un employeur
sur les salaires, étaient supprimés en entier pour atteindre cette moitié.
Les deux lectures se défendent ; elles ne donnent pas la même chose :

| En 2026, Md€ | Ces deux impôts baissent de moitié | Ils sont supprimés en entier |
|---|---:|---:|
| Baisse pour les employeurs qui les paient | 8,6 | 17,2 |
| L'État garde, sur ces deux impôts | 8,6 | 0 |
| L'État garde, tous impôts retirés | 28,6 | 20,0 |
| Il lui reste, les allègements payés (24 à 31) | + 4,3 à − 2,3 | − 4,3 à − 10,9 |

### Les trois CSG

La CSG est un seul impôt, mais son taux et sa destination changent selon le
revenu sur lequel elle est prise (dépôt, `restitution.py` et
`prelevements_remuneration.yaml` ; CCSS pour les montants) :

| La CSG prise sur | Son taux | Ce qui va aux retraites | Qui la paie |
|---|---:|---:|---|
| les salaires | 9,2 % | rien : elle va à la maladie, à la famille, au chômage, à l'autonomie et à la dette sociale | les salariés |
| les pensions | 8,3 % au taux plein ; moins, ou rien, pour les petites pensions | 2,94 points, 9,7 Md€ | les retraités |
| les revenus du capital (loyers, intérêts, dividendes, plus-values) | 10,6 % | 6,67 points, 12,5 Md€ | les épargnants et les propriétaires |

Retirer la CSG aux retraites ne touche donc pas la CSG des salariés : ils
n'en versent aucune aux retraites. Sous la table impôt par impôt, la CSG des
retraités baisse de 1,47 point et celle du capital de 3,3 points.

### Le calcul du solde de toutes les administrations, expliqué

On met dans un seul panier l'État, la sécurité sociale, les caisses de
retraite et les collectivités, et on compte ce qui entre et ce qui sort de
ce panier, vers les ménages et les entreprises ou depuis eux. Ce qu'une
caisse publique verse à une autre ne compte pas : l'argent reste dans le
panier. Par rapport à aujourd'hui, en 2026, en Md€ :

| | Md€ |
|---|---:|
| **Le panier dépense moins** : pensions | + 117,6 |
| **Il dépense plus** : garantie vieillesse 13,9 ; hausse des fonctionnaires 23,6 ; cinq points de capitalisation des agents publics, part de l'employeur 4,6 ; prestation aux parents 2,7 | − 44,8 |
| **Il reçoit moins** : cotisations de retraite des salariés et des employeurs du privé 31,7 ; cotisations que les allègements effacent 24,3 à 30,9 ; baisses d'impôts 27,1 ; CSG et autres prélèvements sur les pensions qui ne sont plus versées 8,1 | − 91,2 à − 97,8 |
| **Total, sans recette nouvelle** | **− 25,0 à − 18,4** |
| **Il reçoit plus** : taxe sur la valeur du terrain, en plus de la taxe foncière | + 30 à + 43 |
| **Total, avec la taxe sur le terrain** | **+ 5,0 à + 24,6** |
| Il reçoit plus : hausse des cotisations chômage et maladie (décision 99) | + 15,4 |
| **Total, après la décision 99** | **+ 20,4 à + 40,0** |

Ce qui pouvait sembler bizarre :

- *Le résultat est une fourchette* parce que deux lignes ne sont connues
  qu'à peu près : les allègements (24 à 31) et la taxe sur le terrain (30 à
  43).
- *Sans la taxe sur le terrain, le panier perd 18 à 25 Md€* : la réforme
  rend plus qu'elle n'économise en 2026. C'est la taxe sur le terrain, un
  impôt nouveau de 30 à 43 Md€ sur les propriétaires, qui fait passer le
  total au-dessus de zéro.
- *Ce n'est pas le solde des retraites*, qui perd 76 Md€ : la différence
  est ce que l'État et la branche famille ne versent plus aux retraites et
  gardent, 69 Md€.
- *« S'ils reçoivent tout »* n'a plus d'objet : c'est la moitié.

Tous ces chiffres sont ceux de la première année, 2026, la baisse des
pensions faite d'un coup comme le modèle la compte ; les 31,7 Md€ sont les
45,0 de baisse des cotisations moins les 13,3 que versaient des employeurs
publics (« 3. »).

## La dernière question, sur deux lignes de la table

Une question, en deux lignes de la table.

**La taxe sur les salaires et le forfait social : de moitié, ou en entier ?**

- *Ce que c'est.* Deux impôts que l'employeur paie sur les salaires qu'il
  verse : la taxe sur les salaires (hôpitaux, banques, assurances,
  associations) et le forfait social (sur l'intéressement et la
  participation). Ensemble, 17,2 Md€ vont aux retraites.
- *De moitié* : 8,6 Md€ de charges en moins ; l'État garde 8,6 et il lui
  reste de quoi payer à peu près les allègements.
- *En entier, comme le 20 septembre* : 17,2 Md€ de charges en moins ; il
  manque alors 4 à 11 Md€ à l'État pour payer les allègements.

**La CSG sur les revenus du capital : de moitié, ou gardée en entier par l'État ?**

- *Ce que c'est.* La CSG prise sur les loyers, les intérêts, les dividendes
  et les plus-values ; 12,5 Md€ vont aux retraites.
- *De moitié, comme les autres impôts* : 3,3 points de CSG en moins pour
  les épargnants, 6,2 Md€. C'est la plus grosse baisse de la table.
- *Gardée en entier par l'État, comme les droits sur les alcools* : rien ne
  change pour les épargnants ; l'État garde 6,2 Md€ de plus. Si la taxe sur
  les salaires et le forfait social sont alors supprimés en entier, il lui
  reste, les allègements payés, entre + 1,9 et − 4,7 Md€ (20,0 + 6,2, moins
  24,3 à 30,9).

## Le même jour, pour finir : la table est confirmée

Le propriétaire, aux deux lignes : « De moitié sur la part retraite. La
moitié est redonnée, l'autre moitié va dans le budget général de l'État. »
La même réponse pour la taxe sur les salaires et le forfait social
(décision 103) et pour la CSG sur les revenus du capital (décision 104).

La table « impôt par impôt » ci-dessus est donc la bonne, sans changement :

- la taxe sur les salaires baisse de la moitié de sa part retraite, 5,3 Md€
  sur 10,6 ; le forfait social, de moitié, 3,3 sur 6,6 ;
- la CSG sur les revenus du capital baisse de la moitié de ses 6,67 points
  de retraite, 3,3 points, 6,2 Md€ ;
- les autres impôts retirés suivent la même règle (décision 94) : la CSG
  sur les pensions, 1,47 point, 4,8 Md€ ; la C3S, 2,7 ; les petites lignes,
  3,2 en tout ;
- trois exceptions décidées : la TVA de l'Agirc-Arrco reste aux retraites
  (79), la CTA est supprimée en entier (88), les droits sur les alcools
  vont en entier à l'État (92).

Les comptes de 2026, tels que ces décisions les laissent (calcul) :

| En Md€ | |
|---|---:|
| Baisses de charges, tous impôts | 27,1 |
| Au budget général de l'État, des impôts retirés aux retraites | 28,6 |
| L'État verse à la retraite pour les allègements (décision 96) | 24,3 à 30,9 |
| Il lui reste, avant la hausse des fonctionnaires | + 4,3 à − 2,3 |
| Hausse des fonctionnaires, au budget général (décision 98) | 23,6 |
| Hausse des cotisations chômage et maladie (décision 99) | 15,4 |
| Solde de toutes les administrations, avec la taxe sur le terrain | + 20,4 à + 40,0 |

## Ce que le propriétaire tranche

Plus rien sur cette table. Deux points lui reviendront quand la session du
modèle les aura chiffrés : le prix de la cotisation que l'assurance chômage
et l'assurance maladie versent pour un chômeur ou un malade, 18 % de
l'allocation ou le forfait d'aujourd'hui (décision 97) ; et le montant
exact des allègements sous le taux unique, que cette note ne connaît qu'entre
24 et 31 Md€.
