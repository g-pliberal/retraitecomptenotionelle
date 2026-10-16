# Étape 18, cinquième partie : le conjoint collaborateur des artisans et des commerçants

**La demande.** La session n° 4 de la vague ter du 16 octobre 2026 : « action
138, étape 18 : le conjoint collaborateur des artisans et des commerçants — ses
cotisations, ses points au régime de base et au RCI, dans les deux moteurs ».
Les dispenses de l'assiette minimale, la Lodeom et les classes d'avant 1973
restent à d'autres sessions. `pages.js` et la saisie n'ont pas été touchés, ni
`textes.py --inscrire`.

**Ce que faisait le dépôt.** Aucun statut : le conjoint collaborateur d'un
artisan ou d'un commerçant ne se saisissait pas (fiche `un_statut_par_annee`,
coupé le 14 octobre comme léger) ; seul `organic_conjoints_batiment`, jusqu'en
2003, nommait un conjoint.

**Ce que disent les textes**, lus le jour même dans l'index LEGI, mis à jour au
15 octobre (détail au journal de veille du jour).

- *Les options.* À sa demande, le tiers du plafond, 33,33 % ou 50 % du revenu
  du chef, ou une fraction de ce revenu déduite de l'assiette du chef
  (L. 633-10 de 2005, L. 662-1 depuis 2018, D. 633-19-2).
- *Le défaut.* Sans choix, le forfait (D. 633-19-3 jusqu'en 2019, R. 662-1).
- *La complémentaire* cotise sur le revenu retenu pour la base (D. 635-10-2).
- *L'affiliation* est obligatoire depuis le 1er juillet 2007 (loi
  n° 2005-882, art. 15, XIV) ; de 1983 à 2007, une assurance volontaire du seul
  régime de base (L. 742-6, 5° ; D. 742-26, D. 742-28).

**Ce qui est fait.** Deux statuts dans `affiliations.yaml`,
`conjoint_collaborateur_artisan` et `conjoint_collaborateur_commercant`, sans
employeur, routés comme l'artisan et le commerçant depuis 2007 (RCO des
artisans ou NRIC jusqu'en 2012, RCI depuis 2013, régime général depuis 2018) et
au seul régime de base de 1983 à 2006 ; inscrits aux sept fiches de régime.
`assiette_du_conjoint_collaborateur` (`carriere.py`), et son jumeau
`assietteDuConjointCollaborateur` (`carriere.js`), appelés par
`_ligne_annuelle` : le revenu de la ligne est l'assiette choisie ; une ligne
d'emploi sans revenu, depuis 2007, prend le tiers du plafond proratisé, qui
valide les trimestres, entre dans le salaire annuel moyen et achète les points
de la complémentaire et du compte notionnel comme un revenu. Fiche
`conjoint_collaborateur_independants`, `transcrite` : aucun exemple chiffré
publié. Le point du registre (modèle des indépendants) passe à `repris`. Quatre
tests dans `tests/test_independants.py`, dont la comparaison des deux moteurs
sur deux relevés.

**Ce que montrent les mesures** (scénario 1, relevé de 1990 à 2025, départ en
avril 2026, née en 1962).

- Conjointe d'artisan sans revenu déclaré : 4 143 € par an, dont 2 948 € au
  régime général, 360 € à la RCO des artisans, 835 € au RCI ; de commerçant,
  4 127 €. L'artisan au tiers du plafond, 7 502 € : ses années 1990-2006, que
  l'assurance volontaire non souscrite laisse vides au conjoint.
- À l'option de 6 000 € par an, 3 312 €, l'artisan au même revenu 3 974 €.

**Pour les pages**, que la session du site tient. Les deux statuts entrent
d'eux-mêmes dans le menu, famille « indépendant », « (depuis 1983) » ; un métier
saisi par niveau de salaire y cotise sur ce salaire, pris pour l'assiette
choisie. Un champ de saisie servirait : l'option (le forfait du tiers du
plafond, ou 33,33 % ou 50 % d'un revenu du chef à saisir), le forfait par
défaut. Le relevé le porte déjà : un revenu nul vaut forfait depuis 2007.

**Ce qui reste**, de ce point : un exemple chiffré de l'Urssaf ; si l'assiette
minimale s'oppose au conjoint à l'option ; la limite de cinq ans du statut
depuis 2022, hors de l'index ; la complémentaire volontaire d'avant 2007 ; le
conjoint du libéral et celui du micro-entrepreneur (D. 613-5) ; le cumul
emploi-retraite (`cumul.INDEPENDANTS`, L. 634-6), où les deux statuts
n'entrent pas, faute d'avoir lu le texte. De l'étape, une session par point :
les dispenses de l'assiette minimale ; la Lodeom ; au fac-similé, les classes
d'avant 1973.
