# L'emploi de l'agent de la Banque de France, déclaré au formulaire

Le 19 novembre 2026, à la demande du propriétaire, le formulaire demande à
l'agent titulaire de la Banque de France si son emploi est de ceux qui
ouvrent le droit cinq ans plus tôt, et le scénario 1 lit sa réponse. C'est la
première des trois approximations que la fiche `decote_banque_de_france`
déclarait (`2026-11-19-decote-de-la-banque-de-france.md`). L'étape s'est
menée sur Fable 5.2.

**Le texte.** Règlement annexé au décret n° 2007-262 du 27 février 2007,
dans les quatorze rédactions de l'annexe que porte l'index LEGI.

- Article 26, a : le droit s'ouvre à « au moins l'âge de cinquante-cinq ans »
  à l'agent qui « appartient à l'une des catégories dont la nomenclature est
  fixée par délibération du conseil général » (`LEGIARTI000006778516`).
- Décret n° 2012-701 du 7 mai 2012, articles 18 et 38 : cinquante-sept ans,
  relevés de trois mois par semestre pour les agents nés de 1956 à juin 1959
  (article 72, I, 2°, `LEGIARTI000025882187`), dès le 9 mai 2012.
- Décret n° 2014-669 du 23 juin 2014, article 16 : le relèvement est décalé
  de cinq ans, aux agents nés de 1961 à juin 1964 (`LEGIARTI000029138467`),
  dès le 26 juin 2014. Ceux de 1956 à 1960 retrouvent cinquante-cinq ans.
- Décret n° 2023-693 du 28 juillet 2023 : l'âge de L. 161-17-2 « abaissé de
  cinq années », cinquante-sept ans pour les agents nés avant 1968, trois
  mois de plus par génération, cinquante-neuf ans depuis 1975, pour les
  pensions prenant effet depuis le 1er janvier 2025 (`LEGIARTI000047909725`).
- La décote : la dernière colonne du tableau de 2007, « pour les agents dont
  les droits sont ouverts à l'âge de 55 ans » ; depuis le 9 mai 2012, « l'âge
  visé au 2° est minoré de 20 trimestres » (article 70), et la limite d'âge
  de l'article 32 de même, pour les pensions de 2016 et après.

**Ce qui change.** Un champ de saisie, `banque`, vide ou `active`, que le
formulaire ne montre qu'avec une période d'agent de la Banque. Une fiche,
`age_ouverture_banque_de_france_actifs`, en cinq versions sur la date
d'effet, que le moteur lit (`ageDesEmploisClassesDeLaBanque`, `ouvrir.js`).
La fiche de la décote gagne un paramètre,
`trimestres_de_moins_des_emplois_classes`, et le moteur lit enfin sa colonne
`age_annulation_a_55_ans` (`decoteBanqueDeFrance`, `liquider.js`). La
réponse passe par la chronologie, en fait de sorte « titre », écrit des deux
côtés (`chronologie.js`, `chronologie.py`).

**Ce qui bouge.** Aucun des 934 témoins de simulation ni des 86 rendus de
page : la question n'a pas de réponse par défaut. Un témoin de plus,
`banque_de_france_emploi_classe`. Pour l'agent qui répond, sur une carrière
commencée à vingt-huit ans, la part de pension que la décote retire devient :

| Né en janvier | Départ | Sans la réponse | Avec |
|---|---|---|---|
| 1954 | 55 ans, 2009 | 2,5 % | 0,5 % |
| 1958 | 58 ans, 2016 | 25 % | 10 % |
| 1958 | 62 ans, 2020 | 15 % | aucune |
| 1962 | 57 ans, 2019 | 25 % | 23,75 % |
| 1964 | 58 ans, 2022 | 25 % | 20 % |

Le modèle servait déjà la pension d'un agent parti avant son âge de droit
commun, dès son départ : l'âge d'ouverture ne la repoussait pas. La réponse
déplace donc la ligne du tableau, l'âge d'annulation, et la durée requise,
lue à l'année où le droit s'ouvre. Le cas de 1954 le montre : sans la
réponse, le modèle comptait vingt trimestres jusqu'à 61 ans, là où la colonne
des agents à 55 ans en compte quatre jusqu'à 56 ans.

**Ce que la relecture a trouvé d'autre.** L'exemption du c de l'article 32
— l'agent d'au moins soixante-cinq ans qui a élevé ou aidé un enfant
handicapé — ne vaut que pour les pensions prenant effet depuis le 1er
janvier 2016 (décret n° 2012-701, articles 25 et 41, I) : la fiche la datait
du 9 mai 2012, et le dit maintenant. Le décret de 2012 change le droit des
agents de ces catégories, à la différence des autres : né au premier
semestre 1955, l'agent passe de 0,25 % et 56 ans et demi à 0,875 % et
58 ans. Transcrit tel quel.

**Ce qui reste.** Les deux autres approximations. Les personnels de
direction du quatrième au septième degré : sur les lignes que les fiches
citent, leur limite d'âge diminuée de leurs trimestres donne l'âge de la
colonne de droit commun, si bien que leur décote est déjà juste ; c'est leur
limite d'âge, plus haute, qui manque, et ses colonnes sont à relire dans
l'arrêté A-2012-02 avant de les servir. L'exemption de l'agent de 65 ans,
que le fonctionnaire n'a pas non plus au modèle, demande les conditions du
décret de l'article L. 14. La nomenclature du conseil général n'est pas
lue : le modèle croit la saisie. L'âge de droit commun de la Banque
(article 72, I, 1°) reste celui des salariés, écart relevé le 17 novembre.
