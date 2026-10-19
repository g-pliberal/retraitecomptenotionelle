# Les neuf modèles du registre : neuf lignes closes, la note n° 129 de l'IPP et l'instruction de la DSS lues

**Le 19 octobre 2026 : neuf lignes réservées (9bc53de), puis closes.** Ce
sont les modèles du registre par lesquels le bloc « Reprise » disait de
commencer : OpenFisca-France-Pension (153), LexImpact, TAXIPP, Saphir,
`ir-catala`, EUROMOD et Retraites 2027 d'A. Tilloy (le net et l'impôt), les
modèles de B. Scherrer et d'A. Corral (la page Coût). Tous avaient leur
entrée au registre (`data/reference/referents.yaml`), lue le 4 octobre, le
14 pour OpenFisca, et ce qu'ils font mieux que le dépôt y a son chantier ;
leurs lignes du sas restaient ouvertes. Elles passent à `epuise`, chacune
avec une note qui dit ce que la source a donné, où c'est passé et ce qui
reste. Le code des étapes 138.3, 138.5 et 138.7 n'est pas touché : ce qu'un
modèle leur apprend est consigné ici et au registre.

- *Les têtes, par `git ls-remote`.* Huit dépôts n'ont pas bougé depuis le
  commit lu : OpenFisca-France-Pension (`1c45423`, du 13 mai 2026), TAXIPP
  (`28e2f0a`) et openfisca-france-data (`1a96eeb`), Saphir (`7bc72c9`, de
  2018), `ir-catala` (`7f5fe83`, de 2024), Scherrer (`f3c2d92`, de 2020),
  Corral (`b75b211`), Tilloy (`431dd9f`) ; EUROMOD sert encore, comme son
  dernier, le paquet J2.54+ et le logiciel 3.8.9. Seul LexImpact a avancé,
  le 7 octobre (`6e2fabf` → `eb3dd8e`) : ses paquets, et l'abattement des
  pensions du PLF pour 2027 récrit, le plafond de 3 000 € par foyer des
  retraites gardé ; ses seize cas types n'ont pas bougé (`15fe1cc`, tête
  `c7f5e45`). Les modèles n'ayant pas changé, leurs écarts restent les leurs.
- *Ce que chaque ligne demandait encore.*
  - OpenFisca : son moteur, que l'action 153 a confronté famille par famille
    (vingt-sept erreurs chez lui, quatre chez nous). Des régimes spéciaux, il
    n'a que les cotisations de la SNCF ; ses paramètres sont les barèmes de
    l'IPP, recoupés table par table le même jour. Trois lignes de ses
    témoins manquaient à son entrée (`manifeste`) : les points enfants de
    l'Arrco, le salaire annuel moyen, les périodes assimilées.
  - LexImpact : ses seize ménages de retraités, dont la confrontation a été
    coupée le 14 octobre (138.2) ; le « taux uniforme de 9,1 % » qu'ils
    devaient éprouver n'est plus celui du modèle depuis le 4 octobre.
  - TAXIPP : la note IPP n° 129 (P. Aubert, S. Duchesne et M. Tô, septembre
    2026), lue au PDF. Pour 2027, la suppression de l'abattement de 10 %
    rapporte 5,4 Md€, le gel des pensions de base 6,6 Md€ d'économie directe
    et 5,2 Md€ nets, l'alignement des taux médian et plein de la CSG sur
    9,2 %, 4,2 Md€. `docs/chiffrage_plf.md` chiffre la proposition, aucune de
    ces mesures : rien à opposer. Ses repères (l'abattement de 4 439 € et
    454 €, les quatre taux, les seuils de 2025) concordent avec le dépôt, qui
    tient ces seuils des barèmes de l'IPP : une confirmation de la même
    famille.
  - Saphir : le recoupement daté tient, ses seuils de 2017 pour une part,
    10 996 € et 14 375 €, sont ceux de `csg_pensions_seuils.csv`.
  - `ir-catala` : le jour qu'attendait sa ligne est venu, le dépôt calcule
    l'impôt du retraité depuis le 10 octobre (138.5) ; Catala en est resté
    aux montants de 2022.
  - EUROMOD, Scherrer et Corral : ce qu'ils font mieux est repris (138.2,
    138.3, 138.5, 138.7, 138.9) ou coupé (138.19) ; rien de neuf.
  - Tilloy : ses seuils de CSG de 2026 citent l'instruction de la DSS du 11
    décembre 2025, lue au PDF sur legislation.lassuranceretraite.fr.
- *L'instruction de la DSS du 11 décembre 2025*, que le dépôt n'avait pas :
  ce que la caisse applique, quand la fiche `csg_des_pensions_selon_le_revenu`
  ne citait pour 2026 que la fiche F2971. Son annexe 2 donne les seuils du
  dépôt, 13 048, 17 057 et 26 472 € pour une part, majorés de 3 484, 4 555
  et 7 066 € par demi-part, de une à trois parts, et ses bornes : le taux
  réduit au revenu « supérieur à » 13 048 €, le médian « supérieur à »
  17 057 €, le plein « égal ou supérieur à » 26 472 €. Cette dernière
  tranche, pour le dépôt, le désaccord que relevait la ligne
  `sp_f2971_csg_crds` : F2971 met 26 472 € au taux médian.
  - *Un écart neuf, d'un euro*, déclaré dans la fiche et dans
    `docs/limites/5-ante-ter-net-et-brut.md`, sans être codé :
    l'instruction arrondit à 2 278 € la majoration d'un quart de part au
    taux réduit, moitié de 4 555 €, comme L. 136-8, III ter, arrondit ses
    seuils, « la fraction d'euro égale à 0,50 étant comptée pour 1 » (lu
    dans l'index LEGI, récupéré à jour au 18 octobre) ; le dépôt garde
    2 277,50 € (`PrelevementsPension.seuil` et son jumeau), si bien qu'à
    1,25 part un revenu fiscal de 19 335 € passe au taux médian au lieu du
    réduit. Les deux autres majorations se partagent sans reste.
  - L'annexe donne aussi les seuils de la Guadeloupe, de la Martinique et de
    La Réunion (15 437 et 18 661 €), de la Guyane et de Mayotte (16 141 et
    19 546 €), que le dépôt n'applique pas, approximation déjà déclarée.
- *Pour les autres sessions.*
  - *La page Coût (138.3)* : les 6,6 Md€ du gel, sous 2,5 % d'inflation,
    disent environ 264 Md€ de pensions de base des retraités de 2026, une
    masse à opposer à celle que la page projette ; et le taux effectif des
    prélèvements, que TAXIPP tire du revenu fiscal réel et le dépôt de la
    DREES depuis le 14 octobre (`depense_nette.taux_effectifs`, 6,8 % de 2020
    à 2022), que la page ne lit pas encore. Le registre le dit (`taxipp`).
  - *Une session du modèle* : arrondir à l'euro, 0,50 compté pour 1, la
    majoration d'un quart de part, dans `remuneration.py` puis
    `moteur/js/remuneration.js`, le test d'abord, contre l'annexe 2.
  - *138.12* : le PLF pour 2027 de LexImpact, récrit le 7 octobre.
- *Ce qui contredit le dépôt* : l'arrondi du quart de part, seul. Ce qui
  attend le propriétaire : rien de neuf. Aucune saisie : le lot n'a pas de
  simulateur.
- *Le lot suivant* trouvera sept lignes `a_explorer` : F33841, après la
  session de 138.12 ; le simulateur du COR, fermé ; cinq qui attendent le
  propriétaire (le lot des simulateurs, Légifrance, Gallica).
- *Fichiers.* `data/sources_a_explorer.yaml`, le registre
  (`openfisca_france_pension`, `leximpact`, `taxipp`, `retraites_2027`), la
  fiche `csg_des_pensions_selon_le_revenu`,
  `docs/limites/5-ante-ter-net-et-brut.md`, le journal de veille et cette
  note. Aucune règle du scénario 1 n'a bougé.
