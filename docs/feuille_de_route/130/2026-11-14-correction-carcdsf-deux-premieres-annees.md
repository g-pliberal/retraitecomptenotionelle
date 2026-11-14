# Correction de la ligne 6 de la file : la CARCDSF dispense la part proportionnelle des deux premières années

Sixième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 11 novembre 2026). Décret n° 50-28,
article 3-1, dans la rédaction de l'article 5 du décret n° 2026-418, en vigueur le
1er juillet 2026 (LEGIARTI000054168193) : « Les nouveaux affiliés sont dispensés de la
cotisation proportionnelle au titre des deux premières années civiles de leur exercice
et peuvent, sur demande écrite, bénéficier également d'une dispense de la cotisation
forfaitaire. » Article 3-5 (LEGIARTI000054168184) : « Les dispenses ou réductions
partielles mentionnées aux articles 3-1 à 3-4 entraînent respectivement la suppression
ou la réduction des droits correspondants. » Article 2 (LEGIARTI000054168195) : une
cotisation forfaitaire « portant attribution de six points », et une proportionnelle
de 0,65 à 5 plafonds. Le texte tranche ce que la ligne dit : la dispense est de droit,
sans condition d'âge, en années civiles, et sans droits ; le forfait reste dû.

**Ce que la relecture a trouvé de plus.** La note de E10 laissait non lu ce que les
statuts disaient avant le 1er juillet 2026, les croyant au seul Bulletin officiel.
L'index LEGI les porte. Les statuts approuvés par l'arrêté du 13 avril 2011
(JORFTEXT000023909782), en vigueur le 1er juillet 2011, écrivent la même dispense dans
les mêmes mots — article 11 (LEGIARTI000023910336, puis LEGIARTI000026210162), « Les
nouveaux adhérents sont dispensés de la cotisation proportionnelle au titre des deux
premières années civiles de leur exercice », et article 16, la suppression des droits
correspondants ; articles 13 et 18 depuis le 25 décembre 2017 (LEGIARTI000036540562,
puis LEGIARTI000036621382). Les statuts d'avant, approuvés par l'arrêté du 1er octobre
2007 (LEGIARTI000023450470), ne dispensaient que « sur demande écrite ». L'erreur de la
ligne valait donc depuis les cotisations de 2012, et la correction les couvre : c'est
la même règle, le même paramètre, et aucun témoin ne porte de dentiste installé depuis
2011.

**Le test d'abord** (`tests/test_sections_sante.py`), vu rouge sur le cas posé
(52 158,40 € servis) :

- `test_la_carcdsf_dispense_la_part_proportionnelle_des_deux_premieres_annees`, cinq
  cas par la requête du formulaire, servis par le portage et refaits au bit près par
  le moteur Python (`servi_et_refait`) : la dentiste du cas posé ; celle qui s'installe
  à 40 ans, dispensée elle aussi ; celles qui s'installent en 2012, en 2011 (la seule
  année 2012 dispensée) et en 2010 (rien) ;
- `test_la_dispense_de_la_carcdsf_retire_1_528_euros_a_la_dentiste_de_26_ans` ;
- `test_le_compte_ne_porte_que_le_forfait_des_deux_premieres_annees_de_la_dentiste`,
  par la lecture du compte au pont, refaite par le moteur Python (`droit_et_refait`).

Les cas de 2012 et de 2011 sont entrés après le paramètre : leurs valeurs d'avant
(35 644,53 € et 34 731,23 €) avaient été relevées, et diffèrent des valeurs posées.

**L'effet au cas posé** : née le 1er janvier 2001, chirurgienne-dentiste au double du
salaire moyen, installée le 1er janvier 2027 à 26 ans, pension à 67 ans. Avant :
876 611,8159 € de cotisations revalorisées × 0,0595 = 52 158,40 € par an. La part
proportionnelle de 2027, 0,1135 × (87 370,5656 − 0,65 × 49 237,47) = 6 284,0648 €
l'année même, × 2,0366 = 12 798,2854 €, et celle de 2028, 12 886,3326 €, ne sont pas
dues : 850 927,1979 × 0,0595 = **50 630,17 € par an**, 1 528,23 € de moins. La base
(31 726,78 €) et les prestations complémentaires de vieillesse (26 394,77 €), que
l'article ne vise pas, ne bougent pas. Au compte notionnel, la complémentaire ne porte
plus que le forfait : 3 266,79 € en 2027 au lieu de 9 550,85 €, 3 323,95 € en 2028.
Installée en 2012 : 34 849,04 € au lieu de 35 644,53 €, 795,50 € de moins.

**La correction.** Le paramètre de la ligne 5, `dispense_de_debut`, prend deux
libertés : `avant_l_age` peut manquer (aucune condition d'âge), et `part:
proportionnelle` ne dispense que la part proportionnelle. Les quatorze périodes de 2012
et d'après de `carcdsf_complementaire.yaml` le portent : `{annees: 2, depuis: 2012,
part: proportionnelle}`. `dispenseDeDebut` (`moteur/js/droit/acquerir.js`) et son
jumeau `dispense_de_debut` rendent ce qui est dispensé — toute la cotisation, sa part
proportionnelle, ou rien ; `acquerir` et le compte (`ConstructeurCompte`) annulent
alors l'assiette de la période avant d'y ajouter le forfait. Le paquet n'écrit que les
clés présentes : l'entrée de la CARMF n'y change pas. Dans la fiche
`decret_2026_418_liberaux`, l'erreur n'est plus déclarée : elle est racontée au champ
`effet`.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page. Le paquet
porte le paramètre quatorze fois de plus. `regenerer.py --verifier` : seuls les
chiffres ancrés du poids du paquet et du moteur sont à refaire, ce que GitHub fait.

**Ce que la correction laisse, déclaré dans la fiche** (`sources.a_relire`).

- L'année 2011 n'est pas dispensée : elle a été appelée sous les statuts de 2007, qui
  ne dispensaient que sur demande, et rien ne dit ce que la caisse en a fait au second
  semestre. Avant le 11 octobre 2007, les statuts ne sont pas lus.
- La dispense du forfait, sur demande écrite, n'est pas portée, ni le rachat des
  points forfaitaires non cotisés (article 3-7, I).
- L'affiliation prend effet « au premier jour du trimestre civil suivant le début » de
  l'activité (article 2) : le modèle compte les années civiles depuis le mois d'entrée
  dans le statut, sans confronter ce décalage.
- Celui qui cesse puis reprend n'est dispensé que depuis sa première entrée.

**La classe, pour les lignes suivantes.** Le paramètre sert tel quel à une dispense de
début d'exercice, entière ou de la seule part proportionnelle, avec ou sans âge. La
ligne 7, l'exemption de la CARMF passé 75 ans, est une autre condition : un âge de fin,
au semestre. Pour la CARMF, les statuts d'avant le 1er juillet 2026 restent à chercher
dans l'index LEGI avant de les dire au seul Bulletin officiel : ceux de la CARCDSF y
étaient.

**Vérifié** : `python -m pytest -m rapide`, `-m site`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py`, `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_pcv_sante.py`,
`test_carte.py`, `test_donnees.py`, les essais de `tests/js/`, verts.
