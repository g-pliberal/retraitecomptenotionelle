# Étape 9, suite de la huitième partie : le retour à la CRPCEN et aux IEG dans la saisie en net

**La demande.** Vague du 28 octobre 2026 : une session par tâche, que le
propriétaire ne suit pas pas à pas, celle-ci seule de la vague sur les pages.
Le point « au site, la saisie en net d'un retour » du bloc « Reprise » de la
huitième partie, que la note « retour à la CRPCEN et aux IEG »
(`2026-10-25-etape-9-retour-crpcen-ieg.md`, « Ce qui reste ») laissait au
site : la saisie en net remontait au brut par la fiche du premier recrutement
(`Saisie.dateEntree`), et un retour que rien ne maintient y gardait la retenue
du régime spécial, quand la carrière le route au régime général et à
l'Agirc-Arrco. Un champ de plus, s'il le fallait, avait sa forme au
propriétaire.

**Ce que disent les textes.** Rien de neuf à lire : la règle est celle du
modèle, écrite le 25 octobre avec ses sources (loi n° 2023-1250, art. 15, V
et VI ; décrets n° 2025-761 et 2025-799 ; fiche
`maintien_affiliation_crpcen_ieg`). Le site la lit, il ne l'écrit pas.

**Ce qui est fait.**

- *Pas de champ de plus.* Les lignes du formulaire disent déjà un retour : un
  métier sous le statut après un autre métier, après une période sans emploi,
  ou après une année que le champ « Interruptions » désigne.
- *La saisie donne ses retours à la loi.* `Saisie.retours(affiliation)` les
  compte comme `Carriere.retours`, par la même fonction, `retoursAuStatut`,
  tirée de la carrière : sur les années du relevé, ou sur celles des métiers
  (`anneesDesMetiers`), rangées comme `lignesDuParcours` les range — chaque
  année au métier principal qui en occupe le plus de mois, à égalité à celui
  qui l'ouvre, de la nature qu'une interruption lui donne, et une de plus par
  année qu'une activité ajoutée touche. La loi lit alors la saisie comme la
  carrière : `Affiliations.dateEntree(saisie, statut, annee)`.
- *Chaque ligne remonte sous la date de sa dernière année*
  (`Saisie.derniereAnnee`, celle dont le formulaire lisait déjà les régimes
  de chaque métier) : l'échelle (`Contexte.echelle`) reçoit l'année de la
  ligne convertie et la passe à la loi — le revenu de chaque métier
  (`niveaux`), l'activité après le départ (l'année où elle commence), la
  bascule net/brut, les repères du champ et le revenu déduit d'une pension
  (ceux de la première ligne). Sans année, la fiche reste celle du premier
  recrutement ; un statut inconnu, que la simulation refuse, n'en a pas.
- *Les tests* (`tests/test_web_saisie.py`, cinq tests, onze cas), vus rouges
  sauf celui du maintien, qui garde de trop corriger : le clerc recruté en
  2010, salarié du privé en 2024, revenu en 2025, l'agent des IEG au chômage
  en 2024, revenu en 2025, le clerc parti fin 2014, revenu en 2026, remontent
  comme un recruté d'après la fermeture, et ce qui précède garde sa fiche ;
  l'agent des IEG parti fin 2020 et revenu en 2026, ou qui élève un enfant en
  2024 et 2025, garde celle de son recrutement ; l'activité après le départ,
  par les métiers ou par le relevé ; la bascule de la page, dans les deux
  sens ; les retours de la saisie sont ceux de la carrière, sur sept saisies
  — un métier entre deux, le chômage, le congé, un retour en juillet qui
  revient l'année suivante, une interruption déclarée, deux activités
  ajoutées, un relevé.

**Ce que montrent les mesures** (2 500 € nets par mois saisis en 2026, le
brut que la saisie en tire) : le clerc recruté en 2010, revenu en 2025 après
une année dans le privé, ou parti fin 2014 et revenu en 2026, de 3 228,32 € à
3 158,09 €, le brut d'un recruté d'après la fermeture ; l'agent des IEG revenu
en 2025 après une année de chômage, de 3 197,76 € à 3 158,09 €. Les retours
que le maintien couvre gardent 3 197,76 €, et les lignes d'avant un retour,
leur fiche. Ni les témoins de simulation ni ceux des pages ne bougent
(`construire_temoins.py --verifier`, le 29 octobre, sur le paquet régénéré) :
aucune de leurs saisies ne revient au statut. Les fichiers fabriqués du dépôt
dataient du dernier commit de GitHub sur `main`, le verdict rouge du
28 octobre à 15 h 52 : sur eux, deux tests du niveau `site` échouaient avec ou
sans ce changement (`test_les_temoins_du_portage_sont_a_jour`,
`test_le_portage_javascript_retrouve_les_chiffres_du_modele`) ; régénérés,
`site` et `rapide` passent.

**Une approximation, déclarée dans `Saisie.retours`.** Sur un relevé, la
saisie ne voit pas un retour que seule la projection jusqu'au départ ferait,
après une interruption déclarée au-delà de sa dernière année : l'activité
après le départ remonterait alors par la fiche d'avant. Une ligne qu'une
interruption déclarée coupe d'un retour remonte, tout entière, par la fiche de
sa dernière année : une ligne n'a qu'un revenu.

**Trouvé en chemin.** Les dates de pension du formulaire
(`regimesDeBaseSaisis`, `pages.js`) lisent les régimes de chaque métier sous
la date du premier recrutement : au clerc de 2010 à 2014, sans emploi de 2015
à 2024, revenu en 2025, que la carrière sert par la CRPCEN puis par le régime
général, le formulaire ne voit que la CRPCEN, et ne propose pas la date de la
seconde pension. Lire chaque métier à `Affiliations.dateEntree(saisie,
statut, derniereAnnee)` le dirait pour les métiers ; un relevé, qui y range
par statut ses premières et dernières années, demande de couper les années
d'un statut à chaque retour. À une session des pages, avec son test.

**Ce qui reste**, une session par point : le plafond de 2027 ; la limite
5 ante ter (2), en fin d'étape ; aux pages, les dates de pension d'un retour
(« Trouvé en chemin »). Au propriétaire, sans changement : la CAMIEG,
l'écrêtement du minimum de la SNCF, l'ASPA de l'article 23, les textes au
fac-similé de la note « seuil de février 1991 ».
