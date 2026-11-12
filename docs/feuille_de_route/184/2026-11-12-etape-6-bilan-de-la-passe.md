# Étape 6 : le bilan de la passe de lecture, et ce qui attend le propriétaire

**Ce qui est fait, le 12 novembre 2026.** Les quatre lots sont poussés, une
session chacun, sur Fable 5.2. L'inscription de l'étape 4 avait porté le
stock de 92 rédactions sur 56 fiches à 100 sur 59 ; la session
d'orchestration a refait les lots sur cette liste. `python scripts/textes.py
--non-lues` ne compte plus aucune fiche avec une rédaction en vigueur ou à
venir non lue, et le compte des rédactions sans statut passe de 9 283 à
9 236. Ni `src/` ni `moteur/` n'ont été touchés : la passe lit et classe.

| Lot | Fiches | Lectures | Sa note |
|---|---|---|---|
| Le code de la sécurité sociale | 24 | 55 | `2026-11-12-etape-6-code-de-la-securite-sociale.md` |
| La fonction publique | 8 | 16 | `2026-11-12-etape-6-fonction-publique.md` |
| Les non-salariés agricoles | 7 | 19 | `2026-11-12-etape-6-non-salaries-agricoles.md` |
| Les autres régimes | 20 | 29 | `2026-11-12-etape-6-autres-regimes.md` |

**Ce qui change une règle : quatre rédactions**, que le modèle n'applique
pas. Aucune n'est écrite ; chaque fiche le déclare, et la note du lot donne
le détail.

1. *La cotisation de retraite complémentaire du chef d'exploitation
   agricole*, article D. 732-165 du code rural, cotisations depuis le
   1er janvier 2026 : une seconde part, de 1 % à 3 % selon le revenu, qui
   achète des points. Le modèle garde 4 % et 133 points. Fiche
   `assiette_minimale_agricole`. Restent à lire l'arrondi et l'année
   incomplète.
2. *Le cumul d'une pension militaire et d'un emploi*, article L. 86 du code
   des pensions, première pension à compter du 1er janvier 2027 : la pension
   militaire se cumule entièrement hors employeur public. Le portage la
   traite comme toute pension de la fonction publique. Fiche
   `cumul_emploi_retraite_fonction_publique`. Lu dans le code, non rejoué par
   un test.
3. *La carrière longue du non-salarié agricole*, article D. 732-40 du code
   rural : quatre trimestres à la fin de l'année de l'anniversaire suffisent,
   quel que soit le mois de naissance ; le modèle en demande cinq. L'écart
   est antérieur à 2026. Fiche `carriere_longue`, laissée `conforme` par le
   lot.
4. *L'abattement de la retraite progressive au régime complémentaire des
   indépendants*, article 12 du règlement, au 1er janvier 2027 : plafonné au
   taux de la deuxième ligne de l'annexe 2, que l'index rend à plat. Le
   modèle sert l'abattement entier. Fiche `abattement_rci`.

**À vérifier contre le modèle, puis à écrire s'il y a lieu.**

- Article R. 643-6 du code de la sécurité sociale : la pension de base des
  libéraux prend effet au premier jour du trimestre civil qui suit la
  demande, au mois pour la seule Cipav depuis le 5 mars 2023. Ce que le
  moteur fait après 2004 n'a pas été regardé.
- Article R. 815-25 : les biens du survivant comptent pour 3 % de leur
  valeur dans les ressources de la réversion. Ce n'est pas un calcul à
  changer, mais ce que la saisie devrait dire.

**Ce que la passe n'a pas lu, parce qu'aucune fiche ne le cite.** L'article
28 du règlement du régime complémentaire des indépendants (1er janvier
2027) ; l'article 12 du décret n° 2004-1056, ouvriers de l'État, et ses trois
rédactions de 2026 (sapeurs-pompiers volontaires, trimestre par enfant né
depuis 2004, élus locaux) ; le 1° de l'article L. 351-3 (rente d'accident du
travail, 1er novembre 2026) ; l'article R. 351-37 (1er novembre 2026) ;
l'article R. 653-2, avocats, qui renvoie à des dispositions abrogées. La
fiche `sam_parents_24_23` ne cite pas l'article R. 173-3-2 par son
identifiant. Une question reste ouverte sur `limite_age_ouvriers_etat`.

**Deux défauts de l'outil, trouvés par les lots.** Le statut d'une rédaction
est commun à toutes les fiches, et le plus établi l'emporte : une rédaction
qu'une fiche déclare sans effet sort de la liste de toutes les autres. Et
tout identifiant écrit dans une entrée `textes_sans_effet`, son motif
compris, reçoit ce statut. Les lots s'en sont gardés à la main : relever ses
identifiants à l'ouverture, nommer une rédaction de comparaison par sa date,
ne déclarer sans effet une rédaction partagée qu'au dernier commit. Trois
rédactions sont ainsi « sans effet » en statut commun alors qu'une autre
fiche les garde à rattacher (articles L. 613-9, R. 351-39 et R. 711-1) : le
compte des rédactions à rattacher ne les voit plus.

**Ce que le propriétaire décide.**

- L'étape qui écrira les quatre règles, et dans quel ordre.
- L'état de `carriere_longue`, `conforme` avec un écart connu.
- Le remède à l'outil : un contrôle qui refuse un identifiant étranger dans
  un motif, ou un statut tenu fiche par fiche.
- Ce que dit `sources.lu_le` : les lots l'ont porté au 12 novembre alors que
  seules les rédactions listées ont été relues ; chaque fiche le dit.

**Ce qui l'attend aussi, des étapes 4 et 5**, closes le même jour (leurs
notes : `2026-11-11-etape-4-liste-tenue-a-jour.md`,
`2026-11-11-etape-5-kali-dans-l-index.md`).

- Quand la DILA renouvelle un dump avant que l'index du JORF ou de LEGI l'ait
  rattrapé, la mise à jour du lundi doit-elle refuser, ou reconstruire
  d'elle-même ? Les deux sessions recommandent le refus. Aujourd'hui elle
  publierait un index troué sans le dire.
- L'index de KALI garde toute la base (352 617 documents, 276 Mo), choix de
  la session de l'étape 5 sur ses mesures ; le seul champ des retraites reste
  possible.
- Les accords Agirc-Arrco restent à faire entrer dans la liste de contrôle
  des textes, et les fiches de la retraite complémentaire à relire sur KALI.
- Le workflow du lundi n'a pas encore commité d'inscription : la course du
  16 novembre à 4 h UTC le montrera, avec la permission `actions: write`
  qu'il a reçue pour lancer la suite.
