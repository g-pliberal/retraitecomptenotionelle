# Étape 17, troisième partie : le plafond de L. 18, la pension civile majorée pour enfants bornée au traitement

**Le 8 octobre 2026, la demande.** Le propriétaire : « Action 138, étape 17 : le
plafond de L. 18, la pension civile majorée pour enfants plafonnée au traitement
de référence (fiche majoration_enfants_plafond_fonction_publique, manquante ;
point de Destinie 2 au registre). » Le bloc « Reprise » le mettait après la
bonification des militaires, qui reste à faire.

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre, « plafond
de L. 18 »).

- *Le plafond.* « Le taux de la majoration de la pension est fixé à 10 % de son
  montant pour les trois premiers enfants et à 5 % par enfant au-delà du
  troisième, sans que le montant de la pension majorée puisse excéder le montant
  des émoluments de base déterminés à l'article L. 15 » (L. 18, V, depuis 1982 ;
  la CNRACL de même dès 1965, décret n° 65-773, article 19 ; le FSPOEIE, décret
  n° 65-836, article 11). Depuis 2004, les décrets de la CNRACL et du FSPOEIE
  réduisent « à due proportion » la pension et la majoration ; L. 18 depuis 2012,
  au traitement « revalorisé dans les conditions prévues à l'article L. 16 » (loi
  n° 2011-1977, article 163). La rédaction de 1964 n'est dans aucun index.
- *La surcote, qu'aucun texte n'excepte.* La fiche le demandait : c'est le
  Conseil d'État qui l'excepte, le 29 décembre 2020 (n° 428626, aux tables). Le
  plafond « ne méconnaît pas, en lui-même », la convention européenne ; mais
  l'appliquer à qui la surcote, déplafonnée par la loi du 9 novembre 2010, porte
  au traitement crée une différence de traitement « dépourvue de rapport avec
  l'objet de l'article L. 18 ». En 2017, la caisse refusait encore la majoration,
  sans réduire la pension, à une inspectrice générale de trois enfants dont la
  surcote de 30 % portait la pension à 104 % de son traitement.
- *Comment les caisses l'appliquent.* La CNRACL : « Pension + surcote + ME :
  Pension + ME = 100 % ; surcote servie sans plafond », la majoration calculée
  sur la pension après décote ou surcote, ou sur le minimum garanti. Le service
  des retraites de l'État : « limité à 100 % de votre dernier traitement
  indiciaire brut […], sauf en cas d'application d'une surcote ». Les deux ne
  diffèrent que pour la pension que le plafond borne déjà sans sa surcote.

**Ce qui est fait.**

- *La fiche* `majoration_enfants_plafond_fonction_publique`, de manquante à
  approchée, en cinq versions sur la date d'effet — avant le code de 1964, sans
  plafond, supposée ; le code de 1964, supposé ; 1982 ; la loi de finances pour
  2012 ; la décision du 29 décembre 2020, qui laisse la surcote hors du plafond —
  que les deux moteurs lisent (`FichesDatees`) ; un plafond ou une surcote
  inconnus les arrêtent. Elle donne leur statut à quinze rédactions : le cliquet
  des textes descend à 9 900.
- *Le modèle* : la liquidation écrit, pour chaque pension des trois régimes du
  code des pensions, le traitement de L. 15 et ce que la surcote y ajoute
  (`EligiblePlafondEnfants`, au schéma de l'étape) ; l'étape qui complète borne la
  majoration à ce qui porte la pension au traitement
  (`majoration_sous_le_traitement`), la pension jamais réduite, la surcote — et
  la surcote parentale de L. 14, IV — hors du plafond depuis la décision, le
  minimum garanti l'effaçant. Le portage JavaScript est son jumeau.
- *Le registre* : le point de Destinie 2, repris ; ses écarts et ceux
  d'OpenFisca-France-Pension, qui bornent la surcote à toute date, déclarés.
  L'inventaire des avantages nomme la fiche ; les limites le disent.

**Les mesures.** Sur les témoins, aucune pension ne bouge ; cinq témoins neufs
balaient le plafond, le portage les retrouve. Retirer la fiche mesure ce qu'elle
borne, à une fonctionnaire de l'État entrée à vingt-deux ans, partie à soixante-
deux ans en 2017 : sept enfants au taux de 80 %, − 3,8 % ; huit, − 7,4 %, à
l'État comme à la CNRACL ; le père entré à vingt ans, au taux de 75 %, huit
enfants, − 1,2 %. La
surcote : la mère de trois enfants partie à soixante-sept ans en 2017, sa
pension à 108 % du traitement, perd sa majoration, − 9,1 %, comme l'inspectrice
de la décision ; partie en 2021, plus rien ; huit enfants et une surcote en 2022,
120 % du traitement au lieu de 135 %, − 11,1 %. Destinie 2 n'a pas été exécuté :
le test rejoue sa formule, qui est celle du modèle jusqu'à la décision.

**Ce qui reste** de cette partie, hors de l'ordre de l'étape :

1. *Un titre de pension ou un exemple chiffré publié* d'une pension plafonnée, et
   la façon dont le service des retraites de l'État sert la pension que le
   plafond borne déjà sans sa surcote.
2. *Les rédactions de 1964 et de 1948*, qu'aucun index ne porte.
3. *Les régimes spéciaux qui copient L. 18* — l'Opéra, la Comédie-Française, la
   RATP, les IEG, la Banque de France —, dont les fiches de majoration ne bornent
   rien : trouvés en route.
