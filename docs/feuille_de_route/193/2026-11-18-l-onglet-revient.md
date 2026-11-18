# « Les caisses » revient au bandeau

Le 18 novembre 2026, le propriétaire ne trouvait plus la page : le commit
234c86d8 l'avait sortie du bandeau (`PAGES_HORS_BANDEAU`), le pied seul y
menait, parce qu'un dixième onglet faisait passer le bandeau sur deux rangées
au bureau et poussait la carte des flux de Coût hors de l'écran.

**Ce qui est fait.** L'onglet revient en tête de « Pour vérifier », et
`PAGES_HORS_BANDEAU` disparaît ; le lien du pied reste. Pour tenir sur une
rangée à 1440 points, les onglets se resserrent (`moteur/style.css`) : 8 points
de retrait au lieu de 12, 2 points entre deux pastilles au lieu de 4,
l'étiquette « Pour vérifier » plus serrée ; les pastilles gardent leurs
44 points de haut. Il reste environ 7 points de marge au bureau.

**Les tests.** `test_la_page_est_au_menu` (`test_page_caisses.py`) rétabli ;
`test_les_onglets_tiennent_sur_une_rangee_au_bureau` (`test_ecrans.py`), neuf,
vu rouge avant la retouche du style ; les listes de pages de `test_adresses`,
`test_pages_en_dossier` et `test_web_revues` reprennent l'ordre du bandeau,
et `docs/parcours_presentation.md` nomme de nouveau l'onglet.

**À savoir.** Un onglet de plus ne tiendra plus : il faudra raccourcir un
libellé ou élargir le bandeau.
