# Étape 5, septième partie : le bénéfice des indépendants dans l'impôt, de l'abattement des adhérents à la majoration de l'article 158, 7

**La demande.** Le point 3 de « Ce qui reste » de
`2026-10-13-etape-5-impot-dans-les-indicateurs.md` : le bénéfice d'un
indépendant au module de l'impôt — la majoration de l'article 158, 7 du code
général des impôts et ses règles d'avant 2006, à lire —, puis ses revenus
après impôt dans les indicateurs de cycle de vie. Ni l'effet retour dans le
solde (au propriétaire), ni l'impôt au site (à la session des pages), ni les
règles d'avant 1981.

**Ce que disent les textes**, lus le 16 octobre 2026 dans l'index LEGI (les
rédactions de l'article 158 de 1979 à 2024) et, pour la seule loi que l'index
n'a pas, au BOFiP.

- *De 1978 à 2005, l'abattement des adhérents* (158, 4 bis) : 20 % du
  bénéfice au réel de l'adhérent d'un centre de gestion agréé
  (LEGIARTI000006307959, rédaction du 1er juillet 1979, « pour l'imposition
  des revenus de 1978 et de 1979 »), qui ne vise les bénéfices non
  commerciaux et les associations agréées qu'à la rédaction du 15 juillet
  1985 (LEGIARTI000006307964, revenus de 1984). Jusqu'aux revenus de 1995,
  10 % seulement au-delà d'un seuil — 150 000 F de 1978 à 1981, 165 000 F en
  1982 et 1983, puis celui des salaires des dirigeants du cinquième alinéa du
  a du 5, de 182 000 F (1984) à 469 000 F (1995) — et rien au-delà d'une
  limite, celle de l'abattement de 20 % des salaires ; la rédaction du 11
  avril 1997 (LEGIARTI000006307975, revenus de 1996) supprime la fraction à
  10 %. Chaque rédaction écrit les montants des revenus de l'année qui la
  précède. Celle de 1979 borne aussi le chiffre d'affaires de l'adhérent
  (1 725 000 et 520 000 F), bornes que la rédaction du 10 juillet 1983 supprime
  pour les revenus de 1983.
- *De 2006 à 2022, la majoration* (158, 7, 1°) : le bénéfice au réel de qui
  n'adhère pas à un organisme de gestion agréé, ni ne fait appel à un
  expert-comptable conventionné, « est multiplié par 1,25 »
  (LEGIARTI000006307988, revenus de 2006) ; puis par 1,20, 1,15 et 1,10 pour
  les revenus de 2020, 2021 et 2022 (loi n° 2020-1721, art. 34, que ni l'index
  LEGI ni celui du JORF ne portent, lu au BOFiP, BOI-IR-BASE-10-10-20-20210512,
  n° 55) ; le 1° est « abrogé à compter de l'imposition des revenus de l'année
  2023 » (LEGIARTI000042978882). Le déficit n'est pas majoré, et le revenu
  fiscal de référence porte la majoration (même BOI, n° 90 et 100) ; son
  exemple, un bénéfice de 50 000 € des revenus de 2019 retenu pour 62 500 €,
  est rejoué.

**Ce qui est fait.**

- `impot_revenu.py` : le déclarant porte un bénéfice (`benefices`, négatif
  pour un déficit), son régime (`REGIMES_DU_BENEFICE` : réel adhérent, le
  défaut, réel non adhérent, micro) et sa catégorie (BIC, BNC, BA) ;
  `benefice_retenu` en tire le bénéfice que l'impôt retient, que le revenu net
  global additionne sans frais professionnels ; l'impôt rend, par déclarant,
  le bénéfice retenu, et pour le foyer l'abattement des adhérents et la
  majoration. Une remarque dit le seuil à 10 % d'avant 1996, et le bénéfice
  d'un adhérent d'avant 1978, laissé sans abattement. Au `HORS_CHAMP` :
  l'abattement forfaitaire des régimes micro (le bénéfice s'entend après
  lui), les revenus non salariés de la prime pour l'emploi, les bornes de
  chiffre d'affaires de 1978 à 1982.
- `cycle_de_vie.py` : chaque année d'indépendant déclare son bénéfice, celui
  d'un adhérent au réel (`benefices_par_annee`, `foyer_de_l_annee`) — non
  commercial pour le libéral et l'avocat, industriel et commercial sinon —,
  et l'année où il est aussi salarié, partage son revenu imposable au prorata
  des revenus bruts. `annees_hors_impot` disparaît : les revenus après impôt
  d'un indépendant, son taux d'annuité, son remplacement après impôt se
  calculent. `ImpotDeLAnnee.benefice` dit le bénéfice déclaré. L'exploitant,
  sans fiche de paie, garde sa pension seule imposée.
- Le portage : `impot-revenu.js` et `cycle-de-vie.js`, les fonctions de
  l'impôt seules ; la grille du portage gagne quatre foyers (l'artisan et le
  libéral adhérents, le non-adhérent, un déficit au micro), que le
  JavaScript retrouve étape par étape.
- Les tests : deux dans `test_impot_revenu.py` (l'exemple du BOFiP, les
  coefficients de chaque année, le déficit, le micro ; l'abattement de 1980,
  de 1997, des BNC de 1983 et 1984, d'avant 1978), un récrit dans
  `test_cycle_de_vie.py` (l'artisan déclare son bénéfice, a ses revenus après
  impôt ; le libéral en BNC), celui du portage.

**Ce que montrent les mesures** (barème projeté sur les prix, convention
nette du dépôt). L'artisan au revenu moyen né en 1970, parti à 64 ans : son
impôt prend 5,4 % de son bénéfice en 1995, 6,8 % en 2005, 6,4 % en 2006 —
l'abattement des adhérents rejoint sans saut le barème de 2006, qui l'a
intégré —, 5,2 % en 2020 ; son taux d'annuité monte de 47,0 à 49,7 %, son
rendement réel baisse de 0,82 à 0,76 %, son taux de remplacement après impôt
est de 82,1 %. Le libéral à une fois et demie le revenu moyen : 7,8 % en 1995,
16,2 % en 2020 ; taux d'annuité de 26,1 à 30,3 %, rendement de 0,66 à 0,62 %,
remplacement après impôt de 50,6 %. Au site, le dépliant « Partir plus tôt ou
plus tard » montre désormais le taux après impôt des carrières qui ont une
année d'indépendant, où il affichait un tiret (cinq témoins de page, refaits
par GitHub) ; aucun témoin de simulation ne bouge.

**Trois décisions de la session, à confirmer par le propriétaire.**

1. *L'indépendant des cas types adhère* à un organisme de gestion agréé : sans
   majoration de 2006 à 2022, avec l'abattement de 1978 à 2005. Le non-adhérent
   se calcule (`regime="reel_non_adherent"`), aucun cas type ne l'est.
2. *Le micro-entrepreneur* se déclare comme un artisan au réel : son revenu
   imposable est celui de sa fiche de paie, et non son chiffre d'affaires
   moins l'abattement forfaitaire, ni le versement libératoire. À reprendre
   avec l'étape 12 (sa cotisation notionnelle, une autre session).
3. *Les seuils de la fraction à 10 %* sont les montants écrits par la
   rédaction de chaque année, sans l'indexation que le code prescrit quand
   une rédaction n'en écrit pas de nouveau (1988, 1992, 1993) ; la limite est
   celle de l'abattement des salaires de l'IPP, où la rédaction de 1979 dit
   « une fois et demie la limite de la dernière tranche ». Ne touche que les
   bénéfices de plus de deux à quatre fois le revenu moyen.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'effet retour dans le solde* : au propriétaire.
2. *L'impôt au site*, et l'affichage de l'effet retour : à la session des pages.
3. *L'abattement des adhérents d'avant 1978* : sa rédaction d'origine (loi de
   finances rectificative pour 1974, qui crée les centres), que l'index n'a
   pas.
4. *Les revenus non salariés de la prime pour l'emploi*, de 2000 à 2015.
5. *L'année de revenus de l'imposition de la majoration pour enfants*, au
   texte de la loi de finances pour 2014.
6. *Les règles d'avant 1981 sans texte lu.*
