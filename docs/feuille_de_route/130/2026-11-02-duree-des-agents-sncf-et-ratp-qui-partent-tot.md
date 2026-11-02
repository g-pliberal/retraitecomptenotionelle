# La durée des agents de la SNCF et de la RATP qui partent tôt

**La demande.** Le 2 novembre 2026, le propriétaire répond « oui », dans la
session de la file E, à la question que sa note laissait
(`130/2026-11-02-carte-des-fiches-sncf-et-ratp-lues-au-droit.md`) : ouvrir une
étape du modèle pour la durée de l'agent de la SNCF ou de la RATP qui part
avant cinquante-cinq ou soixante ans. La session d'orchestration la confie à la
file G. Une donnée change ; aucune ligne du moteur.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; l'index LEGI récupéré et mis à
  jour jusqu'à l'incrément du 2 novembre 2026 au soir ; `textes.py --inscrire`,
  sans rédaction nouvelle. Relus : les trois rédactions de l'article 23-1 du
  décret n° 2008-637 (RATP), les deux de l'article 12-1 du décret n° 2008-639
  (SNCF), et le tableau par génération des agents de conduite de la CPRPSNCF
  (octobre 2023), une image lue à l'œil : 167 trimestres pour le né du
  1er novembre 1968 à 1969, 168 pour 1970 et 1971, 169 pour 1972.
- **Le test d'abord.** Dans `tests/test_sncf_ratp.py`, les cinq écarts déclarés
  deviennent quatorze cas que le modèle doit rendre au droit
  (`AVANT_L_AGE_DE_LECTURE`) : le mois d'ouverture tiré de la table d'âges, la
  durée de la version lue à l'âge de lecture ou, depuis 2025, à l'année, et deux
  départs de 2026 après une ouverture de 2024, que le I bis de l'article 35 et le
  IX de l'article 51-1 gardent sous la règle d'avant. Le test des versions
  confronte la table, mois par mois, à l'âge de lecture ; un test neuf vérifie
  que la durée par année de la RATP ne sert que qui part avant soixante ans. Vus
  rouges, seize échecs : le modèle rendait 168 au lieu de 167, 172 au lieu de
  170 ; puis la fiche, qui déclarait encore les écarts.
- **La donnée.** Dans `legislation/duree_requise_regimes_speciaux.csv`, la
  colonne `age_de_lecture`, que les IEG, la Comédie-Française et l'Opéra
  employaient, à 55 sur les lignes `sncf_2014` et à 60 sur `ratp_2014` ; une
  table neuve, `ratp_avant_60`, lue à soixante ans depuis 2025 — 170 trimestres
  à la génération 1965, 171 à 1968, 172 à 1971, soit la durée de l'année où le
  droit s'ouvre —, que la période de 2025 de `regimes/ratp.yaml` nomme la
  première. Les deux moteurs et la fabrique du paquet lisaient déjà la colonne.
  Les notes des périodes de `regimes/sncf.yaml` et `regimes/ratp.yaml` le
  disent.
- **Ce qu'elle fait à qui partirait après soixante ans** : lue à sa propre
  génération, la table par année lui donnerait un trimestre de moins que
  l'article 51 s'il est né de 1966 à 1970. Le modèle ne sert que le roulant, qui
  ouvre son droit avant cinquante-cinq ans : le test neuf le tient, la fiche le
  déclare.
- **L'effet**, par mois de naissance, l'agent ouvrant son droit à l'âge de sa
  table : l'agent de conduite doit un trimestre de moins — 167 au lieu de 168
  pour le né en novembre ou décembre 1968, 168 au lieu de 169 pour 1970 et 1971,
  169 au lieu de 170 pour 1972 —, deux pour 1969 (167 au lieu de 169). Le
  roulant en doit trois de moins s'il est né de novembre 1968 à 1971, deux pour
  1972, deux s'il ouvre son droit de 2025 à 2027 (nés de 1973 à mars 1975, 170 au
  lieu de 172), un de 2028 à 2030 (nés d'avril 1975 à septembre 1977). Personne
  d'autre ne bouge.
- **Ce que les témoins déplacent** (`resumer_temoins.py`) : trois des 913,
  tous à la RATP, tous à la hausse. Au scénario 1, le roulant né en 1970, parti
  à cinquante-six ans avec 140 trimestres, +1,79 % (140/168 au lieu de
  140/171), et le roulant né en 1975, parent de trois enfants, +1,18 % (140/170
  au lieu de 140/172) ; `statut_agent_ratp`, au taux plein des deux façons, ne
  bouge qu'aux scénarios qui convertissent ses droits acquis (+1,04 % au
  scénario 3). Un témoin neuf, `sncf_generation_1970`
  (`scripts/construire_temoins.py`), tient la SNCF : 140 trimestres sur 168, et
  non 169, soit 0,6 % de pension. La régénération refait aussi le paquet, les
  agrégats, le chiffrage et neuf rendus de page.
- **La fiche `duree_requise_sncf_ratp`** perd trois approximations, l'effet
  dit génération par génération ; elle reste approchée : les pensions du second
  semestre de 2008, la durée par année de la SNCF depuis 2025, l'agent présumé
  agent de conduite ou roulant.

## Ce que l'étape laisse

- **La même famille d'erreur, ailleurs, non corrigée** (« la classe, pas le
  cas »). Les vingt-six rédactions de LEGI qui écrivent « à compter de laquelle
  la liquidation peut intervenir » nomment, outre la SNCF, la RATP, les IEG et la
  fonction publique, que le modèle sert déjà : la CRPCEN (décret n° 90-1215,
  article 85, III, de 2017 à 2024), la Comédie-Française (décret n° 68-960,
  article 12, VI), l'Opéra (décret n° 68-382, article 14, VI) et la Banque de
  France (article 31-1 du règlement annexé au décret n° 2007-262).
  - Qui ouvre son droit APRÈS soixante ans y doit, pour les pensions de 2017 et
    après, la durée « en vigueur lorsque les assurés atteignent l'âge de
    soixante ans » ; le modèle lit le calendrier de 2008 au mois de
    l'ouverture. Un trimestre de trop à la CRPCEN et à la Comédie-Française
    pour les nés de mars à juin 1957 (165 au lieu de 164) et de janvier à juin
    1958 (166 au lieu de 165), dont les soixante ans précèdent une marche du
    calendrier que l'ouverture suit ; rien à la Banque de France. À confirmer
    auprès des caisses avant de l'écrire.
  - Qui part AVANT soixante ans à la CRPCEN ou à la Banque de France doit la
    durée de la génération qui les atteint ; leurs tables de 2014
    (`crpcen_2014`, `banque_de_france_2014`) n'ont pas d'âge de lecture. Leurs
    assurés ouvrent leur droit après soixante ans : seul un départ anticipé —
    carrière longue, handicap — les toucherait, si le modèle le leur ouvre. À
    vérifier.
  L'Opéra lit déjà sa table à soixante ans, et son ballet part à quarante.
- **La SNCF depuis 2025** : l'article 12-1 donne à qui part avant cinquante-cinq
  ans la durée par année de la RATP ; la CPRPSNCF suit la table de l'agent de
  conduite, un trimestre de moins pour le né d'avril à décembre 1975 (170 au
  lieu de 171) ou d'octobre à décembre 1977 (171 au lieu de 172). Le modèle suit
  la caisse, la fiche déclare l'écart, un cas du test le tient ; la question est
  pour la CPRPSNCF.
- **La CRP RATP** ne publie pas ses tableaux : la lecture de l'article 23-1 n'y
  est confrontée à aucune valeur de la caisse.
- **Hors de cette étape, la surcote de la SNCF de 2009 à 2017** : 0,75 % par
  trimestre dans `regimes/sncf.yaml`, 1,25 % à la RATP, sous la même phrase des
  deux décrets, que L. 14 fixe à 1,25 % depuis le 19 décembre 2008 (fiche
  `surcote_regimes_speciaux`) ; et la limite de vingt trimestres, que
  `trimestres_de_surcote_regimes_speciaux` ne porte pas.

## Ce qui attend le propriétaire

Rien pour cette étape. Une question pour une étape à venir : ouvrir une étape du
modèle pour la CRPCEN et la Comédie-Française, une fois leurs caisses
interrogées ? Pour le reste, rien de neuf : la septième étape du sixième
domaine, la décision de la proposition, et celle sur la retraite progressive,
le cumul et la seconde pension, README muet.
