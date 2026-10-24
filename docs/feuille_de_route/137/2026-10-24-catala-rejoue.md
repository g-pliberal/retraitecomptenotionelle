# Catala, rejoué au droit de sa date

**La demande**, le 24 octobre 2026 : le lot d'onze sessions que le
propriétaire a demandé ce jour-là, une par tâche qui se mène sans lui. Pour
l'action 137, « le premier modèle qui reste à confronter dans l'ordre du
registre : Catala, ses règles de retraite mises en regard du seul droit en
vigueur, qu'elles précèdent — ses âges de 2023 pour les générations parties
sous cette loi, jusqu'à 1963, l'âge du taux plein, l'inaptitude, l'ASPA
jusqu'en 2020. Comme modele-as le 23 octobre : rejouer son calcul, confronter
chaque écart au dépôt, et dire de qui est l'erreur. »

**Fait, le 24 octobre 2026 : le calcul rejoué ; le dépôt a raison, et Catala
a quatre erreurs de plus que les trois du registre.**

- *Ce qui a tourné.* catala-examples au commit `2694b17`, encore sa tête,
  cloné à part, et Catala 1.3.0, installé par opam sur l'OCaml du conteneur
  dans le bloc-notes de la session : les six modules dont dépend l'aide au
  logement, copiés dans un projet à part et compilés par `clerk build`, après
  vérification qu'ils ne portent que du Catala, sans module OCaml externe.
  Un fichier de rejeu, resté hors du dépôt, les interroge : l'âge d'ouverture
  que rend `OuvertureDroitsRetraite` pour vingt-huit naissances, calculé le
  31 août 2023, le 1er septembre, le 1er janvier 2024 et le 1er octobre
  2026 ; l'âge du taux plein et celui de l'inapte, internes à son aide au
  logement, lus par leur effet — l'ascendant qu'elle compte à charge
  (R. 823-4, 2°), à un mois près de chaque seuil, en juin 2021 et en mars
  2024 ; le plafond de l'ASPA, par les ressources qui font compter cet
  ascendant, 1,25 fois ce plafond au plus. Pour rejouer :
  `catala interpret … -s OuvertureDroitsRetraite --input '{"date_naissance_assuré":
  "1960-06-15", "date_courante": "2024-01-01"}'`.
- *Ce qui concorde.* Les âges de la loi de 2010, et ceux de la loi de 2023
  sauf 1967, sont ceux que les droits contrefactuels du dépôt gardent
  (`au_31_aout_2023`, `loi_2023_sans_suspension`), et, jusqu'à 1963, ceux du
  droit en vigueur ; l'âge du taux plein d'avant septembre 2023, l'âge légal
  plus cinq ans, est celui du dépôt génération par génération
  (`age_annulation_decote.csv`) ; l'inapte, à 62 ans (fiche
  `inaptitude_au_travail`, que D. 351-1-14 du 1er janvier 2026 ne change
  pas) ; l'ASPA de D. 815-1 de 2018 à 2020, d'une personne seule et d'un
  couple. De 2021 à 2023, Catala porte l'annuel des circulaires de la Cnav,
  que le barème de la caisse redonne au centime, et le dépôt douze fois le
  mensuel tronqué, 3 à 8 centimes de moins par an : l'approximation que la
  fiche `minimum_vieillesse` déclare, coupée le 14 octobre (action 138).
- *Ses erreurs nouvelles.* Après le 1er septembre 2023, il compte le taux
  plein à l'âge légal plus trois ans : 65 ans pour les nés de 1955 à août
  1961, 66 ans pour 1964, 67 ans seulement dès 1968. L. 351-8, 1°, ajoute ces
  trois ans à « l'âge prévu au premier alinéa de l'article L. 161-17-2 »,
  soixante-quatre ans dans ses trois versions depuis 2023 : 67 ans pour tous,
  ce que rejoue l'exemple `sp_f21552_65_ans_158` (né en 1964, parti à 65 ans,
  « 8 jusqu'à 67 ans »), et ce que D. 861-10, que Catala recopie, écrit pour
  Mayotte. Il lit ces âges à la naissance du demandeur, non de l'ascendant :
  avant 2023, un ascendant né en septembre 1954, passé l'âge de sa génération,
  n'est pas à charge d'un demandeur né en 1980. Le 1er septembre 2023, il n'a
  d'âge que pour les nés dès 1968 (« no applicable rule » pour un assuré né en
  1960) : sa D. 161-2-1-9 de 2023 vaut après ce jour, celle de 2011 avant. Et
  son ASPA omet la revalorisation du 1er juillet 2022, puis reste à 11 533,02
  € depuis 2023, quand la Cnav donne 12 523,14 € en 2026. Les quatre sont au
  registre, avec la génération 1967 et le calendrier d'avant la LFSS pour
  2026, que le rejeu confirme.
- *Ce que les tests tiennent* (`tests/test_referents.py`) : les âges des
  vingt-huit naissances, contre les tables du moteur posées comme ses droits
  contrefactuels, sauf 1967 ; le taux plein de dix-huit demandeurs, celui du
  dépôt avant septembre 2023 et 67 ans après ; l'inapte, contre la version de
  la fiche que le moteur lit ; l'ASPA de six années, l'approximation du dépôt
  comprise. Et la version que la ligne de Catala doit nommer, vue rouge avant
  le registre. Le tableau de bord le compte confronté : 26 modèles, et 2 à
  confronter en premier.

**Ce qui reste.** Le premier modèle qui reste à confronter, dans l'ordre du
registre, est le simulateur de SUD éducation, au droit de 2020 ; puis Nos
Retraites. Les autres restes du bloc « Reprise » ne bougent pas. Au
propriétaire, rien à trancher ; s'il le veut, les erreurs de Catala se
signalent à son équipe, ce qu'une session ne fait pas. Aux pages, rien : le
site ne lit pas le registre.

*Fichiers.* Le registre (ligne `catala`), le registre des sources
(`catala_examples`), `tests/test_referents.py`, `docs/etat.md`, la feuille de
route, cette note et l'entrée du journal de veille. Ni fiche, ni règle, ni
page. Catala et le fichier de rejeu sont restés hors du dépôt, qui n'a pas
Catala pour dépendance.
