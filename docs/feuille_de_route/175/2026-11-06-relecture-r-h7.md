# Relecture de l'AVPF du père, ouverte au 1er janvier 1985 (H7)

File R-H7 de la onzième vague, le 6 novembre 2026, sur Opus : relecture indépendante du
commit c68ba87 (session H7, note `2026-11-06-h7-avpf-du-pere.md`). Je n'ai rien repris de
H7 ni de ma mémoire. L'index de la DILA a été récupéré dans la session : LEGI à jour au
2 novembre 2026 (20261102-213929), JORF au 3 novembre (20261103-002311), puis effacé. La base
de législation de la Cnav a été relue ce jour par son API : l'exposé « Parent au foyer -
AVPF » (`/expose`, modifié le 24 octobre 2025), le barème AVPF (modifié le 24 février 2026),
la lettre ministérielle du 13 février 1979, les circulaires 25/79 et 43/80, le décret
n° 73-88 d'origine, les lois n° 72-8 et n° 77-765, les dix-sept circulaires Cnav de 1985 que
le registre connaît. Les deux moteurs ont été essayés par `servi_et_refait` et par le
portage seul ; les tests, sous les deux jeux ; les deux tests de H7, sur l'arbre du commit
parent. Je n'ai rien modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict : la règle est juste, à la bonne année et à la bonne condition, dans les deux
moteurs ; ses chiffres se refont à la main au millionième ; aucun écart grave.** Deux écarts
moyens, tous deux de preuve et sans effet sur une valeur servie : la lettre ministérielle du
13 février 1979, que H7 dit introuvable, est servie par l'API de la Cnav ; l'article 1er
d'origine du décret n° 73-88, que H7 dit lisible au seul fac-similé, aussi. Six écarts
faibles. Ils sont au § 7.

## 1. La règle : quel texte ouvre l'AVPF au père, et quand

**Juillet 1979, le seul père qui a un handicapé à charge, par une lettre et non par un
texte.** Lettre ministérielle du 13 février 1979 (base de la Cnav, `LE_MIN_13021979.aspx`,
Bureau des prestations familiales, signée Pierre Schopflin) : « Aux termes de cet article, la
possibilité d'un telle affiliation est réservée aux femmes et mères de famille. Toutefois dans
des cas extrêmement rares, des hommes assument la charge d'une épouse ou d'un enfant
handicapé. » ; « Dans ces conditions et dans l'attente d'une modification législative sur ce
point, je souhaite que les Caisses d'Allocations Familiales procèdent à l'affiliation et
prennent en charge les cotisations de ces personnes à partir du 1er juillet 1979. Une telle
mesure ne serait pas rétroactive. » ; « l'assurance vieillesse obligatoire ne peut bénéficier
à plus d'une personne par foyer au titre du troisième alinéa de l'article L 242-2 ». La
circulaire Cnav 25/79 du 6 mars 1979 (`CR_CN_2579_06031979.aspx`) la diffuse ; ses trois
phrases que H7 cite sont exactes, à la typographie de « 1 er » et « 3 ème » près, qui est
celle de la base.

**Le père comme la mère : le 1er janvier 1985 selon la caisse.** Exposé « Parent au foyer -
AVPF », partie « Avant le 01/09/2023 - Bénéficiaires », mot pour mot : « Les bénéficiaires
de certaines prestations familiales étaient affiliés obligatoirement à l'AVPF depuis le :
01/07/1972 pour les femmes ; 01/07/1979 pour les hommes. Du 01/07/1979 au 31/12/1984, les
hommes étaient affiliés uniquement s'ils assumaient la charge d'un enfant ou d'un adulte
handicapé. Depuis le 01/01/1985, la condition d'affiliation était identique à celle des
femmes. » Les textes, dans l'index :

- **Décret n° 73-88, article 1er**, ses trois rédactions de LEGI (`--num 1 --titre 73-88`),
  ouvertes en entier : LEGIARTI000006761985 (1er janvier 1978 → 1er janvier 1980, « Les
  mères de famille et les femmes bénéficiaires du complément familial ») ;
  LEGIARTI000006761986 (5 janvier → 4 août 1985, « les femmes isolées », « les mères de
  famille ») ; LEGIARTI000006761987 (4 août → 21 décembre 1985, « les personnes isolées »,
  « celui des conjoints ou concubins »). Conforme à la note de H7.
- **Décret n° 85-830 du 2 août 1985** (JO du 4 août, JORFTEXT000000501925) : sa notice,
  « REMPLACE LES ART. 1 (I,II),2 (AL. 2) ET ABROGE L'ART. 1 (III) DU DECRET 7388 » ; dans
  LEGI, son seul article de l'assurance vieillesse, LEGIARTI000006768734, que LEGI numérote
  1er, transitoire : « la personne isolée et, pour un couple, l'un ou l'autre de ses
  membres », pour un enfant « conçu avant le 1er janvier 1985 ». C'est le premier texte de
  l'index qui nomme le père de droit commun.
- **Loi n° 85-17 du 4 janvier 1985** (JO du 5 janvier) : la notice (« ALLOCATION AU JEUNE
  ENFANT (AJE). ALLOCATION PARENTALE D'EDUCATION (APE). ») et les quatre articles de LEGI,
  7, 9, 19 et 20, ouverts : rien sur la vieillesse. Conforme. Les dix-sept circulaires Cnav
  de 1985 du registre, relues par leur objet : aucune ne traite de l'AVPF.
- **L. 381-1**, rédaction du 21 décembre 1985 (LEGIARTI000006742941) : « La personne isolée
  et, pour un couple, l'un ou l'autre de ses membres [...] est affilié obligatoirement ».

**Le modèle.** `ANNEE_AVPF_DES_HOMMES = 1985` (`donnees/macro.py`, `moteur/js/macro.js`) ;
`_ligne_annuelle` et `ligneAnnuelle` ne portent rien au compte quand `sexe == "H"` et
`annee < 1985`. La borne est à la bonne année (celle de la caisse, que le scénario 1 suit),
et la condition est la bonne : le sexe de la personne et l'année de la ligne, c'est-à-dire
celle dont l'assiette est portée au compte. Le sexe arrive aux trois chemins qui bâtissent
une ligne d'éducation : la fermeture de `Carriere` (relevé et prolongation), le relevé
(`_lignes_du_releve`, `lignesDuReleve`), le parcours (`_lignes_du_parcours`,
`lignesDuParcours`) ; les appels qui ne le reçoivent pas (carriere.py, lignes 2834 et 2909 ;
carriere.js, lignes 2418 et 2688) ne bâtissent que des lignes `emploi`, sans AVPF. Les deux
moteurs disent la même chose.

**Les tests tiennent la règle.** Sur l'arbre du commit parent e0ce789, extrait hors du dépôt,
avec les deux tests de c68ba87 : le test Python échoue sur la seule ligne du père
(« 0 | 3037.699116 | 0 ± 1.0e-06 », trois années sur cinq), et le test JavaScript sur
« 1978 : 3037.699116 contre 0 ». Sur c68ba87, les deux passent, sous les deux jeux
(`PRESOMPTIONS_DECALEES=1` compris) ; huit fichiers de la zone (`test_salaire_annuel_moyen`,
`test_avantages`, `test_scenarios_meres`, `test_natures_assimilees`, `test_regle_de_chacun`,
`test_liquidation`, `test_moteur`, `test_pont`) : 232 passés, et 186 passés, 46 sautés, sous
le jeu décalé ; `moteur.test.js` : 50 sur 50 sous les deux.

**Les deux moteurs, au chemin de la saisie.** `servi_et_refait` (le portage, le Python le
refait au bit près), un salarié né en 1955, à 0,3 salaire moyen, de 22 à 62 ans, sans
enfant déclaré : au foyer de 1980 à 1984, le père a 5 462,27 € par an et la mère 5 657,23 € ;
de 1985 à 1989, tous deux 5 883,11 € ; sans activité de 1980 à 1984, tous deux 4 044,91 €.
Seule l'AVPF d'avant 1985 sépare le père de la mère.

**Le témoin** `interruption_pere_avant_1985` vient du code, comme tout témoin : il fixe ce
que le portage rend, il ne prouve pas la règle ; la preuve est le test, dont les valeurs sont
calculées sur le barème de la caisse (§ 2). Le seul autre cas d'éducation de
`simulations.json`, `interruption_simple` (un homme né en 1975, au foyer de 2000 à 2004), est
hors de la règle.
Que nul autre témoin ne bouge, c'est la course de GitHub sur c68ba87 qui le dit.

## 2. Les chiffres du cas posé, refaits à la main

L'assiette est celle du barème « Assurance vieillesse des parents au foyer (AVPF) » de la
Cnav (`cotisation_salaire_avpf_bar.aspx`), tableau « Avant 1997 », colonne « Métropole »,
au 1er janvier de chaque année, convertie à 6,55957 F pour un euro ; `assiette_avpf.csv`
n'a qu'une ligne pour chacune des cinq années.

| Année | Barème | ÷ 6,55957 | × 12 | Père (H7) |
|---|---|---|---|---|
| 1978 | 1 660,50 F | 253,141593 € | 3 037,699116 € | 0 |
| 1979 | 1 880,63 F | 286,700195 € | 3 440,402340 € | 0 |
| 1984 | 3 699,41 F | 563,971419 € | 6 767,657028 € | 0 |
| 1985 | 4 028,96 F | 614,210992 € | 7 370,531904 € | 7 370,531904 € |
| 1990 | 5 054,79 F | 770,597768 € | 9 247,173216 € | 9 247,173216 € |

Conforme : la mère a les cinq valeurs, le père les deux dernières, dans les deux moteurs.

## 3. « La loi de 1979 n'existe pas », et les cinq versions de la fiche

**Vrai, et mieux prouvé que H7 ne le dit.** La lettre elle-même agit « dans l'attente d'une
modification législative sur ce point ». Dans l'index JORF, de 1972 à 1986, les notices qui
nomment L. 242-2 (« L242 ») sont celles de la loi n° 77-765, du décret n° 78-269 et de la
circulaire du 29 avril 1980, qui nomme encore les seules « MERES DE FAMILLE », « FEMMES ».
Aucune autre loi ne la complète avant la loi n° 85-17, dont le texte manque.

**Les versions.** `lit` (la période d'éducation, le sexe) et `ecrit` (`revenu_avpf`) disent ce
que fait le code. Les citations, contrôlées mot pour mot sur l'index et l'API : la notice de
la loi n° 72-8, LEGIARTI000006761985, LEGIARTI000006760068, les trois de la circulaire 25/79,
l'exposé (deux fois), LEGIARTI000006761986, LEGIARTI000006761987, LEGIARTI000006768734,
LEGIARTI000006742941 : exactes. Les dates `en_vigueur` sont celles de LEGI. Les bornes
(1972-07-01, 1978-01-01, 1979-07-01, 1985-01-01) sont celles des textes et de la caisse.
Écarts : la version de 1972 dite `supposee` (§ 7, écart 2), la date qui décide (écart 3), un
texte de 1985 cité pour 1979 à 1984 (écart 4), un montant inversé (écart 5), la numérotation
de l'article de 85-830 (écart 7).

## 4. Les deux points non tranchés

**Janvier à août 1985 : non tranché à bon droit.** La caisse dit le 1er janvier ; la
rédaction du décret n° 73-88 en vigueur du 5 janvier au 4 août 1985 ne nomme que des femmes ;
la loi n° 85-17, qui seule peut décider, ne se lit pas dans l'index. Aucune des deux lectures
n'est intenable ; le modèle suit la caisse, comme le scénario 1 le veut. Le chiffrage est
juste : 7 × 614,210992 = 4 299,476944 € ; 5 × 614,210992 = 3 071,054960 € ; 7 370,531904 −
3 071,054960 = 4 299,476944 €. Une précision : c'est le cas d'un père d'un enfant né avant
1985, au complément familial transitoire, affilié du mois d'août. Pour l'allocation au jeune
enfant, l'article 2 du décret n° 73-88 dans sa rédaction du 4 août 1985
(LEGIARTI000006761989) fait courir l'immatriculation « avec effet rétroactif à compter du
premier jour du mois civil suivant celui de la naissance » : sous la lecture du décret, la
perte d'un tel père serait moindre. 4 299,48 € est un plafond, non un cas général (écart 6).

**Le handicap, de juillet 1979 à 1984 : écart déclaré à bon droit.** Le droit est clair, la
saisie seule ne le dit pas. 6 × 286,700195 = 1 720,201170 € ; 321,050008 + 369,935834 +
441,807923 + 506,002680 + 563,971419 = 2 202,767864 € ; × 12 = 26 433,214368 € ; total
28 153,415538 €. Conforme. C'est un plafond aussi : la lettre ne vise que « la charge d'une
épouse ou d'un enfant handicapé », sous le plafond de ressources du complément familial, et
une seule personne par foyer.

## 5. Le candidat 67 : une année d'éducation sans AVPF valide quatre trimestres

**Réel, bien décrit, bien chiffré.** La ligne `education_enfant` de
`periodes_non_travaillees.csv` : `education_enfant,4,non,non,oui,plafonne,3,avpf,haute`, soit
quatre trimestres assimilés à toute année, AVPF ou non. Au portage
(`carriereSimple`, né le 1er janvier 1955, salarié du privé non cadre, salaire moyen, profil
plat, de 22 à 62 ans), refait ce jour : au foyer de 1980 à 1984, 160 trimestres et
18 194,730134 € ; sans activité, 140 trimestres et 13 472,376867 €, les valeurs de H7 au
centime ; chacune des cinq années porte 0 € d'AVPF et 4 trimestres. Au chemin de la saisie
(`servi_et_refait`, mêmes bornes), 160 et 140 trimestres, 18 207,58 € et 13 483,04 €, les
deux moteurs d'accord. Au droit, L. 351-3, rédaction du 21 décembre 1985
(LEGIARTI000006742919), énumère six sortes de périodes « prises en considération en vue de
l'ouverture du droit à pension » — maladie, chômage, service national, guerre, détention
provisoire — et pas l'éducation d'un enfant : sans AVPF, une telle année ne valide rien au
régime général. La même ligne sert la fonction publique (`services_fonction_publique`,
`plafonne`, trois ans par enfant) : la retoucher touche aussi les services, ce que H7 dit.

## 6. Les fac-similés, le bloc « Reprise », le README et la carte

| Ligne proposée | Un JO imprimé est-il nécessaire ? |
|---|---|
| loi n° 72-8 | Non pour la règle : le décret d'origine (ci-dessous) dit qui est affilié. Ni LEGI ni la Cnav (« Voir loi ») n'en donnent le texte : le fac-similé ne servirait qu'à citer L. 242-2. |
| décret n° 73-88, article 1er d'origine | Non : la base de la Cnav le sert (`DEC_7388_26011973.aspx`). Le JO ne ferait que certifier la transcription. |
| décret n° 80-1068 | Pas pour la règle (l'exposé et la rédaction de 1985 suffisent) ; seul texte de 1980 à 1984, absent de LEGI et de la base (l'API répond 500). |
| loi n° 85-17 | Oui : seule à pouvoir trancher janvier à août 1985 ; LEGI n'en a que quatre articles, la base rien. |

Le bloc « Reprise » de l'étape 4 : récrit à bon droit, H7 étant une file de l'étape ; daté du
jour, dix lignes. `README.md` et `docs/carte_du_depot.md` : seuls des chiffres ancrés
bougent, que le témoin de plus déplace (931 → 932 simulations, que je recompte dans
`simulations.json` ; 174 905 → 175 111 nombres ; 924 → 925 Ko) ;
`python scripts/verifier_prose.py` : « la prose déclarée dit le vrai ». Conforme.

## 7. Les écarts

1. **Moyen, de preuve.** La fiche (`a_relire`) dit la lettre ministérielle du 13 février 1979
   « jointe à la circulaire 25/79, que l'API ne sert pas ». L'API la sert
   (`/reference/referencesByFileLeafRef/LE_MIN_13021979.aspx`, au registre `a_lire`). Elle
   est la source même de l'affiliation de 1979 et prouve qu'aucune loi ne l'a faite ; la
   version `hommes_ayant_la_charge_d_un_handicape` doit la citer (§ 1). Aucune valeur ne
   change.
2. **Moyen, de preuve.** La version `meres_de_juillet_1972` est `supposee` parce que
   l'article 1er d'origine du décret n° 73-88 « ne se lit qu'au fac-similé ». La base de la
   Cnav le sert (`DEC_7388_26011973.aspx`) : « Les mères de famille et les femmes
   bénéficiaires de la majoration de l'allocation de salaire unique ou de la majoration de
   l'allocation de la mère au foyer instituée par la loi n° 72-8 du 3 janvier 1972 sont
   affiliées obligatoirement à l'assurance vieillesse du régime général de la sécurité
   sociale », et l'article 5 : « prendra effet à compter du 1 er juillet 1972 ». La version
   peut passer `lue`, sur la transcription de la caisse. Ce que H7 supposait est confirmé.
3. **Faible, de déclaration.** `dates_qui_decident: [periode.debut]`, et « Les versions
   forment un partage du début de la période d'éducation ». Le code décide, à bon droit, par
   l'année de chaque ligne : sous la fiche, un père au foyer de 1983 à 1987 relèverait en
   entier de `hommes: false`, quand le code lui sert 1985 à 1987, ce que l'exposé veut
   (« Depuis le 01/01/1985 »). La date qui décide est celle de l'année portée au compte
   (`revenu.annee`, au vocabulaire), non le début de la période.
4. **Faible, de date.** La version `hommes_ayant_la_charge_d_un_handicape` (1979-07-01 →
   1985-01-01) cite LEGIARTI000006761986, en vigueur du 5 janvier 1985 : hors de ses bornes.
   Dans la période valent la rédaction de 1978 (LEGIARTI000006761985, jusqu'au 1er janvier
   1980), puis celle du décret n° 80-1068, que l'index n'a pas ; la citation de 1985 se dit
   postérieure.
5. **Faible, de rédaction.** Approximation de la version `l_un_ou_l_autre_parent` : « 4 299,48
   € portés au compte en moins (7 370,53 € au lieu de 3 071,05 €) » ; sous la lecture du
   décret, c'est 3 071,05 € au lieu de 7 370,53 €, comme la note de H7 l'écrit.
6. **Faible, de chiffrage.** 4 299,48 € vaut pour le père d'un enfant né avant 1985 ; pour
   l'allocation au jeune enfant, l'immatriculation rétroagit au mois qui suit la naissance
   (§ 4). À dire dans l'approximation.
7. **Faible, de citation.** La note de H7 cite L. 381-1 : « La personne isolée et, pour un
   couple, l'un ou l'autre de ses membres », « au premier alinéa comme à celui du handicap » ;
   le second dit « la personne et, pour un couple, l'un ou l'autre de ses membres », sans
   « isolée ». Et l'article de 85-830 que LEGI numérote 1er renvoie aux « articles 1er et 2
   du présent décret » : il n'est pas l'article 1er du JO ; à citer comme « l'article que LEGI
   numérote 1er ».
8. **Faible, de lecture.** Deux textes modificatifs ne sont pas nommés : le décret n° 82-1140
   du 29 décembre 1982 (JORFTEXT000000884294 ; articles 3 du décret n° 73-88 et 4 du décret
   n° 78-269 : la cotisation, non l'affilié) et le décret n° 79-535 du 3 juillet 1979
   (JORFTEXT000000516653, outre-mer, « DES MERES DE FAMILLE ET DES FEMMES » ayant un
   handicapé à charge). Aucun ne nomme le père : la conclusion de H7 tient.

Les notes sont des récits : l'écart 7, qui touche la note de H7, se corrige dans la fiche et
se dit dans la note du « -bis », non dans la sienne. Aucun candidat neuf.
