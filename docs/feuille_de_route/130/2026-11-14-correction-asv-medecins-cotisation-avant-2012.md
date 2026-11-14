# Correction de la ligne 9 de la file : la cotisation d'avant 2012 de l'ASV des médecins est celle du texte

Neuvième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 11 novembre 2026). D. 645-2 du code de la
sécurité sociale, dans ses vingt-deux rédactions, fixe « le montant de la cotisation
annuelle des bénéficiaires » : « pour les médecins, à trente fois la valeur au 1er
janvier de l'année en cause du tarif de la consultation du médecin omnipraticien » de
1985 à 1993 (LEGIARTI000006738371 et 372), cinquante-deux fois de 1994 à 1998 (374 et
375), soixante fois de 1999 à 2011 (376 à LEGIARTI000023380413). D. 645-3 fixe celle
des caisses « au double de la cotisation des bénéficiaires » (LEGIARTI000006738166, 168
et 169), sauf du 30 mars 1993 au 8 juillet 1994 : « égal à la cotisation exigible des
bénéficiaires » (167). Le médecin paie donc N consultations, les caisses 2 N : le texte
tranche ce que la ligne dit. L'article 6 du décret n° 72-968, sept rédactions
(LEGIARTI000006765951 à 957), décide de l'appel : 75 % du 1er juillet 1981 à 1992
(60 % avant), les caisses « dans des conditions identiques » ; trente et une fois en
1988, trente-trois en 1990, trente « majorée de dix fois » en 1992, à 100 % ; pour
l'exercice 1993, « 43,333 2 fois », à 100 %. Le décret n° 94-564 (article 1er, II,
JORFARTI000001585515) porte la cotisation à cinquante-deux fois « à compter du 1er
janvier 1994 » et abroge le décret n° 93-763 (article 4). Comment la caisse l'applique :
la presse médicale donne 1 380 € au secteur 1 et 4 140 € au secteur 2 en 2011, soit
soixante et cent quatre-vingts fois 23 €.

**Le test d'abord** (`tests/test_sections_sante.py`), vu rouge sur ses treize cas : ce
que le compte reçoit de l'ASV, année par année, d'une médecin née le 1er janvier 1945
et installée en 1972, rendu par le portage et refait au bit près par le moteur Python
(`droit_et_refait`).

- `test_le_medecin_verse_a_l_asv_les_consultations_du_texte_et_les_caisses_le_double` :
  les six années où la fiche ancre un tarif, posées à la main ;
- `test_l_appel_de_l_asv_suit_l_article_6_du_decret_de_1972` : le nombre de
  consultations de 1982 à 1992, que le modèle prenait à dix chaque année.

**L'effet aux cas posés**, par an, en euros de l'année : ce que verse le médecin, puis
ce que le compte notionnel reçoit avec la part des caisses.

| Année | Le texte | Médecin, avant | Médecin, après | Compte, avant | Compte, après |
|---|---|---|---|---|---|
| 1985 | 30 × 75 F × 75 % | 114,34 € | 257,26 € | 343,02 € | 771,78 € |
| 1993 | 43,3332 × 100 F | 343,01 € | 660,61 € | 686,02 € | 1 321,22 € |
| 1994 | 52 × 100 F | 348,67 € | 792,73 € | 697,35 € | 2 378,19 € |
| 1995 | 52 × 100 F | 264,27 € | 792,73 € | 792,81 € | 2 378,19 € |
| 1999 | 60 × 110 F | 335,39 € | 1 006,16 € | 1 006,17 € | 3 018,48 € |
| 2004 | 60 × 20 € | 400,00 € | 1 200,00 € | 1 200,00 € | 3 600,00 € |

Le cas de la file, 2004 : 2 400 € de plus par an au compte, comme annoncé. Aucune
pension du scénario 1 ne bouge, sur les 933 témoins : les points ne dépendent pas de la
cotisation. Le compte notionnel de dix-sept témoins de médecins monte, de 8,30 % en
médiane au scénario 2, jusqu'à 22,52 % pour le médecin de secteur 2 né en 1945.

**La correction**, dans les données seules : `regimes/asv_conventionnes.yaml`. Le
forfait de chaque période d'avant 2012 devient la cotisation du médecin : dix-huit
consultations avant 1981, 22,5 de 1981 à 1991, trente et une en 1988, trente-trois en
1990, quarante en 1992, 43,3332 en 1993, cinquante-deux de 1994 à 1998, soixante de
1999 à 2011. La période de 1985 à 1992 est coupée en six ; 1994 passe au double des
caisses. Aucune ligne de code ne change : les deux moteurs lisaient déjà le forfait et
la part des caisses.

**Ce que la correction laisse, déclaré dans la fiche** `asv_medecins_points`
(approximations).

- Le tarif de la consultation n'est pas une série du dépôt. La fiche en garde cinq
  (75 F en 1985, 100 F en 1993, 1994 et 1995, 110 F en 1999, 20 € en 2004), portés par
  les prix, et aucun n'est relu à sa source. Celui de 1999 est douteux : une question
  écrite à l'Assemblée nationale dit 115 F depuis avril 1998, soit 137,20 € de plus par
  an au compte. En 2011, le modèle donne 1 344,76 € au médecin quand le texte en veut
  1 380.
- 1993 : le décret de 1994 ne dit pas ce que les caisses doivent pour cet exercice ; la
  fiche garde l'égalité (660,61 € de plus si c'était le double).
- 1994 : les caisses à l'égalité jusqu'au 8 juillet, au double ensuite ; l'année est
  prise au double (396,37 € de moins si l'on partage par semestre).
- 1981 : l'appel passe de 60 à 75 % le 1er juillet ; l'année est prise à 75 %.
- Avant 1981 : le multiple de la consultation n'est pas lu (décret n° 71-544, article
  1er, a, hors de l'index) ; la fiche prend trente fois, appelées à 60 %.
- De 2005 à 2011 : D. 645-3 abrogé, la part des caisses tient à la convention
  médicale, non lue ; la fiche garde le double, que le recoupement de 2011 confirme.

**La classe.** Les quatre autres ASV (`asv_chirurgiens_dentistes`,
`asv_auxiliaires_medicaux`, `asv_sages_femmes`, `asv_directeurs_laboratoire`) portent,
avant leurs décrets de 2007 et de 2008, le forfait de ces décrets ramené aux prix, et
non les multiples que D. 645-2 leur fixait (treize puis 46,33 et cinquante fois la
lettre-clé C des chirurgiens-dentistes, 1,5 fois le forfait d'accouchement, quarante
fois l'index des auxiliaires). Non relues ici, et hors de la file : à relire avant de
dire s'il y a erreur.

**Ce que la correction déplace.** Le paquet, l'inventaire et le document des régimes,
dix-sept témoins de simulation, trois rendus de page (`avantages`, `methode`, le cumul
de `simuler`), refaits par `regenerer.py` dans le même commit.

**Vérifié** : `python -m pytest -m rapide`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py`, `test_simulateur.py`, `test_sections_sante.py`,
`test_sections_liberales.py`, `test_carte.py`, `test_donnees.py`, `test_prose.py`.
