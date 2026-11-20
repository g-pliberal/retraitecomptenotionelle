# Étape 2 de la note 0009, troisième session : les droits contrefactuels en couches, les deux copies retirées

**Reprise, au 20 novembre 2026.** L'étape 2 de la note de décision 0009 est
finie : l'âge légal se lit dans les versions de sa fiche, sous le droit en
vigueur comme sous les deux droits d'avant réforme, et ses deux copies sont
parties. C'est le point d'arrêt que la note prévoit. Rien ne se lance avant
que le propriétaire ait décidé de l'étape 3, sur ce que l'étape 2 a coûté :
trois sessions, trois commits, compte plus bas. S'il la lance, commencer par
« Pour l'étape 3 » dans
`/mnt/project-files/architecture/191-briefs-amendes.md`. Au propriétaire
aussi : la fiabilité de l'âge légal sous un droit d'avant réforme est passée
du niveau `haute` au niveau `certifiee` pour les générations que la réforme
écartée déplaçait ; et les fiches qui déclarent une réforme écartée sans que
le droit d'avant réforme les écarte, listées dans les deux couches.

Le 20 novembre 2026, troisième des trois sessions de l'étape 2 (« Brief
A2c »), lancée sur l'accord du propriétaire. Elle suit
`2026-11-19-etape-2-age-legal-le-moteur-lit-les-versions.md`.

**Deux couches, deux piles.** Une couche écarte une réforme (champ `ecarte`,
ajouté au contrat C.4) depuis sa date d'effet (`depuis`) :
`sans_la_suspension_de_2026` et `sans_la_reforme_de_2023`, dans
`data/reference/couches/`. Le droit `loi_2023_sans_suspension` est la
première seule ; le droit `au_31_aout_2023` pose la seconde sur la première
(`DROITS`, dans `src/retraite_notionnelle/donnees/droits_contrefactuels.py`).
Dans la fiche de l'âge légal, chaque couche garde la version d'avant : celle
qui valait la veille de la réforme vaut sans fin, celles qui commencent à sa
date ou après sont ôtées (`remplacer_une_version`). La pile se résout à la
fabrique : le paquet porte la fiche résolue sous chaque droit
(`droits_contrefactuels`, version 47), et le moteur la lit par le lecteur
des versions, le même que sous le droit en vigueur
(`FichesDatees.sousLeDroit`, `ScenarioActuel._sousLeDroit`).

**Rien n'y reste par oubli.** Dix-neuf fiches déclarent la réforme de 2023,
douze la suspension. Chacune est décidée dans la couche : l'âge légal y est
gardé dans sa version d'avant ; la durée requise et la carrière longue
gardent leur mécanisme jusqu'à l'étape 3, et le disent ; l'âge du taux plein
attend l'étape 3 ; les autres sont déclarées hors de la couche (`garder`),
avec leur raison. Un test échoue quand une fiche déclare la réforme sans
être décidée, ou quand la couche décide une fiche qui ne la déclare pas
(`tests/test_couches_du_droit.py`). La liste des piles reste dans le code :
un droit contrefactuel n'est pas un scénario du site, et les univers de
`data/reference/univers/` en sont.

**Ce qui est parti.** Les deux fichiers
`age_ouverture_avant_reforme_2023.csv` et
`age_ouverture_avant_suspension.csv`, leurs deux classes des deux côtés,
leurs deux tables du paquet, leurs deux certifications et leurs deux lignes
du journal de certification, la vue qui les fabriquait (`vue_d_avant`), et
leurs deux noms dans le cliquet des copies, qui n'en nomme plus que deux,
celles de la durée requise. `TableRecouverte` ne recouvre plus que la durée
requise : elle part à l'étape 3. Deux tests qui lisaient la copie de la
suspension lisent la version `loi_de_2023` de la fiche.

**Un résultat a bougé, sous un droit contrefactuel : une correction.** La
copie se posait sur les versions pour toutes les dates. Sous la loi de 2023
sans la suspension, elle opposait donc l'âge de cette loi à une demande
d'avant son entrée en vigueur. Né en 1965, une retraite progressive demandée
en mai 2023 : l'âge légal lu à cette date était de 63 ans et 3 mois, soit un
âge minimal de 61 ans et 3 mois ; il est de 62 ans, soit 60 ans, comme sous
le droit en vigueur, la loi du 14 avril 2023 ne valant que pour les pensions
prenant effet à compter du 1er septembre 2023. La demande reste refusée,
l'assurée ayant 58 ans. C'est le seul écart d'une grille de 7 491 cas
(937 requêtes des témoins et 1 560 carrières simples, sous les trois états
du droit), fiabilités comprises ; les témoins de calcul refaits sont
identiques, octet pour octet. Seul le témoin des pages bouge : la page des
données compte 233 séries certifiées au lieu de 235, les deux copies n'en
étant plus. La garde de l'âge du taux plein reste verte : 67 ans sous les
trois états.

**La fiabilité, au propriétaire.** Les copies étaient au niveau `haute` ; la
version gardée porte le niveau de son texte, `certifiee`. Aucun cas de la
grille ne le montre, mais le lecteur le rend (`AgesOuverture.age`). Revenir
à `haute` demanderait un champ de plus dans la couche.

**La seconde lecture des versions de 1985 à 2011.** Relues dans l'index LEGI
le 20 novembre 2026, sans la note de la première lecture : R. 351-2
(LEGIARTI000006749340, du 21 décembre 1985 au 3 juin 2011, « fixé à soixante
ans », puis LEGIARTI000024113000, qui renvoie à L. 161-17-2) ; L. 161-17-2
(LEGIARTI000023030935, « soixante-deux ans pour les assurés nés à compter du
1er janvier 1956 », applicable « aux pensions prenant effet à compter du 1er
juillet 2011 », puis LEGIARTI000025014605, « nés à compter du 1er janvier
1955 ») ; D. 161-2-1-9 (LEGIARTI000023388636 : 60 ans et 4 mois, 60 ans et
8 mois, 61 ans, 61 ans et 4 mois, 61 ans et 8 mois ; LEGIARTI000025089933 :
60 ans et 9 mois, 61 ans et 2 mois, 61 ans et 7 mois). Les versions
`soixante_ans`, `loi_de_2010` et `loi_de_2011` disent ces âges et ces dates.
Une réserve sans effet : la loi de 2011 vaut du 23 décembre 2011, son décret
du 31 ; aucun premier du mois ne tombe entre les deux. Aucun exemple officiel
n'a été trouvé de plus.

**Ce que l'étape 2 a coûté.** Trois sessions sur Fable 5.2, du 19 novembre
22 h 04 UTC au 20 novembre au soir, un commit chacune. La première : 27
fichiers, 1 848 lignes ajoutées, 83 ôtées. La deuxième : 23 fichiers, 1 078
ajoutées, 170 ôtées. La troisième : une trentaine de fichiers, dont six
nouveaux, environ 700 lignes ajoutées et 350 ôtées, hors paquet ; ouverte à
17 h 11 UTC, elle a refait deux fois le paquet et deux fois les témoins, et
attendu son tour pour publier, deux corrections touchant les mêmes
compteurs. Une seule fiche est migrée, six versions, deux copies retirées
sur quatre. Deux corrections en sont sorties : la retraite progressive lue à
la date de la demande, publiée à part le 20 novembre, et celle de cette
note.
