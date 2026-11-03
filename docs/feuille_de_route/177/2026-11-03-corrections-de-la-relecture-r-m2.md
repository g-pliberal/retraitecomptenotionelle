# Étape 9, corrections : ce que la relecture R-M2 a trouvé, corrigé ou déclaré

**Le 3 novembre 2026, file M2.** La relecture indépendante
(`2026-11-03-relecture-assiette-du-rco.md`) jugeait le travail de l'assiette du
RCO et du NRCO conforme sur le fond, et relevait quatre écarts mineurs. Chaque
source a été rouverte ici, sans rien reprendre de la relecture ni du travail :
l'index LEGI à jour du 2 novembre 2026, l'index du JORF à jour du 3 ; la table
des revenus de référence de la caisse et la série de l'IPP, téléchargées le jour,
leur empreinte calculée.

## 1. Le conjoint collaborateur à l'option : corrigé (8f5447b)

Le texte est clair, lu à la version en vigueur de 2007 à 2012 :

- D. 635-10-2 (LEGIARTI000006738041, du 13 décembre 2006 au 1er janvier 2013) :
  « La cotisation d'assurance vieillesse complémentaire du conjoint
  collaborateur est calculée sur le revenu retenu, dans les limites [...], pour
  le calcul de sa cotisation d'assurance vieillesse de base. La cotisation
  d'assurance complémentaire ne fait toutefois pas l'objet de la régularisation
  à laquelle la cotisation d'assurance de base donne lieu le cas échéant. »
- D. 633-19-1 (LEGIARTI000006737949) : ses cotisations « sont définies et
  recouvrées dans les conditions prévues par la sous-section 1 de la présente
  section » ; L. 633-10 (LEGIARTI000006743702) : « Les cotisations sont définies
  conformément aux dispositions de l'article L. 131-6 ».
- L. 131-6 (LEGIARTI000006740121, de 2007 à 2009 ; LEGIARTI000020169101 et
  LEGIARTI000020675442 ensuite) : « Elles sont calculées, à titre provisionnel,
  en pourcentage du revenu professionnel de l'avant-dernière année ou des
  revenus forfaitaires. Lorsque le revenu professionnel est définitivement
  connu, les cotisations font l'objet d'une régularisation » ; en 2012,
  L. 131-6-2 (LEGIARTI000025013725), de même.
- D. 633-19-2 (LEGIARTI000006737951) : le forfait du tiers du plafond (1°), ou
  33,33 %, 50 %, un tiers ou la moitié du revenu du chef (2° à 5°) ; D. 633-19-6
  (LEGIARTI000006737955) : ses deux premières années à l'option, « sur le revenu
  retenu pour le calcul des cotisations dues par le chef d'entreprise pour ces
  années ».

À l'option, la complémentaire reste donc sur la fraction du revenu du chef de
l'avant-dernière année, que la ligne du conjoint de cette année-là porte ; au
forfait, sur le tiers du plafond de l'année. Écrit dans les deux moteurs, le
test d'abord, vu rouge (202,6538 points en 2007, le revenu de l'année, au lieu
de 168,8782) : la ligne dit si elle est au forfait (`forfait_conjoint`), et
`revenu_a_l_option` lit le revenu de deux ans plus tôt, même après une année
d'interruption, le texte ne demandant que la cotisation de base de l'année.
Les taux : D. 635-7 (7 % en 2007, LEGIARTI000006738025 ; 7,2 % de 2008 à 2012,
LEGIARTI000017869802, LEGIARTI000025091410, LEGIARTI000025629857), 7 % en 2008 et
7,1 % en 2009 par dérogation (décret n° 2007-1900, article 1er, III,
JORFARTI000017765872) ; D. 635-10, 6,5 % (LEGIARTI000006738028,
LEGIARTI000020032165). Les revenus de référence : la table « ARTISANS : RCO -
revenu de référence » de la caisse (mise à jour le 14 juin 2012, sha256
fbce0850…c0b91a9), la série de l'IPP des commerçants (sha256 35cbc1b5…e703b6a1b).

| Cas | Assiette | Taux | Référence | Points |
|---|---|---|---|---|
| conjoint d'artisan à l'option depuis 2005, 2007 | revenu de 2005, 10 000 € | 7 % | 4,145 | 168,8782 |
| 2008 | revenu de 2006, 11 000 € | 7 % | 4,207 | 183,0283 |
| 2009 | revenu de 2007, 12 000 € | 7,1 % | 4,500 | 189,3333 |
| 2010 | revenu de 2008, 13 000 € | 7,2 % | 4,692 | 199,4885 |
| 2011 | revenu de 2009, 14 000 € | 7,2 % | 4,79053 | 210,4151 |
| 2012 | revenu de 2010, 15 000 € | 7,2 % | 4,89113 | 220,8079 |
| au forfait en 2007 et 2008, puis à l'option, 2007 | 32 184 / 3 € | 7 % | 4,145 | 181,1725 |
| 2008 | 33 276 / 3 € | 7 % | 4,207 | 184,5591 |
| 2009 | revenu de 2009, 14 000 € (approché) | 7,1 % | 4,500 | 220,8889 |
| 2010 | revenu de 2010, 15 000 € (approché) | 7,2 % | 4,692 | 230,1790 |
| 2011 | revenu de 2009, 14 000 € | 7,2 % | 4,79053 | 210,4151 |
| conjoint de commerçant à l'option depuis 2005, 2007 | revenu de 2005, 10 000 € | 6,5 % | 14,648 | 44,3747 |
| 2008 | revenu de 2006, 11 000 € | 6,5 % | 14,809 | 48,2815 |
| 2009 | revenu de 2007, 12 000 € | 6,5 % | 15,3 | 50,9804 |
| 2010 | revenu de 2008, 13 000 € | 6,5 % | 15,483 | 54,5760 |

Approché, et déclaré (fiche, approximations ; `docs/limites/3-systeme-actuel.md`) :
la ligne qui manque ou est au forfait deux ans plus tôt — ses deux premières
années, le passage du forfait à l'option —, dont le revenu du chef manque au
modèle, qui garde celui de l'année ; les forfaits de D. 635-7 du conjoint qui
débute dans l'une des deux premières années de l'artisan ; le changement de
fraction ; les acomptes sur le revenu estimé de l'année. Aucun des 633 exposés
de la base de la Cnav ne traite cette complémentaire.

Ce que la règle déplace : un témoin sur 930,
`conjoint_collaborateur_au_tiers`, conjointe de commerçant au tiers du revenu du
chef depuis 1998 : 399,39 points du NRCO au lieu de 420,74 (−21,35, −5,1 %), sa
pension du scénario 1 de 16 687,32 à 16 655,95 € (−0,19 %), −0,20 % aux
scénarios 3 et 5. La grille du coût n'a pas de conjoint : l'écart au COR ne bouge
pas (+8,1703 % des complémentaires, +11,2390 % des non-salariés, mesurés ici).

## 2. Le forfait de l'artisan qui commence de 2009 à 2011 : déclaré

Les deux textes, relus : D. 635-2 (LEGIARTI000020032159) calcule la cotisation
« suivant les modalités prévues au cinquième alinéa de l'article L. 131-6 »,
provisionnelle puis régularisée (L. 131-6, LEGIARTI000020169101) ; D. 635-7
(LEGIARTI000017869802) assied l'artisan qui commence « 1° Pour l'année ou la
fraction d'année de début d'exercice, sur un revenu correspondant au tiers du
plafond [...] ; 2° Pour l'année suivante, sur un revenu correspondant à la moitié
dudit plafond ». Ni l'un ni l'autre ne dit si ce forfait se régularise ; le
modèle le tient pour définitif. Écrit dans les approximations de la fiche et
dans la limite publiée.

## 3. L'effet du forfait, et une date : écrits

Mesuré ici sur les témoins de e24714d (avant le travail) et de 144a622 (après) :
`dispense_rsa_releve_artisane` a 1 470,04 points du RCO au lieu de 1 242,32
(+18,3 %), un droit propre de 1 420,54 € au lieu de 1 340,77 € (+5,9 %) au
scénario 1, où le minimum vieillesse (ASPA), différentiel, fait sa pension, qui
ne bouge pas (12 742,23 €), et 1 554,90 € au lieu de 1 469,66 € (+5,8 %) aux
scénarios 3 et 5. Écrit dans l'effet de la fiche, et d'une phrase datée dans la
note du travail. Le revenu minimum, « 200 fois le montant horaire du salaire
minimum de croissance » (D. 633-2, LEGIARTI000006737877 à LEGIARTI000006737879),
vaut jusqu'au 5 avril 2012 : la fiche disait « jusqu'en 2011 ».

## 4. La marge de `tests/test_cout.py` : expliquée, inchangée

Le commentaire dit désormais pourquoi l'écart monte quand les pensions baissent
— il compare la croissance de la dépense de la dernière année observée à
l'horizon, et les années d'avant 2009 pèsent au départ bien plus qu'en 2070 — et
pourquoi les non-salariés bougent sans RCO : le RCO et le NRCO vont au RCI
(`integre_dans`), dans les complémentaires ; le groupe des non-salariés
(`msa_non_salaries`, `cnavpl`, `cnbf`) bouge par le calage des poids
(`_poids_par_groupe`). Ce que le code dit, la mesure ne l'isolant pas.

**Ce qui reste.** Le minimum de la cotisation jusqu'en 2015 ; le forfait du
commerçant qui commence, et celui de l'artisan de 2009 à 2011 ; un exemple de la
caisse pour le conjoint à l'option.

**Ajout du 3 novembre 2026, file M2-ter.** L'empreinte 8f5447b, au titre du
§ 1 et dans l'entrée du journal de veille de cette session, ne désigne aucun
commit du dépôt : le travail publié est cc55cdd. e24714d, au § 3, en est un,
d'avant le travail, dont le témoin des simulations est celui d'eab4dae. Le
détail, et le témoin de page que cette note ne nommait pas :
`2026-11-03-retouches-de-la-relecture-r-m2-bis.md`.
