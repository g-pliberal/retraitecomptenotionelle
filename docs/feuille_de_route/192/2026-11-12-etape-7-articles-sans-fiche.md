# Étape 7 : les articles qu'aucune fiche ne cite, lus et confrontés au modèle

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su**, des notes des lots (`184/2026-11-12-etape-6-…`).

- Décret n° 2004-1056, ouvriers de l'État, article 12 : trois rédactions de
  2026 — la majoration des sapeurs-pompiers volontaires (8°, pensions à
  compter du 1er juillet 2026), un trimestre de bonification par enfant né
  depuis 2004 pour l'ouvrière (2° bis, décret n° 2026-699, à compter du 1er
  septembre 2026), la majoration des élus locaux (9°, à compter du 1er janvier
  2027). Lot des autres régimes, « Vu en passant ».

- Même décret, article 7, fiche `limite_age_ouvriers_etat` : du 1er septembre
  2023 au 2 janvier 2025, les services faits après la limite d'âge au titre du
  maintien ou de la prolongation comptaient-ils ? Lot des autres régimes,
  « Une question ouverte ».

- Article L. 351-3, 1°, du code de la sécurité sociale (LEGIARTI000051288449,
  1er novembre 2026, loi n° 2025-199, article 90) : la rente d'accident du
  travail « pour une incapacité permanente professionnelle ». Aucune fiche ne
  lit le 1°.

- Article R. 351-37, rédaction du 1er novembre 2026, qu'aucune fiche ne cite.

- Article R. 653-2, avocats : il renvoie aux III et IV de l'article 20 de la
  loi n° 2010-1330, abrogés pour les pensions de 2026.

- La fiche `sam_parents_24_23` ne cite pas l'article R. 173-3-2 par son
  identifiant (LEGIARTI000054589934), que le moteur applique déjà.

**Ce qu'il y a à faire.** Pour chaque point : lire la rédaction dans l'index
(`dila_cherche.py legi --num <article> --le <date>`), dire si le modèle sert
ce qu'elle règle, et lui donner sa place — citée par la fiche qui la porte, ou
une fiche nouvelle si la règle n'en a pas. Ce qui change un calcul ne se porte
pas au modèle ici : la fiche le déclare, la note le liste, et le propriétaire
décide de l'étape qui l'écrira. Cette étape se mène sur Fable 5.2, comme toute
lecture du scénario 1, et suit `docs/veille_droit.md`.

**Fini quand** chaque point de la liste a sa fiche et son statut, et que ce
qui change un calcul est porté au propriétaire en une liste.

**Ce qui a été fait, le 12 novembre 2026.** L'étape est close : chaque point a
sa fiche et son statut, lu dans les index LEGI et JORF du dépôt, à jour au
11 novembre 2026, sur Fable 5.2. Ni `src/` ni `moteur/` ne sont touchés, et
aucune règle n'est écrite. Deux points changent un calcul ou pourraient le
changer : ils sont à la liste du propriétaire, plus bas.

| Point | Ce que le texte dit | Ce que le modèle sert | Sa fiche, son statut |
|---|---|---|---|
| Décret n° 2004-1056, article 12, 8° (LEGIARTI000053390016, pensions à compter du 1er juillet 2026) | la majoration des sapeurs-pompiers volontaires s'ajoute aux services de l'ouvrier | rien, dans aucun régime | `majoration_duree_sapeurs_pompiers_volontaires`, qui la citait déjà et nomme le régime ; `pas_encore_modelisee` |
| Même article, 2° bis (LEGIARTI000054590048), et article 17, I (LEGIARTI000054590077), pensions à compter du 1er septembre 2026 | des deux trimestres de l'enfant né depuis 2004, l'un est une bonification | la règle même : le régime déclare les bonifications de la fonction publique | `enfants_fonction_publique`, version `l12bter`, qui cite désormais les deux rédactions |
| Même article, 9° (LEGIARTI000054978200, pensions à compter du 1er janvier 2027) | la majoration des élus locaux | rien, dans aucun régime | `majoration_duree_elus_locaux`, qui la citait déjà ; `pas_encore_modelisee` |
| Même décret, article 7 | voir la liste | les services du maintien comptent dès le 1er septembre 2023 | `limite_age_ouvriers_etat`, question récrite avec ce que les textes établissent |
| L. 351-3, 1° (LEGIARTI000051288449) et R. 351-12, 5° (LEGIARTI000054425288), 1er novembre 2026 | la rente compte pour une incapacité permanente « professionnelle » d'au moins 66 %, pour les victimes consolidées depuis cette date | quatre trimestres par année déclarée « accident du travail », sans demander ni la rente ni son taux | fiche neuve, `accident_du_travail_periodes_assimilees`, `approchee` |
| R. 351-37, 1er novembre 2026 (LEGIARTI000054060160) | seul le III change : la procédure du départ pour incapacité permanente suit la réforme de la rente | ce départ n'est pas modélisé ; la date d'effet, I et II, est inchangée | `inaptitude_invalidite_penibilite_amiante`, à rattacher ; `date_effet_mois_suivant` la citait déjà, contrairement à ce que disait le bilan |
| R. 653-2, avocats (LEGIARTI000047633285) | le III abrogé de l'article 20 de la loi n° 2010-1330, le parent d'un enfant handicapé, est passé au 6° de L. 351-8, que l'article ne nomme pas ; R. 643-7, pour les libéraux, a le même renvoi mort | ni les avocats ni les libéraux n'ont cet âge de soixante-cinq ans : approximation déjà déclarée | `taux_plein_a_soixante_cinq_ans`, sans effet, motif précisé |
| R. 173-3-2, 1er août 2026 (LEGIARTI000054589934) | voir la liste | une ou deux années de moins à toute carrière qui détient des trimestres pour enfants | `sam_parents_24_23`, qui la cite par son identifiant et passe de `transcrite` à `approchee` |

Le cliquet des textes descend de deux, à 9 234 : les articles 12 et 17 du
décret des ouvriers de l'État, rattachés. La carte gagne une fiche.

**La liste pour le propriétaire : ce qui change un calcul.**

1. **Les meilleures années des parents ne valent pas pour la mère dont la
   fonction publique porte les enfants.** Article R. 173-3-2, I, du code de la
   sécurité sociale, rédaction du 1er août 2026 (décret n° 2026-699), pensions
   prenant effet à compter du 1er septembre 2026 : le nombre d'années est
   réduit « pour les bénéficiaires de majoration ou de bonification prévues
   aux articles L. 351-4, L. 351-4-1 et L. 351-5 ou mentionnées à l'article
   R. 351-2-1, à l'exception des bénéficiaires des bonifications mentionnées
   aux 1°, 11° et 12° de cet article » — l'État, les ouvriers de l'État, la
   CNRACL. Le modèle retire une ou deux années dès que la carrière détient des
   trimestres pour enfants, quel que soit le régime qui les porte. Rejoué : née
   en 1962, seize ans fonctionnaire puis vingt-sept ans salariée, deux enfants
   nés en service, partie en février 2027, sa pension du régime général est de
   16 052 euros par an, contre 15 872 sur vingt-cinq années, soit 1,1 % de
   trop ; de même pour l'ouvrière de l'État et l'agente de la CNRACL. Reste à
   lire, dans la circulaire qui n'est pas parue, si l'exception écarte la
   personne ou seulement ses enfants que la fonction publique porte. La Cnav
   n'appliquera ce calcul que « courant 2027 ».

2. **Les services du maintien jusqu'à soixante-dix ans de l'ouvrier de
   l'État, avant le 2 janvier 2025 : le texte ne les comptait pas.** Décret
   n° 2004-1056, article 7 : jusqu'au 1er janvier 2025, les services d'après la
   limite d'âge ne comptent que « dans les conditions prévues par l'article
   1er-1 de la loi du 13 septembre 1984 », la prolongation pour carrière
   incomplète ; le décret n° 2024-1281, article 4, 1°, y met L. 556-1, L. 556-5
   et L. 556-7 au 2 janvier 2025, sans clause d'application. La prolongation
   de l'insalubre comptait déjà, par L. 556-7 lui-même. Le maintien, non : le
   fonctionnaire le tient de L. 10 du code des pensions, que le décret des
   ouvriers ne reprend pas. Le modèle compte ces services dès le 1er septembre
   2023. Rejoué : né en 1957, carrière complète, parti à soixante-sept ans et
   demi en août 2024, 45 674 euros par an, contre 44 723 à soixante-sept ans.
   Seules sont touchées les pensions prenant effet du 1er septembre 2023 au
   1er janvier 2025, pour seize mois de services au plus. Ce que la caisse en
   a fait n'est pas publié : c'est à lui demander avant de rien changer.

Deux manques déjà déclarés, que cette lecture confirme sans rien y ajouter :
le modèle ne sert à l'ouvrier de l'État, comme à personne, ni la majoration
des sapeurs-pompiers volontaires (pensions à compter du 1er juillet 2026), ni
celle des élus locaux (à compter du 1er janvier 2027).

**Ce qui reste.** Le libellé « accident du travail » de la saisie ne dit pas
la condition de 66 % ; c'est une retouche du site, que cette étape ne fait
pas. `sam_parents_24_23`, désormais `approchee`, n'a pas sa mesure dans
`docs/limites/` : elle viendra avec l'étape qui écrira l'exception, ou qui
décidera de la laisser. Les rédactions passées des mêmes articles ne sont pas
lues.
