# Les rédactions dont les fiches ne disaient rien : celles de 2026 et après, lues

**Reprise, au 19 novembre 2026.** Le sixième cliquet de la note de décision
0009 comptait 83 cas où une fiche ne disait rien d'une rédaction en vigueur
d'un article qu'elle cite. Les 32 cas dont la rédaction commence en 2026 ou
après sont lus : aucune ne change la règle que sa fiche porte, et chaque
fiche le déclare, mot à mot à l'appui. Le cliquet est à 51. Restent ces 51
cas, de rédactions d'avant 2026, que le propriétaire a demandé de lire
ensuite. Par quoi commencer :
`python docs/decisions/0009/sixieme-cliquet/mesures.py`, puis
`python scripts/textes.py --sans-reponse <fiche>`, l'index LEGI récupéré.
Aucun résultat n'a bougé.

Le 19 novembre 2026, sur l'accord du propriétaire, la session lit les
dix-huit rédactions de 2026 et après dont trente-deux couples d'une fiche et
d'une rédaction ne disaient rien. Chacune est lue dans l'index LEGI, à jour au
16 novembre, et comparée mot à mot à celle d'avant
(`dila_cherche.py legi --num <article> --diff`).

**Ce que chaque rédaction change, et pourquoi la fiche n'en bouge pas.**

- *Le décret n° 2026-948 du 12 octobre 2026*, la majoration de durée
  d'assurance des élus locaux, pour les pensions prenant effet à compter du
  1er janvier 2027 : il l'ajoute à l'article 15 du décret n° 2003-1306, à
  l'article 12 du décret n° 2004-1056, à R. 8-1 du code des pensions des
  marins, à R. 732-61 du code rural et à l'article 3 du décret n° 2017-1000.
  Treize couples. La majoration a sa fiche, `majoration_duree_elus_locaux`,
  qui rattache les cinq rédactions ; les huit fiches qui citent ces articles
  pour autre chose — la majoration des sapeurs-pompiers volontaires, la
  bonification du cinquième, le taux maximum, les enfants, le barème et la
  durée agricoles — y retrouvent leur clause.
- *R. 351-27 du code de la sécurité sociale, au 1er août 2026* : le
  coefficient de minoration « est 1,25 % », à la place de « 2,5 % pour les
  pensions ayant pris effet avant le 1er janvier 2004 ». La rédaction du
  1er janvier 2026 avait ôté le tableau par génération sans laisser de
  coefficient aux pensions d'après 2003 ; celle-ci le rend. 1,25 % est le
  coefficient des assurés nés après 1952, les seuls qu'une décote atteigne
  encore. Trois couples.
- *R. 351-12, au 1er novembre 2026* : un mot au 5°, la rente pour une
  incapacité permanente « professionnelle ». Trois couples.
- *D. 351-2-2, au 1er août 2026* : un 4° au III, les trimestres de L. 634-4
  du code général de la fonction publique et de L. 4138-6-1 du code de la
  défense ; les 120 trimestres du II, que la fiche des cultes lit, restent.
- *L'article 20 du décret n° 2003-1306, au 1er août 2026* : « bonifications
  et majorations » au I ; le reste mot pour mot. Trois couples.
- *Le code rural, au 1er janvier 2026* : L. 732-56 (des renvois), L. 732-63
  et D. 732-111 (les périodes de chef à titre secondaire et la durée de
  L. 351-1, pour les pensions prenant effet à compter de 2026), que la fiche
  du relèvement de septembre 2023 ne lit que pour des pensions d'avant ;
  D. 732-114, qui écrête à l'année une majoration qui n'est plus celle de la
  fiche qui citait sa rédaction de 2005 ; D. 731-121, les taux d'après 2025,
  quand la fiche n'en tire que ceux de 2016 à 2025.
- *L'article 2 du décret n° 79-262, au 1er juillet 2026* : la Cipav, qui n'a
  plus de classes depuis 2023.
- *Le règlement du RCI, au 1er janvier 2027* (arrêté du 21 septembre 2026) :
  l'article 27 change de renvois, pour le cumul de 2027 ; l'article 39 ne
  vise plus que D. 635-9 ; l'article 41, I, prend le revenu de référence du
  jour de l'effet de la pension du conjoint survivant, non plus de celle de
  l'assuré. Ce I, le versement en une fois de la réversion de moins de
  quarante points, le modèle ne le porte pas : la fiche
  `versement_unique_rci` le déclarait déjà, et rattache la rédaction.

**Ce qui est posé.** Trente-deux déclarations `textes_sans_effet`, dans
vingt-deux fiches, chacune avec ce que la rédaction change et ce que la fiche
tient de l'article ; les citations sont vérifiées contre le texte de l'index.
`sans_un_mot` passe de 83 à 51 dans `data/reference/textes/perimetre.yaml`.
Aucune règle, aucun paramètre, aucun fichier de régime ne change.

**À savoir.** Chacune des dix-huit rédactions était déjà rattachée par une
autre fiche : la lecture n'a trouvé aucune règle que le modèle aurait
manquée. La session, ouverte sur Opus, est passée sur Fable 5.2
avant d'écrire, sur l'accord du propriétaire.
