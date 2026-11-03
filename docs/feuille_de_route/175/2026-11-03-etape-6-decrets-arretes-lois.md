# Étape 6, décrets, arrêtés et lois : les références sans thème, confrontées à la liste des textes et à l'index LEGI

**Reprise, au 3 novembre 2026.** Une nature de l'étape est rangée, les décrets, arrêtés et
lois sans thème : 1 013 des 1 020, sept à lire, nommés ici. Restent, une session par
nature : les 642 articles de code, que la liste de contrôle des textes tient déjà pour
les chapitres de la retraite ; les 496 articles de règlements européens ; les 2 228
circulaires, lettres, instructions et notes, par période ; les 96 autres textes ; les
74 que la base nomme sans les servir ; les 107 accords, avec le thème des accords de
l'étape 4. Commencer par les articles de code, avec la méthode de cette note : la base
relue par l'API, un texte rapproché de l'index par son identifiant Légifrance, puis
par son numéro, jamais par sa seule date.

**Le 3 novembre 2026, ce qui est fait.**

- *La lecture* : les 1 020 références sans thème dont le titre dit un décret, un arrêté,
  une loi, une ordonnance ou un décret-loi — 447, 325, 218, 29 et 1 —, relues par
  l'API, toutes servies, avec l'objet que la base en donne et le lien qu'elle fait vers
  Légifrance. 671 se rapprochent d'un texte des index LEGI et JORF du dépôt, par leur
  identifiant (468), leur numéro (145) ou, pour un arrêté, leur date quand un seul texte
  la porte (58) ; 176 textes, des arrêtés surtout, partagent leur jour avec d'autres, et
  se lisent par l'objet que la base en donne. 27 sont à la liste de contrôle des textes ; 93 sont cités par
  une fiche ou une limite. Par leur numéro seulement : rapprochés aussi par leur date,
  l'ordonnance du 19 octobre 1945 sur la nationalité passait pour celle des assurances
  sociales, et une circulaire « n° 2004/29 » pour le décret du même numéro.
- *Les sorts* : 1 013 références rangées, 661 `limite`, 340 `hors_modele`, 12 `recoupe`.
  Une référence que des fiches ou des limites citent par son numéro prend leurs renvois
  (85). Un texte dont les règles sont devenues des articles des codes que la liste de
  contrôle tient — les décrets de codification de 1985, les lois de financement et les
  lois portant diverses mesures d'ordre social qu'aucune fiche ne cite — renvoie à
  `data/reference/textes/perimetre.yaml` (28) : chaque rédaction de ces articles y
  prend le statut que lui donne sa fiche. Les assiettes forfaitaires et les taux par
  catégorie de salariés vont à `docs/limites/3-systeme-actuel.md` (291), la publication
  d'une convention ou d'un traité européen à la fiche de la totalisation (79), le
  rachat, le versement pour la retraite et les cotisations arriérées à
  `rachats_et_versements` (61), l'assurance volontaire à la caisse des Français de
  l'étranger (41), l'allocation aux vieux travailleurs salariés et le fonds national de
  solidarité aux fiches du minimum vieillesse et des trimestres d'avant 1972. Les douze
  textes qui fixent le plafond de la sécurité sociale, de 1946 à 2012, sont `recoupe`
  par `test_le_plafond_de_la_serie_est_le_salaire_plafond_de_la_caisse` : ceux de 2006,
  2007, 2011 et 2012, lus au JORF, donnent le plafond de la série. Les coefficients de
  revalorisation des pensions de 2004 à 2008, lus au JORF, sont ceux de la série, qui
  cite ces arrêtés. Les décrets du Smic, des taux de cotisation du régime général et
  des minima renvoient aux fiches et à la limite qui portent leurs séries.
- *Hors du modèle*, 340 textes sous 48 raisons : le droit du travail et les contrats
  aidés (35), les règles générales de l'administration (31), le droit civil (30), la
  procédure (26), l'organisation des caisses (25), les lois de finances (20),
  l'assurance maladie (18), l'insertion (14), l'allocation de chômage ou de préretraite,
  dont les trimestres sont aux fiches du chômage (12), les allègements de cotisations
  patronales (10), l'intérêt légal (9), le financement des régimes (8), le veuvage,
  l'invalidité, l'autonomie, le droit des étrangers, les rentes viagères.
- *Sept restent à lire* : `AT_20061946.aspx`, le calcul des rentes de l'assurance
  invalidité-vieillesse locale d'Alsace-Moselle (ordonnance du 18 octobre 1945), que ni
  fiche ni limite ne déclare ; `AT_23031949.aspx` et `DEC_77221_08031977.aspx`, dont la
  base ne dit que l'article appliqué ; `DEC_20051537_08122005.aspx`,
  `DEC_20071729_07122007.aspx`, `DEC_20081288_09122008.aspx` et
  `LOI_72650_11071972.aspx`, dont elle ne sert qu'un titre nu, que l'index social de la
  DILA ne garde pas et que rien ne cite : à lire sur Légifrance.

**Ce que la lecture a trouvé, sans écart.** Aucune valeur lue ne contredit sa série. La
base sert, sous le nom `AT_19122008.aspx` (« Arrêté du 19/12/2008 »), l'arrêté du
21 décembre 2007 sur la revalorisation de 2008, qu'elle sert aussi sous son nom. Deux
silences, rangés sans être déclarés : la cessation progressive d'activité des
fonctionnaires territoriaux (ordonnance n° 82-298), renvoyée à
`temps_partiel_fonction_publique`, qui ne la nomme pas ; l'enfant né sans vie, que les
décrets n° 2008-798 et 2008-800 font inscrire à l'état civil, rangés au droit civil — si
la caisse lui ouvre la majoration de durée d'assurance, la fiche
`majoration_duree_assurance_enfants` le dira.

**Pour la file D**, sans y toucher : rangés avec les renvois à ses fiches, à confronter
par elle — la surcote et la décote des artisans et des commerçants (décrets
n° 2004-156 et 2006-1611), leur durée maximale et leur revenu annuel moyen
(n° 2007-614), la régularisation de leurs cotisations (n° 2000-1226), leur cumul et leur
retraite progressive (n° 2004-1130, 2009-1738 et 2009-1739), le transfert de 1989
(n° 89-640) ; à Mayotte, les revalorisations des pensions de 2007 et de 2009 (arrêtés
du 30 mars 2007 et du 26 mai 2009), l'arrêté du 19 janvier 2005, le décret
n° 2007-1681 et l'article 98 de la loi n° 85-10, que porte `mayotte_pension_de_base`.
Les textes des cultes (loi n° 78-4, décrets n° 2006-1324 et 2008-1497) renvoient aux
fiches de la file E, sans les changer.

**La suite complète, réparée en chemin**, à la demande de la session d'orchestration :
la correction de R. 351-45 de l'étape 4 fait basculer en 2003 la durée du régime
général, et celle des régimes qui la lui empruntent, pour les nés de 1933 à 1942.
`tests/test_regle_de_chacun.py` déclare désormais cette bascule, texte en main, et
retire les déclarations de la CNAVPL et de la CNBF, dont la durée ne bascule plus en
2004 ; le test des nés avant 1943 (`tests/test_cnav_exposes.py`) dit le jour de
naissance, le 15, que la garde des présomptions décalait au 1er. Aucune règle n'a changé.

**À la session du modèle** : la cessation progressive d'activité et l'enfant né sans vie,
ci-dessus, et le régime local d'Alsace-Moselle d'avant 1946, à déclarer s'il ne se sert
pas. Aucune règle n'a été changée ; aucun fichier d'une autre file n'a été touché, et
les blocs « Reprise » de l'action 175 et de ses autres étapes non plus.
