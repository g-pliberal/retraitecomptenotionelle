# Étape 8 : la limite d'âge du personnel de la Banque de France

**Le 16 octobre 2026 : l'agent titulaire de la Banque de France dont le départ saisi
passe sa limite d'âge prend sa retraite à la limite, prorogée pour enfants ou prolongée
pour carrière incomplète comme son statut le dit ; sa pension du régime spécial part de
ce jour. Python et JavaScript.**

## Ce qui a été lu

Les textes que l'étape 6 n'avait pas trouvés dans l'index de la DILA sont sur le site de
la Banque de France, au registre de publication officiel : le statut du personnel s'y
modifie par arrêtés du conseil général.

- **L'arrêté n° A-2012-02** du 1er juin 2012, publié le 26 juillet 2012 (article 1er,
  24°), récrit l'article 241 : « ils doivent prendre leur retraite dès qu'ils ont atteint
  l'âge prévu dans le tableau ci-dessous » ; soixante et un ans pour le né au second
  semestre de 1947, trois mois de plus par semestre, soixante-sept ans depuis le second
  semestre de 1959 ; trois colonnes de plus pour les plus hauts niveaux, qui rejoignent la
  première pour les nés de 1956. Le décret n° 2012-697 qui l'autorise est dans l'index,
  sans son article.
- **L'arrêté n° 2018-02** du 12 mars 2018 récrit tout le statut, en vigueur le 1er
  janvier 2019 : le même tableau (article 241) ; la prorogation d'un an pour deux enfants
  à charge, ou un et deux autres élevés jusqu'à seize ans, de deux pour trois, ou deux et
  un autre, deux ans au plus, plus un an par enfant à l'AAH ou mort au champ d'honneur
  (article 242) ; le maintien pour carrière incomplète jusqu'à la durée de l'article 31 du
  règlement des retraites, dix trimestres au plus, « pas cumulable » avec l'article 242
  (article 242-1).
- **L'arrêté n° A-2024-01** du 22 janvier 2024 réserve ces articles aux agents titulaires
  d'avant le 1er septembre 2023, les seuls que le modèle affilie au régime.

## Ce que fait le modèle

- **`droit/limite_age.py`** et son jumeau : la fiche `limite_age_banque_de_france`, dans
  `FICHE_DU_REGIME`, trois versions (rien avant le 26 juillet 2012, le statut de 2012,
  celui de 2019). Deux paramètres neufs d'une version de limite : `enfants`, la
  prorogation que le statut écrit lui-même, au lieu de celle de la loi de 1936 ;
  `sans_cumul`, la prolongation pour carrière incomplète qui part de la limite et remplace
  la prorogation pour enfants quand elle mène plus loin.
- **Mesuré** : le témoin `limite_age_banque_de_france_1958`, retraité à 68 ans et 9 mois
  (66 ans et 3 mois, puis dix trimestres) ; deux tests de plus dans `test_limite_age.py`,
  un repris (l'agent de la Banque recruté depuis 2023 n'a pas de limite). Aucun autre
  témoin ne bouge.

## Les choix, que le propriétaire peut reprendre

1. **Le niveau n'est pas saisi** : tout agent prend la colonne « Limite d'âge », celle
   des agents qui ne sont pas des niveaux nommés. Un cadre des niveaux 7 et 8 né avant
   1955 partirait plus tard, jusqu'à soixante-cinq ans.
2. **Avant le 26 juillet 2012, aucune limite**, comme la SNCF avant 2010 ; l'agent qui
   avait passé la sienne est radié ce jour-là.
3. **Les articles 242 et 242-1 de 2012 ne sont pas lus** : la version de 2012 leur prête
   leur rédaction de 2019.
4. **L'enfant à charge a moins de dix-huit ans** (la saisie ne dit pas les études) ;
   l'AAH et le champ d'honneur, inconnus de la saisie, ne prorogent rien.

## Ce que la page peut dire (session du site)

`radiation(moteur, carriere).fiche` vaut aussi `limite_age_banque_de_france`, que
`FIN_A_LA_LIMITE` ne nomme pas : « vous devez prendre votre retraite ». La prorogation
pour enfants porte la fiche de la limite, et non `recul_limite_age_enfants`.

## Ce qui reste

- La limite des IEG et de l'Opéra avant 2008, et le statut du mineur.
- La limite de la Banque de France avant 2012 (délibération de 1954, décret n° 68-299,
  arrêté du 19 janvier 2007) ; les articles 242 et 242-1 de 2012.
- Au site, nommer la fin de l'emploi des quatre fiches neuves ; pour le propriétaire, la
  radiation dans les comptes notionnels, l'actif d'avant 2010, les choix des étapes 4, 6
  et 8.
