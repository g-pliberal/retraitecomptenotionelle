# Étape 3 de la note 0009, troisième session : la carrière longue lue dans les versions de sa fiche

**Reprise, au 21 novembre 2026.** L'âge de départ anticipé pour carrière
longue se lit dans les six versions de sa fiche : la date d'effet de la
pension choisit la version, la génération sa ligne. Depuis 2023, l'âge des
générations 1963 à 1969 se calcule depuis l'âge légal de la génération, moins
deux ans et six mois, comme le décret l'écrit. La table indexée par une année
décimale et la coupe du droit contrefactuel sont parties. Aucun résultat ne
bouge. Reste à l'étape 3, dans une session neuve : la surcote. Commencer par
lire la note de l'étape suivante dans le résumé de la note de décision 0009.

Le 21 novembre 2026, la nuit, sur Opus 5.5, au choix du propriétaire, et non
sur Fable 5.2 que le dépôt règle pour le scénario 1 ; aucun point n'a demandé
de consulter Fable. Préparée sur les deux premières sessions de l'étape, non
encore publiées, et remise au coordinateur en correctif, sans envoi sur
`main`. Cinq heures environ ; le coût en jetons n'a pas été mesuré.

**Le texte** (D. 351-1-1 du code de la sécurité sociale, lu dans l'index
LEGI). Six versions bornées sur la date d'effet, qui se suivent sans trou :
rien avant le 1er janvier 2004 ; la loi de 2003 ; la loi de 2010, au
1er juillet 2011 ; le décret de 2012, au 1er novembre 2012, soixante ans
avant vingt ans ; le décret n° 2023-436, au 1er septembre 2023
(LEGIARTI000047634571) ; le décret n° 2026-345, au 1er septembre 2026
(LEGIARTI000054059621).

**La note 0009 avait raison, le brief non.** Le I du décret de 2023 écrit ses
âges en clair : cinquante-huit, soixante, soixante-deux ans. Le renvoi est au
II, 2° : pour les nés du 1er septembre 1963 au 31 décembre 1968, avant vingt
ans, « l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six mois ».
La rédaction de 2026 garde ce renvoi pour les nés de septembre à décembre 1963
et de 1966 à 1969, et écrit en clair 1964, 1965 et 1970. Exemple : né en
octobre 1963, pension du 1er octobre 2023, âge légal de 62 ans et 9 mois, d'où
60 ans et 3 mois. Né en mars 1963 parti avant seize ans : 58 ans, et non son
âge légal moins quatre ans (58 ans et 9 mois).

**Les données.** Le récupérateur (`dila_legi_parametres_retraite.py`) lit
chaque rédaction sans la fusionner : 69 lignes dans un fichier neuf,
`carriere_longue_par_version.csv`, certifiées contre le brut (69 identiques),
et trois renvois, que la fiche écrit (`contenu.renvois`, avec deux champs
additifs du contrat, `naissance` et `ligne`). La table par génération,
`carriere_longue.csv`, reste, que lisent la fabrique et la prose : elle est
désormais une vue des versions, égale à l'octet
(`vue_de_la_carriere_longue`, `tests/test_carriere_longue_versions.py`).

**Le moteur** (`moteur/js/regimes.js`). `CarriereLongue` lit la fiche du
paquet (`fiches_datees`) ; un renvoi copie la ligne générale de la version et
y met l'âge légal lu par `valeurDuRenvoi`. Partis : la clé
`carriere_longue` du paquet, l'année décimale, `CarriereLongue.avant` en
JavaScript et sa lecture du CSV en Python. Les deux couches remplacent la
fiche (`remplacer_une_version`) au lieu de la garder : au droit du
31 août 2023, la rédaction de 2012 vaut sans fin ; sous la loi de 2023 sans la
suspension, celle de 2023, dont le renvoi lit l'âge légal de 2023. Né en
juin 1967, pension d'octobre 2028 : 61 ans et 3 mois sans la suspension,
61 ans avec.

**La clause de sauvegarde de 2023** nomme la rédaction qu'elle garde
(`redactions_anterieures: {carriere_longue: decret_de_2012}`). Le moteur
continue de choisir par la date ; deux tests vérifient que la version en
vigueur la veille de `duree_acquise_avant` est bien celle que la clause nomme.
Choix prudent, réversible : faire lire au moteur la version par son nom
attendra que d'autres clauses en aient besoin.

**Les fiches sœurs** (`carriere_longue_reputes_cotises_autres`,
`taux_plein_carriere_longue`) ont des bornes qui tombent sur celles de la
carrière longue (2004, novembre 2012, septembre 2023) ; elles ne sont pas
touchées.

**Ce qui bouge.** Aucune pension : les témoins refaits sont identiques à
l'octet à ceux d'avant la session. Cliquets : couples réforme et fiche à
classer, 91 à 89 ; citations sans réponse, 432 à 431 ; une constante datée
déclarée hors du droit (`CarriereLongue.GENERATION_GENERALE`, la clé de la
ligne générale, technique).

**Reste.** Le compte de `test_journal_de_certification` est rouge depuis la
première session de l'étape (l'âge du taux plein y est compté deux fois en
`haute`) ; il n'est pas de cette zone. Le test du tableau de bord
(`test_justesse.py`) se refait sur GitHub.
