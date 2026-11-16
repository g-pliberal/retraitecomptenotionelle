# Étape 6, à part : les deux premiers écarts lourds corrigés, la durée de 160 trimestres avant 2009 et le cumul à 160 % du SMIC dès 2007

La note du même jour sur les écarts lourds des circulaires
(`2026-11-16-ecarts-lourds-des-circulaires-au-texte.md`) classe en tête deux écarts,
confirmés à la contre-vérification. Le propriétaire a demandé de les corriger dans le
moteur. Cette note dit ce qui a changé, l'approximation retenue et ce que la
correction déplace. La note 0009 étant encore en essai, les fiches gardent leur forme.

## 1. La durée requise avant 2009, et celle des nés de 1953 à 1955

**Le droit.** R. 351-45, I (version du 10 mai 1995 au 1er janvier 2009,
LEGIARTI000006749450) : 160 trimestres pour toute pension prenant effet après 2002,
« quelle que soit la date de naissance ». La durée par génération n'entre au code
qu'avec le décret n° 2008-1555, article 4, en vigueur le 1er janvier 2009 ; la
circulaire Cnav 2008/41, § 211 et 213, le redit. Pour les nés de 1953 à 1955, la
circulaire Cnav 2011/25 fait décider la date de la demande : 164 trimestres pour une
demande d'avant 2011, 165 après, les attestations d'avant 2011 restant acquises pour
une date d'effet jusqu'au 1er juin 2011. Les nés en 1955 n'ont leurs 166 trimestres
qu'au décret n° 2011-916 (JORFTEXT000024419259), en vigueur le 3 août 2011, « le
lendemain de la publication » (lu dans l'index JORF du 16 novembre 2026).

**Le modèle, avant.** `dureeRequise` (`moteur/js/droit/ouvrir.js`) lisait la table par
la seule génération : 161 à 164 trimestres aux nés de 1949 à 1952 partis avant 2009,
165 ou 166 aux nés de 1953 à 1955 partis avant le décret de leur génération.

**Le modèle, après.** Une pension prenant effet avant le 1er janvier 2009 a 160
trimestres, quelle que soit la génération (`DUREE_PAR_GENERATION_EFFET`, dans
`moteur/js/regimes.js` et `droit/ouvrir.py`). Les nés de 1953 à 1955 ont 164
trimestres jusqu'à une pension prenant effet le 1er juin 2011, et les nés en 1955,
165 jusqu'au 1er août 2011 (`DUREES_AVANT_LE_DECRET`). **Approximation déclarée** : le
modèle n'a pas de date de demande ; la date d'effet du 1er juin 2011, celle que la
circulaire garde aux attestations d'avant 2011, en tient lieu, et la fiabilité de la
durée descend à « moyenne » pour toute pension de 2011 que cette règle touche. La
règle passe par `dureeRequise`, que lisent l'ouverture du droit (la carrière longue,
le handicap), le taux et le prorata : tous suivent. La fonction publique, la SNCF, la
RATP, les IEG, la CRPCEN et la Banque de France gardent leurs propres durées, qui
passent avant (vérifié : 160 à l'État, 150 à la CRPCEN, 153 à la Banque de France
pour un départ de 2008 d'un né en 1950, avant comme après). Les régimes qui empruntent
la durée du régime général, alignés, libéraux, complémentaires dont la durée annule
l'abattement (Agirc-Arrco, Ircantec), la suivent.

**Effet, par le simulateur.** Salarié non cadre à 0,6 fois le salaire moyen, au travail
dès 14 ans, 168 trimestres :

| naissance | départ | avant | après |
|---|---|---|---|
| mars 1952 | 56 ans, avril 2008 | refusé, 164 requis, ouverture à 60 ans et 9 mois | carrière longue, 160 requis, 11 438 € par an |
| juin 1950 | 56 ans, juillet 2006 | refusé, 162 requis, ouverture à 60 ans | carrière longue, 10 855 € par an |
| septembre 1951 | 57 ans, octobre 2008, 169 trimestres | refusé, 163 requis | carrière longue, 11 613 € par an |
| octobre 1949 | 56 ans, novembre 2005 | refusé, 161 requis | carrière longue, 10 559 € par an |

Le départ que le modèle refusait à tort avance de trois ans et quatre mois (né en
1951) à quatre ans et neuf mois (né en 1952) : de 38 000 à 54 000 € de pensions de
base et complémentaire pour chacun de ces cas. Le
montant annuel ne change pas ici, la durée étant atteinte des deux côtés ; il change
quand la durée au régime est sous la limite (prorata de 160/161 à 160/164, de
− 0,6 % à − 2,4 % avant correction). Le cas de contrôle, né en mars 1952 parti à
58 ans en avril 2010, garde 164 trimestres, avant comme après.

Les témoins : aucun des 933 témoins de simulation ni des 85 rendus de page ne bouge
(aucun ne part avant 2009 au-dessus de 160 trimestres). Bougent l'échantillon de la
grille large (`test_grille_large.py` : ses conditions d'ouverture et ses
proratisations), une sortie de `simuler.mjs` et le témoin du droit, qui gagne la
demande du test neuf. Le coût et les carrières types se refont sur GitHub, après
l'envoi : ce qu'ils déplacent se lira au tableau de bord et dans le diff du commit de
la fabrique.

## 2. Le cumul emploi-retraite à 160 % du SMIC dès 2007

**Le droit.** Loi n° 2006-1640 (LFSS pour 2007), article 105, I : L. 161-22 permet la
reprise si les revenus, ajoutés aux pensions, « sont inférieurs à 160 % du salaire
minimum de croissance ou au dernier salaire d'activité ». Circulaire Cnav 2007/34 :
1,6 fois le SMIC mensuel, 2 007 €, « pour les arrérages dus à partir de la mensualité
de janvier 2007 ». L'Agirc et l'Arrco ont la même limite par leur circulaire
2007-7-DRE du 10 avril 2007, que la circulaire commune 2009-7-DRE du 26 mars 2009
rappelle : « 160 % du Smic ou du dernier salaire ou du salaire moyen des 10 dernières
années ».

**Le modèle, après.** Une version de plus dans la fiche
`cumul_emploi_retraite_et_retraite_progressive`, `plafond_a_160_pour_cent_du_smic_2007`,
pour les mois de 2007 et 2008 des pensions prises depuis 2004 ; la version de 2004
s'arrête au 1er janvier 2007. Dans le moteur, `LOI_2007` et `PART_SMIC_2007`
(`cumul.js`, `cumul.py`) : le plancher du plafond passe à 1,6 SMIC en janvier 2007, et
non plus en 2009. Le plafond de l'Agirc-Arrco, qui part de celui de la base, suit. Les
non-salariés (L. 634-6, L. 643-6) ne changent pas.

**Effet.** Le test neuf : retraitée de 2005, dernier salaire sous le SMIC, 800 € de
pensions par mois, reprise à 700 € (1 479 € à l'assiette de la CSG). En 2006, au-delà
du SMIC (1 254 €), rien n'est servi, avant comme après ; en 2007 et 2008, le modèle
suspendait 800 € par mois, il les sert désormais : 19 200 € sur les deux ans.

**Écart restant, déclaré dans la fiche** (`ecart_connu`) : la moyenne des dix
dernières années, troisième limite de l'Agirc-Arrco depuis la 2007-7-DRE, ne vaut dans
le modèle qu'à compter de 2009, faute d'avoir lu la date d'effet de cette circulaire.

## Ce qui reste

La circulaire 2007-7-DRE de l'Agirc-Arrco, pour sa date d'effet et la moyenne des
dix ans ; la circulaire Cnav 2011/24, jumelle de la 2011/25 pour la carrière longue
(inscrite à relire dans la fiche de la durée). Les écarts 3 à 6 de la note des écarts
lourds restent à faire, dans l'ordre qu'elle donne.
