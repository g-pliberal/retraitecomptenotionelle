# La carte des fiches : les cultes lus au droit, septième lot

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la
file E un nouveau lot de la carte (action 130), un régime ou un domaine hors
des zones des autres files et de ce qui est déjà lu. Le lot pris : les cultes,
dont deux fiches n'étaient pas mûres, `cultes_salaire_annuel_moyen` et
`cultes_retraite_complementaire` ; leurs trois sœurs (`cultes_fractions_de_pension`,
`cultes_alsace_moselle_pension`, `cultes_retraite_complementaire_taux_specifiques`)
l'étaient déjà. Aucun chiffre du modèle ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF
  récupérés, à jour de l'incrément du 2 novembre, et du 3 pour le JORF ;
  `textes.py --inscrire`, aucune rédaction nouvelle.
- **Le test d'abord.** Les deux fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs douze manques ; un fichier neuf,
  `tests/test_cultes_au_droit.py`, vu rouge faute de versions. Chaque
  paramètre d'une version porte le nom du champ de la période qui le porterait,
  lu à l'année que la date qui le décide désigne : la base forfaitaire à
  l'année de la période, la règle du salaire annuel moyen à la date d'effet ;
  le taux de la complémentaire renvoie à la tranche 1 de l'Arrco, puis de
  l'Agirc-Arrco, la même année ; les statuts affiliés se lisent dans
  `legislation/affiliations.yaml`, les contributions d'équilibre dans leur
  barème. Cinq cas tiennent les écarts déclarés ; deux tests de plus bornent
  leur effet, et un troisième refait le « taux de base » de la caisse, 10,02 %,
  de la tranche 1 et de la contribution d'équilibre générale. Une valeur
  altérée dans chaque fiche le fait rougir.
- **Les textes**, dans les index du dépôt : l'article 19 de la loi de
  financement pour 1998, qui aligne le régime au 1er janvier 1998 ; le décret
  n° 98-490 du 17 juin 1998 et les rédactions de R. 721-29, R. 721-30 et
  R. 721-39-2 qu'il écrit ; le décret n° 2004-181 du 23 février 2004 ; l'article
  32 de la loi n° 2000-37 ; R. 382-89, R. 382-90 et R. 382-121 ; L. 721-3,
  L. 721-6, L. 382-25 et L. 382-27 dans toutes leurs rédactions ; les huit
  rédactions de L. 921-1 ; l'article 75 de la loi n° 2005-1579 ; l'arrêté du
  24 avril 2018 qui étend l'accord Agirc-Arrco ; les décrets du SMIC de 1998 à
  2012.
- **`cultes_salaire_annuel_moyen`**, du domaine du salaire de référence et de
  l'étape qui acquiert — le salaire que chaque année porte au compte, comme le
  vocabulaire range « les salaires portés au compte » ; la moyenne relève de la
  fiche `salaire_annuel_moyen` —, approchée, de conforme : cinq versions, sur
  deux dates. Rangée dans l'étape qui liquide, la couche des comptes
  notionnels la neutralisait et la gardait à la fois, ce que
  `test_univers.py` refuse : le compte prélève ses cotisations sur cette base.
  Avant 1998, aucun salaire annuel moyen, la pension est forfaitaire ; depuis,
  les années d'avant 1998 n'y entrent pas ; celles de 1998 à 2001 y portent
  169 SMIC horaires par mois ; celles de 2002 au 30 juin 2005, la durée légale,
  « augmentée de la valeur de la garantie mensuelle de rémunération la plus
  élevée », rétroactivement : la rédaction de 2002 et de 2003 disait encore
  169 heures ; depuis, la durée légale seule.
- **`cultes_retraite_complementaire`**, du domaine des points et de l'étape
  qui acquiert, approchée, de conforme : trois versions — rien avant le
  20 décembre 2005 ; l'Arrco ensuite, sur le forfait, au taux de sa tranche 1,
  l'AGFF en plus ; l'Agirc-Arrco depuis 2019, au « taux de base » de 10,02 %.
- **Le cliquet des textes** descend de 9 411 à 9 389. **La carte** passe de 91
  fiches à lire au droit à 89, de 539 manques à 527. `conservation.py --depuis
  HEAD` dit changées les lignes de veille des deux fiches, refaites depuis
  elles, ce que la référence figée admet.

## Ce que l'étape laisse

- **Deux écarts du modèle sur la base des cultes**, pour une étape du modèle
  (la file E ne touche pas au modèle) :
  - le SMIC du 1er janvier : le modèle compte la base de toute l'année au
    SMIC de janvier, quand R. 382-89 et R. 382-90 la font suivre chaque mois le
    SMIC en vigueur ; de 1998 à 2009, relevé chaque 1er juillet, il en manque la
    moitié du relèvement, jusqu'à 2,9 % de la base, en 2004 ;
  - la garantie mensuelle de rémunération : de 2002 au 30 juin 2005, le
    modèle ne compte que la durée légale, 1 820 heures par an, sans la garantie
    qui relève la base, au plus jusqu'à 169 heures par mois — jusqu'à 11 % de
    la base de ces années. Lu à la lettre, « augmentée de la valeur de la
    garantie » doublerait presque la base : la pratique de la caisse est à lire
    avant d'écrire la règle.
  Ensemble, de l'ordre de un à deux pour cent du salaire annuel moyen de la
  fraction d'après 1997, non mesuré.
- **Un fichier d'une autre zone** : `legislation/contributions_equilibre_agirc_arrco.yaml`
  ne fait pas verser l'AGFF au ministre du culte de 2006 à 2018, quand le seul
  guide lu, de 2008, la lui fait verser, 2 % du forfait. Aucun effet sur la
  pension, l'AGFF n'achetant aucun point ; les contributions que le cycle de
  vie compte en manquent. La file E n'y touche pas.
- **À relire** : le taux de la complémentaire de 2006 à 2018, lu pour les
  cultes au seul 1er mai 2008 ; la base du premier semestre 1998, avant le
  décret du 17 juin ; un relevé de carrière d'un ministre du culte, qui dirait
  si la caisse porte au compte la somme des bases des mois.
- Les 89 fiches à lire au droit. Ce que ce lot ajoute : une fiche peut se
  couper sur deux dates, et chaque paramètre se lit alors à la sienne ; un
  paramètre peut renvoyer à un autre régime, et le test le suit.
- `regenerer.py --verifier` dirait périmé le tableau de bord, qui compte la
  carte ; GitHub le refait.

## Ce qui attend le propriétaire

Une question : ouvrir une étape du modèle pour compter la base forfaitaire des
cultes au SMIC de chaque mois, et, une fois la pratique de la caisse lue, avec
la garantie de 2002 à 2005 ? Avis : oui, sans urgence ; l'effet est de l'ordre
d'un ou deux pour cent d'une part de la pension des ministres des cultes. Pour
le reste, rien de neuf : les questions de la note précédente attendent toujours.
