# Relecture du taux plein à 65 ans des parents de trois enfants nés de juillet 1951 à 1955

File R-M4, le 3 novembre 2026 : relecture indépendante des commits ee8e6ac et 213318b
(session M4, note `2026-11-03-taux-plein-parents-de-trois-enfants.md`). Chaque texte a été
rouvert ici, sans rien reprendre de la session ni de mémoire : l'index de la DILA, LEGI et
JORF récupérés et mis à jour (à jour au 2 novembre 2026, aucun incrément depuis) ; la
circulaire de la Cnav et les deux recueils de l'Agirc-Arrco téléchargés le jour, leur
empreinte recalculée ; les exposés de la Cnav servis par son API le jour. Les citations ont
été comparées au texte par un script, fragment par fragment. Rien n'a été modifié : ni règle,
ni donnée, ni test, ni fiche.

**Verdict.** Le régime général, les salariés agricoles, les artisans et les commerçants :
**conforme** — chaque citation mot pour mot, chaque date, chaque valeur attendue refaite à la
main depuis le texte. **Trois écarts** : un grave (l'Agirc-Arrco, point 5), un moyen (des
régimes où vaut le même âge, ni servis ni déclarés, point 6), des références mineures
(point 7).

## 1. Les textes, à la version en vigueur

| Texte | Identifiant ouvert | Constat |
|---|---|---|
| Loi n° 2010-1330, art. 20, IV | LEGIARTI000023023835 | seule rédaction de l'index, du 11 novembre 2010 au 28 février 2025 ; la citation de la fiche s'y trouve mot pour mot : **conforme** |
| Loi n° 2010-1330, art. 118, II | JORFARTI000023022348 ; LEGIARTI000023024205, LEGIARTI000047453380 | « Les articles 18 à 40, 79, 83 et 84 sont applicables aux pensions prenant effet à compter du 1er juillet 2011. » : **conforme** |
| Décret n° 2011-620, art. 2 | LEGIARTI000024111672 | seule rédaction, depuis le 3 juin 2011 ; citation exacte : **conforme** |
| L. 351-12 | LEGIARTI000006742643 | du 27 décembre 1998 au 1er septembre 2023 ; citation exacte : **conforme** |
| R. 351-12, 3° et 5° | LEGIARTI000024113005, LEGIARTI000024438787, LEGIARTI000026560090, LEGIARTI000029012986, LEGIARTI000031285238, LEGIARTI000031828370, LEGIARTI000043495410 | les sept rédactions du 3 juin 2011 au 1er septembre 2023 portent le même 3° et le même 5°, vérifié une à une : **conforme** |
| R. 351-27 | LEGIARTI000024113020 | seule rédaction du 3 juin 2011 au 1er septembre 2023 ; I, 2°, mot pour mot ; II, « 1,5 % pour l'assuré né en 1951 ; 1,375 % pour l'assuré né en 1952 ; 1,25 % pour l'assuré né après 1952 », appliqué « au " taux plein " » : **conforme** |
| R. 351-7 | LEGIARTI000024113035 | citation exacte ; le moteur passe à la majoration le même âge qu'à la décote (`liquider.duree_majoree_apres_taux_plein` reçoit `ouvrir.age_taux_plein`) : **conforme** |
| Loi n° 2025-199, art. 87 | JORFARTI000051269910 | IV, « Les III et IV de l'article 20 et les III à VI de l'article 21 [...] sont abrogés » ; VIII, A, « les IV à VII s'appliquent aux pensions prenant effet à compter du 1er janvier 2026 » : **conforme** |
| L. 161-17-2 | LEGIARTI000025014605 | 62 ans dès 1955, quatre mois de plus par génération de juillet à décembre 1951, cinq de 1952 à 1954 : avec les cinq ans du 1° de L. 351-8, 65 ans et 4 mois, 65 ans et 9 mois, 66 ans et 2 mois, 66 ans et 7 mois, 67 ans : **conforme** à la table de la Cnav |
| L. 351-8 | LEGIARTI000023030950, LEGIARTI000028498855, LEGIARTI000047452736, LEGIARTI000051289852 | dates exactes ; les 1° bis et 6° de la rédaction de 2025, mot pour mot : **conforme** |
| Loi n° 2010-1330, art. 21, IV | LEGIARTI000028498869 | citation exacte : **conforme** |
| Arrêté du 30 décembre 1970, art. 16, I, 3°, d | LEGIARTI000037845437 (et LEGIARTI000024266924, LEGIARTI000036755233, de 2011 à 2018) | « Aux personnes qui bénéficient d'une pension de vieillesse à taux plein du régime général [...] à l'âge de soixante-cinq ans, à savoir : [...] d) Les agents et anciens agents nés entre le 1er juillet 1951 et le 31 décembre 1955 inclus ayant eu ou élevé au moins trois enfants » : **conforme** (l'Ircantec non servie est déclarée) |
| Circulaire Cnav n° 2014-64 | PDF de la base de législation, sha256 f6717a0f61473e4ea56976868f97b2dbb8068ba22d57befbaf2c0e120cdcaccb | empreinte identique à celle de la fiche ; chaque fragment cité se trouve dans le texte : **conforme**, à une coupure près (point 7) |
| Exposé Cnav « Taux plein à 65 ans » | API, modifié le 18 septembre 2026, sha256 bb4093e933487066ab5a116e0fe5d3529148b554ebc54c3c625871de5a897034 | empreinte identique ; citations exactes : **conforme** |
| Exposé Cnav « Taux de la retraite personnelle » | API, modifié le 29 juillet 2026, sha256 68f5253e9b848f77ce335e2eb633fb77d9f750e8eeb2a4532c21c9498fb4b467 | empreinte identique ; les six âges cités exacts : **conforme** |

*Un autre texte change-t-il la règle ?* Les recherches « 1er juillet 1951 » et « 31 décembre
1955 », « IV de l'article 20 de la loi », « trois enfants » avec « soixante-cinq ans » ne
trouvent, pour le régime général, les salariés agricoles et les artisans et commerçants,
que des textes qui l'appliquent : L. 634-2 (rédactions de 2011 à 2023, « L. 351-7 à
L. 351-10-1 », puis les chapitres Ier à V du titre V) et L. 742-3 du code rural (« titre V »)
y portent L. 351-8 ; D. 634-5 (LEGIARTI000023397687, LEGIARTI000034624541,
LEGIARTI000041966606, de 2011 à 2023) y porte la majoration de durée après soixante-cinq ans. Elles trouvent en revanche les mêmes règles dans des régimes que la
fiche ne nomme pas (point 6).

## 2. La circulaire, et les listes du code

L'annexe 1 de la circulaire n° 2014-64 dit, période par période, ce qui compte avant la
naissance, après elle et pour l'activité préalable. Les listes du code
(`_RETENUES_AVANT`, `_ECARTEES_APRES`, l'emploi seul pour l'activité) la suivent pour chaque
motif que la saisie connaît (`SANS_EMPLOI`, `moteur/js/cles.js`) : la maladie, la maternité,
le chômage comptent avant et après ; le service militaire après seulement ; l'invalidité,
l'accident du travail et l'AVPF jamais ; l'activité ne compte que les cotisations, de tous les
régimes de base. L'AVPF ne se porte que sur une ligne non cotisée (`carriere.js`, ligne 774) :
l'écarter par son salaire n'écarte jamais un emploi. Le décompte de l'année de la naissance,
`min(emploi, (mois − 1) // 3)`, est celui des deux exemples du point 2.2.2 (avril 1975 :
1 trimestre ; novembre 1975 : 3), que la circulaire justifie : « il n'y a pas lieu de vérifier
si le salaire reporté au compte [...] correspond à la période effectivement retenue ». Le
point 6 de la circulaire confirme la borne du 1er juillet 2011 : la mesure « peut d'ores et
déjà être mise en œuvre pour la détermination du taux minoré ». **Conforme.**

## 3. Les valeurs du test, refaites à la main

Assurée née le 15 du mois dit, quatre trimestres d'emploi chaque année de `debut` à la veille
du départ, sauf les années dites ; « avant » : les deux années qui précèdent celle de la
naissance (au moins 8) ; « fenêtre » : l'année de la naissance et les deux suivantes, ou les
trois suivantes pour un second semestre (au plus 8) ; « activité » : l'emploi des années
d'avant, plus les trimestres civils écoulés l'année de la naissance (au moins 8).

| Cas | Calcul | Attendu par le test |
|---|---|---|
| interrompue trois ans | avant 4 + 4 = 8 ; fenêtre 1980-1982, 0 ; activité 28 | 65 ans ✓ |
| AVPF, invalidité trois ans | fenêtre 0, l'AVPF et l'invalidité écartées | 65 ans ✓ |
| arrêt maladie trois ans | fenêtre 12 ; enfant de 1984 : fenêtre 12 ; de 1986 : 12 | 66 ans 2 mois ✓ |
| sans interruption ; deux enfants ; naissances non dites | fenêtres 12 ; 2 < 3 ; aucune naissance déclarée | 66 ans 2 mois ✓ |
| à l'année, les deux fenêtres | 1980-1982, 0 ; 1981-1983, 4 ; activité 28 | 65 ans ✓ |
| septembre, 1983 seule | fenêtre 1981-1983, 4 + 4 + 0 = 8 ; activité 28 + min(4, 2) = 30 | 65 ans ✓ |
| mars, 1983 seule ; à l'année, 1983 seule | fenêtre 1980-1982, 12 ; enfant de 1984 : avant 4 + 0 ; de 1986 : fenêtre 12 | 66 ans 2 mois ✓ |
| chômage, novembre | avant 4 (chômage) + 4 = 8 ; fenêtre 0 ; activité 1 + 0 + 4 + 3 = 8, l'exemple 2 de la circulaire | 65 ans ✓ |
| chômage, septembre | activité 1 + 0 + 4 + 2 = 7 ; enfant d'avril 1980 : avant 0 + 4 ; d'avril 1982 : fenêtre 12 | 66 ans 2 mois ✓ |
| juillet 1951 ; décembre 1955 ; janvier 1956 | effets au 1er août 2016 et au 1er janvier 2021, dans la version ; 1956 hors des générations | 65 ans ✓, 65 ans ✓, 67 ans ✓ ; sans interruption, 65 ans et 4 mois ✓ |
| salariés agricoles, RSI | L. 742-3 et L. 634-2 portent L. 351-8 | 65 ans ✓ |
| Arrco, 2018 | voir le point 5 | 66 ans 2 mois ✗ |
| de bout en bout, à 65 ans | effet au 1er avril 2018, après le 65e anniversaire : 0 trimestre | 50 % ✓ |
| deux enfants, à 65 ans | du 1er avril 2018 au 15 mai 2019, 13 mois et demi, 5 trimestres arrondis : 50 % × (1 − 5 × 1,25 %) | 46,875 % ✓ |
| trois enfants, à 64 ans | du 1er avril 2017 au 15 mars 2018, 11 mois et demi, 4 trimestres | 47,5 % ✓ |
| deux enfants, à 64 ans | jusqu'au 15 mai 2019, 25 mois et demi, 9 trimestres | 44,375 % ✓ |

La note de M4 compte 14 et 26 mois depuis l'anniversaire, non depuis la date d'effet : même
nombre de trimestres, aucun effet.

## 4. Les deux moteurs

- `tests/test_taux_plein_a_soixante_cinq_ans.py` : 7 passés.
- `tests/test_regle_de_chacun.py` : 5 passés.
- `python -m pytest -m rapide` : 4 159 passés, 24 échecs, dont aucun ne touche la règle ; les
  mêmes 24 échouent à 0a64139, avant M4, et dès f716130 (action 177, étape 9, le RCO des
  artisans), quand les 21 qui existaient déjà passent à eab4dae : f716130 change
  `rco_artisans.yaml` et `construire_donnees.py` sans le paquet `moteur/donnees.json`, que la
  fabrique de GitHub refait. Hors de cette relecture, à suivre par la course suivante.
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 3 985 passés, 5 échecs, du même lot.

## 5. Écart grave : l'Agirc-Arrco sert ces parents sans abattement

La fiche écrit, comme du droit : « L'Agirc-Arrco garde l'âge de sa génération : ni l'accord du
18 mars 2011 ni celui du 17 novembre 2017, tels que la fiche
coefficients_anticipation_agirc_arrco les cite, ne nomment ces parents » ; le test
`test_les_regimes_alignes_suivent_les_complementaires_non` affirme l'âge de 66 ans et 2 mois
à l'Arrco en 2018. Les textes disent l'inverse.

- *Accord du 18 mars 2011, article 1er* (recueil « Accords nationaux des partenaires
  sociaux », https://www.agirc-arrco.fr/storage/2021/11/liste_accords_paritaires_Agirc_Arrco.pdf,
  sha256 0186b6b165ad2a5f5f561deb969c6a35c661dc2e1fedbfcdcaa24801f51104c1, celle que la fiche
  `coefficients_anticipation_agirc_arrco` consigne, p. 146-147) : les participants qui ont
  fait liquider, avant l'âge du 1° de L. 351-8, leur pension à taux plein du régime général
  ou agricole « soit en application du 1° bis et du 1° ter de l'article L. 351-8 du code de
  la Sécurité sociale ou en application des III et IV de l'article 20 de la loi n° 2010-1330
  du 9 novembre 2010 [...] (aidants familiaux, assurés handicapés, parents d'enfant
  handicapé et parents de 3 enfants sous certaines conditions) ; pourront faire liquider
  leurs allocations AGIRC et/ou ARRCO, sans abattement, sur les tranches A et B des
  rémunérations », « pour toute liquidation [...] prenant effet à compter du 1er juillet
  2011 et jusqu'au 31 décembre 2018 au plus tard ». La fiche
  `coefficients_anticipation_agirc_arrco` résume cette liste sans ces mots, et M4 s'y est
  fié sans rouvrir l'accord.
- *Accord du 17 novembre 2017, article 84* (applicable au 1er janvier 2019,
  https://www.agirc-arrco.fr/storage/2024/09/201809dc_ANI_du_17_novembre_2017.pdf, téléchargé
  le 3 novembre 2026, sha256 b8af8df7372e4f897c1ca0c4fd9bf4baaa5b706ec4737b8e51b593c5a2a4fccb) :
  « 1. Le participant peut bénéficier de sa pension [...] sans abattement dès lors qu'il a
  atteint l'âge visé au 1° de l'article L. 351-8 » — l'âge que le IV de l'article 20 fixe à
  soixante-cinq ans pour ces parents — ; « 3. Le participant bénéficie de sa pension [...]
  sans application des coefficients viagers [...] à l'âge auquel il a obtenu la pension
  d'assurance vieillesse du régime général ou du régime des assurances sociales agricoles à
  taux plein ».

*Ce que le modèle sert* (les deux moteurs, `servi_et_refait`) : la requête de bout en bout du
test, trois enfants, à 65 ans en avril 2018 — régime général « taux 50.000% », Arrco
« coefficient d'anticipation 0.9500 » ; née le 15 septembre 1954, sans activité de 1977 à 1999,
enfants d'avril 1977, juin 1979 et juin 1981, à 65 ans en octobre 2019 — régime général
« taux 50.000% », Agirc-Arrco « coefficient d'anticipation 0.9300 ». Le droit sert ces deux
complémentaires sans coefficient : 5 % et 7 % de trop retirés. La limite de
`docs/limites/ecarts-au-droit-positif.md` (« ses complémentaires ») couvre le résultat, mais
la fiche et le test donnent pour du droit ce qui n'en est pas.

## 6. Écart moyen : les régimes où vaut le même âge, ni servis ni déclarés

La fiche et la limite ne nomment, hors des trois régimes servis, que les non-salariés
agricoles, les libéraux, les avocats et l'Ircantec. Le modèle calcule pourtant trois autres
familles où la même règle est écrite :

- *Les fonctionnaires sédentaires* : loi n° 2010-1330, article 28, III (LEGIARTI000025014566) :
  « l'âge auquel s'annule le coefficient de minoration prévu à l'article L. 14 du code des
  pensions civiles et militaires de retraite ne peut être supérieur à soixante-cinq ans » pour
  ceux nés du 1er juillet 1951 au 31 décembre 1955 qui remplissent « les conditions prévues
  aux 1° à 3° du IV de l'article 20 » ; leurs conditions propres à l'article R. 26 ter du code
  des pensions, inséré par l'article 3 du décret n° 2011-620 (JORFARTI000024110126 : au moins
  une année d'interruption, dans un congé ou une disponibilité de R. 13, ou un temps partiel
  d'une durée qui dépend de la quotité) ; la CNRACL (décret n° 2003-1306, article 65-3,
  LEGIARTI000024113270) et les ouvriers de l'État (décret n° 2004-1056, article 50-3,
  LEGIARTI000024113274), qui renvoient à R. 26 ter (décret n° 2011-620, article 10,
  JORFARTI000024110234). Le simulateur, sur une fonctionnaire de l'État ou de la CNRACL née le
  15 mars 1955, sans activité de 1978 à 2002, trois enfants nés en avril 1978, juin 1980 et
  juin 1982, partie à 65 ans : « taux 70.312% », soit 75 % × (1 − 5 × 1,25 %) — l'âge
  d'annulation du modèle, 67 ans moins 3 trimestres —, quand le droit lui sert 75 % si son
  interruption a été l'un des congés ou la disponibilité de R. 13, ce que la saisie ne
  demande pas : la règle tient donc à un fait non saisi, qui se déclare. Servir la règle
  demande de plafonner l'âge d'annulation de la fonction publique, `age_annulation −
  trimestres_avant / 4` (`liquider.py`), non l'âge du 1° de L. 351-8.
- *Les cultes* : L. 382-27 (LEGIARTI000019959668, de 2008 à 2023) sert la pension de la
  CAVIMAC « dans les conditions définies aux articles [...] L. 351-8 à L. 351-13 », et le IV
  de l'article 20 « est applicable dans tous les régimes obligatoires de retraite auxquels
  s'appliquent les dispositions de l'article L. 351-8 » ; le modèle lit la CAVIMAC à l'âge de
  la génération (`cavimac.yaml`).
- *Les points d'avant 1973 des artisans et des commerçants* : décret n° 73-937, article 3, II
  (LEGIARTI000026474703, du 7 octobre 2012 au 1er septembre 2023) : la minoration se compte
  « de leur soixante-cinquième anniversaire s'ils remplissent les conditions prévues [...] aux
  III ou IV de l'article 20 de la loi n° 2010-1330 » ; `cancava_avant_1973` et
  `organic_avant_1973` ne sont pas dans les `regimes` de la version.

Le reste de ce que le simulateur ne peut pas connaître est déclaré, à la fiche et à la
limite : le mois de naissance des enfants (une naissance présumée n'ouvre rien, une naissance
dite à l'année seulement quand les deux semestres la donnent), l'adoption, les périodes
européennes, les rachats et versements, la formation et la rééducation, les neuf ans
d'éducation de l'enfant qui n'est pas né de l'assuré : **conforme**. Rien d'autre n'est
supposé sans le dire.

## 7. Références mineures, sans effet sur le calcul

- `textes_a_rattacher` : le 6° de L. 351-8 « pour les pensions prenant effet à compter du
  1er janvier 2026 (loi n° 2025-199, article 87, VIII, C) » — l'article 87 n'a pas de VIII, C ;
  le 6° vient du II, 19°, que le VIII, A, applique aux pensions de 2026.
- Les avocats : R. 723-38 jusqu'au 8 juillet 2019, puis R. 653-2 (LEGIARTI000038770285), qui
  porte la même règle.
- La circulaire, point 2.3.2.1 : le fragment cité s'arrête à « les accidents du travail »
  sans marque de coupure ; le texte poursuit « /maladies professionnelles pour incapacité
  temporaire ou permanente au moins égale à 66 % ». La saisie n'a pas de motif de maladie
  professionnelle : sans effet.

## Ce qui reste, pour le propriétaire

- Rectifier la fiche (son approximation sur l'Agirc-Arrco, `a_relire`) et le test qui
  affirme 66 ans et 2 mois à l'Arrco, puis servir les complémentaires sans coefficient à ces
  parents : session du modèle, sur Opus.
- Déclarer à la fiche et à la limite, ou servir, les fonctionnaires, la CAVIMAC et les points
  d'avant 1973.
- Reprendre les trois références du point 7.
