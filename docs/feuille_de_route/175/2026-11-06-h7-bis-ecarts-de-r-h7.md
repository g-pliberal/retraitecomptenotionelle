# Les huit écarts de la relecture R-H7, repris dans la fiche de l'AVPF (H7-bis)

**Le 6 novembre 2026** (session H7-bis, onzième vague, sur Opus). La relecture R-H7
(`2026-11-06-relecture-r-h7.md`, § 7) a trouvé juste le travail de H7 (commit c68ba87),
avec deux écarts moyens et six faibles, tous de preuve ou de déclaration. Chacun est relu à
la source puis écrit dans la fiche `avpf`. Aucune règle, aucun moteur, aucun témoin, aucun
test ne change ; `construire_donnees.py` rend le paquet identique. **La règle de H7 tient** :
rien de ce qui a été lu ne la contredit.

## Ce qui a été lu

Index LEGI à jour au 2 novembre 2026 (20261102-213929) et JORF au 3 novembre
(20261103-002311), récupérés ce jour puis effacés ; la base de législation de la Cnav, par
son API, ce jour à 11 h UTC (hors de son import de nuit).

- *Lettre ministérielle du 13 février 1979* (`LE_MIN_13021979.aspx`, « Bureau des
  Prestations familiales », signée Pierre Schopflin), en entier : « Aux termes de cet
  article, la possibilité d'un telle affiliation est réservée aux femmes et mères de
  famille. Toutefois dans des cas extrêmement rares, des hommes assument la charge d'une
  épouse ou d'un enfant handicapé. » ; « Dans ces conditions et dans l'attente d'une
  modification législative sur ce point, je souhaite que les Caisses d'Allocations
  Familiales procèdent à l'affiliation et prennent en charge les cotisations de ces
  personnes à partir du 1er juillet 1979. Une telle mesure ne serait pas rétroactive. » ;
  « l'assurance vieillesse obligatoire ne peut bénéficier à plus d'une personne par foyer
  au titre du troisième alinéa de l'article L 242-2. » (« un telle » est la graphie de la
  base.)
- *Décret n° 73-88 du 26 janvier 1973*, rédaction d'origine (`DEC_7388_26011973.aspx`), en
  entier : article 1er, « Les mères de famille et les femmes bénéficiaires de la majoration
  de l'allocation de salaire unique ou de la majoration de l'allocation de la mère au foyer
  instituée par la loi n° 72-8 du 3 janvier 1972 sont affiliées obligatoirement à
  l'assurance vieillesse du régime général de la sécurité sociale, à la diligence de
  l'organisme ou du service chargé de la liquidation de ladite majoration. » ; article 5,
  « prendra effet à compter du 1er juillet 1972 » (la base écrit « 1<sup>er</sup> »).
  C'est une transcription : elle porte des coquilles (« dam la région parisienne »).
- *Index JORF*, les notices de 1973 à 1985 qui nomment le décret n° 73-88 : la sienne
  (JORFTEXT000000693989, JO du 28 janvier 1973), celles des décrets n° 78-270
  (JORFTEXT000000874152, « MODIFICATION DU TITRE, DE L'ART. 1ER »), n° 80-1068
  (JORFTEXT000000501301, « L'ART. 1 DU DECRET 7388 DU 26-01-1973 MODIFIE EST ABROGE ET
  REMPLACE. »), n° 82-1140 et n° 85-830 : aucune de 1973 à 1977. Celles de 1972 à 1986 qui
  nomment « L242 » : de 1979 à 1985, la circulaire du 29 avril 1980 (des femmes seules) et
  la loi n° 85-832 (L. 242-4).
- *Décret n° 82-1140 du 29 décembre 1982* (JORFTEXT000000884294, JO du 30 décembre), la
  notice : « Remplacement de l'article 3 (2ème et 3ème alinéas) du décret n° 73-88 précité
  et de l'article 4 du décret n° 78-269 susvisé. » Dans LEGI, les rédactions de ces deux
  articles au 30 décembre 1982 (LEGIARTI000006761991, LEGIARTI000006760072), lues : l'assiette
  « au produit du montant du salaire horaire minimum de croissance et des cinquante-deux
  douzièmes de la durée hebdomadaire légale du travail ». La cotisation, non l'affilié.
- *Décret n° 79-535 du 3 juillet 1979* (JORFTEXT000000516653, JO du 5 juillet), sa notice ;
  dans LEGI, ses six articles (LEGIARTI000006770602 à 006770607, du 1er juillet 1978 au
  21 décembre 1985), lus : outre-mer, « les mères et les femmes ayant la charge d'un enfant
  handicapé ou assumant au foyer familial la charge d'un handicapé adulte » ; aucun ne
  nomme le père.
- *La Cnav*, ces deux décrets : sa recherche ne sert rien pour « 82-1140 » ni « 82/1140 »,
  rien pour « 80-1068 », et pour « 79-535 » le seul décret n° 85-1354 du 17 décembre 1985 ;
  les noms `DEC_821140_29121982.aspx`, `DEC_79535_03071979.aspx`,
  `DEC_801068_23121980.aspx` ne sont pas servis.
- *Décret n° 78-269, article 1er* (LEGIARTI000006760068, du 10 mars 1978 au 21 décembre
  1985) ; *décret n° 73-88, article 1er*, ses trois rédactions de LEGI (1978-01-01 →
  1980-01-01, 1985-01-05 → 1985-08-04, 1985-08-04 → 1985-12-21) ; *article 2*, rédaction du
  4 août 1985 (LEGIARTI000006761989) ; *décret n° 85-830*, son article de l'assurance
  vieillesse (LEGIARTI000006768734) et son texte (LEGITEXT000006065103 : visas et
  signatures, sans numéro d'article) ; *L. 381-1*, rédaction du 21 décembre 1985
  (LEGIARTI000006742941), en entier.

## Les écarts, un à un

1. **Moyen : la lettre du 13 février 1979.** La version
   `hommes_ayant_la_charge_d_un_handicape` la cite d'abord, mot pour mot, avec ce qu'elle
   est : une lettre, non un texte, qui agit « dans l'attente d'une modification
   législative ». `a_relire` ne la dit plus « que l'API ne sert pas ».
2. **Moyen : l'article 1er d'origine du décret n° 73-88.** La version
   `meres_de_juillet_1972` passe de `supposee` à `lue`, et le texte le permet : l'article
   1er n'affilie que « Les mères de famille et les femmes », l'article 5 prend effet au
   1er juillet 1972, et aucune notice ne le modifie avant le décret n° 78-270, d'où vient
   la rédaction du 1er janvier 1978. Le texte cité est le JORFTEXT, avec la transcription de
   la Cnav comme lieu de lecture et sa date (`lu_le`) ; `nee_de` le nomme. Ce que H7
   supposait est confirmé. Ce que le texte ne tranche pas : la transcription n'est pas le
   JO, qui seul la certifierait.
3. **Faible : la date qui décide.** `dates_qui_decident` passe de `periode.debut` à
   `revenu.annee`, et les bornes des cinq versions avec, aux mêmes dates ; le commentaire
   dit que le code décide par l'année de la ligne (`annee < ANNEE_AVPF_DES_HOMMES`,
   `carriere.py`, ligne 858) et par l'assiette mensuelle pour 1972 (`revenu_avpf`, somme des
   mois). Une borne au 1er juillet coupe ainsi une année : c'est dit.
4. **Faible : le texte de 1985 cité pour 1979-1984.** LEGIARTI000006761986 reste cité, dit
   « POSTÉRIEURE à la période ». S'y ajoutent ce qui vaut dans la période : l'article 1er du
   décret n° 78-269 (LEGIARTI000006760068, en vigueur de 1978 à 1985, des femmes seules), et
   la notice du décret n° 80-1068, dont ni LEGI ni la Cnav ne servent le texte ; la
   rédaction de 1978 (LEGIARTI000006761985) est nommée, citée à la version précédente.
5. **Faible : le montant inversé.** « 3 071,05 € au lieu de 7 370,53 € ».
6. **Faible : 4 299,48 €, un plafond.** L'approximation le dit : il vaut pour le père d'un
   enfant conçu avant 1985, au complément familial que l'article transitoire du décret
   n° 85-830 lui ouvre ; pour l'allocation au jeune enfant, l'article 2 du décret n° 73-88
   (rédaction du 4 août 1985) fait rétroagir l'immatriculation « à compter du premier jour
   du mois civil suivant celui de la naissance ». Ce que le texte ne tranche pas : si cette
   rétroactivité remonte avant le 4 août 1985.
7. **Faible : les deux citations.** L. 381-1 : la fiche cite aussi, du handicap, « la
   personne et, pour un couple, l'un ou l'autre de ses membres », sans « isolée » — c'est
   la note de H7, qui reste telle quelle, qui disait les deux alinéas pareils. L'article de
   85-830 est dit « l'article que LEGI numérote 1er », qui renvoie aux « articles 1er et 2
   du présent décret » ; son numéro au JO ne se lit pas, ni dans LEGI ni dans la notice.
8. **Faible : les deux décrets modificatifs.** Les décrets n° 82-1140 et n° 79-535 entrent
   aux lectures (LEGI, JORF, Cnav), avec ce qui montre qu'aucun ne nomme le père.

## Les lignes de la file des fac-similés

Selon R-H7 (§ 6), que la lecture d'aujourd'hui confirme, **seule la loi n° 85-17 du
4 janvier 1985 a besoin du JO imprimé** : elle seule peut trancher janvier à août 1985,
LEGI n'en a que quatre articles, la base de la Cnav rien. Les autres lignes que H7
proposait ne changeraient pas la règle : la loi n° 72-8 (citer L. 242-2), le décret
n° 73-88 d'origine (certifier la transcription de la Cnav), le décret n° 80-1068 (le
texte de 1980 à 1984, que ni LEGI ni la Cnav ne servent). La file 138 est au
propriétaire : rien n'y est écrit ici.

## Ce qui reste

Le candidat 67 (une année d'éducation sans AVPF valide quatre trimestres) n'est pas traité
ici. Au registre de la Cnav, `LE_MIN_13021979.aspx` et `DEC_7388_26011973.aspx` sont déjà
`limite`, renvoyés à la fiche `avpf` (commit 8b588f5, étape 6). Aucun candidat neuf.
