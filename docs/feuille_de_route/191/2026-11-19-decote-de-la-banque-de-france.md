# La décote de la Banque de France, lue dans son règlement

Le 19 novembre 2026, sur l'accord du propriétaire, le scénario 1 oppose à
l'agent titulaire de la Banque de France la décote de son règlement, et non
plus celle de la fonction publique. L'écart avait été relevé le 17 novembre
(`2026-11-17-dix-renvois-sensibles.md`). L'étape s'est menée sur Fable 5.2.

**Le texte.** Règlement annexé au décret n° 2007-262 du 27 février 2007,
articles 32 et 70, dans les quatorze rédactions de l'annexe que porte l'index
LEGI. L'article 70 n'a que trois textes.

- L'origine (`LEGIARTI000006778516`) : un tableau par « période au cours de
  laquelle l'agent est susceptible de liquider sa pension ». « Jusqu'au
  31 décembre 2008. Sans objet » ; puis 0,125 % et 61 ans au premier semestre
  2009, un huitième de point de plus par an jusqu'à 1,25 % en 2018, et un âge
  qui monte jusqu'à 64 ans et 3 trimestres au 30 juin 2022.
- Le décret n° 2012-701 du 7 mai 2012, article 36 (`LEGIARTI000025882187`) :
  le tableau se lit par période de naissance, pour « les agents nés avant le
  1er janvier 1963 », l'âge étant la limite d'âge diminuée d'un à sept
  trimestres. Son article 41 ne le réserve pas aux pensions de 2016 : il vaut
  dès le 9 mai 2012.
- La rédaction du 1er janvier 2025 (`LEGIARTI000047909725`) retire les lignes
  des nés avant 1956, sans changer les autres.

Les deux tableaux disent le même droit aux nés de 1949 à 1955 : la limite
d'âge du statut (fiche `limite_age_banque_de_france`) diminuée des trimestres
de 2012 est l'âge que 2007 écrivait au semestre des soixante ans. Un test le
tient, semestre par semestre.

**Ce qui change.** Une fiche, `decote_banque_de_france`, en trois versions
sur la date d'effet : aucune décote avant le règlement (supposée, l'ancien
règlement n'étant pas dans LEGI), le tableau de 2007, le tableau de 2012. Les
quinze périodes du régime, de 2008 à aujourd'hui, y renvoient. Le portage lit
la version (`decoteBanqueDeFrance`, `liquider.js`) et la limite d'âge du
statut (`limiteDuTableau`, `limite_age.js`). Le renvoi couvre aussi les
périodes de 2023 et de 2025, que l'accord ne nommait pas : le tableau de 2012
vaut pour les nés jusqu'en 1962, qui partent jusqu'en 2029. Les lectures de
la durée requise que la Banque partageait avec la fonction publique restent
telles quelles, non relues (`DUREE_DE_LA_FONCTION_PUBLIQUE`, `ouvrir.js`).

**Ce qui bouge.** Aucun des 934 témoins de simulation ni des 86 rendus de
page : aucun ne porte un agent de la Banque parti avec une décote. Sur des
carrières simples, parties avant l'âge d'annulation avec une durée
incomplète, la part de pension retirée par la décote devient :

| Né en janvier | Départ | Avant | Après |
|---|---|---|---|
| 1948 | 60 ans, 2008 | 1,875 % | aucune |
| 1949 | 60 ans, 2009 | 3,5 % | 0,5 % |
| 1950 | 60 ans, 2010 | 6,25 % | 1,5 % |
| 1951 | 60 ans, 2011 | 8,25 % | 3 % |
| 1954 | 62 ans, 2016 | 14,625 % | 2,25 % |
| 1956 | 62 ans, 2018 | 20 % | 6 % |
| 1958 | 62 ans, 2020 | 23,75 % | 15 % |
| 1960 | 62 ans, 2022 | 23,75 % | 21,25 % |
| 1962 | 62 ans et demi, 2024 | 22,5 % | 21,25 % |
| 1964 | 63 ans, 2027 | 20 % | 20 % |

L'écart tient surtout à l'âge d'annulation : le dépôt comptait jusqu'à 65
puis 67 ans, le règlement jusqu'à la limite d'âge du statut, de 61 ans et
9 mois pour le né au premier semestre 1949 à 67 ans pour celui de 1959.

**Ce qui reste.** La fiche est approchée : la saisie ne dit ni le niveau de
l'agent ni sa catégorie, et ne sont servis ni l'âge des agents dont le droit
s'ouvre à 55 ans, ni celui des personnels de direction nés avant 1956, ni
l'exemption de l'agent de 65 ans qui a élevé un enfant handicapé. Aucun
exemple chiffré publié n'a été trouvé. Les quatre dates fausses relevées le
17 novembre (âge de départ de la Banque, Cavimac, artisans et commerçants
d'avant 1973) attendent toujours l'accord du propriétaire.
