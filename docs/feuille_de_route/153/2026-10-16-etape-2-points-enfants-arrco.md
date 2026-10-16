# Étape 2, sixième famille : les points enfants et la minoration de l'Arrco, confrontés à OpenFisca

**Le 16 octobre 2026, la demande.** La septième de treize sessions
parallèles, le propriétaire absent : « action 153, étape 2, famille suivante.
Les points enfants et la minoration de l'Arrco, confrontés à OpenFisca dans
un script et un test frères. » Aucun fichier des pages ni de la saisie n'est
touché, aucun déplacé ; la liste des textes n'est pas inscrite.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part (avec un
`setuptools` d'avant 70) : `arrco_points_enfants_nes_et_eleves`,
`arrco_points_enfants_a_charge`, `arrco_majoration_pension`, `arrco_pension`,
`arrco_coefficient_de_minoration` et leurs jumeaux de l'Agirc. Sur le
plafond : la page de Legisocial d'août 2011, qui cite la circulaire
Agirc-Arrco du 7 juillet 2011, point 3.3.1, et le document n° 7 de la séance
du COR de mai 2011. L'accord du 18 mars 2011 est à KALI, que la session n'a
pas lu. Le journal de veille a son entrée
(`2026-10-16-action-153-points-enfants-arrco.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_points_enfants_arrco.py` et portée par le témoin
(`tests/temoins/openfisca_points_enfants_arrco.json`) : la carrière de
`openfisca_arrco.py`, de 1999 à 2018 au plus tard, non-cadre sauf un cadre ;
les deux nombres d'enfants d'OpenFisca contre des naissances datées, toutes
d'avant 2010, pour que la décote, d'où l'Arrco tire son coefficient, ne bouge
pas ; la majoration comparée telle que la pension la sert.

**Ce qui est fait.** Treize profils : trois parents de trois ou quatre
enfants, un de deux ; deux au plafond, dont un cadre ; un né en 1950 ; trois
parents d'enfants à charge, avec ou sans décote, avant et après 2012 ; trois
sous un coefficient d'anticipation, dont un à quinze trimestres.
`tests/test_oracle_points_enfants_arrco.py`, au niveau des contrôles : neuf
tests, la convention d'abord, et le jumeau JavaScript sur les treize. Le
manifeste a sa ligne (`openfisca_points_enfants_arrco_oracle`) ; le registre
un écart, une reprise et le point 153.2 ; les deux fiches de la majoration
leur bloc `referents`, la première sa lecture du jour ; les limites un
paragraphe et la table des paramètres sa ligne.

**Ce que la confrontation a trouvé.** Une erreur chez nous, une chez
OpenFisca.

| profil | le dépôt | OpenFisca | ce qui tranche |
|---|---|---|---|
| non-cadre né en 1952, 100 000 €, trois enfants, parti en 2018 | 1 104,68 € : le plafond unifié de 2025, commun | 1 031,15 € : 1 000 € au point du 1er janvier 2012 | accord du 18 mars 2011 ; circulaire du 7 juillet 2011, point 3.3.1 |
| cadre né en 1952, 90 000 €, trois enfants, parti en 2018 | l'Agirc et l'Arrco sous un même plafond | l'Agirc à 1 028,11 €, l'Arrco entier | les mêmes : « au titre de l'Agirc et [...] au titre de l'Arrco » |
| non-cadre né en 1951, deux enfants à charge, huit trimestres de décote, parti en 2014 | 190,32 € : 5 % des droits bruts | 175,09 € : minorée de 0,92 | accord du 8 décembre 1961, annexe A, article 17, rédaction de 2011 |

La correction, dans les deux moteurs : un champ de période,
`plafond_majoration_regime`, qui dit au titre de quel régime le plafond
s'oppose et dont il suit le point (`arrco` ou `agirc`, dans toutes les
périodes d'avant 2019 de l'Arrco, de l'Agirc, de leurs tranches, des
entreprises nouvelles, des cultes et de l'UNIRS, à 1 000 € au point du
31 décembre 2011) ; un seau de plafond par régime ; aucun plafond avant le
1er janvier 2012 ; et, après 2018, le plafond du régime qui a intégré une
fiche fermée (`regime_du_plafond`), si bien que les liquidations depuis 2019
ne bougent pas. Les tranches de l'Arrco, sans valeur de point à elles,
prenaient leur plafond aux prix : elles prennent celui de l'Arrco.

Les taux par période d'acquisition (5 % de 1999 à 2011, 10 % depuis), la
génération du 2 août 1951, la majoration pour enfants à charge avant 2012 et
le coefficient d'anticipation, qui frappe l'allocation et sa majoration,
concordent au centime. La troncature du coefficient à l'année, chez
OpenFisca, était déjà tranchée (`tests/test_oracle.py`).

L'oracle a donc trouvé vingt-trois erreurs chez OpenFisca, une à cette
famille, et quatre chez nous.

**Ce qui reste douteux.** La borne du 2 août 1951 : les deux moteurs
l'opposent, aucune des deux pages lues ne la donne, Legisocial n'assigne au
plafond que les allocations prenant effet depuis 2012 ; à lire dans l'accord
du 18 mars 2011. L'assiette de la majoration pour enfants nés ou élevés sous
un coefficient d'anticipation avant 2019 : les deux la minorent, la
circulaire n° 2020-02-DRJ l'écarte depuis (fiche
`majoration_enfants_agirc_arrco`).

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux ; les chiffres déplacés sont refaits par GitHub.

**Ce qui reste.** L'étape 2 continue, une famille par session : les périodes
assimilées, le salaire annuel moyen sur des salaires qui varient. Le
propriétaire tranche le signalement à OpenFisca, de vingt-trois erreurs
désormais.
