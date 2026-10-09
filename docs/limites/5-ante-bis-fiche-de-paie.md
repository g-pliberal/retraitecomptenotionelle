# 5 ante bis. La fiche de paie : neuf réserves, dont trois décisives, et deux que la restitution ajoute

Le site affiche, sous les quatre pensions, ce qu'un actif touche PENDANT qu'il
cotise : coût du travail, revenu brut, revenu net, sous le droit en vigueur et
sous la proposition. C'est la seule grandeur du dépôt qui ne soit pas une
pension, et elle porte ses incertitudes propres. Trois d'entre elles — la 1, la
2 et la 5 — commandent le SIGNE du résultat, et pas seulement sa taille.

**1. L'incidence est supposée intégrale, et c'est une hypothèse.** Le coût du
travail est tenu fixe, et le salaire brut est celui qui l'épuise sous les
nouveaux taux : ce que l'employeur ne verse plus en cotisations, il le verse en
salaire. C'est la lecture que fait l'économie du travail à long terme — une
cotisation patronale est du salaire différé —, et c'est la plus favorable à une
baisse de cotisation. Rien n'oblige un employeur à rendre son économie du jour
au lendemain, et la lecture prudente, où seule la part salariale bouge, donne
environ la moitié du gain : c'est `Incidence.ASSIETTE` dans `remuneration.py`,
et la réserve 5 dit pour quels statuts c'est la seule lecture disponible.

**2. Le partage salarial/patronal du taux unique n'est pas neutre, et la
proposition ne le fixait pas.** Elle dit « 18 %, salariale et patronale
additionnées ». Le dépôt a partagé moitié-moitié jusqu'au 20 septembre 2026,
faute d'avoir mesuré ; **le programme a tranché ce jour-là, sur la mesure : la
part patronale ne bouge pas — 16,67 points, ce qu'elle vaut aujourd'hui — et la
part salariale tombe de 11,31 à 6,33.** On croirait ce choix sans effet sous
l'incidence intégrale ; il ne l'est pas, pour deux raisons distinctes : la CSG
et la CRDS sont assises sur le BRUT, que le partage déplace ; et la réduction
générale n'efface que des cotisations PATRONALES. À deux fois le SMIC, le gain net
mensuel du partage retenu vaut **+182 € dès le premier mois et +175 € une fois
le brut stabilisé** ; il valait −7 puis +81 sous le moitié-moitié, −426 puis
−141 si les 23 points étaient entièrement salariaux, +412 puis +286 s'ils
étaient entièrement patronaux. Ces quatre lectures isolent le partage : elles
neutralisent la restitution aux salaires décidée le même jour, qui s'ajoute à
toutes et que les réserves 8 et 9 de ce bloc décrivent. Le paramètre pèse donc toujours plus que la
baisse de taux elle-même, et c'est ce qui rend son arbitrage politique.

**Ce que le choix retenu achète, et ce qu'il coûte**, mesuré par
`scripts/partage_taux_unique.py` et détaillé à l'action 56 de la feuille de
route. Il achète l'immédiateté : la baisse est sur la fiche le lendemain de la
réforme, sans hypothèse d'incidence, et elle ne fuit pas, le brut ne bougeant
pas pour grossir l'assiette de la CSG et des autres branches. Il coûte le
brut : celui-ci ne monte pas, donc ni les droits qui en dépendent, ni le crédit
au compte notionnel. Le partage inverse ferait monter le brut de 2,9 %, mais
des années plus tard, amputé du quart en chemin, et de rien du tout au SMIC.
C'est la réserve la plus lourde de ce bloc, et elle n'a pas disparu en étant
tranchée : elle a changé de nature, d'un paramètre non mesuré à un arbitrage
entre le net d'aujourd'hui et le brut de demain.

**3. Le résultat au voisinage du SMIC était négatif, et ne l'est plus.** Il
l'était sous le moitié-moitié, pour une raison qui tient et qu'il faut garder
en tête : la réduction générale dégressive unique efface depuis 2026 la
totalité des cotisations patronales de son périmètre au niveau du SMIC — son
coefficient maximal, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:reduction_generale.coefficient_maximal*100)-->40,21<!--/--> %, est exactement leur somme —, si bien qu'un
salarié au SMIC ne supporte aujourd'hui que ses <!--chiffre:mesure(fiche?exemple=smic&quoi=salarie)-->11,3<!--/--> points salariaux, et que
baisser la part patronale ne lui rend rien. Le partage retenu ne touche pas à
cette part : il ramène la retenue de l'assuré à <!--chiffre:mesure(fiche?exemple=smic&quoi=salarie&systeme=proposition)-->6,33<!--/--> points, et le gain au SMIC
est de **+<!--chiffre:mesure(gain_net?exemple=smic&en=mensuel)-->93<!--/--> € par mois à coût du travail inchangé**, et davantage le premier
mois, à brut inchangé. *Corrigé le 23 septembre 2026* : la phrase disait
l'inverse, ce chiffre pour celui du premier mois.

**Deux réserves subsistent au SMIC, et elles sont de sens opposé.** Le coût du
travail y monte, à brut inchangé, de **66 € par mois** : la part patronale du
pilier capitalisé est hors du périmètre de la réduction générale, donc
l'employeur la verse pour de bon, là où la réduction absorbait ce que le
régime général lui prenait. Ce n'est pas le seul niveau où il bouge, comme
cette réserve l'écrivait jusqu'au 23 septembre 2026 : la réduction s'éteignant
à mesure que le salaire monte, la hausse diminue — 48 € à 1,2 SMIC, 30 € à 1,5,
12 € à 2 — et devient une baisse à 3 SMIC, où la réduction ne mord plus.
`scripts/partage_taux_unique.py` imprime la colonne entière. Et la lecture de long terme y est
impossible en droit, comme la réserve 4 le dit : elle supposerait un brut
inférieur au salaire minimum.

**4. L'incidence intégrale n'est pas praticable au SMIC.** Elle y supposerait un
salaire brut inférieur au salaire minimum, ce que la loi interdit. Dans la
réalité, c'est le coût du travail qui monterait. Le site pose un avertissement
quand le cas se produit ; le modèle, lui, ne recalcule pas la variante « coût du
travail en hausse », qui supposerait de décider ce que l'employeur en fait.

**5. Le gain d'un fonctionnaire et celui d'un salarié du privé ne se comparent
pas terme à terme.** Le site couvre désormais quatre profils, et le découpage
n'est pas celui des familles de statut : c'est celui de ce que l'on sait de
l'employeur. Quand il verse des taux de DROIT COMMUN — un salarié du privé, un
agent d'un régime spécial que la fermeture de 2023 a versé au régime général, un
agent public non titulaire —, le site affiche un coût du travail et le tient
fixe : l'incidence est intégrale. Quand ce qu'il verse est un taux
d'ÉQUILIBRE — <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82,28<!--/--> % du traitement pour l'État en 2026, <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=cnracl)-->37,65<!--/--> % pour la
CNRACL —, **le site n'affiche pas de coût du travail** : ce taux est fixé pour
que le compte d'affectation spéciale « Pensions » tombe juste, non parce que
l'agent acquerrait <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82<!--/--> % de son traitement en droits nouveaux, et poser dessus
l'incidence intégrale afficherait une hausse de salaire de soixante-dix points
qui n'existe pas — la dette de pensions qu'il finance, elle, reste à payer. Pour
ces statuts, le traitement n'est donc ni tenu fixe ni porté à l'incidence
intégrale : la moitié de ce que l'employeur cesse de verser remonte dans le
traitement, l'autre moitié paie la dette de pensions déjà promises
(`Incidence.PARTAGEE`, décidée le 20 septembre 2026). L'État garde en entier ce
que son taux payait de départs anticipés, que la proposition supprime
(<!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*-100?population=militaires&poste=avantages_professionnels)-->33,8<!--/--> points de la solde d'un militaire, <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*-100?population=civils&poste=avantages_professionnels)-->1,5<!--/--> point du traitement d'un civil
dans le tableau de la Cour des comptes) : seul le reste se partage, depuis le
24 septembre 2026. Le partage est une décision, non une mesure, et mettre le
gain qu'il donne en regard de celui d'un salarié du privé compare deux
hypothèses et non deux statuts. La page le dit à l'endroit où elle affiche le
chiffre. Un indépendant, lui, tient son revenu fixe, et là ce n'est pas une
hypothèse : il n'a pas d'employeur, donc rien à répercuter.

**5 bis. Quatre familles de statut ne reçoivent toujours aucune fiche de paie.**
Les salariés et exploitants agricoles — la MSA a ses propres taux hors
retraite —, l'outre-mer, dont chaque collectivité a sa caisse, les élus, dont
l'indemnité de fonction n'est pas un salaire, et qui n'a pas d'emploi. Mieux
vaut rien qu'un net faux, et c'est un test qui le tient.

**5 ter. Ce que chaque profil laisse dehors.** Pour un fonctionnaire, la
retraite additionnelle de la fonction publique (RAFP), assise sur ses PRIMES : la
fiche porte sa rémunération entière, et n'assied la retenue pour pension et la
contribution de l'État que sur son traitement, mais elle ne prélève pas sur les
primes la cotisation de la RAFP, provisionnée et hors de la comparaison, que
son net surestime d'autant. Pour un indépendant, la contribution à la formation
professionnelle (un forfait de <!--chiffre:illustration()-->0,25<!--/--> % du plafond, et non un taux, laissé dehors
par symétrie avec les taxes sur salaires du privé) et l'assiette minimale que la
loi impose aux très bas revenus, faute de savoir si l'assuré relève d'une de ses
exonérations : le net affiché en bas de barème est un plafond. Ses cotisations
de retraite sont par ailleurs celles des fiches de régime, qui alignent
l'artisan et le commerçant sur le régime général — <!--chiffre:valeur(data/reference/regimes/regime_general.yaml:periodes.debut=2023.taux_cotisation_retraite*100)-->15,45<!--/--> % sous le plafond et
<!--chiffre:illustration()-->2,51<!--/--> % déplafonnés plutôt que <!--chiffre:illustration()-->17,15<!--/--> % et <!--chiffre:illustration()-->0,72<!--/--> % : c'est la convention du modèle
entier, et la fiche de paie ne peut pas en diverger sans que le compte notionnel
et elle cessent de dire la même chose. Enfin, pour un agent public non
titulaire, le coefficient maximal de la réduction générale reste celui du décret
— un chiffre national bâti sur les taux du privé —, alors que le périmètre de
son employeur est plus étroit de la CEG et plus large de l'Ircantec ; ce qui
borne la réduction est alors la règle générale, qui interdit d'effacer plus que
ce qui est dû.

**Le 9 octobre 2026, les primes sur la fiche.** Jusque-là, la fiche prélevait la retenue
pour pension et la contribution de l'État sur les primes aussi : elle sous-estimait
le net d'un agent qui en touche, et surestimait ce que la proposition lui rend —
+36,9 % de traitement net au lieu de +33,1 % pour la fonctionnaire de l'exemple du
README, +42,2 % au lieu de +38,3 % de solde nette pour le militaire (action 138,
étape 9).

**6. Le coût du travail affiché est un plancher.** Ne sont comptées ni la taxe
d'apprentissage, ni la contribution à la formation, ni la participation à la
construction, ni le versement mobilité, ni la prévoyance et la mutuelle
d'entreprise. Aucune ne bouge d'un système à l'autre, et plusieurs dépendent de
la commune ou de la taille de l'entreprise ; les porter demanderait de choisir
un employeur type de plus. L'employeur retenu est une entreprise de cinquante
salariés et plus ; sous le seuil, le FNAL et le coefficient de la réduction
générale valent <!--chiffre:illustration()-->0,40<!--/--> point de moins. Le taux d'accidents du travail est le taux
moyen d'OpenFisca (<!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:profils.salarie_prive.postes.code=accidents_travail.employeur.0.taux*100)-->3,00<!--/--> %), au-dessus du taux net moyen national ; il ne déplace
aucun écart entre systèmes, seulement le niveau du coût affiché.

**7. Les taux sont ceux d'un millésime, appliqués aux années à venir.** Le
barème est celui en vigueur au 1er janvier 2026, reconduit tel quel jusqu'au
départ : le modèle ne prévoit pas la prochaine loi de financement. Les salaires,
le plafond et le SMIC, eux, suivent les séries projetées, si bien que le rapport
du salaire au SMIC — ce qui commande la réduction générale — reste stable. Les
taux viennent d'OpenFisca-France, transcription tierce du Journal officiel :
fiabilité `haute`, jamais `certifiee`. Quatre barèmes ont en revanche été lus à
la source dans l'index LEGI : la réduction générale (L. 241-13, version du
1er janvier 2026, LEGIARTI000053280526) et les trois barèmes d'indépendant que
la réforme de l'assiette unique de 2024 a réécrits et dont OpenFisca porte
encore la rédaction de 2018 — maladie et maternité (D. 621-1 et D. 621-2),
allocations familiales (D. 613-1) et indemnités journalières (D. 621-3). C'est
la réserve à surveiller en sens inverse : là où OpenFisca a du retard, le dépôt
ne le voit que s'il va lire.

**8. La suppression de la taxe sur les salaires ne se voit sur aucune fiche de
paie du modèle, et c'est un manque, pas un oubli.** Depuis le 20 septembre
2026, la proposition supprime les deux impôts du poste « impôts et taxes
affectés » qui sortent d'une rémunération — la taxe sur les salaires, dont
<!--chiffre:illustration()-->58,35<!--/--> % va à la branche vieillesse (L. 131-8, 1°), et le forfait social, qui
lui va en entier (L. 241-3, 1°). Or la taxe sur les salaires n'est due que par
les employeurs NON assujettis à la TVA — hôpitaux, banques, assurances,
associations —, et le profil d'employeur du dépôt est une entreprise de
cinquante salariés et plus assujettie à la TVA : la ligne n'y est pas, et sa
suppression n'y rend donc rien. Un salarié d'hôpital ou d'association verrait,
lui, son coût du travail baisser d'autant, et sous l'hypothèse d'incidence du
module cela remonterait dans son salaire. Le dépôt COMPTE cette suppression
dans l'enveloppe rendue — c'est ce que la page Coût chiffre —, mais ne la
RÉPARTIT sur personne. Le corriger demanderait un cinquième profil, celui de
l'employeur non assujetti, et le barème de la taxe, qui est progressif par
tranches. Même remarque pour le forfait social, assis sur l'intéressement et la
participation, que la fiche du dépôt ne porte pas davantage.

**9. La pension est calculée sur le revenu de la carrière, pas sur le brut que
la fiche affiche.** C'est vrai depuis toujours et cela ne pesait presque rien :
sous l'incidence intégrale, le brut d'un salarié du privé monte de quelques
pour cent, et la pension calculée sur l'ancien brut est sous-estimée d'autant.
Depuis que la contribution d'équilibre d'un employeur public est partagée, cela
pèse beaucoup plus : le traitement d'un fonctionnaire d'État monte d'un tiers
sur la fiche, et sa pension continue d'être calculée sur le traitement
d'avant. **Le dépôt sous-estime donc la pension de la proposition pour les
agents publics**, et l'écart est du même ordre que la hausse du traitement. Le
corriger demanderait de reboucler la fiche de paie sur la carrière — le brut
sous la proposition devenant l'assiette de la cotisation —, ce qui est une
boucle de point fixe et non un calcul de plus. La fiche de paie et la pension
restent, pour l'instant, deux lectures d'un même monde qui ne se parlent pas.

Rien de tout cela ne touche une pension : retiré, le modèle calcule exactement
les mêmes six scénarios.
