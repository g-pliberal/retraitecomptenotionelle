# Étape 2 du domaine du cumul : les droits après la première pension et la seconde pension, lus dans leurs fiches

Le 17 novembre 2026, le propriétaire décide que l'étape 2 du domaine `cumul`
se mène en parallèle de l'ordre de la note 0009 ; il le redit le 19, « si ça
ne pose pas de problème en le faisant en parallèle des autres tâches ». Elle
fait pour `droits_apres_la_premiere_pension` et `seconde_pension` ce que
l'étape 1 a fait pour `retraite_progressive`
(`2026-11-09-etape-1-mesure-et-retraite-progressive.md`). Aucun résultat ne
bouge.

## Ce qui change

- **Le paquet.** Les deux fiches entrent à `FichesDatees.NOMS` ; le paquet
  refait ne change que par elles.
- **Les droits de l'activité.** `motif`, dans `moteur/js/droit/seconde.js`,
  ne recalcule plus de ses dates laquelle des quatre versions vaut : il lit
  celle de `droits_apres_la_premiere_pension` aux deux dates qui décident, la
  première pension de base et le mois d'activité (`versionDesDroits`, par
  `versionAuxDates`), rend son identifiant, et tire de ses paramètres ce que
  l'activité ouvre : `droits_nouveaux`, et les exceptions du cumul intégral
  ou entier. La fiche n'a pas eu à changer : ses versions portaient déjà
  leurs paramètres et leurs bornes, au jour près celles du code.
- **La seconde pension.** Chaque version de `seconde_pension` dit désormais
  si le droit existe (`existe`), et porte deux dates que le code écrivait : la
  deuxième pension de l'Agirc-Arrco « prend effet, au plus tôt, le 1er
  janvier 2024 » (`agirc_arrco_effet_au_plus_tot`), et le RCI n'ouvre de
  droits que depuis le 1er janvier 2025 (`rci_droits_depuis`). Le moteur lit
  la version à la date d'effet de la nouvelle pension et à celle de la
  première (`regleDeLaNouvellePension`) : le plafond de 5 %, qui tombe pour
  les premières pensions de 2027, et ces deux dates. La date d'effet au plus
  tôt, le 1er septembre 2023, n'est plus un nombre : c'est la fin de la
  version sans droit, que `effetDeLaNouvellePension` cherche, comme la note
  0009 le veut pour toute règle qui ouvre un droit.
- **Sont parties du module** sept constantes : `PREMIERE_2015`,
  `DROITS_2023`, `LIQUIDATION_2023`, `LIQUIDATION_AGIRC_ARRCO`, `DROITS_RCI`,
  `PREMIERE_2027` et `PLAFOND_EN_PASS`. Une fiche absente du paquet, ou une
  valeur de `droits_nouveaux` que le moteur ne connaît pas, arrête le calcul.
  `moteur/js/echeancier.js`, que le brief donnait pour probable, n'écrit
  aucune date de ces règles : il n'a pas changé.

## Les cliquets, arrivés pendant l'étape

Les cinq cliquets de la note 0009 sont entrés sur `main` pendant la session.
Deux regardaient l'étape.

- **Les constantes datées.** Les six dates parties du module quittent la
  liste (`tests/cliquets_du_droit_date/constantes.yaml`) : 113 constantes du
  droit restent à migrer, au lieu de 119, et 67 sans fiche désignée, au lieu
  de 68.
- **Les deux preuves.** Une fiche qui entre à `FichesDatees.NOMS` apporte ses
  versions, « qui naissent donc prouvées » ; six des sept n'avaient pas
  d'exemple. Trois le prennent. La circulaire Cnav 2015/8 du 6 février 2015,
  lue dans la base de législation de la Cnav, en donne deux : son exemple 6,
  une première retraite du 1er janvier 2014 et une reprise d'avril 2015 qui
  est « génératrice de droit » dans le régime nouveau (`sans_regle_generale`) ;
  son exemple 7, une première retraite du 1er mars 2015 dont la reprise
  « n'ouvre aucun droit » (`loi_2014`). La fiche F13243 de service-public,
  vérifiée le 12 novembre 2026, dit les deux cas de `loi_2023`, que deux de
  ses exemples déjà au dépôt rejouent. Les quatre se rejouent par une
  grandeur neuve des exemples officiels, `regles_des_droits_apres_le_depart`,
  et une lecture de plus au pont. Les trois autres versions, dont deux de
  2027, écrivent « aucun trouvé » et ce qui a été cherché.
- **La place de ce qui a été cherché.** Le contrat de la fiche n'en avait
  pas, et le cliquet la demandait à la première étape qui reprend une fiche :
  la version prend un champ facultatif, `exemples_cherches` (règle additive,
  § 13.3 de l'architecture). Le cliquet lit aussi ce que la note dit du
  texte, « son statut [dit] ce qui manque » : une version supposée, qui porte
  son hypothèse et son exemple, ne se compte plus. Il descend de 238 à 237,
  par une version de `pension_maximale_regime_general` qui était dans ce cas.

## Les textes, relus avant d'écrire

Dans les index LEGI et KALI de la DILA, le 19 novembre : L. 161-22-1 A
(`LEGIARTI000028496884`) ; L. 161-22-1 dans sa rédaction de 2023
(`LEGIARTI000047453688`) ; L. 161-22-1-1 dans celle de 2026
(`LEGIARTI000053279747`), qui « s'applique aux assurés qui entrent en
jouissance de leur première pension de vieillesse de base à compter du
1er janvier 2027 » et ne porte plus la phrase du plafond ; D. 161-2-22-1
(`LEGIARTI000047958952`), « 5 % du montant annuel du plafond », pour les
nouvelles pensions « prenant effet à compter du 1er septembre 2023 » ;
l'article 27 du règlement du RCI (`LEGIARTI000054906651`), en vigueur le
1er janvier 2025 ; l'article 91 de l'accord du 17 novembre 2017
(`KALIARTI000049290254`). Chacun dit ce que la fiche en cite. Dans l'index
JORF, le VIII de l'article 19 de la loi n° 2014-40 et le XII de l'article 26
de la loi n° 2023-270.

## Ce qui est vérifié, et comment

- `tests/js/droits-apres-la-premiere-pension.test.js`, douze essais, vus
  rouges puis verts. Leurs valeurs sont celles des textes ci-dessus. Trois
  retouchent une copie du paquet, une borne de chaque fiche et le plafond, et
  vérifient que le résultat suit : c'est la fiche qui pilote. Un autre tient
  les sept constantes hors du module.
- Les témoins refaits par le portage (`construire_temoins.py`) : aucun
  fichier ne bouge. Le paquet refait : seule `fiches_datees` change, de deux
  fiches.
- `python -m pytest -m rapide` (5 556 passés) ; `tests/test_emploi_retraite.py`,
  dont les essais des droits et de la nouvelle pension n'ont pas été
  retouchés ; `test_carte.py`, `test_contrats.py`, `test_facade.py`,
  `test_moteur_a_part.py`, `test_oracle.py`, `test_destinie.py`,
  `test_estimation_officielle.py`, `test_verification.py`,
  `test_cliquets_du_droit_date.py` ; les 267 essais de `tests/js/`. La suite
  complète est à GitHub.

## La trouvaille, gardée et déclarée

Le titulaire d'une pension militaire garde ses droits sous toutes les
versions, mais le moteur nomme la règle de ses mois par la seule date du
droit : `loi_2014` avant 2023, `loi_2023` ensuite. Pour une première pension
d'avant 2015, la version qui vaut est `sans_regle_generale` ; pour une
première pension de 2027, `lfss_2026`. Seul le nom de la règle diffère, non
les droits ouverts. Un rangement ne déplace aucun résultat : l'étape garde ce
nom, lu par l'identifiant de la version et la borne de `loi_2023`, et l'écrit
aux approximations de la fiche. Au propriétaire : le corriger déplace ce nom
dans les résultats de ces deux cas.

## Une question de lecture, relevée et non tranchée

Le XII de l'article 26 de la loi n° 2023-270 fait entrer l'article en vigueur
le 1er septembre 2023, et ne remonte au 1er janvier 2023 que pour « les droits
en vue d'une nouvelle pension » du cumul intégral. La fiche, et le moteur
avant elle, éteignent dès le 1er janvier 2023 les droits de l'activité de qui
a pris sa première pension avant 2015. Ses mois de janvier à août 2023
relèvent peut-être encore des règles d'avant. La borne n'a pas bougé ; la
question est inscrite aux sources de la fiche (`a_relire`). Elle demande une
lecture à part, et, si elle se confirme, une correction sur l'accord du
propriétaire.

Les versions sans exemple officiel décident de pensions à des dates d'effet
récentes ou à venir : la note 0009 leur demande une seconde lecture du texte,
par une session qui n'a pas vu celle-ci.

## Ce que l'étape laisse

- Le taux de 50 % (`TAUX_PLEIN`), que la version dit par `taux_plein: true`
  sans que le moteur le lise ; les 150 heures de SMIC d'un trimestre, qui
  sont d'une autre fiche ; le délai de six mois chez le dernier employeur.
- Les quatre identifiants de version restent des constantes du module
  (`LOI_2014`…), que lisent les tests et la façade ; plus aucune date ne les
  choisit.
- Six fiches du domaine, celles du cumul emploi-retraite, restent à lire par
  leurs versions (`droit/cumul.js`, où vivent encore `PREMIERE_2015` et
  `PREMIERE_2027`).
- La fenêtre que l'étape 1 signalait vaut encore : entre l'envoi et la
  fabrique de GitHub, un paquet sans les deux fiches arrête le calcul d'une
  activité après le départ.

## Ce que l'étape a coûté

Une session, le 19 novembre, de trois heures environ, dont la moitié pour
les cliquets arrivés en route ; un commit ; quatorze fichiers écrits à la
main, et le paquet refait.
