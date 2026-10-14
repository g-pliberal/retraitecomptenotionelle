# Le sixième domaine, mesuré : les périodes assimilées manquantes

Session de nuit du 14 octobre 2026, sans le propriétaire. L'étape : mesurer
sur les sources publiques les quatre domaines qui restent à la liste du § 11
de `docs/architecture.md`, choisir, et ouvrir le domaine si la mesure le
désigne sans ambiguïté. Aucun fichier du modèle ni du site ne bouge ; aucun
témoin non plus.

## La mesure

La règle du § 11 : l'ordre se fixe par le nombre de personnes concernées. La
mesure du 28 septembre (feuille de route, « Le deuxième domaine ») comptait
des retraités ; elle disait les périodes assimilées manquantes sans mesure
publique, aucune source ne dénombrant les retraités qui en ont eu. Celle-ci
compte, à défaut, les personnes qui en relèvent.

- **Les périodes assimilées manquantes** — apprentissage, TUC, stages,
  sportifs de haut niveau, congé de naissance. L'apprentissage valide depuis
  le 1er janvier 2014 un trimestre par trimestre de contrat, au-delà de son
  assiette (L. 6243-3 du code du travail ; inventaire des avantages non
  contributifs, code `apprentissage`, `etat_modele: absent`) : 878 871
  contrats ont commencé en 2024, et 1 042 500 étaient en cours au
  31 décembre 2024 (DARES, relayée par Centre Inffo et la Banque des
  territoires). Les TUC, de 1984 à 1990, ont touché « au moins
  350 000 personnes » (questions écrites de l'Assemblée nationale, dont la
  n° 16536 du 30 juin 2026, sans réponse), jusqu'à « près d'1,7 million de
  stages » selon une synthèse de l'Assemblée ; la loi de financement
  rectificative pour 2023 en fait des trimestres assimilés, par des textes
  d'août 2023 que les questions écrites citent sans les nommer. Les
  stagiaires, les sportifs et le congé de naissance ne sont pas dénombrés ici.
- **Les départs anticipés particuliers** — incapacité permanente, compte
  professionnel de prévention, amiante ; le handicap est déjà servi. À la
  Cnav, fin 2024 : 44 630 retraités partis pour incapacité permanente,
  13 148 au titre du compte de prévention, 52 113 au titre de l'amiante,
  soit 109 891 ; en 2024, 4 679, 2 864 et 2 003 départs, soit 9 546 sur
  648 346 (DREES, enquête annuelle auprès des caisses de retraite, classeur
  du 26 mai 2026, partie 2, feuille `H-Conditions_liq`, champ
  `Type_depart`). L'Agirc-Arrco en compte autant à peu près (37 607 et
  47 357 en stock pour le compte et l'amiante). Le compte de prévention seul :
  21 380 assurés partis en 2021 avec au moins un point, 1 900 ayant converti
  leurs points en trimestres, 1 010 avec un droit en plus (Cnav, étude
  2023-010 du 6 mars 2023, COR, séance du 23 mars 2023, document n° 14).
- **Les rachats** — 74 371 versements pour la retraite au régime général du
  1er janvier 2004 au 31 décembre 2022, 3 914 par an en moyenne, environ
  6 600 personnes en 2022, « moins d'1 % » des nouveaux retraités (COR,
  séance du 25 mai 2023, document n° 9). Ceux de la fonction publique ne sont
  pas comptés ici ; rien ne laisse penser qu'ils changent l'ordre.
- **Les régimes hors champ** — vingt-trois lignes de l'inventaire, presque
  toutes éteintes ou fermées depuis des décennies (Alsace-Moselle d'avant
  1946, caisses coloniales, ORTF, Crédit foncier, Imprimerie nationale :
  dix affiliés en 2007), et sans effectif publié ensemble. Les sessions 1
  (action 121) et 17 (action 145) y travaillent cette nuit.

## Le choix

Les périodes assimilées manquantes passent les premières, d'un ordre de
grandeur : les TUC seuls, au plus bas, font plus de trois fois le stock des
départs anticipés particuliers, et l'apprentissage en fait entrer chaque
année huit fois ce stock. Le choix ne tient pas à la base de la mesure : en
retraités, les départs anticipés particuliers font 9 546 départs par an à la
Cnav, quand les seuls anciens des TUC, nés pour l'essentiel de 1960 à 1974,
en font plus de 20 000 par an pendant quinze ans s'ils étaient 350 000. Puis
les départs anticipés particuliers, les rachats, les régimes hors champ.

**Le sixième domaine, les périodes assimilées manquantes, est ouvert ce
jour.** Le § 11 de `docs/architecture.md` le dit ; sa liste de première
lecture n'est pas récrite, elle est d'un autre jour.

## Son gabarit, en étapes

1. **Les fiches, lues à la source** (scénario 1 : `scripts/veille_droit.py`
   d'abord, et une entrée du journal de veille) : `apprentissage` (L. 6243-3
   du code du travail, 2014, et ses décrets ; l'avant-2014, assiette
   forfaitaire, à dire tel quel) ; les TUC (la loi de 2023 et ses textes
   d'août 2023, à trouver dans l'index LEGI et JORF) ; les stagiaires de la
   formation professionnelle ; les sportifs de haut niveau ; le congé de
   naissance (loi de financement pour 2026). Les stages gratifiés relèvent
   d'un rachat, donc du domaine des rachats.
2. **Les faits de la chronologie** : la sorte `periode_assimilee` existe au
   vocabulaire ; il lui faut son motif, et une présomption par défaut (aucune
   période déclarée, comme aujourd'hui).
3. **Les fonctions dans l'étape** d'acquisition, dans les deux moteurs.
4. **Les exemples publiés** : circulaires de la Cnav sur l'apprentissage et
   les TUC.
5. **Le bloc du formulaire** : un motif de plus aux lignes de carrière. Il
   revient à la seule session des pages et de la saisie.
6. **La page Coût** : le complément de l'apprentissage, versé par le FSV puis
   par la branche, n'est isolé dans aucune publication lue (inventaire).
7. **La décision de la proposition** : à lire au README, qui dit comment le
   compte reçoit les périodes que paie un tiers ; au propriétaire s'il est
   muet.

Aucun déplacement de fichiers n'est prévu.

## Ce qui attend le propriétaire

- Le choix lui-même, s'il le veut autrement : il a ouvert les trois derniers
  domaines à sa demande, et celui-ci l'est sur la seule mesure.
- La décision de la proposition, quand l'étape 7 viendra.
