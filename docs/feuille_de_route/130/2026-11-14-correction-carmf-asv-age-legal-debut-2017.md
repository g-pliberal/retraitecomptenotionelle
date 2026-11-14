# Correction de la ligne 13 de la file : la CARMF et l'ASV majorent depuis l'âge légal de janvier à mars 2017

Treizième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026). Arrêté du
30 novembre 2016, annexe, 1° (JORFARTI000033521562), article 15 des statuts du régime
complémentaire : « A compter du 1er janvier 2017 […] 1. Etre âgé de l'âge prévu au
premier alinéa de l'article L. 351-1 du code de la sécurité sociale. Si le médecin
demande à bénéficier de la retraite complémentaire après cet âge, il est fait
application d'un coefficient de majoration de 1,25 % par trimestre séparant le premier
jour du trimestre civil suivant celui où le médecin atteint cet âge de la date d'effet
de la retraite », « réduit à 0,75 % par trimestre à partir du premier jour du trimestre
civil suivant celui où le médecin atteint l'âge de 65 ans ». Arrêté du 1er décembre
2016, annexe, 3° (JORFARTI000033538061), article 12 des statuts de l'ASV : mêmes mots.
L. 351-1, en vigueur en 2017 (LEGIARTI000023035688), renvoie à « l'âge mentionné à
l'article L. 161-17-2 » ; D. 161-2-1-9 (LEGIARTI000025089933) : 60 ans pour les nés
avant le 1er juillet 1951, 60 ans et 4 mois, 60 ans et 9 mois, 61 ans et 2 mois, 61 ans
et 7 mois ensuite, 62 ans depuis 1955. Arrêté du 22 mars 2017, annexe
(JORFARTI000034298521) : « les mots : « après cet âge » sont remplacés par les mots :
« après l'âge de 62 ans » », aux deux articles ; publié le 29 mars, ses articles 1er et
2 ne le datent pas : en vigueur le 30 mars 2017. Le texte tranche ce que la ligne dit :
une pension qui prend effet du 1er janvier au 1er mars 2017 se majore depuis l'âge
légal de la génération.

**L'erreur.** Les périodes de 2017 des deux régimes comptaient de 62 ans toute l'année
(`surcote_age_debut: 62`) : les médecins nés avant 1955, dont l'âge légal est plus bas,
perdaient les trimestres écoulés entre cet âge et 62 ans.

**Le test d'abord** (`tests/test_sections_sante.py`,
`CARMF_AU_TEXTE_DE_JANVIER_A_MARS_2017`, joué par
`test_la_carmf_sert_ses_coefficients_dans_les_deux_moteurs`), cinq cas posés à la main
depuis le texte, servis par le portage et refaits au bit près par le moteur Python
(`servi_et_refait`), vu rouge (1,1375 où le texte donne 1,20), puis vert :

- née le 10 mars 1952, pension au 1er janvier 2017 : 60 ans et 9 mois le 10 décembre
  2012, seize trimestres du 1er janvier 2013, 1,20 ; au 1er mars 2017, 1,20 encore ; au
  1er avril 2017, sous l'arrêté du 22 mars, douze trimestres de 62 ans, 1,15 ;
- né le 10 mars 1948, pension au 1er janvier 2017 : vingt trimestres à 1,25 % du
  1er avril 2008, quinze à 0,75 % du 1er avril 2013, 1,3625 ;
- né le 10 août 1951, pension au 1er janvier 2017 : 60 ans et 4 mois le 10 décembre
  2011, dix-neuf trimestres à 1,25 % du 1er janvier 2012, un à 0,75 % du 1er octobre
  2016, 1,245 (vu rouge à part, 1,24, avant la retouche du second taux).

`tests/test_coupures_au_mois.py` : la CARMF et l'ASV entrent dans la liste des régimes
dont une période se coupe au jour.

**L'effet au cas posé** (médecin libéral entré à 22 ans, deux salaires moyens, euros de
2026). Née le 10 mars 1952, pension au 1er janvier 2017 : la CARMF sert 13 043,35 € au
lieu de 12 364,01 €, **679,34 € par an** de plus ; l'ASV 16 768,15 € au lieu de
15 894,81 €, **873,34 € par an** de plus. Né le 10 mars 1948 : 15 652,73 € à la CARMF
et 20 084,55 € à l'ASV, au coefficient 1,3625 au lieu de 1,2625.

**La correction.**

- Les données : dans `carmf_complementaire.yaml` et `asv_conventionnes.yaml`, la
  période de 2017 liquide du 1er janvier au 29 mars 2017 (`date_effet: [2017-01-01,
  2017-03-30]`) et compte de l'âge légal (`surcote_depuis_l_age_legal`, un
  interrupteur neuf, déclaré au schéma et à la fiche `surcote_par_age_seul`) ; la
  période suivante, qui ne diffère de celle de 2017 que par le taux de cotisation,
  liquide depuis le 30 mars 2017. Les années bornent toujours l'acquisition.
- Le moteur, des deux côtés (`surcotePoints`, `surcote_points`) : sous l'interrupteur,
  le décompte part de l'âge d'ouverture de la période lu à la génération
  (`ageOuvertureCommun`). Le second taux part du premier trimestre qui commence au
  palier ou après, et non plus du dernier qui finit avant lui : rien ne change quand
  le palier tombe à un nombre entier de trimestres du début (62 et 65 ans, tous les cas
  d'avant), et le né d'août 1951 garde à 1,25 % le trimestre où tombent ses 65 ans,
  comme le texte.
- Le chargeur et le paquet (`regimes.py`, `construire_donnees.py`) portent le champ.
  Aucun témoin de simulation ni de page ne bouge.

**Les fiches.** `surcote_par_age_seul` : l'erreur de la version `carmf_asv_2017` sort
des approximations et passe à l'histoire (`effet`) ; la version dit son interrupteur.
`carmf_asv_minoration_enfants` : la version `statuts_de_2017` porte ses deux paramètres ;
le point non tranché demeure, retourné : le modèle suit la date d'effet, et la lecture
contraire (62 ans pour une pension de ces trois mois liquidée après le 29 mars) est ce
qui reste possible.

**Ce qui reste, déclaré, pour la ligne 18.** Le modèle compte des trimestres de trois
mois depuis le premier du mois où l'âge est atteint, non des trimestres civils. De
janvier à mars 2017, l'âge légal des nés de juillet à décembre 1951 (60 ans et 4 mois)
ne tombe pas à un nombre entier de trimestres des 65 ans, et le passage à 0,75 % dépend
alors du mois de naissance dans le trimestre civil : né le 10 septembre 1951, pension
au 1er janvier 2017, le texte donne 1,2325 (dix-huit trimestres à 1,25 % du 1er avril
2012, un à 0,75 %), le modèle 1,2375, soit 55,16 € par an de trop à la CARMF
(13 653,27 € servis) et 70,72 € à l'ASV (17 503,22 €). Écrit à l'approximation du
trimestre civil de la fiche `surcote_par_age_seul`, que la ligne 18 corrige : un
décompte en trimestres civils, depuis la date de naissance, règle les deux.

**Vérifié** : `python -m pytest -m rapide`, les fichiers de tests des sections, de la
carte, des coupures au mois et des données, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts ; `regenerer.py` passé.
