# Le personnel de direction de la Banque de France, servi à la limite de son degré

Le 20 novembre 2026, à la demande du propriétaire, le formulaire laisse l'agent
titulaire de la Banque de France dire qu'il est du personnel de direction, au
quatrième ou cinquième degré, au sixième ou au septième, et le scénario 1 lui
oppose la limite d'âge de sa colonne. C'est la deuxième des trois
approximations que la fiche `decote_banque_de_france` déclarait
(`2026-11-19-emploi-de-l-agent-de-la-banque-de-france.md`). L'étape s'est
menée sur Fable 5.2.

**Le texte.** Deux arrêtés du conseil général, relus sur le site de la Banque,
et l'article 70 du règlement, dans l'index LEGI.

- Arrêté n° A-2012-02 du 1er juin 2012, article 1er, 24° (Registre de
  publication officiel, 26 juillet 2012) : l'article 241 du statut du
  personnel porte un tableau de vingt-cinq lignes, du second semestre 1947 au
  second semestre 1959, à quatre colonnes — « Limite d'âge », « Agents des 4e
  et 5e degrés », « Agents du 6e degré », « Agents du 7e degré ». Les 4e et 5e
  degrés ont un an de plus que les autres agents jusqu'à 65 ans, atteints au
  second semestre 1953 ; le 6e degré a 64 ans au second semestre 1947 et 65
  ans depuis le second semestre 1949 ; le 7e, 65 ans. Les quatre colonnes
  s'égalent au second semestre 1955 et ne se quittent plus.
- Arrêté n° 2018-02 du 12 mars 2018, en vigueur le 1er janvier 2019 : le même
  tableau depuis le premier semestre 1950, à trois colonnes, « Agents des
  niveaux 5 et 6 » et « Agents des niveaux 7 et 8 », aux âges des colonnes de
  2012, ligne à ligne.
- Règlement annexé au décret n° 2007-262, article 70, rédaction du 9 mai 2012
  (`LEGIARTI000025882187`) : un second tableau, « pour les personnels de
  direction à partir du quatrième degré nés avant le 1er janvier 1956 »,
  quatorze lignes et trois colonnes, de « Lim. âge - 7 », « - 15 », « - 16
  trimestres » au premier semestre 1949 à sept partout au second semestre
  1955.

**Ce qui change.** Trois choix de plus au menu `banque` de la saisie :
`direction_4_5`, `direction_6`, `direction_7`. Les deux versions lues de la
fiche `limite_age_banque_de_france` portent les trois colonnes (`colonnes`),
que le moteur lit à la naissance de l'agent (`ageDeSaColonne`,
`limite_age.js`). La fiche de la décote porte le second tableau
(`trimestres_avant_limite_de_la_direction`), que `decoteBanqueDeFrance`
retranche de la limite de la colonne.

**La décote ne bouge pas.** À chacune des quatorze lignes et dans chaque
colonne, la limite de la direction diminuée de ses trimestres est l'âge de
l'agent de droit commun : le test le vérifie sur les quarante-deux cases, pour
les deux statuts. Le second tableau n'existe que pour défaire, sur la décote,
ce que la limite plus haute y aurait ajouté.

**Ce qui bouge.** Aucun des 935 témoins de simulation ni des 86 rendus de
page : sans réponse, rien ne change. Un témoin de plus,
`banque_de_france_direction_6e_degre`. Pour l'agent qui répond, entré à
vingt-deux ans, le jour où il doit partir et le taux de sa pension de la
Banque deviennent :

| Né en janvier | Départ voulu | Droit commun | 4e ou 5e degré | 6e degré |
|---|---|---|---|---|
| 1950 | 64 ans et demi | juillet 2012, 79,7 % | 63 ans 3 mois, 82,5 % | au départ, 87,2 % |
| 1952 | 65 ans | 63 ans 3 mois, 78,75 % | 64 ans 3 mois, 82,5 % | au départ, 85,3 % |
| 1954 | 65 ans | 64 ans 3 mois, 78,75 % | au départ, 81,6 % | au départ, 81,6 % |

L'agent dont la carrière est incomplète n'y gagne rien : le modèle lui prête
déjà le maintien en activité de l'article 242-1, dix trimestres au plus, qui
couvre l'écart.

**Ce que la relecture a trouvé d'autre.** Rien qui démente les fiches. Les
articles lus de l'arrêté de 2018 ne disent pas quels degrés deviennent quels
niveaux : le modèle range les 4e et 5e degrés aux niveaux 5 et 6, les 6e et 7e
aux niveaux 7 et 8, parce que les âges sont les mêmes colonne à colonne
(présomption écrite à la fiche, sans effet depuis les nés de 1954). Le tableau
de 2019 ne nomme plus les nés avant 1950 : le modèle leur garde les lignes de
2012.

**Ce qui reste.** La troisième approximation, l'exemption de l'agent d'au
moins soixante-cinq ans qui a élevé ou aidé un enfant handicapé (c de
l'article 32). Les limites d'avant le 26 juillet 2012, arrêtées par grade, que
le modèle n'oppose pas : le cadre de direction parti avant cette date n'est
pas concerné par cette étape. Le modèle croit la saisie sur le degré.
