# Les notes de msa_non_salaries : ce que « aucune source » veut dire, et le 17,37 % après 2025 lu au décret n° 2025-1417 et à L. 731-42

Vague 11, le 6 novembre 2026 (file K-notes). Ce que la note de K-ter
(`2026-11-05-retouches-de-la-relecture-r-k-ter.md`, § 1 et « Signalé, non fait ») a signalé
sans le faire. Changent : les notes de six périodes de `data/reference/regimes/msa_non_salaries.yaml`
(2003, 2004 à 2008, 2009 à 2010, 2011 à 2025, 2026 à 2027, 2028 sans fin) ; la fiche
`cotisation_vieillesse_agricole_avant_2003` (l'`effet` de l'approximation `depuis_2003`, une
lecture, l'historique) ; `moteur/donnees.json`, aux six notes seules. Aucun taux, aucune valeur,
aucun test, aucune règle. Vérifié : le régime relu en YAML, notes ôtées, est identique à celui de
`HEAD` ; le paquet ne diffère qu'en `regimes[52]/periodes[5..10]/notes`.

**Pièces ouvertes** : l'index LEGI du dépôt (dump du 13 juillet 2025, incréments jusqu'au
`LEGI_20261105-214938`) et l'index JORF (jusqu'au `JORF_20261106-002608`), récupérés et mis à jour
dans la session ; `data/sources.yaml` (msa_parametres) ; `data/reference/macro/plafond_securite_sociale.csv`
et `smic_horaire.csv` ; `data/reference/regimes/taux_cotisation_annuels.csv` ; le code du compte
(`moteur/js/compte.js`, `src/retraite_notionnelle/moteur/compte.py`) et de l'acquisition
(`moteur/js/droit/acquerir.js`).

## 1. Le droit de 2026, lu

**Le décret n° 2025-1417 du 30 décembre 2025** « relatif aux taux et à l'assiette de la cotisation
d'assurance vieillesse de base des non-salariés agricoles et portant diverses dispositions en
matière d'affiliation » (JORF du 31 décembre 2025, JORFTEXT000053228345). Sa notice : « Objet : le
texte modifie les dispositions relatives aux taux et à l'assiette des cotisations d'assurance
vieillesse de base des non-salariés agricoles afin notamment d'aligner le taux de cette cotisation
vieillesse sur celui des travailleurs indépendants non agricoles. Il définit également des
dispositions transitoires pour certaines catégories de non-salariés agricoles pour les périodes
comprises entre le 1 er janvier 2026 et le 31 décembre 2028. » Il est « pris pour application des
articles 3 et 87 de la loi n° 2025-199 du 28 février 2025 ».

- **Article 4** (JORFARTI000053228364), 2° : « L'article D. 731-120 est ainsi rédigé : « Art.
  731-120.-La cotisation d'assurance vieillesse prévue au 1° de l'article L. 731-42 est assise sur
  une assiette au moins égale à 600 fois le montant horaire du salaire minimum de croissance en
  vigueur le 1 er janvier de l'année considérée » » ; 3° : « L'article D. 731-121 est ainsi rédigé :
  « Art. D. 731-121.-Les taux applicables à la cotisation prévue au 1° de l'article L. 731-42 sont
  égaux à ceux fixés respectivement au I de l'article D. 633-3 du code de la sécurité sociale pour
  la part calculée sur l'assiette retenue dans la limite du plafond mentionné au premier alinéa de
  l'article L. 241-3 du même code et au II du même article pour la part calculée sur la totalité de
  l'assiette. » » ; 4° : D. 731-123, « L'assiette forfaitaire de la cotisation prévue au 2° de
  l'article L. 731-42 est égale à l'assiette minimale prévue à l'article D. 731-120. « Le taux
  applicable à cette cotisation est égal à la somme des taux mentionnés à l'article D. 731-121. » » ;
  5°, c : « 2° La cotisation prévue au 2° de l'article L. 731-42 due pour leurs aides familiaux
  majeurs et due pour leur conjoint collaborateur. » ; 8° : « Les articles D. 731-79, D. 731-122 et
  D. 731-124 sont abrogés. »
- **Article 5** (JORFARTI000053228374), mot pour mot : « I. - Les articles 2 à 4 du présent décret
  entrent en vigueur le 1 er janvier 2026 et s'appliquent aux cotisations dues au titre des
  périodes courant à compter de cette date. II. - Par dérogation aux articles D. 731-121 et
  D.731-123 du code rural et de la pêche maritime, le taux de la part des cotisations prévues aux
  1° et 2° de l'article L. 731-42 du même code calculée sur l'assiette retenue dans la limite du
  plafond mentionné au premier alinéa de l'article L. 241-3 du code de la sécurité sociale, pour
  les périodes courant du 1 er janvier 2026 au 31 décembre 2028, est fixé dans les conditions
  suivantes : 1° pour les personnes mentionnées au 1° de l'article L. 731-42 du même code exerçant
  leur activité à titre secondaire et pour les personnes mentionnées au 2° du même article exerçant
  à titre principal ou exclusif : Année au titre de laquelle la cotisation est due Taux de la part
  de la cotisation assise sur l'assiette dans la limite du plafond annuel de la sécurité sociale
  2026 14,15 % 2027 15,15 % 2028 16,15 % 2° pour les personnes mentionnées au 2° de l'article
  L. 731-42 du même code exerçant leur activité à titre secondaire : Année au titre de laquelle la
  cotisation est due Taux de la part de la cotisation assise sur l'assiette dans la limite du
  plafond annuel de la sécurité sociale 2026 12,33 % 2027 13,83 % 2028 16,15 % »

**L. 731-42 en 2026** (LEGIARTI000051284150, en vigueur depuis le 28 février 2025, la seule
rédaction depuis à l'index) : « Les cotisations dues pour la couverture des dépenses de prestations
de l'assurance vieillesse et de l'assurance veuvage sont à la charge du chef d'exploitation ou
d'entreprise. Elles comprennent : 1° Pour chaque chef d'exploitation ou d'entreprise, une
cotisation calculée pour partie sur l'assiette déterminée en application des articles L. 731-15,
L. 731-16 et L. 731-22, retenue dans la limite du plafond mentionné au premier alinéa de l'article
L. 241-3 du code de la sécurité sociale, et pour partie sur la totalité de cette assiette. Cette
cotisation ne peut être inférieure à un montant fixé par décret. Les taux applicables à chacune de
ces deux parties sont identiques à ceux déterminés en application de l'article L. 633-1 du même
code ; 2° Pour chaque personne mentionnée au 2° de l'article L. 722-10 du présent code, à partir de
l'âge de seize ans, et pour chaque collaborateur d'exploitation ou d'entreprise mentionné à
l'article L. 321-5, une cotisation calculée sur une assiette forfaitaire fixée par décret. Le taux
de cette cotisation est égal à la somme des taux de la cotisation mentionnée au 1° du présent
article. » C'est la loi n° 2025-199, article 3, I, 8° (JORFARTI000051269492) : « Les cinq derniers
alinéas de l'article L. 731-42 sont remplacés par des 1° et 2° ainsi rédigés » ; son III : « Les
4°, 5° et 8° à 12° du I s'appliquent aux cotisations dues au titre des périodes courant à compter
du 1er janvier 2026. [...] Par dérogation au second alinéa des 1° et 2° de l'article L. 731-42 du
code rural et de la pêche maritime, pour les périodes courant du 1er janvier 2026 au 31 décembre
2028, un décret fixe les taux des cotisations mentionnées au 1° du même article L. 731-42 dues par
les chefs d'exploitation et d'entreprise agricole exerçant à titre secondaire et de celles
mentionnées au 2° dudit article L. 731-42 de manière à résorber progressivement, chaque année, les
écarts entre, d'une part, la somme des taux des cotisations d'assurance vieillesse de base
applicables aux personnes concernées au 31 décembre 2025 et, d'autre part, les taux mentionnés au
second alinéa des 1° et 2° du même article L. 731-42. »

**« Le 1° » en 2026** est donc la cotisation unique du chef, en deux parts, plafonnée et sur la
totalité, qui remplace l'AVI du 1°, l'AVA plafonnée du 2° a et l'AVA déplafonnée du 3° des
rédactions d'avant (dont D. 731-122 et D. 731-124, abrogés par l'article 4, 8°, finissent à
l'index au 1er janvier 2026) ; « le 2° » est celle de l'aide familial et du collaborateur, sur un
forfait de 600 SMIC horaires.

**Les taux** : D. 731-121 depuis le 1er janvier 2026 (LEGIARTI000053296666) renvoie à D. 633-3,
en vigueur depuis le 7 juillet 2024 (LEGIARTI000049904636, seule rédaction depuis à l'index) :
« I.-Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est
fixé à 17,15 %. II.-Le taux des cotisations assises sur la totalité de l'assiette de cotisations est
fixé à 0,72 %. » L. 633-1 (LEGIARTI000037062182, depuis le 14 juin 2018) : « La somme des taux de
ces cotisations est égale à la somme des taux fixés en application des deuxième et quatrième
alinéas du même article L. 241-3. »

| Année | Chef à titre principal | Chef à titre secondaire ; 2° à titre principal | 2° à titre secondaire |
|---|---|---|---|
| 2026 | 17,15 % + 0,72 % | 14,15 % + 0,72 % | 12,33 % + 0,72 % |
| 2027 | 17,15 % + 0,72 % | 15,15 % + 0,72 % | 13,83 % + 0,72 % |
| 2028 | 17,15 % + 0,72 % | 16,15 % + 0,72 % | 16,15 % + 0,72 % |
| 2029 et après | 17,15 % + 0,72 % | 17,15 % + 0,72 % | 17,15 % + 0,72 % |

Le premier taux porte sur l'assiette sous le plafond, le second sur la totalité. **Aucun texte ne
fixe 17,37 %** : aucun de ces taux ni aucune de ces sommes (17,87, 14,87, 15,87, 16,87, 13,05,
14,55 %) ne l'est.

**Point non tranché** (le 2° pendant la dérogation) : l'article 5, II, ne déroge qu'à « la part
[...] calculée sur l'assiette retenue dans la limite du plafond » ; le 0,72 % de la part sur la
totalité s'ajoute-t-il, sur le forfait du 2°, au 14,15 % ? Lecture 1, oui (D. 731-123 somme les
taux de D. 731-121, dont la dérogation ne touche qu'un) : 14,87 % en 2026, soit 600 × 14,87 % =
89,22 SMIC horaires par an. Lecture 2, non : 600 × 14,15 % = 84,90 SMIC horaires. La période du
modèle porte 600 × 17,37 % = 104,22 SMIC horaires. Le texte ne le dit pas en toutes lettres ; la
question est sans effet sur les résultats (§ 2).

**Textes modificatifs, cherchés tous** (index JORF, sans borne de réponses) : « 2025-1417 » rend
le décret lui-même (sept documents) et le décret n° 2025-1410, article 1er, qui ne cite le décret
n° 2025-1417 que pour des rachats (« dans sa rédaction antérieure au décret n° 2025-1417 ») ;
« D. 731-121 » depuis 2025, les articles 4 et 5 du décret ; « L. 731-42 » depuis 2025, la loi
n° 2025-199 (articles 3 et 87), les décrets n° 2025-1409, 2025-1410 et 2025-1417, et le décret
n° 2026-889 du 24 septembre 2026, article 5, qui ne vise que l'assiette du prélèvement mensuel
de l'expérimentation de l'article 16 de la loi de financement pour 2026 ; « D. 633-3 » depuis
2024, les décrets n° 2024-484 et 2025-943 (taux globaux du micro-entrepreneur, qui citent l'article
sans le modifier), n° 2024-688 et n° 2025-1417. Dans l'index LEGI, aucune rédaction de L. 731-42,
D. 731-121 ou D. 633-3 postérieure à celles citées. « cotisation NEAR(vieillesse) NEAR(agricoles) »
depuis 2026 : la loi de finances pour 2026 (ses états, sans rapport), le décret n° 2026-418
(régimes complémentaires des libéraux) et l'ordonnance n° 2026-647 (extension outre-mer).

## 2. Ce que le modèle fait du 17,37 % depuis 2026 : mesuré

La donnée est fausse : le 17,37 % des périodes de 2026 à 2027 et de 2028 sans fin n'est le taux
d'aucune cotisation, de personne, en aucune année depuis 2026. La lecture contraire est intenable :
L. 731-42 rend les taux du chef « identiques » à ceux des travailleurs indépendants, et le modèle
porte lui-même, pour l'indépendant du régime général en 2026, 17,15 % et 0,72 %
(`taux_cotisation_annuels.csv`, `regime_general,2026,taux_plafonne_non_salarie,0.171500,certifiee`
et `taux_deplafonne_non_salarie,0.007200,certifiee`).

**Mais aucun résultat mesuré ne la lit.** La mesure : une copie de `data/` (sans `brut/`) dans le
dossier de travail de la session, où les deux périodes de 2026 et de 2028 portent 0,2737 au lieu de
0,1737 ; le simulateur Python (`Simulateur(Parametres(racine_donnees=…))`, `CALCULS_SANS_MEMOIRE=1`)
sur `carriere_simple(…, affiliation="exploitant_agricole", age_debut=25)`, né en 1966 et parti à
64 ans (2030), né en 1962 et parti à 64 ans et un trimestre (2026). Résultats identiques au
centime avec les deux données : 1966, pension du scénario 1 21 572,418327 €, pension MSA
18 648,135992 €, capital du scénario 2 382 933,341922 € (les cinq scénarios notionnels identiques) ;
1962, 20 433,462855 €, 18 134,684283 € et 319 674,054554 €. Le témoin que la copie est bien lue :
porté aussi aux périodes de 2003 à 2025, le capital du scénario 2 de 1966 passe à 512 975,234122 €.
La raison, lue au détail du compte du scénario 2 de 1966 (`compte.cotisations`) : de 2023 à 2025,
il reçoit `('msa_non_salaries', 'msa_rco')` (taux 0,2137, soit 17,37 + 4 %, en 2024 et 2025) ; de
2026 à 2030, `('regime_unifie',)`, à 0,2583. Au scénario 1, les points de 2026 et de 2027 viennent
du barème de R. 732-71 et la pension de 2028 du revenu : la mesure le confirme, le taux n'y entre
pas. Le coût n'est pas mesuré ici.

**Le cas posé, à la main** (ce que la période dit et ce que le texte prélève, en 2026, le PASS de
2026 étant de 48 060 €, `plafond_securite_sociale.csv`, certifiée, et 600 SMIC horaires de
600 × 12,02 = 7 212 €, `smic_horaire.csv`, haute) :

- chef à titre principal, 30 000 € de revenu (entre les deux bornes) : la période, 30 000 × 17,37 %
  = 5 211,00 € ; le texte, 30 000 × 17,15 % + 30 000 × 0,72 % = 5 145,00 + 216,00 = 5 361,00 € ;
  écart, − 150,00 € (− 2,80 %) ;
- le même à 60 000 € : la période, 48 060 × 17,37 % = 8 348,02 € ; le texte, 48 060 × 17,15 % +
  60 000 × 0,72 % = 8 242,29 + 432,00 = 8 674,29 € ; écart, − 326,27 € (− 3,76 %) ;
- chef à titre secondaire, 30 000 € : le texte, 30 000 × 14,15 % + 216,00 = 4 245,00 + 216,00 =
  4 461,00 € ; écart, + 750,00 € (+ 16,8 %).

Rien n'en passe au compte ni à la pension, puisque le compte reçoit depuis 2026 le taux du régime
unifié. **Erreur de la donnée, sans effet mesuré** (candidat) : non corrigée, le taux du compte des
exploitants attendant la réponse du propriétaire ; la question posée par K-ter ne porte, pour le
compte, que sur 2003 à 2025.

## 3. Ce qui est écrit

- **Les quatre périodes de 2003 à 2025** : « LE TAUX DE 17,37 % N'A AUCUNE SOURCE : aucun texte lu
  ne le fixe, et aucune somme des taux lus ne le donne. » devient « LE TAUX DE 17,37 % N'A AUCUNE
  SOURCE, au sens où l'entend la fiche cotisation_vieillesse_agricole_avant_2003 (approximation
  depuis_2003) : aucun texte, aucune page précise, sans texte qui le fixe ni note qui le justifie ;
  le régime ne porte que la source générale msa_parametres, la page d'accueil de la MSA
  (data/sources.yaml), et ces notes le nomment sans le justifier. Aucune somme des taux lus ne le
  donne : », la suite inchangée. `data/sources.yaml` : `msa_parametres`, « Paramètres des régimes
  agricoles (RCO, points, AVA) », `https://www.msa.fr/`.
- **Les périodes de 2026 à 2027 et de 2028 sans fin** : un paragraphe chacune, qui cite L. 731-42,
  la loi n° 2025-199 (article 3, I, 8°, et III), D. 731-121, D. 633-3 et l'article 5, II, du
  décret, aux taux de ses années ; 2026 à 2027 cite aussi D. 731-120 (« au moins égale à 600 fois
  le montant horaire du salaire minimum de croissance »), qui fonde les 600 SMIC de
  `assiette_repere_smic` ; les deux disent que le 17,37 % n'est pas changé et pourquoi.
- **La fiche** : l'`effet` de l'approximation `depuis_2003` remplace « c'est une piste, non une
  lecture » par la lecture et la mesure ; une lecture du 6 novembre aux `sources.lectures` ; une
  ligne d'historique.

## 4. Tests

`python -m pytest -m rapide` : 4 574 verts, 11 rouges, tous de `test_pages_en_dossier.py` (rouges
locaux connus, refaits par GitHub). Sous `PRESOMPTIONS_DECALEES=1` : 4 369 verts, les mêmes 11.
En entier : `test_conditions_selon_l_age`, `test_controle_drees_panorama`,
`test_drees_panorama_solde`, `test_minima_agricoles`, `test_pension_minimum_avant_1983`,
`test_prelevements_historiques`, `test_regle_de_chacun`, `test_carte`, `test_textes`,
`test_donnees` : 386 verts ; `test_simulateur` et `test_cout` : voir le compte rendu du commit.

## Signalé, non fait (candidats)

- **Le 17,37 % des périodes de 2026 et de 2028** : erreur de la donnée, sans effet mesuré (§ 2) ;
  la valeur juste dépend de la qualité (principal, secondaire, 2°) et de l'année jusqu'en 2028,
  que la période ne distingue pas.
- **L. 731-42 de 2025 (LEGIARTI000051284150)** reste « a_rattacher » à la fiche
  `cotisation_vieillesse_agricole_avant_2003` (`textes.py --non-lues`) : il fonde la cotisation de
  2026, qu'aucune fiche ni version ne porte. Une version ou une fiche de la cotisation de 2026 la
  rattacherait.
- **D. 731-120 de 2026 est à l'index sous le numéro « 731-120 »** (LEGIARTI000053296657), comme le
  Journal officiel l'imprime (« Art. 731-120 ») : `dila_cherche.py legi --num D731-120` ne le montre
  pas, et la liste de contrôle des textes peut le manquer.
