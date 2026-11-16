# Étape 6, à part : les écarts les plus lourds des circulaires de 2002 à 2008, vérifiés au texte et chiffrés

Les lectures des circulaires de 2002 à 2008 (les notes `2026-11-16-etape-6-circulaires-*`)
ont relevé des écarts candidats entre la pratique de la caisse et le modèle. Cette note
reprend les plus lourds, les vérifie dans le texte primaire (loi, décret, code, par
l'index de la DILA, `dila_cherche.py`, à jour au 16 novembre 2026) et en chiffre l'effet
sur un cas posé à la main. Elle ne corrige ni le moteur ni les fiches (chantiers 161 et
de la note 0009 en cours) : elle dit lesquels méritent une correction, et dans quel
ordre.

## En bref

| # | Écart | Au texte | Qui | Effet sur un cas | Déclaré ? | Corriger ? |
|---|---|---|---|---|---|---|
| 1 | Carrière longue et handicap avant 2009 : 160 trimestres, non 161 à 164 | confirmé | nés 1949-1952, pension avant 2009 | départ refusé jusqu'à deux ans ; ou pension réduite de 0,6 à 2,4 % | non | **oui, d'abord** |
| 1 bis | Nés 1953-1955 avant le décret de leur génération : 164 trimestres (165 pour 1955) | confirmé (circulaire Cnav n° 2011/25) | demandes avant 2011 (1955 : avant août 2011) | un trimestre de trop, mêmes effets en plus petit | non | oui, avec le 1 |
| 2 | Cumul emploi-retraite plafonné à 160 % du SMIC dès 2007 | confirmé | reprises d'activité 2007-2008, pensions depuis 2004 | pension suspendue à tort chaque mois où pension et revenus passent un SMIC | non | **oui** |
| 3 | Pension d'inapte ou d'ex-invalide suspendue avant 65 ans au-delà de 50 % du SMIC × 520 h par trimestre | confirmé | inaptes de 60 à 64 ans qui travaillent, jusqu'au 19 décembre 2008 | pension entière servie à tort, chaque trimestre de dépassement | non | oui, plus tard (rare) |
| 4 | Convention franco-tchécoslovaque : totalisation-proratisation | confirmé (article 13 de 1967, rapport du Sénat) | périodes tchécoslovaques, surtout pensions avant le 21 février 2003 | le modèle sert 20 % de trop sur le cas de la note de 2003 | en partie (`calcul: non_lu`) | oui, plus tard (rare) |
| 5 | RETREP : proratisation sur 150 trimestres | tolérance ministérielle, sans texte au JO | maîtres du privé, avantage avant 2004 | aucun aujourd'hui : régime non modélisé, absent de la saisie | fiche non modélisée | non, à noter dans la fiche |
| 6 | Réversion juillet 2004 - juin 2006 : réversions des autres régimes de base hors des ressources | confirmé | survivants à plusieurs réversions de base, 2004-2006 | quelques centaines d'euros par an, au plus deux ans | non | oui, petit |

## 1. La carrière longue et le handicap avant 2009, à 160 trimestres

**Confirmé.** Trois textes, lus dans leur version en vigueur avant 2009 :

- R. 351-45 CSS, I, version du 10 mai 1995 au 1er janvier 2009 (LEGIARTI000006749450) :
  « La durée d'assurance et de périodes reconnues équivalentes de 160 trimestres
  mentionnée au 1° de l'article R. 351-27 et à l'article R. 351-39 est applicable aux
  pensions prenant effet postérieurement au 31 décembre 2002, quelle que soit la date de
  naissance de l'assuré. »
- Loi n° 2003-775, article 5, III (JORFARTI000001914387) : « A compter de 2009, la durée
  d'assurance nécessaire pour bénéficier d'une pension de retraite au taux plein [...]
  [est] majorée d'un trimestre par année pour atteindre quarante et une annuités en
  2012 ». Le V attache la durée à l'année des 60 ans, mais le III ne la majore qu'à
  compter de 2009 : jusque-là, aucune durée par génération n'existe.
- Décret n° 2008-1555 du 31 décembre 2008, article 4 (JORFARTI000020021132), en vigueur
  le 1er janvier 2009 (art. 5) : il remplace au 1° de R. 351-27 « 160 trimestres » par
  « une limite », « celle résultant de l'article 5 de la loi n° 2003-775 », et abroge la
  section qui portait R. 351-45. C'est ce décret, et lui seul, qui fait entrer la durée
  par génération dans le code, pour les pensions prenant effet depuis 2009.

La condition de la carrière longue suit la même limite : D. 351-1-1, version du
31 octobre 2003 au 1er juillet 2011 (LEGIARTI000006736521), « une durée minimale
d'assurance [...] au moins égale à la limite fixée en application du deuxième alinéa de
l'article L. 351-1 majorée de huit trimestres », et les durées cotisées des trois âges
(56, 58, 59 ans) se comptent sur cette même limite. La proratisation aussi : R. 351-6, I
(version du 27 avril 2007, LEGIARTI000006749349) prend pour durée maximum, pour les nés
après 1947, celle de L. 351-1, soit 160 avant 2009. Les circulaires de 2007 et 2008
(ministérielle n° 2007/396, lettre du 7 juillet 2008, RSI n° 2008/056 et 2008/059 : « 168
trimestres quel que soit l'âge de départ ») disent la même chose.

**Ce que fait le moteur.** `ageCarriereLongue` (`moteur/js/droit/ouvrir.js`, l. 1061 et
suivantes) prend pour `requis` la durée de `dureeRequise`, qui lit la table par la seule
génération (l. 401 à 416 : 161 à 164 pour les nés de 1949 à 1952), sans regarder la date
d'effet ; son jumeau Python fait de même (note de 2007).

**Effet, à la main.**

- *Le départ refusé.* Né en mars 1952, au travail depuis 15 ans, 168 trimestres validés,
  tous cotisés, à 56 ans en avril 2008. Le droit : 160 + 8 = 168, et 168 cotisés, départ
  au 1er avril 2008. Le modèle : 164 + 8 = 172 ; refusé à 56 ans, à 58 ans s'il cesse alors
  (172 validés exigés), à 59 ans de même : il ne part qu'à 60 ans, en 2012, ou à 58 ans en
  2010 s'il travaille jusque-là. Sur un salaire annuel moyen de 18 000 €, la pension de
  base vaut 9 000 € par an : le modèle en retire de deux à quatre ans, 18 000 à 36 000 €,
  et autant de complémentaire, qui suit la base. Touche chaque né de 1949 à 1952 dont la
  durée tombe entre 168 et sa limite du modèle plus 7 (1949 : 168 ; 1950 : 168 et 169 ;
  1951 : 168 à 170 ; 1952 : 168 à 171), et de même sur les durées cotisées.
- *La pension trop proratisée.* Si la durée au régime général est sous la limite (un
  polypensionné, ou un départ au titre du handicap), la pension est multipliée par
  160/161 à 160/164 : − 0,6 % (1949), − 1,2 % (1950), − 1,8 % (1951), − 2,4 % (1952). Né en
  1951, 130 trimestres au régime général sur 172 : 0,406 S selon le droit, 0,399 S selon
  le modèle.

**Déclaré ?** Non : ni la fiche `duree_requise_par_generation.yaml`, qui cite R. 351-45
sans en tirer l'effet, ni `docs/limites/` (recherche de « 1949 », « avant 2009 », « 160
trimestres »). `scenarios/actuel.py` ne fixe 160 avant 2009 qu'aux fonctionnaires (note
de 2008).

## 1 bis. Les nés de 1953 à 1955 partis avant le décret de leur génération

**Confirmé pour 1953 et 1954 ; probable pour 1955.** Décret n° 2010-1734 du 30 décembre
2010, article 9 (JORFARTI000023334359) : 165 trimestres « pour les assurés nés en 1953 et
1954 ». Son article 11, qui reporte au 1er juillet 2011 une liste d'articles, n'y met pas
l'article 9 : il vaut dès la publication, le 31 décembre 2010, sans effet rétroactif
écrit. Avant lui, aucun texte ne donne de durée à ces générations ; la lettre
ministérielle du 7 juillet 2008 leur garde celle de 1952, 164 trimestres. Pour 1955, le
décret n° 2011-916 du 1er août 2011 (166 trimestres, JORFARTI000024419267) : la durée
d'un départ de 2011 antérieur au 2 août reste à lire dans la circulaire qui l'applique
(165 ou 164).

**Effet.** Les départs anticipés de 2009 et 2010 (carrière longue à 56 ou 57 ans, handicap)
des nés de 1953 et 1954 : condition de 172 validés, non 173, et prorata 164/165, − 0,6 %.
Un trimestre de durée en moins : une seule valeur de durée refusée à tort par génération.

**Déclaré ?** Non. La table `duree_assurance_requise.csv` ne porte pas de date d'effet.

## 2. Le cumul emploi-retraite plafonné à 160 % du SMIC dès 2007

**Confirmé.** Loi n° 2006-1640 du 21 décembre 2006 (LFSS 2007), article 105, I
(JORFARTI000001688673) : dans L. 161-22, « après les mots : "sont inférieurs", sont
insérés les mots : "à 160 % du salaire minimum de croissance ou" ». L. 161-22 dans sa
version du 22 décembre 2006 au 19 décembre 2008 (LEGIARTI000006741561) : la reprise est
permise si les revenus, « ajoutés aux pensions [...], sont inférieurs à 160 % du salaire
minimum de croissance ou au dernier salaire d'activité ». Le plafond est donc le plus
haut des deux. La lettre ministérielle du 26 décembre 2006 (note de 2006) fixe
l'application au 1er janvier 2007, à 2 007 € par mois (8,27 € × 1 820 h / 12 × 1,6 =
2 006,85 €).

**Ce que fait le modèle.** La version `plafond_du_dernier_salaire_2004` de
`cumul_emploi_retraite_et_retraite_progressive.yaml` (l. 74 à 126), bornée par
`periode.debut` avant 2009, garde `part_du_smic: 1.0` (D. 161-2-9 : le dernier salaire
« ne peut être inférieur au montant mensuel du salaire minimum de croissance ») ; elle ne
cite pas la version de 2006 de L. 161-22, et le 160 % n'arrive qu'avec
`cumul_liberalise_2009`. La loi prime le décret : de 2007 à 2008, le plancher de
D. 161-2-9 est dépassé par celui de L. 161-22.

**Effet, à la main.** Retraité depuis 2005, dernier salaire 1 000 € par mois, pensions de
base et complémentaire 800 € par mois, reprise en 2007 à 700 € par mois : 1 500 € au
total. Le droit : 1 500 € < 2 007 €, pension servie. Le modèle : plafond au SMIC,
1 254 €, dépassé ; la pension « n'est pas due pour le mois civil » (D. 161-2-16). Écart :
800 € par mois de reprise, 19 200 € sur 2007 et 2008. Touche toute reprise de 2007 et 2008
dont pensions et revenus tombent entre le plus haut du SMIC et du dernier salaire, et
160 % du SMIC (entre 1 254 € et 2 007 € par mois en 2007), soit le cas ordinaire du petit
salaire repris.

**Déclaré ?** Non : aucune fiche ni limite ne cite la loi n° 2006-1640.

## 3. La pension d'inapte avant 65 ans, suspendue au-delà d'un plafond de revenus

**Confirmé.** R. 352-2 CSS, version du 1er décembre 1986 au 9 janvier 2010
(LEGIARTI000006750050 ; une version proche dès la codification de 1985) : les titulaires
d'une pension « substituée à une pension d'invalidité ou d'une pension de vieillesse
attribuée au titre de l'inaptitude au travail » qui « exercent une activité
professionnelle quelconque avant l'âge de soixante-cinq ans » voient « le service des
arrérages de leur pension [...] suspendu à compter du premier jour du mois suivant le
trimestre au cours duquel il a été constaté que le total des revenus professionnels du
pensionné dépasse 50 % du montant du salaire minimum de croissance calculé sur la base de
520 heures » ; le service reprend le trimestre où les revenus repassent sous la limite,
et en tout cas au mois qui suit les 65 ans. La limite : 1 869,40 € par trimestre au
1er juillet 2003 (7,19 € × 260), 2 087,80 € en 2005, 2 150,20 € en 2006.

**Effet, à la main.** Inapte de 62 ans en 2005, pension de base 7 000 € par an, salarié
d'un autre employeur à 2 500 € par trimestre. Le droit : suspendue le trimestre suivant,
1 750 € de moins par trimestre de dépassement, jusqu'à 65 ans. Le modèle : servie (avant
2004, entière chez un autre employeur ; de 2004 à 2008, sous le plafond du dernier
salaire, qu'une telle reprise ne dépasse pas). Rare (l'inapte travaille peu), mais
l'écart est la pension entière.

**Déclaré ?** Non : ni `inaptitude_au_travail`, ni `pension_d_invalidite_substituee`, ni
les limites ne portent l'article.

## 4. La convention franco-tchécoslovaque, sans prorata dans le modèle

**Confirmé au texte d'application, non à la convention.** La convention générale du
12 octobre 1948 (loi d'autorisation n° 49-421 du 25 mars 1949, avenant publié par le
décret n° 70-84 du 20 janvier 1970) n'est dans l'index de la DILA que par ses titres :
son texte n'a pas été lu. La circulaire ministérielle n° 2003/88 du 21 février 2003 en
dit la règle : la seule convention sans droit d'option, qui « impose toujours la règle de
la totalisation-proratisation », sur la carrière entière, « non limitée au maximum de 150
trimestres » ; abandonnée depuis 1990 pour l'assuré résidant en France qui a 150
trimestres français ; depuis le 21 février 2003, comparaison avec la pension des seules
périodes françaises, la plus élevée servie. Le règlement n° 1408/71 la remplace au
1er mai 2004 pour la République tchèque et la Slovaquie.

**Effet** (note de 2003). 120 trimestres français, 60 tchécoslovaques, départ en 2002 :
le modèle sert 0,400 S, la caisse 0,333 S. Le modèle sert 20 % de trop.

**Déclaré ?** En partie : le tableau des accords porte la convention en `calcul: non_lu`
(`data/reference/legislation/accords_internationaux.yaml`), et une convention non lue
compte ses périodes sans prorata. L'écart est connu de la donnée, non dit aux limites.

## 5. Le RETREP et la proratisation sur 150 trimestres

**Non confirmable au Journal officiel.** La lettre ministérielle du 4 avril 2005 demande
de « neutraliser » l'allongement de la durée de référence pour les avantages temporaires
pris avant 2004. Aucun décret ne l'écrit (recherche dans le JORF de 2003 à 2006) : c'est
une tolérance de la caisse, qui vaut pour le scénario 1 (« tel que la caisse
l'applique »), mais n'a pas d'autre source. **Effet aujourd'hui : aucun.** La fiche
`retrep_avantages_temporaires` est `pas_encore_modelisee` et la saisie ne connaît pas
l'avantage. À écrire dans la fiche le jour où elle sera modélisée.

## 6. La réversion de juillet 2004 à juin 2006

**Confirmé.** Décret n° 2004-857 du 24 août 2004, article 10 (JORFARTI000002110957) :
« II. - Par dérogation à l'article R. 353-1 [...], jusqu'au 30 juin 2006 inclus, les
ressources [...] sont appréciées [...] sans toutefois tenir compte des avantages de
réversion servis par les régimes de base d'assurance vieillesse mentionnés aux articles
L. 200-2 et L. 621-3 ainsi qu'à l'article L. 722-20 du code rural » (régime général,
artisans et commerçants, salariés agricoles) ; « I. - Les dispositions de l'article 1er
[R. 173-17, le partage entre régimes] sont applicables à compter du 1er juillet 2006. » Le
décret n° 2004-1447 du 23 décembre 2004, article 3 (JORFARTI000001653734), ôte de cette
dérogation les réversions complémentaires.

**Effet, à la main.** Survivante de 62 ans en 2005, ressources propres 12 000 € par an,
réversions de 3 000 € (régime général) et 2 000 € (salariés agricoles), plafond 2005
16 702,40 € (8,03 € × 2 080). Le droit : chaque régime compte les seules ressources
propres et sa réversion, 15 000 € et 14 000 €, sous le plafond : 5 000 € servis. Le
modèle compte les deux réversions (`reversion.yaml`, l. 1100 et 1101) : 17 000 €, soit
298 € de trop, retranchés. Quelques centaines d'euros par an, au plus deux ans, pour les
seuls survivants qui touchent deux réversions de ces régimes.

**La suspension de l'automne 2004** (lettre du 5 octobre 2004) n'a pas de texte au
Journal officiel : les décrets n° 2004-857 et 2004-858 valent depuis le 1er juillet 2004.
La caisse a appliqué l'ancienne règle du 1er juillet 2004 au 29 mars 2005, puis révisé
quand la nouvelle était plus favorable (annexe de la n° 2006/37) : la pension servie est
la plus haute des deux, sur neuf mois de décès. Effet faible, non chiffré.

**Déclaré ?** Non.

## Ce qui mérite une correction, dans l'ordre

1. **La durée de 160 trimestres avant 2009** (1 et 1 bis) : la plus lourde, puisqu'elle
   refuse des départs entiers, et la plus simple, puisque le moteur a déjà la branche
   (`DUREE_UNIQUE_2003`, l. 404 à 415) : il suffit de l'étendre aux générations au-dessus
   de 160 pour une pension prenant effet avant 2009, et de dater la table pour 1953 à
   1955. Test d'abord : le cas du né en mars 1952 ci-dessus.
2. **Le cumul à 160 % du SMIC en 2007 et 2008** (2) : une version de plus dans la fiche,
   bornée au 1er janvier 2007, sur L. 161-22 de 2006.
3. **L'inapte avant 65 ans** (3) et **la convention tchécoslovaque** (4) : rares, mais
   l'écart y est entier ; au moins à déclarer aux limites, faute de les modéliser.
4. **La réversion de 2004 à 2006** (6) : une version coupée au 1er juillet 2006 ; petit.
5. **Le RETREP** (5) : rien à corriger tant que le régime n'est pas modélisé.

## Ce qui n'a pas été fait

Les cas sont posés à la main, non passés au moteur. La circulaire Cnav n° 2011/24 (carrière
longue des nés de 1953 et après) et la circulaire de 1990 sur la convention
tchécoslovaque n'ont pas été lues. Voir la contre-vérification, plus bas, qui corrige le
1 bis et la fin du 3.

## Contre-vérification, le même jour : ce qui confirme, ce qui contredit

À la demande du propriétaire, chaque écart a été confronté à ce qui pourrait le
contredire : textes ultérieurs ou rétroactifs, doctrine de la Cnav, réponses
ministérielles au Parlement, rapports, chiffres publics. Sources lues en entier : les
circulaires Cnav n° 2007/34 (30 avril 2007), 2008/41 (25 juillet 2008) et 2011/25
(17 mars 2011), dans les copies de documents.gereso.com ; les réponses aux questions
écrites AN n° 39666, 100263 et 54631 (13e législature) et n° 334, 94754 ; le rapport du
Sénat n° 27 (1969-1970) sur l'avenant franco-tchécoslovaque de 1967 ; LEGI pour L. 352-1
et les articles 10 et 18 des décrets n° 2004-857 et 2004-858. Aucune décision de justice
trouvée sur ces points (recherche web, sans accès à Légifrance JURI).

**1. Carrière longue avant 2009 — confirmé, certitude haute, droit et calcul.**
Confirment : la circulaire Cnav n° 2008/41, § 211 : les durées totale et cotisée
« évoluent à compter du 1er janvier 2009 » ; « A compter du 1er janvier 2009 [...] Les
durées d'assurance pour l'ouverture du droit et le calcul sont déterminées en fonction de
la génération » ; § 213, les demandes « pour des dates d'effet postérieures au
1er décembre 2008 » se liquident aux nouvelles durées. La circulaire DSS n° 2007/396
(note de 2007) : « la durée d'assurance à retenir pour le calcul demeure fixée à 160
trimestres ». Les réponses AN n° 39666 et 100263 : les nés en 1952 partent à 56 ans avec
168 trimestres jusqu'à une date d'effet au 1er décembre 2008, 172 au-delà ; la mesure
« dépasse les deux milliards d'euros par an », « plus de 100 000 assurés par an ». La
DREES : 21 % de la génération 1952 du régime général est partie en carrière longue.
Pourrait contredire : la n° 2008/41, § 1, dit l'allongement « applicable à la génération
à laquelle appartient l'assuré quelle que soit la date d'effet de sa pension » ; mais ce
paragraphe vise la pension à 60 ans et au-delà, qui ne peut prendre effet avant 2009
pour ces générations, et le § 211 tranche pour l'anticipée. Rien ne rend rétroactif le
décret n° 2008-1555. L'enjeu est de masse : les générations 1949 à 1952 forment le gros
des 100 000 départs annuels de 2005 à 2008.

**1 bis. Nés de 1953 à 1955 — confirmé, et précisé : la date de la demande décide.**
La circulaire Cnav n° 2011/25 : « La durée d'assurance à retenir pour les assurés nés au
cours des années 1953, 1954 et suivantes est donc de 164 ou 165 trimestres selon que la
date de demande [...] se situe avant ou après le 1er janvier 2011 », pour l'ouverture du
droit « de même que pour procéder au calcul de la pension » ; les attestations délivrées
avant 2011 « pour des dates d'effet de pension jusqu'au 1er juin 2011 au plus tard ne
doivent pas être remises en cause ». Pour les nés de 1955 et après, « dans l'attente », la
durée de 1953 et 1954, 165, non 164 : la note ci-dessus est corrigée sur ce point, le
modèle oppose 166 au lieu de 165 aux départs de 1955 antérieurs au décret du 1er août
2011. Certitude haute pour le handicap, que la n° 2011/25 traite ; la circulaire jumelle
de la carrière longue (n° 2011/24) n'a pas été lue. Le critère de la demande n'est pas
dans le modèle, qui ne connaît que la date d'effet : la date d'effet au plus tard le
1er juin 2011 en est l'approche la plus sûre.

**2. Cumul à 160 % du SMIC dès 2007 — confirmé, certitude haute.** La circulaire Cnav
n° 2007/34 : « La Loi de financement de la sécurité sociale pour 2007 porte la limite
minimum de cumul à 1,6 fois le SMIC mensuel, soit 2007,00 euros », « pour les arrérages
dus à partir de la mensualité de janvier 2007 », avec un exemple chiffré. La réponse AN
n° 334 le redit (« 1,61 fois » le SMIC, coquille du ministère). Rien de contraire trouvé.

**3. L'inapte avant 65 ans — confirmé, la fin à corriger.** La base légale est L. 352-1
(version de 1985 au 19 décembre 2008), que la LFSS pour 2009 abroge (art. 88, II ;
réponse AN n° 54631 : elle « autorisai[t] l'exercice d'une activité professionnelle par
les personnes titulaires d'une pension de retraite allouée au titre de l'inaptitude sous
réserve que le revenu tiré de cette activité n'excède la moitié du [SMIC] »). R. 352-2 ne
disparaît qu'au 9 janvier 2010, sans loi qui le porte depuis décembre 2008 : la fin à
retenir est le 19 décembre 2008, non 2010 (certitude moyenne sur la date exacte,
haute sur la règle). La Cnav en a publié le plafond chaque année (n° 2003/31, 2006/40,
2007/49, 2008/28) : elle l'appliquait.

**4. Convention franco-tchécoslovaque — confirmé au texte, portée plus étroite.** Le
rapport du Sénat n° 27 (1969-1970) reproduit l'article 13 de la convention, dans la
rédaction de l'avenant du 17 octobre 1967 : totalisation des périodes, puis « les
avantages [...] sont déterminés, en principe, en réduisant le montant des avantages
auxquels il aurait droit si la totalité des périodes [...] avait été effectuée sous le
régime correspondant français [...] et ce, au prorata de la durée des périodes accomplies
sous ce régime ». Aucune option de calcul national. Ce qui réduit l'écart : depuis 1990,
l'assuré résidant en France qui a 150 trimestres français est payé sans prorata (le
modèle aussi, sans écart) ; depuis le 21 février 2003, à 65 ans ou au taux plein, la
caisse sert la plus haute de la pension proratisée et de la pension des seules périodes
françaises, que le modèle égale ou dépasse peu. L'écart de 20 % du cas de la note de 2003
vaut donc pour les pensions prises avant le 21 février 2003 et, jusqu'au 1er mai 2004,
pour les départs avant 65 ans sans taux plein au titre des seules périodes françaises.
Certitude haute sur la règle, moyenne sur la portée (la circulaire de 1990 n'a pas été
relue).

**5. RETREP — rien de contraire, contexte précisé.** Les réponses AN de 2005 (n° 63505,
82062 et voisines) disent que le ministère a fait liquider dès 2005 les avantages
temporaires sur 160 trimestres, la lettre du 4 avril 2005 gardant 150 à ceux pris avant
2004. Toujours sans effet sur le modèle, qui ne connaît pas le régime.

**6. Réversion de juillet 2004 à juin 2006 — confirmé, certitude haute.** La réponse AN
n° 94754 (19 décembre 2006) lit l'article 3 du décret n° 2004-1447 comme rendant
permanente l'exclusion des seules réversions complémentaires ; le texte (JORFARTI000001653734)
ne supprime de l'article 10, II, que les mots qui les visaient : l'exclusion des
réversions des régimes de base y reste jusqu'au 30 juin 2006, et LEGI garde l'article dans
cette rédaction depuis le 30 décembre 2004 (LEGIARTI000006233640). Même dérogation pour
les salariés agricoles (décret n° 2004-858, art. 18, versions jusqu'au 22 avril 2005 et
depuis). La Cnav l'appliquait (annexe de la n° 2006/37, « PR V1 [...] exclusion des PR des
régimes visés »).

**Bilan.** Aucun des six n'est infirmé. Deux sont précisés : les nés de 1953 à 1955
(critère de la demande ; 165 et non 164 pour 1955) et l'inapte (fin au 19 décembre
2008). Un est rétréci : la convention tchécoslovaque, surtout avant février 2003. L'ordre
des corrections ne change pas.
