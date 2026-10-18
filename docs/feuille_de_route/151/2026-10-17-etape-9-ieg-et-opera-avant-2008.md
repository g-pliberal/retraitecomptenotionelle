# Étape 9 : la limite d'âge des IEG et de l'Opéra avant 2008

**Le 17 octobre 2026 : de 1954 au 27 novembre 2007, l'agent des industries électriques et
gazières dont le départ saisi passe l'ouverture de son droit est admis d'office à la
retraite, à cinquante-cinq ans ou le jour où il réunit vingt-cinq ans de services, à
soixante ans au plus tard ; sa pension du régime spécial part de ce jour. La limite de
l'Opéra ne vaut que du 1er juillet 2008. Python et JavaScript.**

## Ce qui a été lu

- **Les IEG.** Le statut national d'avant 2008 ne porte aucune limite : son annexe 3, que
  la fiche disait absente de l'index et qui y est (`LEGIARTI000006632496`), ne dit que l'âge
  et les services de la pension d'ancienneté — cinquante-cinq ans pour l'actif, soixante
  pour le sédentaire, vingt-cinq ans de services (article 3, § 1) —, et sa mise à la
  retraite d'office est une sanction (article 6). La limite est dans le décret n° 54-50 du
  16 janvier 1954, pris pour EDF et GDF en application du décret n° 53-711 (article 5), dont
  l'index ne porte que le titre. Son article 2 est cité par la cour d'appel de Paris, que
  reproduit l'arrêt de la Cour de cassation du 9 mars 2016 (n° 14-25.840) : « L'admission à
  la retraite est prononcée d'office quand l'intéressé a atteint l'âge d'ouverture du droit
  à pension d'ancienneté en ce qui concerne les agents ayant accompli la durée des services
  requise à cette fin par le statut national du personnel et en ce qui concerne les agents
  n'ayant pas atteint l'âge d'ouverture du droit à pension d'ancienneté fixé pour les agents
  appartenant aux services sédentaires ». Les réponses ministérielles du 14 octobre 2008
  (questions écrites n° 26598 et 28700) décrivent ces clauses, et la recommandation
  patronale du 28 novembre 2007, qui laisse poursuivre l'agent qui le souhaite ; le décret
  n° 2008-1072 abroge le décret n° 54-50 le 23 octobre 2008.
- **L'Opéra.** « Le présent décret entre en vigueur au 1er juillet 2008 » (décret
  n° 2008-240, article 3) : l'article 2, que LEGI date du 10 mars, ne vaut que de ce jour,
  où l'article 6 du décret n° 68-382 perd aussi son IV. Ce IV, écrit par le décret
  n° 2002-347, permettait depuis le 14 mars 2002 de mettre l'artiste du ballet à la
  retraite à quarante-deux ans ; aucune autre limite n'est dans l'index avant.
- **La classe de l'erreur** : aucune autre fiche de limite d'âge ne cite un décret dont
  l'entrée en vigueur est différée.

## Ce que fait le modèle

- **Les fiches.** `limite_age_ieg` : rien avant le 18 janvier 1954 ; le décret n° 54-50
  jusqu'au 27 novembre 2007 ; la recommandation patronale, sans limite, jusqu'au 5 juillet
  2008. `limite_age_opera` : rien avant le 14 mars 2002 ; le ballet seul, que la saisie ne
  distingue pas, jusqu'au 1er juillet 2008 ; la limite de 2008 depuis ce jour.
- **`droit/limite_age.py` et son jumeau** : trois paramètres neufs d'une version de limite.
  `classe_presumee`, la classe que le modèle prête à l'agent ; `services_requis`, les
  années de services dans l'emploi sans lesquelles la limite n'est pas atteinte, la
  radiation tombant le mois qui suit celui où l'agent les réunit ; `a_defaut_des_services`,
  l'âge où l'agent qui ne les a pas est radié.
- **Mesuré** : trois tests neufs et un repris dans `test_limite_age.py` ; dans
  `test_simulateur.py`, la surcote de juillet 2008 ne se teste plus sur l'agent des IEG né
  en 1945, parti en 2000 ; deux témoins neufs (`limite_age_ieg_1940_entre_a_32_ans`,
  `limite_age_ieg_1940_entre_a_40_ans`). Trois témoins bougent, les agents des IEG nés en
  1925, 1935 et 1945 partis à soixante-quatre ans, admis d'office à cinquante-cinq : leur
  pension baisse de 16,6 à 22,0 % aux scénarios 1, 3 et 5, rien d'autre ne bouge. Le
  cliquet des textes descend à 9716, quatre rédactions étant citées par les versions
  neuves.

## Les choix, que le propriétaire peut reprendre

1. **L'agent des IEG est présumé actif**, comme le modèle liquide sa pension depuis la
   fiche du régime : admis d'office à cinquante-cinq ans. Le sédentaire, que la saisie ne
   distingue pas, l'était à soixante.
2. **La seconde branche de l'article 2, tronquée, se lit pour l'agent qui n'a pas ses
   vingt-cinq ans** : admis d'office à l'âge des sédentaires, soixante ans. L'autre lecture
   le laisserait sans limite jusqu'à ce qu'il les ait.
3. **La recommandation de 2007 est présumée suivie**, le départ saisi étant le souhait de
   l'agent ; un agent d'EDF s'est encore vu refuser de poursuivre en juin 2008 (question
   écrite n° 28700).
4. **Les autres catégories de l'Opéra restent sans limite avant le 1er juillet 2008**,
   aucune règle n'étant lue.

## Ce que la page peut dire (session du site)

`radiation(moteur, carriere).version` vaut `decret_de_1954` pour l'agent des IEG admis
d'office avant le 28 novembre 2007 : la fin de l'emploi y est l'« admission d'office à la
retraite », et non la « mise en inactivité » de 2008, sous la même fiche `limite_age_ieg`.

## Ce qui reste

- Lire le décret n° 54-50 au Journal officiel du 17 janvier 1954, sur Légifrance ou
  Gallica, que le réseau de la session refuse : la seconde branche de l'article 2, et le
  maintien au-delà de soixante ans que la question écrite n° 28700 lui prête.
- Le décret n° 54-51 du même jour fixe « l'âge limite de maintien en activité » du mineur à
  l'âge d'ouverture de sa pension, l'agent pouvant rester « dans l'intérêt du service »
  (articles 2 et 3, dans l'index LEGI) : le statut du mineur. Les décrets frères pour la
  SNCF (n° 54-24) et la RATP (n° 54-23), dont l'index porte un sommaire — « admission
  d'office à la retraite » —, et pour la Banque (n° 54-776), éclaireraient leurs limites
  d'avant 2010 et 2012.
- Au site, nommer la fin de l'emploi des quatre fiches neuves ; pour le propriétaire, la
  radiation dans les comptes notionnels, l'actif d'avant 2010, les choix des étapes 4, 6, 8
  et 9.
