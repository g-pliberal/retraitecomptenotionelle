# Étape 9, suite de la huitième partie : la réversion de la SNCF, et sa cotisation maladie sous la moitié du plafond

**La demande.** Vague 2b des 17 et 18 octobre 2026, lancée par la session
d'orchestration : le premier point du bloc « Reprise » de la huitième partie
(`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`) — la réversion au
plafond de moitié, avec celle de la SNCF, que la note du 17 octobre
(`2026-10-17-etape-9-cotisation-sncf-par-etage.md`, « Ce qui n'est pas
fait ») attendait : la table des réversions n'avait pas de fiche pour la
SNCF, dont la ligne valait 0 €, et le plafond de moitié n'avait rien à
montrer.

**Ce que disent les textes, lus le jour même dans l'index LEGI, mis à jour
le 18 octobre.**

- *Le décret n° 2008-639* : la pension « reversée pour moitié au conjoint
  survivant et, s'il y a lieu, au conjoint divorcé », « majorée[s] dans les
  conditions fixées à l'article 16 » ; au décès avant la liquidation, « les
  mêmes droits que si l'agent avait été admis à la retraite le jour de son
  décès » (article 18). Deux ans de mariage « le jour de la cessation des
  fonctions », ou quatre ans au décès, deux « s'il existe un ou plusieurs
  enfants issus du mariage » ; aucune durée avec un enfant « né ou conçu des
  conjoints avant la date de cessation des fonctions » ; rien au conjoint
  « vivant en concubinage au moment du décès » (article 19, I). Le partage
  au prorata des mariages (article 20) ; le conjoint divorcé remarié avant
  le décès exclu (article 19, II). Le remariage, le pacs ou le concubinage
  après le décès figent la réversion « sans revalorisation ultérieure »
  (article 31). Deux minima : 54 % du minimum de pension de l'article 15
  (article 18), l'ASPA pour la personne seule de 55 à 64 ans (article 23).
- *La caisse* (CPRP, page « La pension de réversion — régime spécial »,
  sous son nouveau domaine, `cprpf.fr`) l'applique ainsi, et date la
  réversion du lendemain du décès de l'agent en activité, du premier jour du
  mois qui suit celui du retraité.
- *Avant le 1er juillet 2008*, le règlement de retraites de la SNCF n'est ni
  dans l'index LEGI ni au JORF : la fiche lui prête la règle de 2008, en
  version supposée.

**Ce qui est fait.**

- *La fiche* `reversion_sncf` : deux versions, le règlement d'avant
  juillet 2008 (supposée) et le décret de 2008 (lue, onze rédactions
  citées) ; ses approximations déclarées. Le cliquet des rédactions sans
  statut descend à 9 695.
- *Le modèle* (`droit/reversion.py`, puis `reversion.js`) : la branche des
  IEG devient celle des fiches qui reversent la moitié de la majoration
  (`MOITIE_MAJORATION_COMPRISE`), avec la condition de l'article 19
  (`_mariage_sncf`) et le concubinage au décès
  (`_sans_jouissance_au_deces`) ; la réversion de la SNCF compte parmi les
  autres régimes de base (`AUTRES_BASES`).
- *La page* (`pages.js`) : la colonne « Sa réversion » prend la cotisation
  de la SNCF sous la moitié du plafond, « Votre pension » sous le plafond
  entier ; la majoration pour enfants reversée ne paie aucune cotisation
  maladie (L. 131-2, 1°), comme celle de l'agent — ce qui vaut aussi pour la
  réversion de l'Agirc-Arrco, qui payait le 1 % sur la sienne ; la ligne dit
  « la moitié de la vôtre » aux IEG et à la SNCF, où elle disait « reversée
  en entier ». `pension_du_regime` et son jumeau prennent la majoration.
- *Les tests* : `test_reversion.py`, la condition de l'article 19 (sept cas,
  dont deux que L. 39 servirait), la majoration, l'union nouvelle, le
  partage ; `test_net_pensions.py`, la réversion sous la moitié du plafond,
  hors majoration, dans les deux moteurs ; `test_web.py`, la carte de la
  réversion d'un agent de la SNCF, contre le calcul posé à la main ; trois
  témoins de simulation, `reversion_agent_sncf*`.

**Ce que montrent les mesures.** L'agent né en 1958, parti à 57 ans, trois
enfants, mort en mai 2023 : 15 995 € de réversion par an en euros de 2023,
dont 1 454 € de majoration, là où la ligne disait 0 €. Né en 1960, au double
du salaire moyen, trois enfants, mort cette année : la réversion nette passe
de 2 631 € à 2 638 € par mois — 7 € de cotisation de moins, prise sous la
moitié du plafond (1 066 € par mois) au lieu du plafond entier. Aucun témoin
de page ne bouge.

**Ce qui reste**, une session par point :

1. *Les minima de la réversion de la SNCF* : 54 % du minimum de pension,
   que le modèle ne porte pas à la pension de l'agent non plus (article 15),
   et l'ASPA de 55 à 64 ans, sous condition de ressources (article 23).
2. *La majoration pour trois enfants de la réversion du régime général*,
   hors de la cotisation du non-résident (« Trouvé en chemin »).
3. *Inchangés* : le plafond de 2027 ; la limite 5 ante ter (2), en fin
   d'étape ; la CNBF et la Cipav dans la fiche de paie ; les décrets qu'aucune
   marche ne rejoint ; au propriétaire, les décrets des exploitants de 1980 à
   1989, au fac-similé.

**Trouvé en chemin.** La majoration pour trois enfants de la réversion du
régime général (R. 353-2) paie encore, au non-résident, la cotisation maladie
de la base (3,20 %), que L. 131-2, 1°, exclurait comme les autres
majorations pour enfants ; seule celle du défunt, que reversent l'Agirc-Arrco,
les IEG et la SNCF, en est sortie. Une session, avec son test.
