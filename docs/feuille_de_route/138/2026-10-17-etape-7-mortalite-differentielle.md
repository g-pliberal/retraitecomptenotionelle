# Étape 7, neuvième partie : la mortalité différentielle des cas types de la page Coût

Le 17 octobre 2026, le premier des points qui restaient à l'étape (note
« indexation sous la variante », « Ce qui reste », 2) : les cas types de la
page Coût vivaient tous comme la population générale, quand leur diviseur
les fait vivre comme leur vingtile de niveau de vie depuis le 21 septembre
(misraa, pablo, canopee et prisme au registre, chantier « 138.7 »).

**La règle.** Chaque cohorte de la grille porte sa survie rapportée à celle
de la population générale, année par année depuis sa liquidation
(`Pensionne.survie`, `cout._survies`) : celle de la population que son
diviseur lui rattache, le vingtile où son salaire la range — ou sa pension
du droit en vigueur, sous le rattachement par la pension —, en table de
génération et unisexe, comme la pyramide qu'elle corrige, un cas type
pesant les retraités de sa caisse, des deux sexes. Les masses la prennent
*à nombre de décès égal* (misraa) : dans chaque cohorte, chaque survie est
divisée par leur moyenne, les cas types pesés comme la grille les pèse cette
année-là (`cout._survies_alignees`). La pyramide de l'INSEE garde ainsi ses
survivants ; ce qui change est leur répartition entre fortes et faibles
pensions. Têtes et masses en suivent, dans les six systèmes et dans chaque
régime, le calage sur les groupes du COR compris, qui pèse les cas types un
à un et les aligne sur toute la grille (`poids_alignement`) ; ce que la
proposition fait encore cotiser après le départ du droit en vigueur, et les
rentes de son pilier, chacun à ses poids ; la garantie ; l'engagement
acquis. Un cas type seul de sa grille vit comme la pyramide. L'interrupteur
est celui du diviseur, et il n'y en a qu'un : sous la table commune
(`population_conversion=None`), la page revient à la pyramide seule. Aucune
règle du scénario 1 n'est en cause, ni aucun texte : ni veille du droit, ni
entrée au journal.

**Pourquoi aligner.** Rapportée à la population générale, la survie d'un
vingtile garde le nombre des décès dans une population où chaque vingtile
pèse un vingtième ; la grille, qui n'en est pas une, en perdait. Pesée par
ses effectifs de 2024 et partie à 62 ans, elle gardait la pyramide à un
millième près à 70 et 80 ans, la dépassait de 1 à 2 % à 90 ans
(générations 1955 et 1975) ; mais en 2009, ses exploitants et ses salariés
au SMIC des vieilles générations portaient l'écart de ses têtes à l'enquête
auprès des caisses de −6,2 à −6,6 %, au-delà du cliquet de
`test_la_reconstitution_se_decompose_en_tetes_pension_et_reversion`.
Alignées, les têtes de 2009 restent à −6,2 %, et la pension par tête passe
de −7,4 à −7,3 %.

**Ce qu'elle déplace**, mesuré sur `d8af61d`, contre sa table. Le
système actuel reste calé sur la dépense du COR, 15,30 % du PIB en 2070 ;
sa dérive, ce que ses masses font seules, passe de 1,0121 à 1,0128 en 2030,
de 1,0047 à 1,0060 en 2050, de 1,0307 à 1,0298 en 2070. La proposition
passe de 8,768 à 8,759 % du PIB en 2030, de 9,749 à 9,753 % en 2050, de
8,156 à 8,163 % en 2070 ; son solde moyen de 2026 à 2070, de −1,076 à
−1,078 point. Le scénario 2 passe de 4,670 à 4,684 % du PIB en 2070, le
scénario 4 de 10,405 à 10,412 % ; la garantie de la proposition, de 13,69 à
13,74 Md€ constants. Les gros capitaux sont servis plus longtemps : le cadre
et le libéral, rangés au dix-neuvième et au vingtième vingtile, pèsent
davantage aux grands âges, le SMIC et l'exploitant, au quatrième et au
troisième, moins ; et ce sont les premiers que la proposition éloigne le
moins du droit en vigueur : le cadre y perd de 9 à 24 % de sa pension, le
libéral de 8 à 12 %, l'exploitant de 21 à 53 % (générations 1960, 1980 et
2000, page Cas types). C'est dans ce que la limite annonçait, sans aligner
(« moins de 1 % du rapport de masses, un dixième de point de PIB au plus en
2070 », `docs/limites/5-hors-du-modele.md`).

**Les tests** (`test_cout.py`) :
`test_chaque_cohorte_survit_au_rythme_de_sa_population`, deux cas types aux
survies posées à la main — les têtes de la pyramide, les masses, les
régimes, le calage cas type par cas type, les cotisations et le pilier,
rien avant la liquidation ni pour un cas type seul ;
`test_la_survie_d_un_cas_type_est_celle_du_vingtile_de_son_diviseur`, le
SMIC au quatrième vingtile et le cadre au dix-neuvième
(`docs/methodologie.md`, § 5), aucune survie sous la table commune ;
`test_l_engagement_compte_les_survivants_de_chaque_population`, qu'une
survie divisée pour tous ne change pas et qu'une survie divisée pour le
seul SMIC relève. Quatre cliquets descendent, leur écart étant passé d'un
point sous eux : le passé refait (`test_la_projection_refait_le_passe`), de
0,142 à 0,135 — 2009 passe de −13,2 à −13,1 % ; dans
`test_l_ecart_au_cor_groupe_par_groupe`, la pension relative de
l'Agirc-Arrco, de 0,23 à 0,22 (de +22,2 à +21,4 % du COR à l'horizon), la
dépense de la FPE, de 0,20 à 0,19 (de +19,3 à +18,9 %), celle des régimes
spéciaux, de 0,34 à 0,33 (de −33,6 à −32,3 %).

**Le registre** : misraa, pablo et canopee passent à `repris`. Prisme reste
`a_reprendre` : sa mortalité est celle du type de pension, et la grille n'a
pas de retraité pour inaptitude.

**Ce qui reste** du point, dans l'ordre :

1. *Les inaptes de la Cnav* (prisme), qui vivent au moins quatre ans de
   moins : un cas type de plus à la grille, sa part des retraités du régime
   général et sa mortalité, que le dépôt n'a pas.
2. *Les autres pesées de la grille par la pyramide*, qui gardent la
   population générale : le contrôle sur Ancetre (`controle_ancetre.py`),
   celui sur l'EACR (`controle_eacr.py`), le bilan du compte
   (`bilan_compte.py`), le coût des avantages (`avantages.py`).
3. *La page Coût*, à une session des pages : sa phrase « Les poids sont les
   effectifs réels de chaque génération, lus dans la pyramide des âges de
   l'INSEE » (`pages.js`) peut dire que chaque cas type y survit au rythme
   de son vingtile, à nombre de décès égal.
4. *La limite*, à la fin de l'étape : deux récits datés de
   `docs/limites/5-hors-du-modele.md` disent la page à la mortalité
   générale ; un paragraphe d'état dira la règle.
