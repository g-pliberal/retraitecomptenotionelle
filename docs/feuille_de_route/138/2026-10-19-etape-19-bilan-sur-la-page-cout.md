# Étape 19, troisième partie : le bilan du compte sur la page Coût

**La demande.** Vague du 19 octobre 2026, session 11 de la deuxième salve,
lancée par la session de suivi sur la demande du propriétaire, « les sessions
qui n'ont pas besoin de moi » : « À une session des pages : le bilan sur la
page Coût » (bloc « Reprise » de l'étape), en partant de ce que l'action 161
a fait passer cette nuit par le pont. Ce que le pont a pris est le bilan
figé de l'accueil (`donnees/bilan.py`, `equilibre.json`), non
`bilan_compte.py`, qui n'a pas de jumeau et lit la grille du coût, encore
simulée en Python (note de l'action 161 du 19 octobre, « Ce qui suit ») : le
bilan du compte entre donc dans la table des agrégats, comme le coût.

**La grille du bilan, d'abord.** `calculer_bilans` pesait par défaut ses
profils et sa dette sur les treize cas types (`CAS_TYPES`), quand le coût,
ses masses et l'engagement acquis les pèsent depuis le 16 octobre sur la
grille du coût (`GRILLE_DU_COUT`), où les actifs de l'État et de la CNRACL
pèsent leurs départs (étape 3). Il lit désormais celle-ci
(`test_le_bilan_se_pese_sur_la_grille_du_cout`, vu rouge). Le système actuel
passe d'une dette de 503 % du PIB et d'un ratio de 0,648 à 501 % et 0,649 ;
la proposition, de 361 % et 0,905 à 362 % et 0,903.

**La table.** `bilan_compte` dans `data/derive/agregats.json` : l'année, le
rendement comptable des réserves, et, pour chaque système que le site
compare, les huit champs de `BilanCompte` et les sept indicateurs qu'il en
tire (`CHAMPS_BILAN_COMPTE`), figés pour que le lecteur n'en refasse aucune
opération — `figer_bilan_compte` et `BilanCompteFige` dans
`donnees/agregats.py`, son jumeau dans `agregats.js` ; la version du paquet
passe à 27 des deux côtés. L'année est la dernière dont le COR donne le
stock des réserves (`Reserves.derniere_annee`, 2025). Le bilan simule deux
fois la grille du coût, pour l'engagement et pour les profils, soit plus de
quatre-vingts secondes : `bilans_gardes` le confie à `memoire`, si bien que
la fabrique le paie une fois et que son test (`test_agregats.py`) et le
contrôle de la page le relisent. S'il prenait, avec `calculer_engagements`,
la grille que le coût a déjà simulée (`grille_simulee`, comme
`calculer_cout`), il ne coûterait que quelques secondes ; `cout.py` était
cette nuit à d'autres sessions.

**La page.** « Le bilan du compte, à la suédoise » (`cout-bilan-compte`),
replié après la dette que les soldes accumulent : ce qu'est le bilan suédois
et ce qu'il règle, le tableau des quatre systèmes, ce qu'il dit du système
actuel et de la proposition, puis ses limites — la coupe d'une année, la
convention de la dette, les réserves communes, leur rendement. Sa phrase en
gras est au catalogue (`cout.bilan_du_compte`, contrôle
`bilan_du_compte_du_depot`, qui interroge le modèle), « durée de rotation »
en `sans_portee`. Le budget de lecture de la page passe de 970 à 977 mots :
elle l'atteignait exactement, et le titre d'une section repliée se lit dans
son plan. Le registre ne dit plus « Aucune page ne l'affiche » (`referents.yaml`,
`balanstal_suede`).

Ce que la page montre, fin 2025 :

| Système | Durée de rotation | Actif de cotisation | Dette | Ratio | Taux de cotisation d'équilibre |
|---|---:|---:|---:|---:|---:|
| 1. Système actuel | 29,4 ans | 317 % | 501 % | 0,65 | 25,8 % |
| 2. Part salariale | 29,6 ans | 319 % | 162 % | 2,01 | 3,5 % |
| 3. Les deux parts | 29,4 ans | 317 % | 394 % | 0,83 | 16,1 % |
| 4. La proposition | 29,5 ans | 318 % | 362 % | 0,90 | 16,1 % |

Les réserves, 8,2 % du PIB, sont les mêmes pour tous ; elles ont rapporté
1,6 % en 2025.

**Tests.** 2 858 rapides ; `-m site` ; les trois fichiers du site,
`test_agregats.py` et `test_bilan_compte.py`, 545 ; le catalogue des
affirmations, 637 ; la carte des jumeaux, la fabrique, les niveaux et les
confrontations légères, 407 ; `construire_donnees.py --verifier` : « paquet
à jour ». Les témoins : quatre rendus de la page Coût changent, aucune
simulation.

**Ce qui reste**, outre le bloc « Reprise » : quand l'action 161 fera passer
la grille du coût par le pont, le bilan la suivra, qui appelle `_pensionnes`
et `calculer_engagements` ; les réserves projetées et leur emploi contre les
déficits, et le bilan d'une année projetée (note du 14 octobre).
