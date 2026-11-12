# Étape 6 : la retraite progressive au régime complémentaire des indépendants, en 2027

**Reprise, au 12 novembre 2026.** La lecture est faite, la règle est écrite,
mais elle n'est pas publiée : il y manque une décision du propriétaire. Au
1er janvier 2027, le règlement du régime complémentaire des indépendants
plafonne l'abattement de la fraction servie en retraite progressive au taux de
« la deuxième ligne » du tableau de son annexe 2. Aucun texte lu ne dit si
c'est la ligne des vingt trimestres, 22 %, ou celle des dix-neuf, 20,75 %. La
règle est écrite sur 22 %, et la ligne est un paramètre de la fiche. Elle et
ses tests, verts dans les deux moteurs, sont gardés dans un fichier à rejouer.
Elle ne déplace aucun témoin. Ce qui reste : la réponse du propriétaire ;
rejouer le fichier ; régler le paramètre ; refaire le paquet et les témoins.
L'autre article, sur le complément de points, ne touche rien de ce que le
modèle sert. Détail plus bas.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot des autres régimes l'a lu
(`184/2026-11-12-etape-6-autres-regimes.md`, « Ce qui change une règle ») :
règlement du régime complémentaire des indépendants (arrêté du 9 février
2012), article 12 (LEGIARTI000054908824), date d'effet 1er janvier 2027
(arrêtés du 6 octobre 2025 et du 21 septembre 2026) ; article 28
(LEGIARTI000054908892), même date. Le lot du code de la sécurité sociale a
relevé dans l'article 12 l'âge du taux plein « au sens du 1° ou, du 1° bis ou
du 6° de l'article L. 351-8 ». Fiche : `abattement_rci`.

**Ce qu'il y a à faire.**

1. Lire les articles 12 et 28 et l'annexe 2. L'annexe se lit dans l'arrêté au
   Journal officiel, par l'index du JORF, si LEGI la rend à plat ; si elle
   reste illisible, le dire au propriétaire plutôt que de deviner la ligne.

2. Le test, vu rouge : une fraction de retraite progressive en 2027, sous le
   plafond du texte.

3. La règle, datée du 1er janvier 2027, dans le modèle et son portage ; le
   complément de points de l'article 28, s'il touche ce que le modèle sert.

4. La fiche `abattement_rci`, et celle qui porte le complément.

**Fini quand** la fraction servie en 2027 est celle du règlement, ou que la
ligne de l'annexe est une question posée au propriétaire.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.

## Ce qui a été fait, le 12 novembre 2026

**Ce que la lecture a établi.** L'article 12 du règlement, dans sa rédaction
du 1er janvier 2027 (LEGIARTI000054908824, arrêtés du 6 octobre 2025 et du
21 septembre 2026), ajoute un alinéa : « Lorsque l'assuré bénéficie d'une
fraction de pension au titre de la retraite progressive par application de
l'article 28 du présent régime, le coefficient d'abattement ne peut excéder le
taux prévu à la deuxième ligne du tableau de l'annexe 2. » L'arrêté du
21 septembre 2026 (JORFTEXT000054888294, article 1er, 5° c) l'insère mot pour
mot, et entre en vigueur le 1er janvier 2027 (article 2). Il ne modifie pas
l'annexe 2 (LEGIARTI000054907665), qui porte depuis 2013 le même tableau :
vingt lignes, de « 20 | 22,00 % » à « 01 | 1,00 % », sous deux titres de
colonnes, « TRIMESTRES MANQUANTS » et « COEFFICIENT DE DÉCOTE ».

**Quelle ligne est la deuxième : aucun texte lu ne le dit.** L'index LEGI rend
le tableau à plat. Légifrance l'a servi à l'agent de lecture, en texte seul :
le titre, les deux titres de colonnes, puis les lignes dans l'ordre, sans la
structure du tableau. Le navigateur de la session y est refusé, et la DILA a
retiré de son serveur les incréments de septembre 2026, qui la portaient. Ni
l'arrêté au Journal officiel, ni la page de l'Assurance retraite sur la
retraite complémentaire des indépendants, ni une recherche sur le web ne
donnent le taux que la caisse retient. Deux lectures restent donc :

- sous la ligne des titres, la deuxième ligne est « 20 | 22,00 % » : le
  coefficient de la fraction ne descend pas sous 0,78 ;
- à ne compter que les lignes de taux, c'est « 19 | 20,75 % » : il ne descend
  pas sous 0,7925.

La première seule donne un sens au plafond. Le tableau s'arrête à vingt
trimestres ; au départ, vingt trimestres au plus séparent l'âge légal de l'âge
du taux plein, et le tableau suffit. La retraite progressive, ouverte à
soixante ans depuis le 1er septembre 2025, est seule à en compter davantage :
vingt-huit à soixante ans. L'alinéa dit alors quel taux servir là où le tableau
n'a plus de ligne : le dernier, 22 %. Le régime de base faisait de même de
2014 à 2023, où la décote de la pension provisoire ne dépassait pas 25 %,
vingt trimestres (R. 351-41, D. 634-19).

**L'article 28** (LEGIARTI000054908892), à la même date, ajoute : « L'assuré
ne peut prétendre au bénéfice du dispositif de complément différentiel de
points mentionné aux articles 9-1 à 9-6 du présent règlement, lorsqu'il
demande à bénéficier de la fraction de pension au titre de la retraite
progressive. » Ce complément naît lui-même le 1er janvier 2027 (article 9-1,
LEGIARTI000054908851) : des points donnés au retraité parti au taux plein,
toutes ses pensions liquidées. Le modèle ne le sert à personne ; l'alinéa ne
touche donc rien de ce qu'il calcule. Aucune fiche ne porte ce complément.
L'article 28, que nulle fiche ne citait, est rattaché à `abattement_rci`,
rédaction par rédaction : c'est lui qui fait servir au régime « la même
fraction » que la base, ce que le modèle fait.

**Ce que le moteur faisait.** Il abat les points du régime par deux
décomptes, la durée et l'âge, et retient le plus favorable. Jusqu'à vingt
trimestres, c'est le tableau de l'annexe 2. Au-delà de vingt trimestres aux
deux décomptes, il prolonge la table des âges de l'Agirc-Arrco, 1,75 % par
trimestre, que le règlement n'écrit pas : 36 % d'abattement à vingt-huit
trimestres, un coefficient de 0,64. Le bloc « Reprise » d'avant disait
« jusqu'à 22 % » : c'était vrai au départ, non en retraite progressive.

**La règle écrite.** La fiche `abattement_rci` prend trois versions, que la
date d'effet partage : avant 2013, supposée ; le règlement de 2013 ; le
plafond de 2027. Chacune porte les régimes que le règlement abat et le
paramètre `trimestres_de_la_ligne_du_plafond_en_retraite_progressive`, nul
avant 2027, 20 ensuite. La fiche entre aux fiches que le paquet porte. Le
moteur lit le paramètre (`plafondEnRetraiteProgressive`,
`moteur/js/droit/liquider.js`, et son jumeau) quand la demande est une
retraite progressive, et ne laisse pas le coefficient sous celui de la ligne.
La pension complète, liquidée au départ, garde le tableau entier. Aucune
constante de plus dans le code ; rien de ce que l'action 191 a posé n'est
défait, et les lignes que changent les correctifs des étapes 2 et 3 ne sont
pas touchées.

**Le test d'abord.** Un artisan né le 15 janvier 1967, entré à vingt-deux ans
et demi, demande le 1er février 2027 une retraite progressive à 60 % : cent
cinquante trimestres pour cent soixante-douze, vingt-huit trimestres avant
soixante-sept ans. Coefficient attendu, posé depuis le texte : 1 − 0,22 =
0,78, sur les points du régime et sur ceux de l'ancien régime des artisans.
Vu rouge dans les deux moteurs, à 0,64 ; vert ensuite. Un second test dit que
la fiche ne plafonne rien avant 2027, que le même artisan né en 1966 garde son
coefficient, et que le paramètre ôté rend l'ancien calcul.

**Les chiffres, pour cet artisan.** Avant la règle : 1 941,83 € au régime
complémentaire, 2 215,93 € à l'ancien régime des artisans, une pension
provisoire de 18 558,49 € et une fraction servie de 7 423,40 € par an. Sous
22 % : 2 366,60 € et 2 700,67 €, 19 468,00 € et 7 787,20 €, soit 363,80 € de
plus par an. Sous 20,75 %, calcul posé à la main : 19 549,21 € et 7 819,68 €,
32,48 € de plus encore.

**Ce que la règle déplace.** Rien avant 2027. Aucun des 934 témoins de
simulation ne bouge, ni aucun des 85 rendus de page ; un témoin de plus,
`progressive_artisan_2027`. La suite rapide est verte, comme les essais du
portage, les confrontations des deux moteurs et les tests du coût
(`test_cout.py`, `test_cout_age_depart.py`, `test_controle_drees_panorama.py`,
`test_solde_fusion.py`).

**Pourquoi elle n'est pas sur `main`.** La ligne du tableau est une décision
du propriétaire, que la consigne de l'étape lui réserve. La règle et ses tests
sont dans `docs/mesures/192/2026-11-12-etape-6-la-regle-et-ses-tests.txt`, à
rejouer par `git apply`. Sur `main` : la lecture, dans les sources de la
fiche, l'écart du moteur au-delà de vingt trimestres, dans ses approximations,
cette note et l'entrée du journal de veille.

**Au propriétaire.**

1. La ligne : 22 % ou 20,75 % ? Recommandation : 22 %, pour la raison dite
   plus haut. Si c'est 20,75 %, le paramètre de la fiche passe de 20 à 19, et
   la valeur du test de 0,78 à 0,7925.
2. Avant 2027, au-delà de vingt trimestres : le modèle sert 0,64 là où le
   règlement n'écrit rien. La fiche le déclare, et ce que la caisse servait
   n'a pas été trouvé. Recommandation : laisser l'écart déclaré, et le lever
   quand une circulaire ou la caisse le dira.
3. Le complément différentiel de points du régime, créé au 1er janvier 2027
   (articles 9-1 à 9-6), n'a pas de fiche. Recommandation : une étape à lui,
   qui le lit et dit s'il se modélise.
