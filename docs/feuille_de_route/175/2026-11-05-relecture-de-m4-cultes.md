# Relecture de M4/cultes

File R-M4/cultes de la septième vague, le 5 novembre 2026. C'est une relecture
indépendante des commits 62fe670, 9dce08d, f16bdf0 et 01856a9 (file M4/cultes, note
`2026-11-05-cultes-fraction-d-avant-1998.md`). Je n'ai rien repris de M4/cultes ni de ma
mémoire.

L'index LEGI de la DILA a été récupéré dans la session (`dila_index.py legi --recuperer`)
et il est à jour au 2 novembre 2026. Chaque article a été ouvert par `dila_cherche.py`
(`--texte`, `--num`, `--le`) dans sa rédaction en vigueur aux dates qui comptent. Les trois
pièces publiques ont été relues en ligne le 5 novembre 2026 :

- la page de la CAVIMAC et la réponse du Sénat, par un agent de lecture qui en a rendu les
  phrases mot pour mot ;
- le triptyque de 2024, téléchargé puis lu par `pdftotext`.

Les montants ont été refaits par un calcul qui n'appelle pas le modèle. Les moteurs ont été
éprouvés dans un worktree jetable, retiré depuis. Je n'ai rien modifié : ni règle, ni
donnée, ni test, ni fiche.

**Verdict : conforme pour les points 2 et 3, avec deux écarts faibles de forme. Le point 1
est conforme dans sa forme : l'écart est déclaré, mesuré et laissé au propriétaire. Son
fondement est pourtant plus faible que la fiche ne le dit (écart moyen, de preuve).** Aucune
valeur servie n'est à corriger avant la décision du propriétaire. Toutes les citations que
j'ai relues sont exactes.

## 1. L'âge du taux plein de la fraction d'avant 1998

**Les textes, mot pour mot : conforme.**

- **Décret n° 2006-1325, article 2**, rédaction du 1er juillet 2011 (LEGIARTI000023397816).
  Les extraits que la note et la fiche citent des I, II et V sont exacts, coupures
  comprises :
  - I : « est celui résultant des dispositions de l'article L. 161-17-2 [...] pour les
    assurés qui justifient » ;
  - II : « peut également être allouée à partir de l'âge mentionné au I. Il lui est alors
    appliqué le coefficient de minoration fixé au 2° du I et au II de l'article R. 351-27 » ;
  - V : « soit remplissent les conditions prévues à l'article D. 721-6 [...] soit justifient
    de la durée d'assurance visée au I ».
- **D. 721-6** (LEGIARTI000006738898, du 21 décembre 1985 au 26 février 2004, donc en
  vigueur au 31 décembre 1997) : « L'âge à partir duquel est allouée la pension de
  vieillesse prévue à la présente sous-section est fixé à soixante-cinq ans. »
- **R. 351-27** (LEGIARTI000024113020, du 3 juin 2011 au 1er septembre 2023) : la citation
  est exacte, « 1,25 % pour l'assuré né après 1952 » compris. L'arrondi y est « au chiffre
  immédiatement supérieur ».

**La lecture à la lettre de la note est juste.** Prenons une assurée de soixante-cinq ans
qui n'a pas la durée :
- elle ne relève pas du I : pour elle, l'âge de D. 721-6 reste soixante-cinq ans ;
- le II lui offre seulement une faculté (« également ») de partir plus tôt, avec le
  coefficient ;
- le V vise qui « remplissent les conditions prévues à l'article D. 721-6 ».

**Un argument de plus pour la lettre, que la note ne donne pas.** Le I a changé en 2011 :
- dans la rédaction du 30 janvier 2010 au 1er juillet 2011 (LEGIARTI000021763033), il
  disait : « est également abaissé à soixante ans au profit des assurés qui justifient
  [...] » ;
- la rédaction du 1er juillet 2011 y met l'âge de L. 161-17-2. L'index la rattache au
  décret n° 2010-1734 (article 11 : « applicables aux pensions prenant effet à compter du
  1er juillet 2011 »).

La réforme de 2010 a reporté l'âge du taux plein du régime général. L. 351-8, 1°
(LEGIARTI000028498855, en vigueur en 2018), le fixe à « l'âge prévu à l'article L. 161-17-2
augmenté de cinq années ». Le I a donc été récrit à ce moment-là, sans toucher aux
soixante-cinq ans de D. 721-6 pour qui n'a pas la durée. Cet argument ne tranche pas seul la
question, mais il pèse pour la lettre.

**Les pièces de la caisse sont citées exactement, mais elles ne disent pas tout ce que la
fiche leur prête. Écart moyen, de preuve.** Voici ce qu'elles disent :
- la page « Demander ma retraite de base » : « Si vous bénéficiez d'une pension calculée à
  taux minoré, les fractions de pension avant 1979 et de 1979 à 1997 seront portées au
  niveau du montant maximum de la pension « Cavimac » et vous aurez de plus une décote
  [...] » ; puis « on calcule le nombre de trimestres entre la date d'effet de la pension et
  l'âge du taux plein. Après comparaison, on retient le nombre de trimestres le plus faible
  pour calculer la décote » ;
- le triptyque : « L'âge d'obtention du taux plein dépend de l'année de naissance. L'âge
  auquel la retraite peut être attribuée à taux plein, quel que soit le nombre de
  trimestres, varie de 65 à 67 ans » ; et « il aura une décote, sauf s'il demande sa
  pension à l'âge du taux plein ».

Ce qu'elles ne disent pas :
- la page ne chiffre jamais « l'âge du taux plein ». Elle ne nomme ni soixante-cinq ans, ni
  D. 721-6, ni le décret n° 2006-1325 ;
- le triptyque parle de « la retraite » en général, dans un paragraphe qui ne distingue pas
  les fractions ;
- les deux pièces datent de 2024 et de 2026 : la page cite la loi de financement du 30
  décembre 2025 et les montants du 1er janvier 2026. Or le cas de la note se règle en 2018.

La note écrit : « Pour la caisse, [...] ses fractions d'avant 1998 se décotent jusqu'à
lui ». La fiche, de son côté, dit : « C'est ce que la caisse publie ». Ces deux phrases
assemblent deux énoncés généraux. La lecture est plausible : la page lie la décote des
fractions à « une pension calculée à taux minoré », c'est-à-dire à la pension entière, et
compte les trimestres jusqu'à un seul âge du taux plein. Mais ce n'est pas une déclaration
de la caisse sur ce cas.

La fiche le reconnaît d'ailleurs dans le même paragraphe (« aucune circulaire, aucun exemple
chiffré de la caisse ne tranche le cas lui-même »), ce qui contredit « C'est ce que la
caisse publie ». Le scénario 1 suit donc ici une déduction tirée de pages d'information,
contre une lettre que je lis comme la note, et que la récriture de 2011 renforce. La
question est bien posée au propriétaire. Il manque, pour la justifier par écrit, une pièce
de la caisse qui nomme le cas :
- une circulaire ou une instruction de la CAVIMAC sur le décret n° 2010-1734 ;
- ou la notification d'un ministre parti entre soixante-cinq ans et l'âge de sa
  génération ;
- ou une réponse écrite de la caisse.

**Les chiffres : conformes.**

- **66 ans et 2 mois.** D. 161-2-1-9 (LEGIARTI000025089933, du 31 décembre 2011 au 1er
  septembre 2023) : « Soixante et un ans et deux mois pour les assurés nés en 1953 ». On y
  ajoute cinq ans (L. 351-8, 1°), ce qui donne le 15 mai 2019. Du 1er avril 2018 au 15 mai
  2019, il y a 13 mois et 14 jours, soit 4,48 trimestres, arrondis à 5. Le coefficient vaut
  1 − 5 × 1,25 % = 0,9375.
- **165 trimestres.** Décret n° 2010-1734, article 9 (LEGIARTI000023383430) : « sont fixées
  à 165 trimestres pour les assurés nés en 1953 et 1954 ». La note ne l'avait pas relu ; je
  l'ai lu, et la valeur est exacte.
- **Le minimum au 1er octobre 2017** : 7 615,94 € et 8 322,13 € par an. Ces montants
  viennent de `legislation/minimum_contributif.csv` (barème de la Cnav, fiabilité `haute`),
  qui n'a pas d'autre date avant 2019. Ils sont repris du fichier ; je n'ai pas relu le
  barème en ligne.
- **Le maximum de 2018**, 4 635,65 €, est celui du modèle (`MaximumDesCultes`). Je ne l'ai
  pas refait ; il ne joue que sur 289,73 €.
- **Les calculs :**
  - 4 635,65 × 11 = 50 992,15 ; ÷ 165 = 309,0433 ; × 0,9375 = 289,7281, soit
    **289,73 €** ;
  - 7 615,94 × 11 = 83 775,34 ; ÷ 165 = 507,7293, soit **507,73 €** ;
  - le V seul : (7 615,94 − 4 635,65) × 11 ÷ 165 = 198,686 ;
  - l'écart entre les deux lectures : 218,00 € ;
  - avec le minimum majoré, sans la condition des 120 trimestres : 8 322,13 × 11 ÷ 165 =
    554,8087, soit 554,81 €.

## 2. Le minimum majoré du V : conforme

**Les textes.**

- **Le V.** Sa rédaction de 2006 (LEGIARTI000006256155, du 1er novembre 2006 au 30 janvier
  2010) est citée exactement. Il n'a pas changé dans les rédactions de 2010
  (LEGIARTI000021763033) et de 2011.
- **L. 351-10**, en deux rédactions :
  - du 1er janvier 2004 au 19 décembre 2008 (LEGIARTI000006742926) : « Ce montant minimum
    est majoré au titre des périodes ayant donné lieu à cotisations à la charge de
    l'assuré. » La citation est exacte, et il n'y a aucune condition de durée ;
  - à partir du 19 décembre 2008 (LEGIARTI000019959492) : la condition est citée exactement.
    La note de l'index porte : « Loi n° 2008-1330 du 17 décembre 2008 articles 81 II et 89
    III : Les modifications introduites par les présents articles sont applicables aux
    pensions prenant effet à compter du 1er avril 2009 ». Je l'ai lue dans l'index LEGI, non
    au JORF.
- **D. 351-2-2** (LEGIARTI000020090096, du 1er avril 2009 au 1er septembre 2023) : « est
  fixée à 120 trimestres ».
- **D. 351-2-1**, en deux rédactions :
  - du 31 décembre 2007 au 1er avril 2009 (LEGIARTI000017870194) : « 6 958,21 euros par an
    au 1er janvier 2008 » ; « de façon à atteindre 7 603,41 euros par an au 1er janvier
    2008 ». Cette rédaction ne pose aucune condition de 120 trimestres ;
  - à partir du 1er avril 2009 (LEGIARTI000020090091), elle ajoute : « Sous réserve de la
    condition prévue à la deuxième phrase du premier alinéa de l'article L. 351-10 ».
- **R. 351-6** (LEGIARTI000006749349) : « 150 trimestres pour les assurés nés avant
  1944 ».

**Une autre date, propre aux cultes ? Aucune.** Le V ne date rien lui-même, et il n'a
changé ni en 2010 ni en 2011. L. 382-27 (LEGIARTI000019959668, à partir du 19 décembre 2008)
renvoie l'après-1998 à « L. 351-8 à L. 351-13 ». Il renvoie l'avant-1998 aux règles de 1997
« sous réserve d'adaptation par décret », sans date à lui. Le renvoi du V emporte donc la
date de L. 351-10 elle-même, le 1er avril 2009.

Avant cette date, les deux lectures du V concordent : qu'on prenne le montant seul, ou le
montant avec sa condition, le résultat est le même. La correction ne dépend donc pas de la
question que la note laisse ouverte pour la période d'après.

**Le calcul.**
- 7 603,41 × 40 = 304 136,40 ; ÷ 150 = 2 027,576, soit **2 027,58 €** ;
- 6 958,21 × 40 = 278 328,40 ; ÷ 150 = 1 855,523, soit **1 855,52 €**.

**Écart faible, de forme.** « 172,06 € de plus par an » est la différence des deux montants
arrondis. La différence des montants exacts est de 172,053, soit 172,05 €. C'est sans effet.

**Les moteurs.**

- **Vert dans les deux moteurs.** `tests/test_cultes.py` donne 10 tests verts, avec et sans
  `PRESOMPTIONS_DECALEES=1`. Le test passe par `droit_et_refait`, qui confronte au bit près
  le portage JavaScript et son jumeau Python.
- **Rouge sans la correction.** Dans le worktree jetable :
  - avec `cultes.js` et `cultes.py` de d79ba65, le test échoue sur « 40 trimestres cotisés
    de 1979 à 1997 (minimum contributif) = 1,855.52 € » ;
  - avec l'ancien `cultes.js` seul, la confrontation des deux moteurs échoue (« attendu
    3883.0986666666668, lu 4055.152 ») ;
  - avec l'ancien `cultes.py` seul, elle échoue aussi, dans l'autre sens.
- **La frontière du 1er avril 2009.** J'ai pris la carrière du test (ministre de 45 à 65 ans)
  et fait varier la date de naissance :

  | Naissance | Pension au | Trimestres cotisés | Niveau servi |
  |---|---|---|---|
  | 15 janvier 1944 | 1er février 2009 | moins de 120 | « minimum contributif majoré » |
  | 15 février 1944 | 1er mars 2009 | moins de 120 | « minimum contributif majoré » |
  | 15 mars 1944 | 1er avril 2009 | 80 | « minimum contributif » |
  | 1945 | 2010 | 80 | minimum |
  | 1945, ministre dès 35 ans | 2010 | 120 | majoré |

  Les résultats sont les mêmes sous `PRESOMPTIONS_DECALEES=1`. Après le 1er avril 2009, le
  seuil tient.
- **La classe, pas le cas.** Il ne reste aucune constante de 120 trimestres dans
  `moteur/js/droit/`.

## 3. « Gratuitement » : conforme

- **Les pièces citées sont exactes.**
  - La page de la CAVIMAC : « Une fraction de pension pour les périodes d'activité cultuelle
    réalisées avant 1979 correspondant à des trimestres validés à titre gratuit ».
  - Le triptyque : « Les trimestres sont validés à titre gratuit avant 1979. »
  - Le Sénat : question orale n° 0122S de M. Auguste Cazalet, publiée au JO Sénat du 6
    décembre 2007, p. 2204. La réponse a été apportée en séance le 15 janvier 2008 et
    publiée au JO Sénat du 16 janvier 2008, p. 207. On y lit : « pour les années
    antérieures à 1979, qui n'ont donné lieu à aucune cotisation et ont été validées
    gratuitement ». Le texte est exact.
- **D. 721-11 et l'article 42.** D. 721-11 (LEGIARTI000006739120, du 13 novembre 1988 au 21
  juin 1998) et le décret n° 79-607, article 42 (LEGIARTI000006766268, du 1er janvier 1979
  au 21 décembre 1985), disent tous deux « sont prises en compte pour l'ouverture du droit
  et le calcul de la pension ». Ni l'un ni l'autre ne dit « sans cotisation ». Les
  commentaires des deux moteurs et la docstring du test citent juste. Il en va de même de
  L. 382-25 (LEGIARTI000006742803) : « Des cotisations à la charge des assurés ».
- **Écart faible, de forme.** La note (§ 3) donne une seule citation pour D. 721-11 et pour
  l'article 42. Or ses mots « mentionnées à l'article 1er de la loi du 2 janvier 1978
  susvisée » sont ceux de l'article 42. D. 721-11 dit « mentionnées à l'article L. 721-1 »
  et « départements mentionnés à l'article L. 751-1 ». Le sens est le même, et le code comme
  la fiche citent chacun le bon texte.

## 4. Les témoins : conforme

Dix-huit témoins de simulation portent une fraction d'avant 1998, et treize d'entre eux la
majoration du V. Ces treize-là sont tous servis au « minimum contributif majoré », et tous
ont des carrières cultuelles entières, à 120 trimestres cotisés ou plus. Aucun n'a sa
pension entre le 1er novembre 2006 et le 31 mars 2009 avec moins de 120 trimestres cotisés.

« Aucun témoin ne bouge » est donc exact, mais faute de témoin du cas. Ce n'est pas un
écart : le cas est tenu par un test qui confronte les deux moteurs, et qui rougit si l'un ou
l'autre perd la correction. Or `src/CLAUDE.md` ne demande un témoin de plus que « quand la
confrontation ne rougit pas sans lui ».

## Ce qui reste

- **Au propriétaire, le point 1.** Il faut choisir entre la lettre du décret (507,73 €) et la
  pratique que l'on prête à la caisse (289,73 €). Pour une preuve écrite, il faut une pièce
  de la caisse qui nomme le cas (voir § 1). Tant qu'elle manque, la phrase « C'est ce que la
  caisse publie » de la fiche dit plus que ses deux pièces. Le propriétaire décidera s'il
  faut la récrire.
- **Non relu ici :**
  - le maximum de 4 635,65 € (la chaîne des revalorisations depuis 1997) ;
  - le barème du minimum de la Cnav, lu dans le fichier du dépôt ;
  - la loi n° 2008-1330 au JORF, lue par la note de l'index LEGI.
- **Textes manquants :** aucun.
