# Retouches de la relecture R-M4/cultes : « C'est ce que la caisse publie » dit à la mesure des pièces, 172,05 € au lieu de 172,06, une citation rendue à son texte (Retouches 4)

**Le 5 novembre 2026, « Retouches 4 ».** La relecture R-M4/cultes
(`2026-11-05-relecture-de-m4-cultes.md`) jugeait la note de M4/cultes
(`2026-11-05-cultes-fraction-d-avant-1998.md`) conforme pour ses points 2 et 3, avec deux
écarts faibles de forme, et conforme dans sa forme pour le point 1, dont le fondement était
pourtant plus faible que la fiche ne le disait (écart moyen, de preuve). Chaque pièce a été
rouverte ici ; aucune valeur du modèle, aucun témoin, aucun test ne bouge, et rien n'est
corrigé dans les moteurs : la question de l'âge du taux plein de la fraction d'avant 1998
reste posée au propriétaire. Le paquet (`python scripts/construire_donnees.py`) ne change
pas.

## 1. B1 — « C'est ce que la caisse publie » : ce que les pièces disent, et ne disent pas

**Les pièces, rouvertes le 5 novembre 2026.**

- La page « Demander ma retraite de base » de la CAVIMAC (sha256 5fd415b5…df4ba3268 du HTML
  téléchargé). Elle cite « le 30 décembre 2025, la loi de financement de la sécurité sociale
  pour 2026 » et les montants « au 1er janvier 2026 ». Sous « Le taux minoré » : « Si vous
  bénéficiez d'une pension calculée à taux minoré, les fractions de pension avant 1979 et de
  1979 à 1997 seront portées au niveau du montant maximum de la pension « Cavimac » et vous
  aurez de plus une décote qui sera appliquée sur le taux retenu pour le calcul de ces deux
  fractions (une décote de 1,25 % par trimestre manquant sera appliquée sur le taux plein
  qui est de 100 %). » Sous « La décote et la surcote » : « Pour calculer le nombre de
  trimestre de décote, on comptabilise tout d'abord le nombre de trimestres compris entre
  le nombre de trimestres tous régimes confondus et le nombre de trimestres requis pour
  l'obtention du taux plein puis on calcule le nombre de trimestres entre la date d'effet de
  la pension et l'âge du taux plein. Après comparaison, on retient le nombre de trimestres
  le plus faible pour calculer la décote. » Aucun âge du taux plein n'y est chiffré : « le
  taux plein » n'y est défini que par son taux (« 50% dans les régimes alignés »).
- Le triptyque « Votre assurance retraite » (sha256 868aa09c…ab0df4f91 du PDF, créé le 26 mars
  2024 selon ses métadonnées). Sous « L'âge de la retraite à taux plein » : « L'âge d'obtention
  du taux plein dépend de l'année de naissance. L'âge auquel la retraite peut être attribuée
  à taux plein, quel que soit le nombre de trimestres, varie de 65 à 67 ans. » Le paragraphe
  parle de « la retraite » ; la section « Le calcul de la retraite », où les trois périodes
  sont distinguées, est ailleurs dans le dépliant.
- Le décret n° 2006-1325, article 2, au I et au II, dans ses deux rédactions : du 30 janvier
  2010 au 1er juillet 2011 (LEGIARTI000021763033, décret n° 2010-103) : « I. - L'âge fixé au
  premier alinéa de l'article D. 721-6 [...] est également abaissé à soixante ans au profit
  des assurés qui justifient [...] d'une durée au moins égale à la durée fixée au 1° de
  l'article R. 351-27 [...] » ; « II. - [...] peut également être allouée à partir de l'âge de
  soixante ans. » ; depuis le 1er juillet 2011 (LEGIARTI000023397816, décret n° 2010-1734,
  article 11, « applicables aux pensions prenant effet à compter du 1er juillet 2011 ») :
  « I. - L'âge fixé au premier alinéa de l'article D. 721-6 [...] est celui résultant des
  dispositions de l'article L. 161-17-2 [...] pour les assurés qui justifient [...] » ;
  « II. - [...] peut également être allouée à partir de l'âge mentionné au I. »

**Ce que la fiche disait, et ce que les pièces permettent d'écrire.** La fiche écrivait
« C'est ce que la caisse publie » et, plus bas, « Le scénario 1 suit la caisse, qui publie
la règle », tout en reconnaissant, dans le même paragraphe, qu'« aucune circulaire, aucun
exemple chiffré de la caisse ne tranche le cas lui-même ». Les pièces disent :

- la page lie la décote des fractions à « une pension calculée à taux minoré », donc à la
  pension entière, et compte les trimestres jusqu'à « l'âge du taux plein », un seul, qu'elle
  ne chiffre jamais ;
- le triptyque chiffre cet âge, de 65 à 67 ans, de « la retraite » en général, dans un
  paragraphe qui ne distingue pas les fractions ;
- aucune ne nomme D. 721-6 ni le décret n° 2006-1325, aucune ne dit l'âge du taux plein de la
  fraction d'avant 1998 ; elles datent de mars 2024 et de 2026 (la page cite la loi du 30
  décembre 2025), quand le cas du modèle, la ministre du culte née en 1953 partie en 2018,
  se règle en 2018.

La lecture que le modèle sert, celle d'un seul âge du taux plein pour toute la pension, est
donc une déduction de deux pièces d'information, non une règle que la caisse publie. Elle
est plausible, et la lettre du décret dit autre chose. La récriture du I en 2011, que R-M4
a relevée (« abaissé à soixante ans » remplacé par l'âge de L. 161-17-2, sans toucher aux
soixante-cinq ans de D. 721-6 pour qui n'a pas la durée), pèse pour la lettre sans la
trancher seule ; je l'ai relue aux deux rédactions ci-dessus, la citation est exacte.

**Écrit.**

- Fiche `cultes_fractions_de_pension`, l'écart de la version `decret_de_2010` : la phrase est
  récrite pour dire que c'est une lecture de deux pièces d'information, ce que chacune dit,
  ce qu'aucune ne dit (l'âge de la fraction, D. 721-6, le décret, un cas de 2018), puis la
  lettre du décret et la récriture de 2011 avec ses deux rédactions ; « le scénario 1 suit la
  caisse, qui publie la règle » devient « le scénario 1 sert la lecture des pièces de la
  caisse, non la lettre » ; l'effet dit « selon la lecture des pièces de la caisse » là où il
  disait « comme la caisse le décrit » ; les pièces qui manquent (circulaire sur le décret,
  notification d'un ministre du culte parti entre soixante-cinq ans et l'âge de sa
  génération, réponse écrite de la caisse) sont aux `a_relire`.
- La même phrase se retrouvait, sous une autre forme, à deux autres places, corrigées de
  même : l'effet de la fiche `taux_plein_a_soixante_cinq_ans` (« la caisse publie l'âge du
  taux plein de la génération [...] et la décote des fractions d'avant 1998 à taux minoré,
  que le modèle suit » devient ce que les pièces disent, sans chiffrer l'âge de la fraction)
  et `docs/limites/4-regimes-incomplets.md` (le taux plein du régime général pour la
  fraction d'avant 1998, que le décret laisse à soixante-cinq ans à qui n'a pas la durée,
  rendu comme question au propriétaire).
- La question reste au propriétaire : suivre la lecture des pièces (289,73 € par an avant
  1998) ou la lettre (507,73 €). Rien n'est changé au modèle.

## 2. B2 — deux écarts faibles

**172,05 €, non 172,06 €.** La note de M4/cultes (§ 2, le test des 120 trimestres avant avril
2009) donne « 2 027,58 € [...] au lieu de [...] 1 855,52 € : 172,06 € de plus par an ». Au
calcul : 7 603,41 × 40 / 150 = 304 136,40 / 150 = 2 027,576 ; 6 958,21 × 40 / 150 =
278 328,40 / 150 = 1 855,5227 ; l'écart exact est (7 603,41 − 6 958,21) × 40 / 150 = 645,20 ×
40 / 150 = 25 808 / 150 = 172,0533, soit **172,05 €**. 172,06 est la différence des deux
montants arrondis chacun au centime (2 027,58 − 1 855,52). Le bon écart est 172,05 € ; les deux
montants, eux, sont justes. Le chiffre n'est que dans cette note, qui est un récit : la fiche
et les tests ne le portent pas (`grep` de « 172,06 » et « 172.06 » dans le dépôt hors paquet
et archives : la note, et la relecture qui le relève ; le seul autre « 172,058… » est la
pension mensuelle d'un autre cas dans un témoin).

**L'article 42 du décret n° 79-607 et D. 721-11 ne sont pas le même texte.** Ouverts tous deux à
l'index LEGI :

- D. 721-11 (LEGIARTI000006739120, du 13 novembre 1988 au 21 juin 1998) : « Sous réserve qu'à la
  date d'entrée en jouissance de la pension l'assuré soit à jour de ses cotisations
  personnelles, sont prises en compte pour l'ouverture du droit et le calcul de la pension,
  les périodes d'exercice d'activités mentionnées à l'article L. 721-1 accomplies
  antérieurement au 1er janvier 1979 [...], en France métropolitaine et dans les départements
  mentionnés à l'article L. 751-1, lorsque ces périodes ne sont pas validées par un autre
  régime obligatoire d'assurance vieillesse de base. Il en est de même pour les périodes
  d'exercice desdites activités accomplies à l'étranger et dans les territoires français
  d'outre-mer par des personnes de nationalité française [...] dès lors que ces personnes
  fournissent la preuve par tous moyens de l'exercice d'une telle activité. »
- Le décret n° 79-607, article 42 (LEGIARTI000006766268, du 1er janvier 1979 au 21 décembre
  1985) : la même phrase, avec « mentionnées à l'article 1er de la loi du 2 janvier 1978
  susvisée » et « dans les départements d'outre-mer mentionnés à l'article 1er », et, pour la
  seconde, « dans la mesure où ces périodes ont été validées par les régimes de prévoyance
  mentionnés à l'article 59 ».

La note de M4/cultes (§ 3) donne une seule citation, celle de l'article 42 (« l'article 1er de
la loi du 2 janvier 1978 susvisée »), pour les deux. Le sens de la règle qu'elle cite, « sont
prises en compte pour l'ouverture du droit et le calcul de la pension », est le même ; ni l'un
ni l'autre ne dit « sans cotisation ». **Rien à corriger dans la fiche** `cultes_fractions_de_pension`,
qui porte à ses `textes` chaque citation à son texte (D. 721-11 avec « l'article L. 721-1 »,
l'article 42 avec « l'article 1er de la loi du 2 janvier 1978 susvisée »), ni dans
`affiliations.yaml`, dont la citation est la partie commune aux deux ; seule la note mêle les
deux, et elle ne se récrit pas.

## Sources ouvertes dans la session

- **Pièces publiques** : la page de la CAVIMAC « Demander ma retraite de base »
  (https://www.cavimac.fr/assurance-retraite/assurance-retraite/demander-ma-retraite-de-base-0)
  et le triptyque
  (https://www.cavimac.fr/sites/default/files/medias/documents/Triptyque%20retraite_2024.pdf),
  téléchargés le 5 novembre 2026, lus en texte.
- **Index LEGI** (à jour au 2 novembre 2026) : décret n° 2006-1325, article 2, LEGIARTI000021763033
  et LEGIARTI000023397816 ; D. 721-11, LEGIARTI000006739120 ; décret n° 79-607, article 42,
  LEGIARTI000006766268.
- **Dépôt** : la fiche `cultes_fractions_de_pension`, `affiliations.yaml`.
