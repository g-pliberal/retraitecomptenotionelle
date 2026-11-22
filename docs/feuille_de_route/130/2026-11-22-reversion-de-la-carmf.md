# La réversion de la complémentaire et de l'ASV de la CARMF servie

Deuxième écart de réversion du 22 novembre 2026, après la base des libéraux (note
`2026-11-22-reversion-de-la-base-des-liberaux.md`, dont ce travail suit le commit). Le
simulateur de réversion d'info-retraite sert à la veuve d'un médecin 480 € pour 800 € de
complémentaire et 200 € pour 400 € d'ASV ; le modèle, rien (motif `non_portee`).

**Le texte, lu à l'index JORF** (à jour du 16 novembre 2026). Règlements de la CARMF,
annexe de l'arrêté du 10 juillet 2026 (JORFARTI000054435859), en vigueur le 18 juillet.
Complémentaire : le conjoint survivant « âgé d'au moins soixante-deux ans », « marié
depuis deux ans au moins », sauf « au moins un enfant né de l'union » (article 10) ;
« 60 % de la retraite complémentaire versée au médecin » (article 16), ou de celle à
laquelle il aurait eu droit (article 17) ; partage au prorata avec les divorcés non
remariés (articles 11 et 12) ; perte au remariage (article 13) ; 10 % pour trois enfants
(article 23). ASV : « réversibles à raison de 50 % », à 62 ans, deux ans de mariage
(article 6), les autres règles de la complémentaire (article 7), 10 % pour trois enfants
(article 8). Le guide de la caisse de juin 2026 dit de même : 62 ans, 60 % et 50 %.

**Avant le 18 juillet 2026**, les statuts ne sont au Journal officiel que par les
arrêtés qui les modifient (2005, 2006, 2010, 2011, 2014, 2016, 2020, 2025), qui ne disent
ni le taux ni l'âge du conjoint ; celui du 9 août 2010 parle encore du conjoint « qui, à
60 ans, n'a pu bénéficier d'une majoration ». La question de les servir sur le guide de
la caisse a été posée au propriétaire, sans réponse : sur la consigne du coordinateur,
ces décès ne sont pas servis (`portee: false`), et la fiche le déclare.

**Le test d'abord** (`tests/test_reversion.py`, « la complémentaire et l'ASV des
médecins »), vu rouge sur l'exemple du simulateur (`non_portee`) : la veuve née le
15 mars 1960 d'un médecin mort le 15 novembre 2026, 60 % × 9 600 = 5 760 € et 50 % ×
4 800 = 2 400 € par an au 1er décembre ; la survivante de 56 ans servie à 62 ans, le
1er février 2032, au mois qui suit ses 62 ans comme le dit le guide ; deux ans de mariage ou un enfant ; le remariage, et le pacte civil qui
ne retire rien ; les deux tiers devant une précédente épouse ; 10 % pour trois enfants ;
rien pour un décès du 17 juillet 2026 ; puis le médecin du formulaire, mort en août
2026, servi par le portage et figé au témoin des servis.

**La correction.** Deux fiches, `reversion_carmf` et `reversion_asv_medecins`, deux
versions chacune sur la date du décès, lues par la branche de la CARCDSF et de la
CAVAMAC (`Reversions.FICHES`, des deux côtés) ; aucun paramètre neuf, aucun code de
règle.

**L'effet, exemple chiffré.** La veuve de l'exemple officiel : 1 000 € de base, 800 €
de complémentaire et 400 € d'ASV par mois au médecin ; le modèle lui sert désormais
540 + 480 + 200 = 1 220 € par mois, comme le simulateur, au lieu de 540 € (et de rien
avant le commit de la base).

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page ; le témoin
des servis, deux cas de plus (le médecin de 2026) ; le paquet et `docs/etat.md`.

**Ce que la correction laisse, déclaré dans les fiches.** Les décès d'avant le
18 juillet 2026 ; la version choisie au décès ; la réversion calculée sur la pension
servie, quand le texte ne la minore pas de l'anticipation d'avant 2017 et porte à 15 %
la majoration du médecin parti depuis ; l'effet au mois qui suit le décès du cotisant,
non au lendemain (article 25), et au mois des 62 ans, comme le guide, non au trimestre
civil de l'article 24 ; tout enfant déclaré lève la condition de
mariage ; l'article 11, qui retire le droit du divorcé si le médecin s'est remarié,
contredit par l'article 12, que le modèle suit ; la rente temporaire du conjoint de
moins de 62 ans ; l'âge de 60 ans du simulateur, que le texte et le guide contredisent.

**La classe.** Restent non servies : les complémentaires et ASV ou PCV de la CARPIMKO,
de la CAVEC, de la CPRN, de la CAVOM, de la CAVP, de la CIPAV, de la CARPV, la CNBF, puis
les régimes spéciaux et agricoles de la note précédente.

**Vérifié** : `python -m pytest -m rapide`, `test_reversion.py`, `test_carte.py`,
`test_textes.py`, `test_justesse.py`, `test_pont.py`, `test_donnees.py`,
`test_sections_liberales.py`, `test_sections_sante.py`, les confrontations légères,
`tests/js/*.test.js`, verts. Relu sur Opus, dans un contexte neuf : une approximation vide,
la date d'effet aux 62 ans sans fondement cité, l'effet du cotisant non déclaré, corrigés.
