# Étape 2, suite : la voie des quatre trimestres agricoles publiée, et le pilote qui datait l'exploitant trop tôt

**Le 15 novembre 2026, à la demande du propriétaire** (« On peut faire les
deux corrections ? »), après l'audit des portes de la carrière longue
(`153/2026-11-15-les-portes-des-ouvriers-de-l-etat.md`). Le cas type de
l'exploitant agricole est gardé tel quel, et la rédaction de 2026 de
D. 732-40 lue comme une voie qui s'ajoute à la voie générale : les deux
recommandations de la note de l'étape, que le propriétaire avait faites
siennes le 12 novembre (« je choisis tes recommandations »).

**Le pilote, le test d'abord.** `test_le_pilote_ne_fait_pas_partir_l_exploitant_avant_que_sa_duree_soit_reunie`
(`tests/test_liquidation.py`), vu rouge à 60 ans et 8 mois : l'exploitant né
en janvier 1953, installé au 1er janvier 1973, a 160 trimestres à la fin de
2012, 164 avec 2013, 168 avec 2014, pour 165 requis ; il part à 61 ans, et le
né de 1954 aussi. Le droit date la durée cotisée au fil des mois, quand le
régime agricole valide l'année au 1er janvier : liquidée en 2013, la carrière
se voit opposer un trimestre de plus ; liquidée en 2014, un âge de 2013. Le
point fixe passait de l'un à l'autre jusqu'au bout de ses quatre passes. La
montée qu'il tente quand un âge plus précoce ne se confirme pas
(`premierAgeOuvert`, `pilote.js`, et son jumeau `_premier_age_ouvert`) ne
retient plus que l'âge qui se confirme lui-même. Aucun témoin ne bouge.

**La règle**, rejouée du correctif
`docs/mesures/192/2026-11-12-etape-2-la-regle-et-ses-tests.txt`, code des
deux moteurs et tests, sans le témoin de plus : ajouté, il décalait
l'échantillon d'un témoin sur quarante de `tests/test_facade_jumeau.py` sur
`rattachement_pension_smic`, dont la réduction générale de la proposition
diffère de 3,45 € entre les deux moteurs, sur `main` déjà (écart ancien, sans
lien, signalé à la session du retrait du Python). Le test de
`test_simulateur.py` confronte déjà la règle dans les deux moteurs.

**Ce qui se déplace.** L'exploitant part à 61 ans au lieu de 62 de 1953 à
1960, à 61 ans et 3 mois au lieu de 62 et demi en 1962, à 62 ans au lieu de
63 à partir de 1964. Huit tests de la suite complète :
`test_controle_drees_panorama.py` (l'exploitant n'a plus de cohorte qui
liquide en 2024 ; les minima déduits de la garantie, remesurés aux deux
jours de naissance présumés), `test_cout.py` (la borne haute, 0,2048 :
seuil porté à 0,22), `test_cout_age_depart.py` (l'exploitant de 1955 à
61 ans, posé à la main ; le scénario à cotisation employeur à −0,17 point
pour +0,26 au système actuel : le « petit devant » passe de trois cinquièmes
à deux tiers) ; le bilan figé et les mesures de l'accueil, que GitHub
refait. `test_cycle_de_vie_script.py` est remis à sa valeur par le correctif.

**Les artisans et commerçants nés au dernier trimestre**, de juillet 2011 à
octobre 2012 : le même article 11 du décret n° 2010-1734 écrit « seizième,
dix-septième ou dix-huitième » au 2° de D. 351-1-3 et de D. 16-3, et omet le
dix-huitième au 3 bis du décret n° 73-937. Ne touche que les nés d'octobre à
décembre 1951. Soumis au propriétaire : la lecture alignée, que le modèle
applique et que la session recommande, ou la lettre.

**Ce qui reste** : la décision du propriétaire sur le 3 bis ; la lettre à
toutes les caisses MSA n° 2026-298 pour la rédaction de 2026 ; la
coordination des régimes pour l'ancien aide familial devenu salarié (fiche
`carriere_longue`, `a_relire`).
