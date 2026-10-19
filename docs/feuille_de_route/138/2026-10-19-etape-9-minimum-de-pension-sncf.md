# Étape 9, suite de la huitième partie : le minimum de pension de l'agent de la SNCF, porté à la pension d'ancienneté

**La demande.** Vague du 19 octobre 2026, session 7 de la première salve,
lancée par la session de suivi « Tâches restantes » : le point « le minimum de
pension de l'agent » du bloc « Reprise » de la huitième partie
(`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`), que la note « minimum
de la réversion » (`2026-10-18-etape-9-minimum-de-la-reversion-sncf.md`,
« Ce qui reste », 1) décrivait. Règle du scénario 1, en Python puis en
JavaScript ; les pages et la saisie ne sont pas touchées : la session 138.8 les
tient.

**Ce que disent les textes, lus le jour même dans l'index LEGI, mis à jour
le 18 octobre.**

- *L'article 15 du décret n° 2008-639*, I, du 1er juillet 2008 au 31 décembre
  2016 : « Lorsqu'il est procédé à la liquidation de la pension d'ancienneté,
  le montant de celle-ci ne peut être inférieur à un montant minimal défini au
  IV ci-dessous. » Depuis le 1er janvier 2017 (rédaction du décret
  n° 2011-291, que son article 18, II, applique « aux pensions prenant effet à
  compter du 1er janvier 2017 ») : « Si le nombre de trimestres de durée
  d'assurance, telle que définie au III de l'article 13, est égal au nombre de
  trimestres nécessaire pour obtenir le pourcentage maximum de la pension [...]
  ou si l'intéressé a atteint l'âge auquel s'annule le coefficient de
  minoration [...] ou si la liquidation intervient pour les motifs prévus au II
  de l'article 3, à l'article 4 et à l'article 5 ». « Toutefois, les agents qui
  ont atteint, avant cette date, l'âge de liquidation qui leur était applicable
  [...] conservent le bénéfice des dispositions de l'article 15 [...] dans leur
  rédaction antérieure » (article 18, II) : cinquante ans pour l'agent de
  conduite, cinquante-cinq pour les autres.
- *La pension d'ancienneté* est celle de l'agent qui « a au moins vingt-cinq
  années de services valables pour la retraite » et l'âge de l'article 1er
  (rédaction de 2008), vingt-sept depuis 2017 ; « abaissée [...] à vingt-cinq
  ans pour les agents qui atteignent la durée de services de vingt-cinq ans
  [...] avant le 1er janvier 2017 », puis quatre mois de plus pour chaque année
  de 2017 à 2021 (article 37-1, I, 3°, le même dans ses quatre rédactions) ; en
  deçà, « une pension de retraite proportionnelle » (article 3), que le minimum
  ne relève pas. La caisse l'écrit (« Comprendre ses droits », lue le jour
  même) : « Si vous avez plus de 27 années de services valables pour la
  retraite, vous bénéficiez d'une pension d'ancienneté » ; « La pension
  d'ancienneté permet de bénéficier du minimum de pension » — sans montant ni
  condition.
- *Le IV* depuis 2017 : le minimum « est versé sous réserve que le montant
  mensuel total des pensions personnelles de retraite de droit direct [...]
  n'excède pas le montant fixé par le décret prévu à l'antépénultième alinéa
  de l'article L. 17 du code des pensions civiles et militaires de retraite
  ou, si celui-ci est plus élevé, le montant du minimum », et aux seuls agents
  qui « ont fait valoir leurs droits aux pensions personnelles » ; jusqu'au
  21 octobre 2023, « les modalités d'application des deux précédents alinéas
  sont celles fixées par le décret prévu au dernier alinéa de l'article
  L. 17 ». Ce décret n'a jamais paru, et la fonction publique n'applique ni
  l'écrêtement ni la condition (fiche `minimum_garanti`).
- *La surcote* « s'applique au montant de la pension calculée en application
  de l'article 12 » (article 13, II) : le minimum se compare à la pension
  surcotée ; la majoration pour enfants est « de 10 % de leur pension »
  (article 16) : de la pension portée au minimum.

**Ce qui est fait.**

- *La fiche* `minimum_pension_sncf`, `approchee` : trois versions sur la date
  d'effet — `avant_2008` (supposée : le règlement d'avant le décret n'est pas
  lu, aucun minimum), `anciennete_2008` (vingt-cinq ans de services, sans autre
  condition), `taux_plein_2017` (vingt-sept ans, les durées abaissées de
  l'article 37-1, le taux plein, le droit ancien de qui avait cinquante ans
  avant 2017) — ; ses approximations, et l'écrêtement du IV à relire. Les
  quatre périodes du régime déclarent `minimum_pension_sncf` ; le registre des
  avantages non contributifs a sa ligne, chiffrée par la cascade ; le cliquet
  des rédactions sans statut descend à 9 660.
- *Le modèle* : `liquider.minimum_de_pension_ouvert` (`minimumDePensionOuvert`)
  dit si le minimum relève la pension — pension d'ancienneté, puis taux plein
  ou droit ancien — ; `EligibleMinimumDePension` le porte à l'étape suivante,
  dont le contrat (`liquider_chaque_regime.yaml`) gagne l'objet
  `minimum_de_pension` ; `completer.minimum_de_pension_sncf`
  (`minimumDePensionSncf`) rend le minimum de la date d'effet, l'ancre de son
  année revalorisée par l'article 30, et la cascade écrit la ligne « Minimum de
  pension de la SNCF », après le minimum garanti et avant la majoration pour
  enfants.
- *La réversion de la pension relevée.* Le minimum de l'article 18 ne jouait
  que si la pension de l'agent, menée à l'année du décès, atteignait le
  minimum de cette année ; mais la pension portée au minimum avant octobre
  2014, revalorisée comme les pensions, reste 0,3 % sous celui que le décret
  de 2015 écrit, l'article 36, c, n'étant pas porté : sa réversion retombait à
  la moitié. La ligne de la cascade dit désormais la pension relevée
  (`par_regime`), l'échéancier la passe à la réversion avec la part du minimum
  contributif (`MINIMA_REVERSES`, dans `minima`), et `_minimum_de_pension`
  (`minimumDePension`) la tient pour portée au minimum, quel que soit son
  montant (article 18 : « Lorsque la pension de l'agent a été portée au montant
  du minimum »).
- *Les tests* : `tests/test_minimum_pension_sncf.py`, dix cas posés à la main
  sur le texte — la pension d'ancienneté de 2010 portée au minimum, la
  proportionnelle sous vingt-cinq ans, rien avant juillet 2008, la pension
  décotée de 2019 sans minimum, la même à cinquante-six ans avec, le droit
  ancien de l'agent né en 1966, les vingt-six ans de qui a eu vingt-cinq ans de
  services en 2019 (vingt-six ans et demi, oui ; vingt-cinq et demi, non), la
  majoration pour enfants sur le minimum, la réversion de la pension relevée
  en 2010 d'un agent mort en mai 2023 (54 % du minimum de 2023, rouge avant le
  correctif : la moitié de sa pension) — et le portage, sur dix requêtes, la
  réversion comprise. `-m rapide`, `-m site`, les trois fichiers du site, les
  confrontations légères, `test_reversion.py`, `test_liquidation.py`,
  `test_avantages.py` : verts le 19 octobre.

**Ce que montrent les mesures** (requêtes du formulaire, agent né en janvier,
à 30 % du salaire moyen, entré à vingt ans, avant et après) :

- *En 2010*, parti à cinquante-cinq ans avec trente-cinq ans de services : de
  6 461 € à 13 653 € par an ; mort en mai 2023, il laisse à sa veuve 8 568 €
  par an, 54 % du minimum de 2023, au lieu de 3 744 €.
- *En 2024*, né en 1968, parti à cinquante-six ans, au-delà de l'âge
  d'annulation de la décote : de 7 982 € à 16 707 € ; le même parti à
  cinquante et un ans en 2019, décoté, garde 5 103 €, sans minimum.
- *En 2017*, né en 1966, parti décoté à cinquante et un ans, au droit ancien :
  de 5 552 € à 14 602 €.
- *Une carrière complète* le touche aussi : né en 1955, entré à vingt ans, à
  40 % du salaire moyen, parti à soixante-quatre ans en 2019, surcote
  comprise, de 14 510 € à 14 763 €. C'est le balayage de
  `test_toute_formule_affichee_retrouve_le_montant_de_sa_ligne` qui l'a
  trouvé : sa lecture des formules (`tests/test_web.py`) apprend la troisième
  phrase des planchers, « porté au minimum de pension par + … € », et la
  branche s'ajoute à celles qu'il exige.
- Sur les 886 témoins, aucune pension ne bouge : ceux de la SNCF, au salaire
  moyen ou à 55 % de lui, dépassent le minimum ; un rendu de page change, la
  page des dispositifs, qui nomme le minimum de pension de la SNCF. Les
  agrégats de la page Coût ne bougent pas : aucune carrière de la SNCF de la
  grille n'est sous le minimum, et sa ligne du coût reste vide, ce que le
  registre dit (`sans_chiffre`).

**Ce qui reste**, une session par point :

1. *L'écrêtement du IV*, au propriétaire (ci-dessous).
2. *Inchangés* : l'ASPA de l'article 23, au propriétaire ; le plafond de 2027 ;
   la date d'entrée dans la saisie en net, à une session des pages ; la limite
   5 ante ter (2), en fin d'étape ; les décrets qu'aucune marche ne rejoint ;
   au propriétaire, les décrets des exploitants de 1980 à 1989, au fac-similé.
3. *Non portés*, déclarés dans la fiche : le minimum du grade à service
   discontinu et celui de la pension de réforme, que le modèle ne liquide pas ;
   les motifs de l'enfant invalide, de l'amiante et du handicap ; le 5° du I
   de l'article 37-1 ; le règlement d'avant juillet 2008.

**Au propriétaire : l'écrêtement du IV.** Jusqu'au 21 octobre 2023, le texte
renvoyait ses modalités au décret de L. 17, qui n'a jamais paru : ni
l'écrêtement ni la condition d'avoir liquidé toutes ses pensions ne
s'appliquaient, comme à la fonction publique. Depuis le 22 octobre 2023
(rédaction LEGIARTI000048240197), ce renvoi a disparu, et le texte borne le
total des pensions de droit direct au montant du décret « ou, si celui-ci est
plus élevé, [au] montant du minimum ». Le modèle ne l'applique pas, faute du
décret. L'autre lecture borne ce total au minimum lui-même : un agent dont la
pension de la SNCF est portée au minimum et qui a 300 € par mois d'une autre
caisse verrait son minimum réduit d'autant. Une question à poser à la CPRP,
depuis un poste : « depuis le 22 octobre 2023, le minimum de pension de
l'article 15 est-il réduit quand le total des pensions de droit direct dépasse
le minimum, et à quel montant ce total se compare-t-il ? »

**Pour la session des pages.** La page Coût (« Ce que la garantie remplace »,
`pages.js`) somme quatre minima de la cascade ; le minimum de pension de la
SNCF en est une cinquième ligne, `minimum_pension_sncf`, à y joindre si la
grille lui donne un coût. La page des dispositifs le nomme d'elle-même, par le
registre.
