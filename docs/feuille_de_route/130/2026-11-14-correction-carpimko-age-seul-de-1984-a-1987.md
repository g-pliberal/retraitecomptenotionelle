# Correction de la ligne 20 de la file : la CARPIMKO minore par l'âge seul de 1984 au 4 juin 1987

Vingtième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 11 novembre 2026). Statuts approuvés par
l'arrêté du 22 février 1984 (JORFTEXT000000315359), que LEGI garde dans leur seule
rédaction du 1er janvier 1984. Article 12 (LEGIARTI000006782881) : « Le bénéfice de la
retraite peut être accordé par anticipation si l'adhérent a versé toutes les cotisations
dues. Dans ce cas, la retraite est affectée des coefficients de minoration suivants :
0,75 si la liquidation intervient à soixante ans ; 0,80 si la liquidation intervient à
soixante et un ans ; 0,85 si la liquidation intervient à soixante-deux ans ; 0,90 si la
liquidation intervient à soixante-trois ans ; 0,95 si la liquidation intervient à
soixante-quatre ans. » Article 10 (LEGIARTI000006782879), 1° : « Etre âgés de
soixante-cinq ans ou de soixante ans en cas d'inaptitude au travail, ou s'ils ont la
qualité d'ancien déporté ou interné ». Article 11 (LEGIARTI000006782880) : « Les
dispositions de la loi du 21 novembre 1973 concernant les anciens prisonniers de guerre
et les anciens combattants […] sont applicables au présent régime complémentaire. »

Le texte tranche ce que la ligne dit : aucune durée n'entre dans la minoration, et l'âge
qui l'arrête est 65 ans, pour tous. Il ne vaut que jusqu'au 4 juin 1987, jour où paraît
l'arrêté du 20 mai 1987 (JORFTEXT000000844323), dont l'index n'a que le titre.

**L'erreur.** Le modèle annulait la minoration quand la durée du régime de base était
atteinte. Une seconde, que la fiche ne voyait pas, s'est montrée au test : la table des
âges d'annulation de la décote commence à la génération 1930, et la période repliait
les générations d'avant sur 67 ans — sans la durée, 0,75 à 61 ans au lieu de 0,80, et
0,90 à 65 ans au lieu de rien. La fiche ne l'avait vérifié qu'à 60 ans, où la limite de
vingt trimestres donne par hasard le 0,75 du texte.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_carpimko_minore_par_l_age_seul_de_1984_a_juin_1987`), vu rouge (1,0 où le texte
donne 0,75), puis vert. Auxiliaires médicaux entrés à vingt ans, au double du salaire
moyen, leur durée atteinte à 60 ans.

| né le | titre | pension au | le texte | servi avant | servi depuis |
|---|---|---|---|---|---|
| 10 mars 1925 | aucun | 1er avril 1985, 60 ans | 0,75 | 114,27 € | 85,71 € |
| 10 mars 1925 | aucun | 1er avril 1986, 61 ans | 0,80 | 175,97 € | 140,77 € |
| 10 mars 1922 | aucun | 1er avril 1986, 64 ans | 0,95 | 175,97 € | 167,17 € |
| 10 mars 1922 | aucun | 1er avril 1987, 65 ans | rien | 242,00 € | 242,00 € |
| 10 mars 1925 | inapte, ou déporté | 1er avril 1985 | rien | 114,27 € | 114,27 € |
| 10 mars 1925 | cinquante-quatre mois de guerre | 1er avril 1985 | rien | 114,27 € | 114,27 € |
| 10 mars 1925 | six mois de guerre | 1er avril 1985 | 0,75 | 114,27 € | 85,71 € |
| 10 mars 1927 | aucun | 1er avril 1987, 60 ans | 0,75 | 242,00 € | 181,50 € |
| 10 mars 1930 | aucun | 1er avril 1990, 60 ans | non lu | 465,78 € | 465,78 € |

L'effet au cas posé de la ligne : 114,2748 € sans coefficient, × 0,75 = 85,71 €,
28,57 € par an de moins. Le test passe par `servi_et_refait` : le moteur Python refait
chaque cas au bit près.

**Le code.** Aucun : les données du régime. La période de 1984 de
`carpimko_complementaire.yaml` est coupée en deux. La première, de 1984 à 1986, liquide
du 1er janvier 1984 au 4 juin 1987 (`date_effet`), avec
`decote_annulee_par_la_duree: carpimko_ages_2015`, `age_taux_plein: 65` sans lecture à
la génération, `age_sans_coefficient_de_l_inapte: 60` et les deux catégories servies
sans coefficient. La seconde, de 1987 à 1995, garde la règle présumée. La fiche déclare
l'interrupteur (`code.interrupteurs`).

**Ce que la correction déplace.** Aucun témoin de simulation. Le compte des périodes qui
annoncent la réversion passe de 968 à 969, la période coupée en comptant deux : un mot
de la page des avantages, son témoin (`tests/temoins/pages.json`) et la page toute faite
`avantages/index.html`, refaite par `python scripts/construire_pages.py` parce que la
suite rapide la réclamait. Fabriqués refaits : le paquet, les témoins, cette page.

**La fiche.** `carpimko_ages_2015` : l'erreur sort des approximations et passe à
l'histoire (`effet`) ; l'approximation de l'âge entamé ne dépend plus de la durée. Les
limites ne nommaient pas cette erreur : rien à y récrire.

**La classe, pas le cas : une erreur de plus, déclarée, non corrigée.** Le repli sur
67 ans des générations d'avant 1930 tient à la table `age_annulation_decote.csv`, qui
commence en 1930, et à l'`age_taux_plein: 67` que portent les périodes d'avant 1995 de
quinze régimes en points : la CARPIMKO de 1987 à 1995, la CARMF, la CARCDSF, la CAVP,
la CAVOM, la Cipav, la CNBF, la CPRN, les ASV des médecins, des dentistes et des
sages-femmes, les trois régimes de l'IRCEC, les conjoints du bâtiment de l'Organic.
Mesuré à la CARPIMKO seule : né le 10 mars 1925, entré à trente ans, parti à 65 ans le
1er avril 1990, 0,90, 419,20 € par an au lieu de 465,78 €. Déclaré dans la fiche
`carpimko_ages_2015` (version `statuts_de_1987`) ; les quatorze autres régimes restent
à mesurer, chacun selon que sa minoration lit ou non cet âge. À inscrire à la file par
le propriétaire, s'il le veut : hors de cette ligne.

**Ce qui reste déclaré.** L'âge entamé, que l'article 12 ne tranche pas : le modèle
compte 1,25 % par trimestre, 0,775 à 60 ans et 6 mois, quand les années révolues
donneraient 0,75. Les statuts d'après l'arrêté du 20 mai 1987, non lus : une pension
présumée au 1er mai 1987, que l'article 11 reporte au 1er juillet, se liquide sous la
règle présumée. Les régimes de 1956, avant 1984. Le bloc « Reprise » de l'action 130
n'est pas récrit : la file dit où elle en est.
