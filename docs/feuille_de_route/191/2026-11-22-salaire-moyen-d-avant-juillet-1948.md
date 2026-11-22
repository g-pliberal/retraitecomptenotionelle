# Le salaire moyen des pensions d'avant juillet 1948, au décret n° 45-0179 d'origine

Le 22 novembre 2026, sur Opus 5.5, d'après les écarts que le lot 1 des
fac-similés du Journal officiel a relevés (décret n° 45-0179 du 29 décembre
1945, chapitre VII, transcrit dans
`data/reference/textes/apportes/decret_1945_12_29_assurances_sociales.md`) ;
relu avant l'envoi sur Opus 5.5, Fable 5.2 étant à sa limite d'usage jusqu'au
25 novembre, et repris d'après cette relecture. Au titre de la règle du
propriétaire : ce qui s'écarte du texte se corrige, puis se dit.

**Deux corrections** à la version `dix_dernieres_annees_avant_soixante_ans`
de `salaire_annuel_moyen` (date d'effet avant le 1er juillet 1948) :

| Le modèle | Le texte |
|---|---|
| les années de deux trimestres assimilés ou plus sortent de la moyenne | « les périodes visées à l'article 70 de ladite ordonnance entrent en compte » (art. 74, § 3, d'origine) |
| seules les années d'avant soixante ans | « A défaut de justification de quarante trimestres d'assurance avant l'âge de soixante ans », les trimestres d'après, « jusqu'à concurrence de ce nombre et dans leur ordre chronologique » (§ 4) |

**L'exclusion des années assimilées est de 1949.** La circulaire n° 143 SS du
29 juin 1949 la tient du « paragraphe 7 de l'article 74 du R.A.P. modifié » :
la rédaction du décret n° 49-328 du 7 mars 1949 (JO du 12 mars 1949,
JORFTEXT000000848692, dont l'index de la DILA n'a que la notice, qui nomme
l'article 74), applicable aux entrées en jouissance « au 1er juillet 1948 ou à
une date postérieure ». Le § 7 d'origine porte sur la rente capitalisée avant
1941. Avant 1948, la caisse a suivi deux pratiques, lues dans la base de
législation de la Cnav : la circulaire n° 151 du 5 août 1946 donne aux
périodes assimilées un « salaire fictif » (arrêté du 14 mai 1946, non lu) ;
la circulaire n° 246 du 25 août 1947 calcule « sur la base des salaires
réels », les périodes sans cotisation « neutralisées ». Le modèle neutralise :
une année compte son salaire réel sur ses trimestres cotisés.

**Le code.** Un paramètre de version, `apres_soixante_ans_a_defaut`, lu par
`moyenneSelonLaRegle` (`moteur/js/droit/liquider.js`). Le défaut se mesure
aux trimestres d'avant soixante ans, que compte `trimestresAvantSoixanteAns`,
ceux des assurances sociales de 1930 à 1944 compris : leurs salaires n'entrent
pas dans la moyenne du modèle, mais leurs trimestres justifient les quarante.
Les années d'après soixante ans, l'année des soixante ans d'abord, s'ajoutent
dans l'ordre jusqu'à couvrir les trimestres qui manquent ; une année sans
trimestre est sautée. La première version, relue, comptait les années au
compte du régime : le complément jouait pour presque toutes les pensions
d'avant 1948, puisque les années d'avant 1945 n'y sont pas. Le jumeau Python
n'existe plus. Écarts déclarés dans la fiche : le salaire fictif d'avant
août 1947 ; le complément par années civiles entières ; le dénominateur
« toujours 10 » de la circulaire n° 151, non suivi.

**Ce qui bouge.** Aucun des 935 témoins. Né en 1886, salarié de 1945 à 1947,
parti à 62 ans au début de 1948 : quatre trimestres avant soixante ans, 1946
et 1947 viennent compléter ; salaire de référence de 213,18 € au lieu de
204,32 €. Le même avec neuf années aux assurances sociales, de 1936 à 1944 :
quarante trimestres avant soixante ans, rien ne s'ajoute.

**Les tests**, vus rouges : cinq de `tests/test_salaire_annuel_moyen.py`,
posés à la main depuis le texte (le complément, son déclenchement en
trimestres, les années assimilées, la fiche, deux pensions du début de 1948) ;
leur portage dans `tests/js/moteur.test.js`.

**Aussi.** La note des fiches `arrco` et `arrco_tranche_2` disait l'accord du
8 décembre 1961 « hors JORF » : il est publié avec son arrêté d'agrément au
JO du 31 mars 1962. Phrase récrite, aucun chiffre ne bouge.

**Reste.** Le salaire de 1930 à 1944 n'entre pas dans le salaire moyen du
régime général : un assuré parti avant 1955 dont les dix dernières années
remontent avant 1945 a un salaire de référence nul ou presque (déjà dit par
`2026-11-20-annees-des-assurances-sociales.md`) ; la circulaire n° 151 y
revalorise les cotisations de 1930 à 1944 par 3, 2 et 1. À lire : l'arrêté du
14 mai 1946, l'arrêté du 9 septembre 1946 et la circulaire n° 171 du 30 mai
1947 (périodes de guerre), et le décret n° 49-328, dont l'article 74 dit si le
complément d'après soixante ans vaut aussi depuis juillet 1948. Signalés, non
touchés : la table de l'Arrco d'avant 1965 (étape 4 de la note 0009, en
pause), l'affiliation à l'Arrco avant 21 ans (règlements des institutions non
lus), et la note de la fiche `arrco`, qui dit le taux de la tranche 1
« celui de tous les salariés » quand l'accord de 1961 (annexe I, art. 4)
exclut les cadres du régime de 1947.
