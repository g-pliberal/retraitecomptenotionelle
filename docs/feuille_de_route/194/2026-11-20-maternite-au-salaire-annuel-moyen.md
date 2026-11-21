# Action 194 : la maternité au salaire annuel moyen, le forfait écrit et confronté

Le 20 novembre 2026. Troisième usage du format de preuve de l'étape A, sur la
fiche `sam_indemnites_de_maternite`, que la carte montrait fausse.

## Ce qui est fait

**Le forfait des congés d'avant 2012** (`moteur/js/droit/liquider.js` :
`forfaitsDeMaternite`, `retenirAvecLesIndemnites`, dans `salaireDeReference`).
Pour une pension prenant effet depuis le 1er septembre 2023, la mère salariée
du régime général ou du régime agricole reçoit, au compte de l'année de chaque
naissance, une fraction du salaire médian de l'année précédente : 140/365 pour
les deux premières naissances, 228/365 ensuite, 298/365 pour des jumeaux,
403/365 au-delà (loi n° 2010-1330, article 118, VI ; R. 351-29, IV et V ;
arrêté du 29 avril 2024). La circulaire Cnav 2025/11 donne l'arrondi à l'euro
et l'écrêtement : le total borné au plafond pour les années depuis 2005
(décret n° 2005-1351, article 3), libre de le passer avant. Le forfait ne
valide aucun trimestre. Les paramètres, salaire médian compris, sont dans les
versions de la fiche, que le paquet porte.

**Quatre exemples de la circulaire** dans `tests/temoins/exemples_officiels.yaml`
(`cnav_2025_11_maternite_*`), par deux grandeurs neuves de l'oracle :
`indemnites_de_maternite_au_compte` et `salaire_retenu_avec_les_indemnites`.

**Deux grilles indépendantes**, 53 cas (`data/reference/preuves/
grille_sam_maternite_forfait_2023.yaml` et `_2025.yaml`). La session
indépendante a cherché ses textes dans les index LEGI et JORF, écrit sa
lecture avant d'ouvrir la circulaire, puis son calcul ; 17 cas sont d'elle. Le
guetteur n'a vu aucune ouverture sous le dépôt. Le décret n° 2005-1351 lui
avait échappé : signalé sans son effet, elle a refait dix-huit cas. Le moteur
rend 52 valeurs au centime. La cinquante-troisième est un écart connu : pour
une pension d'avant le 22 février 2025, le texte demande une cotisation dans
les douze mois qui précèdent la naissance, et le simulateur, qui ne connaît
que des années, lit l'année civile comme la rédaction de 2025 et la caisse.

**Une erreur voisine, trouvée par la grille** : les parents nés avant 1948
gardent le nombre d'années de leur génération (R. 173-3-2, III) ; le moteur
leur en retirait une ou deux depuis septembre 2026. Corrigé
(`nombreDAnneesRetenues`), avec son test : la borne se lit à la table du
régime général (R. 351-29-1), sans constante de plus dans le moteur.

## Ce que la carte dit

Aucune des deux parties n'est prouvée. Celle de 2023 est en écart, par le cas
des douze mois. Celle de 2025 reste approchée : la fiche déclare trois
simplifications, et la carte ne dit prouvée qu'une version sans aucune.

## Ce qui reste

- Les 125 % des indemnités d'un congé débuté depuis 2012. Le simulateur n'a
  pas leur montant ; le choix de la donnée est soumis au propriétaire. D'ici
  là le salaire saisi de l'année du congé est pris entier.
- Le forfait s'ajoute au salaire saisi de l'année de la naissance, qu'une
  carrière saisie sans relevé ne réduit pas des semaines du congé.
- L'adoption, le père après le décès de la mère, les allocations des
  salariées dispensées de travail : à la demande, non saisis.

## Ce qui bouge

Onze témoins de simulation sur 937, de +0,15 % à +1,09 % au scénario 1. Une
salariée née en 1962, à 60 % du salaire moyen, deux enfants en 1990 et 1993,
pension à 63 ans : salaire annuel moyen de 23 106 à 23 668 euros, pension de
base de 11 697 à 11 982 euros par an.
