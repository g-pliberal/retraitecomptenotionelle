# Étape 5, neuvième partie : la prime pour l'emploi des non-salariés, et sa fin aux revenus de 2014

**La demande.** Le point 4 de « Ce qui reste » de
`2026-10-17-etape-5-adherents-d-avant-1978.md` : les revenus non salariés de
la prime pour l'emploi. Ni les décisions du propriétaire (l'effet retour dans
le solde, les trois sur le bénéfice), ni l'impôt au site, ni les règles
d'avant 1981.

**Où les textes se lisent.** L'index LEGI a les dix-huit rédactions de
l'article 200 sexies. Les archives du BOFiP servent le BOI 5 B-12-01 (n° 114
du 26 juin 2001), qui commente la première, et l'image de son exemple ; le
BOFiP, BOI-IR-RICI-310-10-30, de 2012 à 2015 ; impots.gouv.fr, la notice
2041 GS des revenus de 2014, la dernière. Le projet de loi de finances pour
2002, qui a mis les déficits au III, ne se lit pas en texte (sa police est
mal encodée) : la rédaction qui porte les montants des revenus de 2001 suffit.

**Ce que disent les textes.**

- *Les bénéfices entrent dans le revenu d'activité.* Article 200 sexies, I, B,
  3°, c à e : les bénéfices industriels et commerciaux « définis aux articles
  34 et 35 », les bénéfices agricoles, les bénéfices non commerciaux « au 1 de
  l'article 92 ». Le III, dans la première rédaction (LEGIARTI000006303351,
  revenus de 2000) : « majorés de 11,11 % » ; dès la suivante
  (LEGIARTI000006303352, qui porte les montants des revenus de 2001), jusqu'à
  la dernière : « majorés, ou diminués en cas de déficits, de 11,11 % ».
- *Le bénéfice déclaré.* Le salaire se prend « avant toute déduction de frais
  professionnels » (BOI 5 B-12-01, n° 13), et le bénéfice est majoré « afin
  d'assurer une égalité de traitement avec les salariés » (n° 16), « dans tous
  les cas, [...] avant application de l'abattement pour adhésion » (n° 17) ;
  « avant application de la majoration de 25% » de qui n'adhère pas
  (BOI-IR-RICI-310-10-30, n° 90). Au micro, après l'abattement forfaitaire.
- *Le déficit.* « il est fait masse des sommes déclarées à son nom d'une part
  en revenu et d'autre part en déficit » (BOI 5 B-12-01, n° 15) ; dès 2001,
  « les déficits déclarés sont minorés de 11,11 % » (BOFiP, n° 80), « soit :
  multiplié par (1-0.1111) », et « le déficit ainsi minoré vient en déduction
  de l'activité salariée » (notice 2041 GS).
- *L'arrondi.* « Majoration 11,11 % = + 7 777 F » pour 70 000 F (BOI 5
  B-12-01, n° 16), quand un neuvième donnerait 7 778 : le taux est 0,1111. La
  notice arrondit à l'euro le plus proche (16 000 – 7 000 × 0,8889 = 9 777,7,
  « 9 778 € ») ; l'exemple du BOFiP, les francs du BOI divisés par dix, tronque
  (7 000 €, « + 777 euros »).
- *La fin.* La dernière version du BOFiP (15 mai 2015) : ses commentaires « ne
  trouvent plus à s'appliquer à compter de l'imposition des revenus de 2015,
  compte tenu des dispositions de l'article 28 de la loi n° 2014-1655 [...] qui
  abroge l'article 200 sexies » ; « Le dispositif de la PPE reste applicable
  en 2015 pour l'imposition des revenus de 2014 ». La dernière rédaction de
  l'article finit le 30 décembre 2014. Le dépôt, sur la note de l'IPP (« À
  compter du 1er janvier 2016, la PPE est remplacée par la prime d'activité »),
  donnait la prime aux revenus de 2015.

**Ce qui est fait.**

- `impot_revenu.py` : `revenus_de_la_prime` fait le revenu d'activité de
  chaque déclarant, ses salaires et son bénéfice déclaré, majoré de 11,11 %
  (`TAUX_NON_SALARIES_DE_LA_PPE`) ou, déficit, minoré dès 2001
  (`PREMIERE_ANNEE_DEFICIT_MINORE`), à l'unité ; la prime le prend au lieu des
  seuls salaires, et l'impôt le rend (`revenus_d_activite`). Le `HORS_CHAMP`
  perd les revenus non salariés de la prime.
- La donnée : la prime est supprimée aux revenus de 2015 (`impot_revenu.yaml`,
  et `FINS` dans `scripts/fetch/ipp_impot_revenu.py`, qui l'écrit).
- Le portage : `impot-revenu.js`, de même (`revenusDeLaPrime`) ; la grille du
  portage gagne deux foyers, un salaire mêlé d'un bénéfice, puis d'un déficit,
  et vérifie que la prime y joue, en 2000 comme en 2001, et pour l'artisan
  seul. Le paquet du site prendra la fin de la prime à la fabrique de GitHub.
- Les tests : cinq exemples (`exemples_impot_revenu.yaml`) — le BOI 5 B-12-01
  (77 777 F), le BOFiP en écart connu (7 778 € au lieu de 7 777), les trois de
  la notice (le micro, 4 511 € ; le déficit, 9 778 € ; l'agriculteur, 12 600 €
  et 936 € de prime, son bénéfice de 6 840 € étant celui que la majoration
  porte aux 7 600 € qu'elle dit) — ;
  `test_la_prime_pour_l_emploi_retient_le_benefice_majore_de_11_11` et
  `test_la_prime_pour_l_emploi_finit_avec_les_revenus_de_2014`, vus rouges
  avant le code ; la grille du portage, rouge avant le JavaScript.

**Ce que montrent les mesures** (barème projeté sur les prix, convention après
impôt). Un artisan né en 1970, entré à 21 ans, parti à 64, à la moitié du
revenu moyen : la prime chaque année de 2000 à 2014, de 302 € à 846 € ; son
taux d'annuité passe de 54,25 à 52,88 %, son rendement réel ne bouge pas. Au
revenu moyen, en 2000 et 2001 seulement (103 € en 2000). Une libérale née en
1975, à la moitié : de 210 à 949 €, taux d'annuité de 35,63 à 34,82 % ; un
micro-entrepreneur né en 1980 : de 2005 à 2014, de 418 à 801 € (46,32 à
45,48 %) ; une commerçante née en 1965, à 0,6 : de 443 à 796 € (50,58 à
49,28 %) ; une artisane née en 1955, partie à 62 ans : de 364 à 886 € (62,00 à
60,34 %). La fin de la prime retire celle de 2015 : 906 € à l'artisan né en
1970, 770 € à un salarié seul de 10 000 €.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'effet retour dans le solde* : au propriétaire.
2. *Les trois décisions sur le bénéfice* : au propriétaire. La deuxième, le
   micro-entrepreneur déclaré comme un artisan au réel, fait aussi sa prime :
   le module y prend le bénéfice de sa fiche de paie, quand le code prend le
   chiffre d'affaires moins l'abattement forfaitaire, même sous le versement
   libératoire (rédaction du 1er janvier 2009, LEGIARTI000019287110).
3. *L'impôt au site*, et l'affichage de l'effet retour : à la session des
   pages.
4. *L'année de revenus de l'imposition de la majoration pour enfants*, au
   texte de la loi de finances pour 2014.
5. *Les règles d'avant 1981 sans texte lu.*
6. *Ce que la prime ne prend pas* : le temps partiel et l'activité d'une partie
   de l'année, dont les jours d'un non-salarié (`HORS_CHAMP`) ; les bénéfices
   exonérés (art. 44 sexies et suivants) ; le bénéfice de l'exploitant
   agricole, que le cycle de vie ne déclare pas, faute de fiche de paie.
