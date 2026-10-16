# Étape 6 : la limite d'âge des autres régimes spéciaux

**Le 16 octobre 2026 : l'agent des industries électriques et gazières, le personnel
de l'Opéra national de Paris et l'agent de la SEITA dont le départ saisi passe sa
limite d'âge la quittent à la limite, reculée et prolongée par les seules exceptions
que leur statut leur ouvre ; leur pension du régime spécial part de ce jour. Python
et JavaScript. Les six autres régimes spéciaux n'ont pas de limite au modèle, et
leur fiche dit pourquoi.**

## Ce qui a été lu

- **Les IEG** (fiche `limite_age_ieg`) : le statut national, annexe, article 4.
  Soixante-cinq ans depuis le 5 juillet 2008 ; soixante-sept pour les nés depuis
  1962 depuis le 21 mars 2011, par une marche de quatre mois par génération que le
  texte écrit ; le recul pour enfants, la prolongation pour carrière incomplète,
  bornée à la durée du taux maximum moins cent cinquante trimestres ; depuis le
  1er septembre 2023, le maintien jusqu'à soixante-dix ans, qui borne le tout.
- **L'Opéra** (fiche `limite_age_opera`) : le décret n° 2008-240, article 2.
  Quarante-deux ans pour les danseurs, soixante pour le chœur, soixante-deux pour
  les musiciens, soixante-cinq pour les autres, depuis le 10 mars 2008 ;
  soixante-sept pour les nés depuis 1962 depuis le 13 août 2011 ; dix trimestres de
  maintien pour carrière incomplète.
- **La SEITA** (fiche `limite_age_seita`) : le décret n° 62-766, article 111.
  Soixante-cinq ans, soixante pour l'ouvrière, sans exception.
- **Sans limite au modèle**, consignés dans `limite_age_sncf_ratp` : la Banque de
  France, dont les limites par grade tiennent à une délibération de 1954 et au
  décret n° 68-299, absents de l'index ; la Comédie-Française, dont le sociétaire
  est mis à la retraite par arrêté après ses années de services, et non à un âge ;
  la CRPCEN, de droit privé ; les mines, les marins et le port de Strasbourg, sans
  limite trouvée.

## Ce que fait le modèle

- **`droit/limite_age.py`** et son jumeau : trois fiches de plus dans
  `FICHE_DU_REGIME` (`ieg`, `opera_de_paris`, `seita`). Une version de la limite
  qui porte `incomplete_au_dela_de` borne la prolongation pour carrière incomplète
  à la durée du taux maximum moins ce nombre de trimestres, et la prolongation est
  alors la sienne : celle des IEG.
- **Mesuré** : trois témoins neufs (`limite_age_ieg_1955`, `limite_age_opera_1950`,
  `limite_age_seita_1940`) ; sept tests de plus ou repris dans `test_limite_age.py`.

## Les choix, que le propriétaire peut reprendre

1. **La catégorie n'est pas saisie** : l'agent de l'Opéra est des « autres
   catégories de personnel », l'agent de la SEITA de « tous les autres agents ».
2. **Avant le premier texte lu, aucune limite** : 2008 pour les IEG et l'Opéra,
   1962 pour la SEITA, comme la SNCF avant 2010.
3. **La durée manquante de l'agent des IEG se compte sur ses seuls services au
   régime**, comme celle du fonctionnaire, quand la rédaction de 2023 dit « la durée
   d'assurance requise ».

## Ce que la page peut dire (session du site)

`radiation(moteur, carriere).fiche` vaut désormais aussi `limite_age_ieg`,
`limite_age_opera` ou `limite_age_seita`, que `FIN_A_LA_LIMITE` ne nomme pas
encore : « vous êtes mis en inactivité », « vos fonctions cessent », « vous êtes
mis à la retraite ». La prolongation de l'agent des IEG porte la fiche
`limite_age_ieg`.

## Ce qui reste

- La Banque de France, si ses textes se trouvent ; la limite des IEG et de l'Opéra
  avant 2008 ; le statut du mineur.
- Ceux que les étapes 3 et 4 laissaient : la CARMF avant 2017, le taux acquis au
  31 mars 1983, et, pour le propriétaire, la radiation dans les comptes notionnels,
  l'actif d'avant 2010 et les choix de l'étape 4.
