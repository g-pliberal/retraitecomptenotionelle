# La carte des fiches : les IEG lus au droit, troisième lot

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après les
deux premiers lots des fiches à lire au droit, le RAFP puis la CNAVPL
(`130/2026-10-29-carte-des-fiches-cnavpl-lu-au-droit.md`). Celle-ci : un lot
des 101 qui restaient, selon `docs/veille_droit.md`. Le lot pris est un régime,
celui des industries électriques et gazières, dont les trois fiches qui ne
portent que lui n'étaient pas mûres : `age_ouverture_ieg_actifs`,
`age_reference_decote_ieg` et `duree_requise_ieg`. Aucun chiffre du modèle ne
bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF récupérés
  et mis à jour, jusqu'aux incréments du 28 et du 29 octobre ; `textes.py
  --inscrire`, sans rédaction nouvelle, avant la lecture et après.
- **Le test d'abord.** Les trois fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs dix-huit manques. Et un fichier
  neuf, `tests/test_ieg.py`, vu rouge faute de versions : ce que chaque version
  lit, les périodes de `regimes/ieg.yaml` et les tables qu'elles nomment le
  portent — l'âge de l'actif et celui de sa surcote pour toute génération qui
  peut les avoir l'année, la diminution de l'âge d'annulation et le calendrier
  de la durée mois par mois, les tables par génération de semestre en semestre.
  Une valeur altérée dans chaque fiche le fait rougir.
- **Les vingt et une rédactions de l'annexe 3**, de 1946 au 6 août 2025, que
  LEGI consolide chacune en un seul document, confrontées article par article :
  quatre ne sont jamais entrées en vigueur ; les articles 3, 9, 9-1, 10, 16 et
  45 ne changent qu'au 1er juillet 2008 (décret n° 2008-627, qui remplace avant
  son entrée en vigueur l'annexe du décret n° 2008-69), au 21 mars 2011 (décret
  n° 2011-290, dont l'article 25 reporte l'article 9-1 aux pensions de 2017), au
  28 juin 2014 et au 1er janvier 2017 (décret n° 2014-698), au 1er janvier 2025
  (décret n° 2023-692) ; celle du 6 août 2025 (décret n° 2025-761) ne change que
  l'article 1er.
- **`age_ouverture_ieg_actifs`**, du domaine de l'âge et de l'étape qui ouvre
  le droit : quatre versions sur la date d'effet. Cinquante-cinq ans pour
  l'agent actif depuis 1946, soixante pour le sédentaire, sans surcote ; au 1er
  juillet 2008, quinze ans de services actifs, et la surcote au-delà de
  soixante ans ; au 21 mars 2011, dix-sept ans, l'âge relevé de quatre mois par
  génération née depuis 1962 jusqu'à cinquante-sept ans pour 1967, la surcote
  au-delà de l'âge du 1° du I de l'article 16, soixante-deux ans pour 1962 ;
  pour les pensions de 2025, trois mois de plus par génération jusqu'à
  cinquante-huit ans et neuf mois pour 1974, cinquante-neuf ans ensuite, et la
  surcote jusqu'à soixante-quatre ans pour 1970. La suspension de 2026 est sans
  effet : l'annexe n'envoie à L. 161-17-2 que les générations qu'elle ne touche
  pas. Approchée, de conforme : l'agent est présumé actif, de ses dix-sept ans,
  que la saisie ne distingue pas, jusqu'à cinq ans trop tôt pour le sédentaire ;
  la bonification d'âge des mères de trois enfants de 1946 n'est pas servie ;
  les pensions du second semestre de 2008, liquidées sous la période d'avant la
  réforme, n'ont pas de surcote, au plus deux trimestres à 0,75 %.
- **`age_reference_decote_ieg`**, du domaine de la décote et de l'étape qui
  liquide : trois versions sur le mois où le droit s'ouvre — aucune décote avant
  le 1er juillet 2010 ; l'âge minimum majoré de cinq ans, diminué de seize
  trimestres à rien, de 2010 à 2024 ; l'âge minimum majoré de trois ans depuis
  2025, soixante-deux ans pour l'actif. La lecture divergente du I ter, que la
  CNIEG étend à l'âge d'annulation, passe dans les sources de la fiche, qui suit
  la caisse ; les exemples de Madame D et de Monsieur A rejouent la version de
  2010 à 2024. Approchée, de conforme : l'âge de référence est celui de l'actif
  présumé.
- **`duree_requise_ieg`**, du domaine de la durée et de l'étape qui ouvre le
  droit : quatre versions sur le mois où le droit s'ouvre — les trente-sept
  annuités et demie de 1946, gardées à qui a réuni les conditions avant le 1er
  juillet 2008, ce que le texte de 2008 ne dit pas ; le calendrier de 151 à 166
  trimestres ; la table par génération de 2014, depuis juillet 2019, lue à la
  génération qui a soixante ans à l'ouverture (article 9-1) ; les tables par
  durée de services actifs de 2025. Approchée, de conforme : les pensions du
  second semestre de 2008 gardent 150 trimestres au lieu de 151, au plus 0,7 %
  de pension ; l'agent présumé actif.
- **Le cliquet des textes** descend de 9 447 à 9 446 : L. 161-17-2 dans sa
  rédaction du 1er septembre 2023, qu'une version cite. Les rédactions de
  l'annexe 3 avaient toutes un statut.
- **La carte** passe de 101 fiches à lire au droit à 98, de 600 manques à
  582 ; elle compte trois fiches conformes de moins, trois approchées de plus.
  `conservation.py --depuis HEAD` dit changées les lignes de veille des trois
  fiches, refaites depuis elles, ce que la référence figée admet.

## Ce que l'étape laisse

- Les 98 fiches à lire au droit, par lots d'un régime ou d'un domaine. Ce que
  ce lot ajoute à ceux des deux premiers : un texte que LEGI consolide en un
  seul article se lit article par article, rédaction contre rédaction, celles
  qui ne sont jamais entrées en vigueur (leur fin précède leur début) mises à
  part ; un décret qui ne fait que reporter une partie de lui-même le dit dans
  ses dispositions finales (article 25 du décret n° 2011-290) ; une
  confrontation aux données balaye toutes les générations, et non les seules
  marches de la fiche, sans quoi une marche déplacée passe.
- Lu en chemin, hors du lot : les services actifs « bonifiés d'un sixième », les
  insalubres d'un tiers, pour les agents recrutés avant 2009 (article 2 de
  l'annexe 3 ; « majorés de deux mois par année » en 1946), que le modèle ne
  compte pas et qu'aucune fiche ne porte ; de même, en 1946, la réduction de
  moitié de la pension au-delà de la moyenne de deux traitements de la grille,
  et la déduction des rentes des anciens régimes (article 3, § 3).
- Une correction à mener, dans les deux moteurs : couper les périodes de
  `regimes/ieg.yaml` au 1er juillet 2008 par leur `date_effet`, le second
  semestre de 2008 ayant sa période à lui, avec ses 151 trimestres et sa
  surcote à 0,75 % (L. 14, III, du code des pensions, dans sa rédaction de
  2004), quand celle de 2009 surcote à 1,25 %.
- La circulaire PERS 70 du 21 mai 1952, qui ferait l'agent actif d'avant 2008 de
  quinze ans de services actifs, n'est pas publiée : connue par sa citation.
- `regenerer.py --verifier` dirait périmé le tableau de bord, qui compte la
  carte ; GitHub le refait.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
