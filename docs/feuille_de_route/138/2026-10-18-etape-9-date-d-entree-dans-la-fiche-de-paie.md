# Étape 9, suite de la huitième partie : la date d'entrée dans la fiche de paie

**La demande.** Vague du 18 octobre 2026 : un point du bloc « Reprise » de la
huitième partie (`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`) qui ne
dépend pas du propriétaire, la date d'entrée dans la fiche de paie, que la note
« CNBF et Cipav » (`2026-10-18-etape-9-cnbf-et-cipav-dans-la-fiche-de-paie.md`,
« Trouvé en chemin ») relevait : la fiche lisait les régimes d'un nouvel
entrant. Les pages et la saisie ne sont pas touchées : la session 138.18 les
tient.

**Ce que disent les textes.** Rien de neuf à lire : les fermetures et leur
clause du grand-père sont portées par `affiliations.yaml` (`entres_avant`,
`entres_depuis`), qui cite leurs textes — la SNCF au 1er janvier 2020 (loi du
27 juin 2018), la RATP, les IEG, la CRPCEN et la Banque de France au
1er septembre 2023 (loi n° 2023-270, art. 1er), les mines au 1er septembre
2010 (décret n° 2010-975), la SEITA en 1981 (loi n° 84-603, art. 6), la
CNAVPL et la Cipav des libéraux non réglementés au 1er janvier 2019 (loi
n° 2017-1836, art. 15). Le compte et le scénario 1 les suivaient ; la fiche,
non.

**Ce qui est fait.**

- *La fiche lit les régimes de la date d'entrée* (`annee_entree`,
  `anneeEntree`) : `bloc_droit_en_vigueur`, `profil_de_la_fiche`,
  `famille_du_statut`, `contribution_equilibre`, `departs_anticipes`, puis
  `fiche_depuis_brut`, `salaire_net_depuis_brut`, `salaire_brut_depuis_net`, et
  leurs jumeaux ; sans elle, les régimes d'un nouvel entrant, comme avant. La
  carrière la donne ligne par ligne (`Carriere.date_entree`) à
  `remuneration_de_la_carriere` et aux indicateurs de cycle de vie
  (`_net_annualise`, `benefices_par_annee`).
- *Le profil suit.* L'agent de la SNCF entré avant 2020 garde après la
  fermeture le profil `agent_seul` qu'il avait en 2019 : sa retenue seule, sans
  coût du travail, et, sous la proposition, l'incidence partagée et la
  contribution de l'employeur public de son régime ; de même la RATP, les IEG,
  la CRPCEN, la Banque de France, les mines et la SEITA. Le libéral installé
  avant 2019 garde la famille des libéraux : l'indemnité journalière de 0,30 %
  sous trois plafonds (D. 621-3, I), et non celle des commerçants.
- *Les tests.* `tests/test_fiche_date_d_entree.py`, vingt-deux cas : les
  régimes de la fiche de huit statuts fermés, entrés avant la fermeture et sans
  date ; chaque ligne de retraite égale à ce que le compte reçoit, de deux ans
  avant la fermeture à 2029 ; le profil et la famille ; l'indemnité du
  libéral ; le net de l'agent de la SNCF posé à la main (40 000 € bruts,
  31 847,90 € nets : 10,85 % de retenue, 9,7 % de CSG et de CRDS sur
  98,25 %), ses deux conversions, ses nets de cycle de vie de 2019 à 2025, sa
  rémunération de la bascule au départ ; le portage, sur seize fiches.
  `test_remuneration.py` : l'agent de la SNCF entré en 2007 passe au profil
  `agent_seul`. `test_cycle_de_vie_portage.py` : un agent de la SNCF né en
  1975, entré en 1996, rouge sur le portage d'avant.

**Ce que montrent les mesures** (carrière simple au salaire moyen,
scénario 1, convention nette, taux de remplacement sur le cycle, avant et
après) :

- *La SNCF* : l'agent né en 1975, entré à 21 ans, de 0,711 à 0,713, son net
  de 2026 de 37 164 € à 36 977 € ; né en 1985, entré en 2007, de 0,754 à
  0,756, et la rémunération que la page montre passe du profil du salarié du
  privé à celui de l'agent.
- *Les régimes fermés en 2023* : l'agent de la RATP né en 1990, de 0,838 à
  0,852, son net de 2026 de 35 712 € à 34 890 € ; celui des IEG, de 0,875 à
  0,891 ; le clerc de notaire né en 1980, de 0,844 à 0,858.
- *Le mineur* né en 1970, parti à 55 ans : de 0,460 à 0,451. *Le libéral non
  réglementé* né en 1975, installé à 30 ans : de 0,507 à 0,483, son net de
  2026 de 27 605 € à 29 720 €.
- Les rendements internes ne bougent pas : leurs cotisations sont celles du
  compte. Ni les témoins, en brut, ni rien de ce que `regenerer.py` fabrique
  (`--verifier`, le 18 octobre).

**Ce qui reste**, une session par point : le minimum de pension de l'agent de
la SNCF (article 15) ; le plafond de 2027 ; la limite 5 ante ter (2), en fin
d'étape ; les décrets qu'aucune marche ne rejoint ; au propriétaire, l'ASPA de
l'article 23 et les décrets des exploitants de 1980 à 1989, au fac-similé.

**Pour la session des pages.** La saisie en net remonte au brut par la fiche
d'un nouvel entrant : `Echelle.brut_mensuel` et son sens direct (`contexte.py`,
`contexte.js`, `saisie.py`, `saisie.js`) ne connaissent que le statut. Leur
passer la date d'entrée du métier, que `salaire_brut_depuis_net`,
`salaireBrutDepuisNet` et leur sens direct prennent maintenant (`annee_entree`,
`anneeEntree`), avec son test : l'agent de la SNCF entré en 1996 qui saisit
2 653,99 € nets par mois en 2026 a 3 333,33 € bruts.
