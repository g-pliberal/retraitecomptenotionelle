# Le minimum des cultes et la carrière longue de la Carpimko, relus au texte

Le 19 novembre 2026, la session instruit les deux points que la note
`2026-11-19-redactions-dont-les-fiches-ne-disent-rien.md` laissait ouverts.
Aucun résultat ne change.

## Le minimum contributif des cultes

**Lu.** L. 173-2 du code de la sécurité sociale nommait, de 2012 à 2017, les
régimes « mentionnés aux articles L. 200-2 et L. 382-15 et au 2° de l'article
L. 611-1 du présent code ou à l'article L. 722-20 du code rural et de la pêche
maritime ». La loi n° 2017-1836 du 30 décembre 2017, article 15, 20°, qui
supprime le régime social des indépendants, en récrit le début : « Dans le cas
où l'assuré a relevé du régime général de sécurité sociale, du régime des
salariés agricoles ou du régime social des indépendants et lorsqu'il... (le
reste sans changement) » (JORFARTI000036339157 ; LEGIARTI000036391874).
L. 382-15, dans sa rédaction en vigueur (LEGIARTI000031686004), écrit que les
ministres des cultes et les membres des congrégations « relèvent du régime
général de sécurité sociale », et L. 382-27 leur sert la pension « dans les
conditions définies aux articles » L. 351-8 à L. 351-13, donc le minimum de
L. 351-10. Les exposés de la Cnav, mis à jour les 24 octobre et 11 novembre
2025 et lus le 19 novembre 2026, comptent le régime des cultes : « Le
dépassement peut être réparti entre les régimes suivants : le régime général ;
le régime social des indépendants ; le régime des salariés agricoles ; le
régime des cultes » (« Minimum contributif », depuis 2012) ; de même « Calcul
du minimum contributif ».

**Déduit.** La rédaction de 2018 ne sort pas les cultes du plafond : elle
remplace une liste d'articles par des noms de régimes, dans un article de
coordination, et les cultes relèvent du régime général.

**Non établi.** Ce que la Cavimac applique elle-même : sa page « Demander ma
retraite de base » donne les montants du minimum sans parler du plafond.

**Le moteur.** Il écrête tout minimum d'une pension prenant effet depuis 2012,
celui de la Cavimac compris (`completer.js`, paramètre `ecretement` de la
fiche). La règle tient : la fiche `minimum_contributif` déclare la rédaction
de 2018 sans effet, et `sans_un_mot` passe de 1 à 0.

## La carrière longue de la Carpimko

**Lu.** L. 643-3, dans sa rédaction du 1er septembre 2023
(LEGIARTI000047453031) : le II est le départ des assurés « qui ont commencé
leur activité avant un des quatre âges », la carrière longue ; le III, celui
des « assurés handicapés » ; le IV, celui des assurés des 2° et 3° de
L. 643-4. Les statuts de la Carpimko, article 11 (arrêté du 27 décembre 2023,
JORFARTI000048880643), et son règlement de 2026, article 3
(JORFARTI000054435915), ouvrent le taux plein à l'âge du 1° de L. 351-8 ;
« à partir de l'âge prévu à l'article L. 161-17-2 » à qui peut liquider sa
base sans abattement ; à l'âge du IV, à l'inapte et aux catégories ; et « dès
l'âge prévu au III de l'article L. 643-3 […] pour les affiliés qui bénéficient
de ce départ anticipé au titre du régime de base ». Le II n'y est pas. La
caisse écrit, pour le régime de base et le régime complémentaire, « Âge
minimum légal 62 ans à 64 ans », et que des situations « permettent un départ
anticipé sans application de décote au titre du régime de base », en
prévenant : « Le taux plein peut être obtenu dans un régime mais pas dans les
autres » (carpimko.com, « À quel âge prendre ma retraite » et notice « Départ
anticipé 2024 », lues le 19 novembre 2026).

**Déduit.** La carrière longue n'ouvre pas la complémentaire : elle se sert à
son âge, celui de L. 161-17-2 ou de la table des nés avant le 1er septembre
1961, et au taux plein, puisque l'assuré peut alors liquider sa base sans
abattement.

**Non établi.** Ce que la caisse sert en fait à qui part en carrière longue :
aucune de ses pages ne le dit de la complémentaire. Une autre lecture reste
possible depuis 2024 pour les nés après le 31 août 1961, dont le texte ne dit
plus l'âge minimal : la pension avant l'âge légal, minorée de 1,25 % par
trimestre « manquant pour pouvoir liquider la retraite de base à taux plein »,
donc de rien pour qui a sa durée. Elle rendrait le résultat d'aujourd'hui.

**Le moteur.** Il sert la complémentaire avec la base, au départ pour carrière
longue, sans coefficient, à toute date. Les fiches le déclaraient pour les
pensions d'avant 2024 et le croyaient fondé depuis, en lisant le III comme la
carrière longue. `carpimko_ages_2015` et `liquidation_regime_par_regime` sont
corrigées : l'écart vaut pour 2024 et après aussi.

**La correction, prête et non publiée.** Un paramètre de période,
`fermee_a_la_carriere_longue`, posé sur les onze périodes qui lisent la table
`carpimko_2016` ; `ouvertureSous`, dans `departs.js`, n'offre plus l'âge de la
carrière longue à ces périodes. Le test, tiré du texte, est vu rouge sur le
moteur d'aujourd'hui et vert avec la correction ; les tests rapides passent,
la suite complète et les témoins n'ont pas été rejoués.

**Ce qui bougerait**, auxiliaire médical à deux fois le Smic, parti à
soixante ans, montants annuels en euros de l'année du départ :

| Né le 10 mars | Entré à | Base servie le | Complémentaire aujourd'hui | Après correction |
|---|---|---|---|---|
| 1957 | 18 ans | 1er avril 2017 | le même jour, 5 665,30 | 1er décembre 2017, 5 665,30 |
| 1960 | 17 ans | 1er avril 2020 | le même jour, 6 264,52 | 1er décembre 2021, 5 931,78 |
| 1962 | 17 ans | 1er avril 2022 | le même jour, 6 646,27 | 1er octobre 2024, 5 761,10 |
| 1964 | 17 ans | 1er avril 2024 | le même jour, 6 736,86 | 1er janvier 2027, 4 815,80 |
| 1966 | 17 ans | 1er avril 2026 | le même jour, 5 346,20 | 1er juillet 2029, 5 346,20 |

Le montant baisse quand le rendement que le modèle donne aux cotisations
baisse entre les deux dates d'effet. Qui part à l'âge légal ou après ne bouge
pas (né en 1964, parti à 63 ou 67 ans : identique).

**À savoir.** L'avantage social vieillesse des auxiliaires médicaux se
liquide avec la complémentaire : il attendrait le même jour, au même montant.
Aujourd'hui, le modèle le sert aussi sans coefficient au départ pour carrière
longue, ce que son règlement, qui ouvre à 65 ans ou à 60 ans à l'inapte, ne
fonde pas davantage : non instruit ici. La CAVOM et la CPRN, dont les statuts
ne disent rien non plus de la carrière longue, gardent leur écart déclaré.

**Publiée le 20 novembre 2026.** Le propriétaire a choisi de publier la
correction. Elle est sur `main` telle que préparée, le paquet refait ; aucun
des 936 témoins de simulation ni des 86 rendus de page ne bouge, aucun ne
portant d'auxiliaire médical parti en carrière longue. Les deux fiches disent
la règle servie et ce que le texte laisse ouvert. Reste, pour une autre étape :
l'avantage social vieillesse des auxiliaires médicaux, que la correction
retarde avec la complémentaire sans que son règlement ait été lu pour ce cas.
