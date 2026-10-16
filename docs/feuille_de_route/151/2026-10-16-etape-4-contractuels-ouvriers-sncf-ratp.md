# Étape 4 : la limite d'âge des contractuels, des ouvriers de l'État, de la SNCF et de la RATP

**Le 16 octobre 2026 : l'agent contractuel, l'ouvrier de l'État et l'agent de la SNCF
ou de la RATP dont le départ saisi passe sa limite d'âge la quittent à la limite,
reculée et prolongée par les seules exceptions que leur droit leur ouvre ; leurs
pensions partent de ce jour. Python et JavaScript, témoins compris (5313523).**

## Ce qui a été lu

- **Le contractuel** (fiche `limite_age_contractuels`) : la loi du 8 août 1947,
  article 20, le maintien sur demande jusqu'à soixante-cinq ans, porté à soixante-sept
  par la loi de 2010, qui le relève comme la limite des sédentaires ; depuis le
  14 mars 2012, l'article 6-1 de la loi n° 84-834, devenu L. 556-11 à L. 556-13 du code
  général : soixante-sept ans, le recul pour enfants de la loi de 1936, la prolongation
  de dix trimestres au plus pour qui n'a pas la durée d'assurance tous régimes ; depuis
  le 14 juin 2023, le maintien jusqu'à soixante-dix ans, qui borne le tout.
- **L'ouvrier de l'État** (fiche `limite_age_ouvriers_etat`) : le décret n° 2004-1057,
  soixante-cinq ans et soixante pour qui a quinze ans de travaux insalubres, atteints
  par paliers de six mois de 2004 à 2012, l'insalubre abaissé jusqu'à cinq ans ;
  soixante-sept et soixante-deux relevés depuis le 1er juillet 2011 ; le recul pour
  enfants et la prolongation pour carrière incomplète depuis 2004 ; depuis le
  1er septembre 2023, L. 556-1 à L. 556-7 du code général, dont le maintien jusqu'à
  soixante-dix ans et la prolongation de l'insalubre jusqu'à la limite des autres.
- **La SNCF et la RATP** (fiche `limite_age_sncf_ratp`) : le décret n° 2010-105,
  soixante-cinq ans depuis le 31 janvier 2010 ; le décret n° 2011-288, soixante-sept
  pour les nés depuis 1962 ; depuis le 1er septembre 2023, le maintien du sédentaire
  jusqu'à soixante-dix ans, sur autorisation de l'employeur.

## Ce que fait le modèle

- **`droit/limite_age.py`** et son jumeau : `emploi_de` dit la fiche et la classe de
  chaque statut, à sa date d'entrée, si bien que le cheminot recruté depuis 2020,
  salarié de droit commun, n'a pas de limite ; chaque version des trois fiches nomme,
  par son paramètre `exceptions`, celles qui jouent ce jour-là. `Radiation` porte sa
  `fiche`, et `radier` n'arrête que les services de l'emploi radié.
- **La pension** : celle de tous les régimes que l'emploi radié route — régime général
  et Ircantec du contractuel, FSPOEIE, régime spécial — part de la radiation.
- **Mesuré** : sept témoins baissent au scénario 1, de 4 à 15 %, les ouvriers de
  l'État nés de 1925 à 1955 dont le départ saisi à 64 ans passait leur limite ; aucun
  contractuel ni cheminot témoin ne la passait. Quatre témoins neufs (`limite_age_*`) ;
  les 849 se retrouvent en JavaScript.

## Les choix, que le propriétaire peut reprendre

1. **L'ouvrier avant 2004 est supposé limité à soixante ans**, le point de départ des
   paliers du décret de 2004, dont les décrets de 1954 à 1960 qu'il abroge ne sont pas
   lus. Les ouvriers nés de 1925 à 1935 en baissent de 4 à 8 %.
2. **Les paliers de 2004 s'appliquent à tout ouvrier**, la saisie ne disant pas qui
   avait déjà soixante-cinq ans.
3. **La marche des cheminots nés de 1957 à 1961 est supposée** de quatre mois par
   génération, comme leur âge d'ouverture ; la rédaction de 2011 n'est pas dans
   l'index. Le roulant est traité en sédentaire, maintenu jusqu'à soixante-dix ans.
4. **La durée d'assurance du contractuel se compte par ses années cotisées**, toute la
   carrière, sans les périodes assimilées.
5. **Le contractuel radié liquide au régime général à la radiation**, comme le
   fonctionnaire au code des pensions : le métier salarié qu'il exercerait ensuite
   garderait ses droits au modèle, alors que, depuis 2015, l'activité après une
   première pension n'en ouvre plus (L. 161-22-1 A, constat de l'étape 3).

## Ce que la page doit dire (session du site)

Rien de neuf dans la forme : `radiation(moteur, carriere)` porte désormais `fiche`,
qui dit si la limite est celle du contractuel, de l'ouvrier ou du cheminot ; la page
peut dire « votre contrat prend fin à 67 ans », « vous êtes mis à la retraite à
67 ans », et nommer de même les exceptions présumées.

## Ce qui reste

- Les autres régimes spéciaux — IEG, Banque de France, CRPCEN, mines, marins, Opéra,
  Comédie-Française, SEITA, port de Strasbourg —, dont les statuts ne sont pas lus, et
  la limite des cheminots avant 2010 (décrets n° 54-23 et n° 54-24).
- Les lectures que les trois fiches gardent (`sources.a_relire`), dont L. 556-11 et
  L. 556-12, absents de l'index.
- Ceux que l'étape 3 laissait : la CARMF avant 2017, le taux acquis au 31 mars 1983,
  et, pour le propriétaire, la radiation dans les comptes notionnels.
