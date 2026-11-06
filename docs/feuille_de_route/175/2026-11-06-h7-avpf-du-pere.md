# L'AVPF du père : ouverte au 1er janvier 1985 dans les deux moteurs (H7)

**Le 6 novembre 2026** (session H7, onzième vague, sur Opus). La note du thème
« Carrière : cotisations-salaires » (`2026-11-03-etape-4-cotisations-salaires.md`,
lignes 31 à 35) avait relevé que le modèle sert l'assurance vieillesse des parents au
foyer à toute période d'éducation déclarée depuis juillet 1972, au père comme à la mère,
quand la caisse n'affilie le père que depuis 1979, et pleinement depuis 1985. Cette
session lit tout ce qui se lit de 1972 à la codification, corrige ce que les textes
prouvent, et déclare le reste.

## Ce qui a été lu

Index LEGI à jour au 2 novembre 2026 (20261102-213929) et JORF au 3 novembre
(20261103-002311), récupérés pour la session puis effacés. La base de législation de la
Cnav, par son API, le 6 novembre 2026.

- **Décret n° 73-88 du 26 janvier 1973**, tous ses articles dans LEGI
  (LEGITEXT000006062138) : l'article 1er n'y a que trois rédactions, du 1er janvier 1978
  au 1er janvier 1980 (LEGIARTI000006761985, « Les mères de famille et les femmes
  bénéficiaires du complément familial »), du 5 janvier au 4 août 1985
  (LEGIARTI000006761986, « les femmes isolées », « les mères de famille »), du 4 août au
  21 décembre 1985 (LEGIARTI000006761987, « les personnes isolées », « celui des
  conjoints ou concubins »). Ni la rédaction d'origine (1973 à 1977) ni celle du décret
  n° 80-1068 (1980 à 1984) ne sont dans l'index.
- **Décret n° 76-153 du 13 février 1976** (LEGIARTI000006760501 à 006760505) : l'AVPF
  des « mères » d'un enfant handicapé ; **décret n° 78-269 du 8 mars 1978**
  (LEGIARTI000006760068 à 006760074) : « les mères et les femmes » ayant la charge d'un
  handicapé, sans rédaction qui nomme les hommes jusqu'à la codification.
- **Décret n° 85-830 du 2 août 1985**, article 1er (LEGIARTI000006768734), transitoire :
  « la personne isolée et, pour un couple, l'un ou l'autre de ses membres ».
- **L. 381-1**, rédaction du 21 décembre 1985 (LEGIARTI000006742941) : « La personne
  isolée et, pour un couple, l'un ou l'autre de ses membres », au premier alinéa comme à
  celui du handicap.
- **Les lois**, dans les deux index. Loi n° 72-8 : notice seule (JORFTEXT000000509305).
  Loi n° 77-765 : notice, qui dit qu'elle « MODIFIE » L. 242-2. Loi n° 79-1129 du 28
  décembre 1979 : ses articles que LEGI garde (3, 5, 11, 13 à 15, 17 à 19, 22, 26, 27, 30
  à 32), dont aucun ne touche L. 242-2 ni l'AVPF ; les autres, incorporés au code, ne se
  lisent qu'au fac-similé. Loi n° 85-17 du 4 janvier 1985 : notice, et ses articles 7, 9,
  19 et 20, les seuls de LEGI, sans rien sur la vieillesse. Aucune notice du JORF de 1971
  à 1986 ne nomme une loi qui « complète » L. 242-2 pour les hommes ; la circulaire du
  29 avril 1980 (JORFTEXT000000326008) nomme encore, à L. 242-2, « MERES DE FAMILLE,
  FEMMES BENEFICIAIRES DU COMPLEMENT FAMILIAL, FEMMES ISOLEES ET FEMMES N'EXERCANT PAS
  D'ACTIVITE PROFESSIONNELLE ».
- **La caisse.** L'exposé « Parent au foyer - AVPF » (version du 24 octobre 2025) : les
  bénéficiaires de prestations familiales sont affiliés « depuis le : 01/07/1972 pour les
  femmes ; 01/07/1979 pour les hommes. Du 01/07/1979 au 31/12/1984, les hommes étaient
  affiliés uniquement s'ils assumaient la charge d'un enfant ou d'un adulte handicapé.
  Depuis le 01/01/1985, la condition d'affiliation était identique à celle des
  femmes. » La circulaire Cnav 25/79 du 6 mars 1979 : « A compter du 1er juillet 1979 les
  Caisses d'Allocation Familiales sont autorisées à procéder à l'affiliation [...] des
  hommes assumant la charge d'une épouse ou d'un enfant handicapé », sur une lettre
  ministérielle du 13 février 1979, « L'article L. 242.2 précité sera ultérieurement
  complété sur ce point. » La circulaire 2011/38, que l'exposé cite aussi, ne dit rien du
  père.

**Ce que « la loi de 1979 » était.** Il n'y en a pas : l'extension de juillet 1979 tient
à une lettre ministérielle, que la circulaire 25/79 applique, et la loi qui devait
compléter L. 242-2 n'est nommée par aucune notice de l'index JORF.

## Ce qui est corrigé

Le père (sexe « H ») n'a l'AVPF que pour les années d'éducation depuis 1985
(`ANNEE_AVPF_DES_HOMMES`, `moteur/js/macro.js` et `donnees/macro.py`) ; la ligne
annuelle apprend le sexe de la personne (`ligneAnnuelle`, `_ligne_annuelle`, et les trois
chemins qui bâtissent une ligne d'éducation : le parcours, le relevé, la prolongation).
La mère garde l'AVPF depuis juillet 1972. Avant juillet 1979, la caisse n'affilie aucun
homme ; de juillet 1979 à 1984, seulement celui qui a un handicapé à charge, ce que la
saisie ne dit pas : le modèle ne lui sert rien, et l'écart est déclaré.

**Le cas posé** (`test_l_avpf_du_pere_ne_court_que_depuis_1985` et son portage) : né en
1950, au foyer en 1978, 1979, 1984, 1985 et 1990, années entières. Le salaire porté au
compte est douze fois l'assiette mensuelle de la Cnav (`assiette_avpf.csv`, une seule
valeur pour chacune de ces années) :

| Année | Assiette mensuelle | Mère | Père |
|---|---|---|---|
| 1978 | 253,141593 € | 12 × 253,141593 = 3 037,699116 € | 0 (avant juillet 1979) |
| 1979 | 286,700195 € | 12 × 286,700195 = 3 440,40234 € | 0 (handicap non saisi) |
| 1984 | 563,971419 € | 12 × 563,971419 = 6 767,657028 € | 0 (handicap non saisi) |
| 1985 | 614,210992 € | 12 × 614,210992 = 7 370,531904 € | 7 370,531904 € |
| 1990 | 770,597768 € | 12 × 770,597768 = 9 247,173216 € | 9 247,173216 € |

Le modèle portait au père les valeurs de la mère, toutes années. Un témoin de plus
(`interruption_pere_avant_1985` : un homme né en 1955, au foyer de 1980 à 1986, à 0,3
salaire moyen) fixe ce que rend le portage ; aucun autre témoin ne bouge. Les deux moteurs
rendent la même valeur au cas posé.

## Ce qui n'est pas tranché

**Du 1er janvier au 3 août 1985.** La caisse affilie le père « Depuis le 01/01/1985 » ;
le décret n° 73-88, en vigueur du 5 janvier au 4 août 1985, ne nomme que « les femmes
isolées » et « les mères de famille ». La loi n° 85-17, qui a pu changer L. 242-2 dès
janvier, ne se lit qu'au fac-similé. Le modèle suit la caisse. Sous la lecture du
décret, avec une affiliation au 1er août, le père d'une année 1985 entière aurait
5 × 614,210992 = 3 071,05496 € au compte au lieu de 7 370,531904 €, soit
7 × 614,210992 = 4 299,476944 € de moins.

**Le handicap, de juillet 1979 à 1984.** Le père qui l'avait à charge était affilié. Sur
toute la période, le modèle lui porte en moins : 6 × 286,700195 + 12 × (321,050008 +
369,935834 + 441,807923 + 506,002680 + 563,971419) = 1 720,20117 + 12 × 2 202,767864 =
1 720,20117 + 26 433,214368 = 28 153,415538 €.

**La période de 1972 à 1977.** La version de la fiche est `supposee` : la caisse dit
« 01/07/1972 pour les femmes », et l'article 1er d'origine du décret n° 73-88 ne se lit
qu'au fac-similé. La lecture contraire, un père affilié avant 1979, contredit l'exposé et
la circulaire 25/79, qui étend en 1979 aux hommes ce qui était « non seulement [aux]
mères de famille et [aux] femmes ».

Lignes à ajouter à la file des fac-similés
(`docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md`), proposées à la
session qui la tient :

| JO | Texte | Identifiant | Pour |
|---|---|---|---|
| 5 janvier 1972 | loi n° 72-8, L. 242-2 de l'ancien code | JORFTEXT000000509305 | 175, AVPF du père |
| 28 janvier 1973 | décret n° 73-88, article 1er d'origine | JORFTEXT000000693989 | 175, AVPF du père |
| 26 décembre 1980 | décret n° 80-1068, article 1er du décret n° 73-88 | JORFTEXT000000501301 | 175, AVPF du père |
| 5 janvier 1985 | loi n° 85-17, ce qu'elle fait de L. 242-2 | JORFTEXT000000521299 | 175, AVPF du père |

## Candidats

1. **Une année d'éducation valide quatre trimestres sans AVPF.** La colonne
   `trimestres_assimiles` de `education_enfant` (`periodes_non_travaillees.csv`) donne
   quatre trimestres à toute année d'éducation, que l'AVPF la couvre ou non : la mère avant
   juillet 1972, et, après cette correction, le père avant 1985. Mesuré au portage : un
   père né en 1955, salarié du privé au salaire moyen de 22 à 62 ans, au foyer de 1980 à
   1984, a 160 trimestres et 18 194,73 € de pension annuelle ; si ces cinq années ne
   validaient rien (motif `sans_activite`), 140 trimestres et 13 472,38 €. La même ligne
   sert les services de la fonction publique (colonne `services_fonction_publique`,
   « plafonne ») : la correction, la classe entière, attend la lecture de leurs règles.
   Écart de loin le plus lourd : à la session du modèle suivante, avant tout autre.
   L'année 1972 de la mère n'en est pas : ses six mois d'assiette, 6 × 101,732278 € =
   610,393668 €, soit 4 004 F, valent plus de quatre fois les 788 F d'un trimestre de
   1972 (200 heures du SMIC de janvier, 3,94 F), et l'année valide bien quatre
   trimestres.

Aucun site ni aucune saisie ne change : le modèle sait déjà le sexe (`sexe`, « H » ou
« F », au formulaire et dans la chronologie).
