# La table des références : à quoi chaque élément du calcul se confronte

**La demande**, le 22 novembre 2026 : « Comment avoir le meilleur de chaque
simulateur ? », puis « Oui » au chantier de confrontation permanente : pour
chaque élément du calcul, une source de référence, et un test qui échoue dès
qu'on s'en écarte sans raison écrite. Le texte tranche, jamais le simulateur.
Cette note est la première étape : la table. Point d'arrêt : le propriétaire
la valide avant la suite.

**Fait.**

- `data/reference/references_par_element.yaml` : 17 éléments du calcul (âge,
  durée, périodes assimilées, départ anticipé, salaire de référence et
  plafond de la pension, taux et proratisation, décote et surcote, points,
  minima, enfants, réversion, cumul, coordination, cotisations et plafond de
  la sécurité sociale, prélèvements sur la pension, revalorisation, date
  d'effet et paramètres), chacun sur les 8 familles de régimes de
  l'inventaire : 136 cases. Chaque fiche de la carte (280) est rangée dans un
  seul élément, par son domaine ou nommément pour les 65 qui n'en ont pas.
- Chaque case dit ses références (exemple officiel, grille posée sans le
  code, simulateur de caisse ou page officielle du vivier, autre modèle du
  registre qui confronte le droit réel), ou son absence en une phrase, ou
  qu'elle est sans objet ; `a_chercher` nomme la référence à trouver quand le
  plan de couverture du 21 novembre la connaît.
- `scripts/table_des_references.py` relève ce que le dépôt sait de chaque
  case et imprime la table (`--trous` : les absences).
  `tests/test_table_des_references.py` (8 tests, rapides) tient la table
  complète et d'accord avec ce relevé : un exemple officiel ou une grille qui
  entre dans une case la fait citer, un modèle qu'une fiche cite y est.

**Ce que la table dit ce jour.** 49 cases ont une référence officielle, 30 ne
tiennent que par d'autres modèles, 38 n'ont rien que le texte (119 fiches),
19 sont sans objet. Les trous principaux : la coordination entre régimes, sur
les huit familles ; les périodes assimilées hors régime général ; les
paramètres annuels et la date d'effet hors régime général ; la réversion du
RAFP ; les points du régime général (la retraite des cultes, les points
gratuits) et des agricoles ; le cumul des complémentaires et des régimes
spéciaux. Les régimes spéciaux, les libéraux et les agricoles n'ont le plus
souvent que des modèles : TRAJECTOiRE et OpenFisca, qui lisent le même texte
que nous.

**Les choix.** La famille d'un exemple est celle de la pension de base de son
affiliation, sauf pour les grandeurs des complémentaires (points, coefficients,
cotisation de l'Agirc-Arrco, prestation du RAFP), que l'élément force. Un
modèle de coût qu'une fiche cite (TAXIPP) n'est pas une référence du calcul.
Le texte d'une case est celui de ses fiches : la table ne le répète pas.

**Suite**, après validation : comparer les barèmes datés à OpenFisca et à
l'IPP ; rejouer les simulateurs des caisses comme témoins ; trier les écarts
du registre ; Catala ; les agrégats de la DREES et de l'INSEE.
