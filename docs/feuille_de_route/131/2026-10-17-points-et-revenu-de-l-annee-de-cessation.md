# Les points et le revenu de l'année où l'exploitant cesse, cotisée entière

Le reste que la note de l'année de cessation
(`2026-10-16-annee-de-cessation-agricole.md`) avait laissé : l'exploitant qui
cesse en cours d'année comptait ses quatre trimestres, mais ses points de
l'année restaient ceux de ses mois, et le revenu de l'année n'entrait pas dans
le revenu annuel moyen des pensions prenant effet depuis 2026.

**La règle, lue.** Code rural, L. 731-10-1 (LEGIARTI000019950453) : le chef
qui cesse en cours d'année « est tenu au paiement des cotisations [...] au
titre de l'année civile entière » ; L. 731-15 (LEGIARTI000037988682,
LEGIARTI000048683906) : elles sont calculées « sur la moyenne des revenus
professionnels [...] se rapportant aux trois années antérieures », un revenu
annuel que la cessation n'écourte pas. R. 732-70 (LEGIARTI000024113180) : la
cotisation donne droit, « pour l'année au titre de laquelle [elle est] due »,
à des points « fonction du montant des revenus professionnels », au barème de
R. 732-71 (LEGIARTI000035918339), sans prorata. D. 732-155
(LEGIARTI000034578860, LEGIARTI000049904715) : la RCO porte au compte un
« nombre annuel de points », sur « la totalité des revenus professionnels »,
quand « la cotisation de l'année considérée est acquittée dans sa totalité ».
Depuis 2026, R. 732-60, 1° (LEGIARTI000053336726), par dérogation à R. 351-1 :
les droits « sont déterminés en tenant compte des cotisations versées et
arrêtées au dernier jour de l'année civile de l'entrée en jouissance », la
révision prenant effet au mois qui suit leur encaissement. La pratique : la
réponse à la question écrite n° 96453 (JO du 26 juillet 2016, page 6956)
défend l'annualité pour ses effets « sur le calcul des droits à retraite en
fin d'activité », et laisse au conjoint survivant l'annualité des cotisations
vieillesse « afin de préserver les avantages prévus actuellement en matière de
retraite ». Aucune page de la MSA trouvée ne chiffre les points de l'année de
cessation.

**Ce qui est fait.** `Carriere.part_cotisee_ligne` (`partCotiseeLigne`) : la
part de l'année que cotise une ligne, celle de ses mois, sauf l'année de
cessation (`annee_entiere_agricole`, rendue publique), cotisée entière, dont
les lignes agricoles se partagent les douze mois au prorata des leurs.
`acquerir` la lit : le revenu de la ligne, celui de ses mois, est porté à sa
part des douze (la règle de trois `part / fraction_annee`, qui ne faisait que
réduire), sous les bornes, le repère et le plancher de l'année, et les points
de R. 732-71 ne sont plus multipliés par les mois. `salaire_de_reference` fait
entrer la ligne de l'année de cessation, seule de l'année de liquidation, dans
le revenu annuel moyen de 2026, au même revenu, au plancher et au plafond de
l'année entière. Trois tests, dans les deux moteurs : le chef à 12 000 € par
an, 7 000 € pour ses sept mois de 2024, a 30 points en 2024 (R. 732-71, 3°) et
non 23 × 7/12, et 133 points de RCO ; le collaborateur, 16 et 88, et non leurs
sept douzièmes ; deux lignes, chef puis collaborateur, se partagent l'année,
trois septièmes et quatre septièmes, au lieu d'en faire deux (46 points) ; et
l'exploitant parti le 1er août 2028 gagne 750 € de moyenne quand ses sept mois
de 2028 passent de 21 000 € à 24 500 €. Les fiches retraite_proportionnelle_msa,
assiette_minimale_agricole, pension_non_salaries_agricoles_2026 et
taux_plein_et_proratisation le disent.

**Le revenu de l'année.** Le moteur prend pour assiette d'une année son propre
revenu, quand L. 731-15 prend la moyenne des trois années d'avant. L'année de
cessation, ce revenu ne couvre que ses mois : porté à douze, il garde le
niveau de l'activité. Une carrière construite par parcours, dont la dernière
ligne n'a que le revenu de janvier, y retrouve les points de ses autres années
(30, et non les seize du plancher), et la RCO, qui rapportait déjà ce revenu à
un repère des mêmes mois, n'en change pas. Un relevé qui déclarerait pour
cette année l'assiette annuelle, et non le revenu de ses mois, serait porté
trop haut.

**Ce qui bouge.** Quinze des 874 témoins de simulation au scénario 1, tous des
exploitants ou des collaborateurs agricoles, tous en hausse : +0,75 % en
médiane, de +0,08 % (`statut_collaborateur_agricole_ne_le_20_septembre_1968`)
à +3,69 % (`statut_exploitant_agricole_1935`) ; neuf aux scénarios 3 et 5
(+2,39 % en médiane), rien aux scénarios 2, 4 et 6 ; dix-huit rendus de pages
(`resumer_temoins.py`, après `regenerer.py` ; GitHub refait les fichiers).
Trois tests changent d'attendu, sans que leur code change : le chef modeste de
2026 compte 1 320 points et non 1 291,25, les 30 points de 2026 et non 1,25 ;
le chef au triple du salaire moyen, parti en février 2026, garde son calcul
provisoire, qu'aucune moitié du plafond ne borne, devant le recalcul borné à
25 231,50 € ; le chef des plans de 2001 (`test_minima_agricoles.py`) naît en
décembre 1940 et part le 1er janvier : parti en février, il compterait les
trente points de son année de cessation, et sa moyenne passerait les seize.

**Restes, trouvés en chemin.** Les années incomplètes autres que la
cessation : l'installation en cours d'année, que L. 731-10-1 exonère (la
situation s'apprécie au 1er janvier), et le départ vers un autre métier
(R. 731-83), auxquels le moteur donne les points de leurs mois. Le chemin
`points_maximum` d'`acquerir`, celui de la RCO et peut-être de la CNAVPL, ne
proratise pas les points d'une ligne incomplète : son repère et son assiette le
sont ensemble, et le rapport rend une année au taux des mois ; deux lignes de
l'année de cessation gardent ainsi 183 points de RCO au lieu de 133. Le statut
au 1er janvier, qui fixe la cotisation de l'année entière, n'est pas lu quand
l'année de cessation change de statut. Ce que l'exploitant verse l'année où il
cesse, que le compte (`moteur/compte.py`) et les indicateurs de cycle de vie
lisent encore aux mois.

**Ce qui attend le propriétaire.** Rien.
