# La carte de justesse dit à quoi chaque règle se confronte

**La demande**, le 22 novembre 2026 : « Comment avoir le meilleur de chaque
simulateur ? », puis « Oui » au chantier de confrontation permanente : pour
chaque élément du calcul, une source de référence, et un test qui échoue dès
qu'on s'en écarte sans raison écrite. Le texte tranche, jamais le simulateur.
C'est la première étape. Point d'arrêt : le propriétaire valide avant la
suite.

**Une première version, retirée.** Une table écrite à la main croisait 17
éléments du calcul et 8 familles de régimes. Elle était trop grossière (une
case verte cachait des régimes sans rien), doublait la carte de justesse, et
ses références tenaient au jugement de qui l'écrivait. Le propriétaire a
choisi, le même jour, d'améliorer l'existant plutôt que d'ajouter un doublon.

**Fait.**

- `noyau/justesse.py` : chaque partie de la carte dit sa `reference`, la
  meilleure qu'elle ait. Officielle : un témoin, une grille, un exemple même
  en écart. Modèle : un autre modèle qui lit le droit réel, que sa fiche cite
  sous `referents` (TAXIPP, modèle de coût, n'en est pas un). À confronter :
  une source repérée à rejouer, que la fiche nomme sous `a_confronter`. Aucune :
  l'absence, que la fiche dit sous `sans_reference`.
  `references_par_domaine` en tire une vue, domaine par famille, que le
  tableau de bord publie après la carte.
- `tests/test_justesse_references.py` : les quatre réponses sur des cas
  fabriqués ; puis, sur le dépôt, aucune partie dans le champ ne reste sans
  rien dire, une absence ne se dit que là où rien n'existe, et chaque source
  à confronter est au vivier ou au registre.
- 178 fiches complétées : 112 nomment leurs sources à rejouer (le simulateur
  de réversion, de carrière longue et d'âge d'Union Retraite, les pages de
  la CNIEG, du SRE, de l'ENIM, de la CRPN, de l'Ircantec, de la MSA, de
  chaque section libérale, les simulateurs de mon-entreprise, du RAFP, de la
  CNRACL et de la CARMF…) ; 66 disent n'en avoir aucune.
- Les deux champs nouveaux sont documentaires (`memoire.py`) : ils ne
  refont pas la mémoire des calculs.

**Ce que la carte dit ce jour**, sur les 253 fiches dans le champ (899
parties) : 69 fiches ont une partie au moins confirmée par une référence
officielle, 48 ne tiennent que par un autre modèle, 112 ont une source à
rejouer, 66 n'ont que le texte. Les trous : les cotisations, les points hors
de l'Agirc-Arrco et du RAFP, les périodes assimilées, la revalorisation, les
majorations pour enfants, et la réversion des régimes spéciaux et des
libéraux, qu'aucune référence officielle ne confirme encore.

**Suite**, après validation : rejouer les sources à confronter, une famille à
la fois, en grilles ou en témoins (une partie passe alors d'« à confronter »
à « officielle ») ; comparer les barèmes datés à OpenFisca et à l'IPP ; trier
les écarts du registre.
