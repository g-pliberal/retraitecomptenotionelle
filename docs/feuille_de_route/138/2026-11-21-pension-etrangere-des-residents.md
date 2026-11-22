# La pension étrangère de qui réside en France : sa CSG, et ce qu'elle change à la pension française

**La demande.** Le propriétaire, le 21 novembre 2026 : « on a pas trop parlé
des étrangers, des Français à l'étranger et d'autres cas de ce style ». L'état
des lieux a relevé, parmi trois manques, la pension étrangère du frontalier
revenu en France (465 000 frontaliers en 2021, Insee Première n° 2027) : ni
nettée ni comptée dans l'impôt. Écart au droit, corrigé sans accord préalable
(règle 1 du projet).

**Ce que le droit dit, lu le 21 novembre 2026.**

- Revenu fiscal de référence : il compte les revenus « exonérés par
  application d'une convention internationale relative aux doubles
  impositions » (CGI, art. 1417, IV, 1°, c ; index LEGI, version du
  1er janvier 2026).
- Contributions sociales : la CSG (CSS, L. 136-1), la CRDS (ordonnance
  n° 96-50, art. 14) et la CASA (L. 137-41) frappent toute pension, quelle que
  soit sa source, de qui est domicilié en France et à la charge d'un régime
  français d'assurance maladie, « sous réserve » que la convention fiscale
  n'exclue pas l'imposition par la France (BOI-RES-RSA-000219, 11 août 2025,
  qui cite CE, 25 octobre 2024, n° 473997). Taux : ceux de la tranche du
  foyer ; la CASA aux seuls taux médian et plein ; CSG déductible de 5,90 %
  au taux plein (notice 2041 GG, revenus 2025, tableaux 1 à 4).
- Allemagne : l'avenant du 31 mars 2015 réserve à la France, depuis 2016,
  l'imposition des pensions des assurances sociales légales allemandes de ses
  résidents (rapport Doligé, Sénat n° 231, 2015-2016). La CSG y est donc due.
  La Suisse : convention non relue ici.

**Ce qui a été fait.**

1. Le revenu fiscal présumé compte les pensions étrangères servies au même
   mois que la pension affichée (`contexte.js`, `Montants.depuis`, `foyer`) :
   la tranche de CSG de la pension française peut monter.
2. L'impôt de chaque année déclare la pension étrangère, moins sa CSG
   déductible (`pensionsEtrangeresImposables`, `impotsParAnnee`) ; la pension
   française supporte sa part de l'impôt des pensions, au prorata ; la pension
   du départ après impôt aussi (`pensionApresImpotDe`).
3. La pension étrangère paie la CSG, la CRDS et la CASA de la tranche du
   foyer (`Montants.tauxPensionEtrangere`), et la page du simulateur le dit
   sous la note des pensions étrangères.

Tests : `tests/js/pension-etrangere-residente.test.js` (six essais) et
`test_la_pension_etrangere_de_qui_reside_en_france_dit_ses_prelevements`,
vus rouges avant le code. Aucun témoin de simulation ni de page ne bouge.

**Exemple.** Né le 15 mars 1958, salarié du privé depuis 1980, parti en
avril 2022, résidant en France, pension suisse de 1 500 € par mois : la
pension française passe du taux médian de CSG au taux plein (prélèvements de
7,66 % à 9,36 %) ; la pension suisse paie 9,1 %, 137 € par mois, que le modèle
ne prélevait pas ; l'impôt 2026 de la pension française passe de 910 € à
3 058 € ; le taux de remplacement après impôt au départ, de 71,5 % à 66,1 %.

**Reste, déclaré dans la limite 5 ante ter (1).** Les conventions ne sont pas
lues État par État : la CSG est prélevée même sur une pension que sa
convention réserve à l'État qui la paie, souvent celle d'un ancien
fonctionnaire de cet État ; la saisie ne dit pas si la pension est publique.
La CSG déductible se retire l'année même, non l'année suivante. Ni l'impôt de
l'État source, ni ses cotisations sociales.
