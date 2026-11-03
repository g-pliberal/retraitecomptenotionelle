# Étape 8 : les non-salariés de Mayotte, leur statut, leurs trimestres et leur assiette minimale

**Le 3 novembre 2026, ce qui est fait.** Les textes d'abord, lus dans l'index
LEGI à jour du 2 novembre 2026 : « les résidents à Mayotte ayant la qualité de
travailleurs non salariés des professions artisanales, industrielles et
commerciales » sont affiliés au régime de base de la caisse de Mayotte depuis
le 1er juillet 2012, « et agricoles » jusqu'en 2014, les libéraux de L. 631-1
depuis le 23 juillet 2026 (ordonnance n° 2002-411, article 23-1, trois
rédactions ; article 23-4, II) ; « le droit à pension de vieillesse des
travailleurs non salariés est déterminé selon les dispositions prévues au
chapitre Ier » (article 23-4, I), le revenu annuel moyen adapté par l'article 32
du décret n° 2003-589. Leurs taux, que la fiche disait introuvables, sont à
l'article 4-2 du décret n° 2011-2085, créé par le décret n° 2019-632 pour les
cotisations de 2019 : 5,85 % en 2019, 0,70 point de plus chaque année jusqu'à
17,75 % en 2036, sous le plafond de la caisse, sur une assiette qui « ne peut
être calculée » sous 450 fois le Smic horaire de Mayotte, quatre-vingt-dix jours
d'affiliation exigés depuis 2026 (rédaction du décret n° 2026-82). Deux
comportements, un par commit, chacun vu rouge d'abord, dans les deux moteurs.

1. *Le statut.* `independant_mayotte`, « Travailleur indépendant de Mayotte
   (artisan, commerçant) », famille outre-mer, sans employeur, routé à
   `cssm_mayotte` depuis 2012 ; rien avant. Ses trimestres se valident au revenu
   cotisé, comme ceux du salarié — 200 heures du Smig de Mayotte jusqu'en 2016,
   150 depuis —, par le seul routage (`statuts_de_mayotte`). La circulaire de la
   Cnav n° 2025-04 l'écrit : « le salaire ou revenu cotisé à retenir en 2025 est
   de 1 347 euros pour la validation d'un trimestre », et, « concernant les
   travailleurs indépendants », 135 € de cotisations, 10,05 % de 1 347 €.
   `tests/test_mayotte.py` : 2 800 € font deux trimestres en 2013, 2 220 € deux
   en 2017, 5 400 € quatre en 2025, un, un et trois au seuil de la métropole ;
   la pension vient de la caisse de Mayotte, sans part d'employeur.
   `tests/test_cnav_baremes.py` recoupe le barème de la caisse : 2025 concorde à
   l'euro ; 2026 non (voir plus bas). Le statut neuf suit dans ce qui le
   compte : la liste des statuts sans employeur (`test_donnees.py`), la fiche de
   régime et l'inventaire, `docs/regimes.md`, les statuts des témoins
   (`construire_temoins.py`), le compte du menu du simulateur, 74
   (`test_web_revues.py`), le chiffre ancré du README.
2. *L'assiette minimale.* Deux lignes de
   `assiette_minimale_independants.csv`, de 2019 à 2025 sans condition de durée,
   depuis 2026 sous quatre-vingt-dix jours, et le Smic du territoire du statut,
   que `smicHoraireDe` (macro.js) et `smic_horaire_de` (macro.py) donnent :
   celui de Mayotte pour un statut de sa caisse, celui de la métropole sinon.
   L'artisane qui déclare 1 000 € cotise sur 3 406,50 € en 2019 et 4 041 € en
   2025, trois trimestres au lieu d'aucun ; au Smic de la métropole, ce serait
   4 513,50 € et 5 346 €. La famille `independants_de_mayotte` entre dans
   `dispenses_assiette_minimale.yaml`, sans dispense : L. 613-11 ne lève que les
   minima des articles du code qu'il nomme.

**Ce que le calcul en reçoit.** Mesuré au moteur Python : l'artisane de Mayotte
née en 1975, à 1 000 € par an de 2013 à 2025 et partie à soixante-sept ans,
valide 21 trimestres au lieu d'aucun, et la caisse lui sert 219,96 € par an au
lieu de rien. Des 923 témoins de simulation, huit naissent — un par génération
du statut neuf, et `independante_mayotte_assiette_minimale` —, aucun ne bouge ;
vingt rendus de page changent, par le seul menu des statuts et la page Méthode,
qui montre l'inventaire. La confrontation des témoins simule au Python la
carrière que bâtit le portage : c'est le test à deux moteurs de
`test_mayotte.py` qui confronte la construction des lignes, et il rougit quand
le jumeau Python prend le Smic de la métropole.

**Vu en chemin, non corrigé.**

- *Le barème de 2026.* La caisse publie 250 € de cotisations par trimestre :
  17,87 % de 1 399,50 €, le taux des artisans et des commerçants de la
  métropole, quand celui de Mayotte est de 10,75 % (150 €). Le modèle suit le
  décret et la circulaire, qui disent le revenu cotisé ; l'écart est déclaré
  dans `ECARTS_COTISATIONS_VALIDANTES_MAYOTTE`. Au barème, l'assiette minimale
  de 2026, 4 198,50 €, ne validerait qu'un trimestre, quand elle en vaut trois.
  Question au propriétaire.
- *Les taux dans la série.* Ceux de l'article 4-2 ne sont pas encore dans
  `taux_cotisation_annuels.csv` : le compte notionnel et la fiche de paie de
  l'indépendant de Mayotte paient le taux entier du régime général. Ils y
  entrent comme ceux de D. 633-3, par un récupérateur de l'index LEGI et une
  certification de `verifier_donnees.py` (`taux_plafonne_non_salarie` de
  `cssm_mayotte`) ; aucun texte lu ne dit leur taux de 2012 à 2018, quand
  l'article 4 du décret n° 2011-2085 ne fixe qu'une part salariale et une part
  patronale. `docs/limites/1-certification.md` le dit.
- 2012 compte entière, quand l'affiliation part du 1er juillet ; l'article 32
  neutralise les années de deux trimestres assimilés ou plus, ce que le modèle
  ne fait pas ; le cumul emploi-retraite de l'article 34, au plafond de la
  caisse, n'est pas lu, comme celui du salarié de Mayotte (le groupe
  « outre-mer » de `cumul.js`).
- *D'autres files.* `inventaire.yaml` est en retard sur la fiche de la CAFAT
  (file A, action 145) : la fabrique de GitHub le refait. La loi n° 48-1469,
  qu'une fiche de la file E cite, attend son `textes.py --inscrire`.

**L'étape est faite**, aux taux près. La suite : l'étape 9, l'assiette du RCO
des artisans, à lire puis à trancher avec le propriétaire.
