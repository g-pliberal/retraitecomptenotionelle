# CALIPER et `calcul_pension` : deux mentions périmées

**Le 11 octobre 2026 : la reprise de l'action et le registre des sources
disent ce que le registre des modèles sait depuis le 4 octobre.**

- *La question.* Le propriétaire a trouvé le dépôt de la DREES,
  `gitlab.com/DREES_code/public/outils/calcul_pension`, et demandait s'il
  réglait l'accès à CALIPER, dont le site ne répondait pas. C'est l'adresse
  du registre des modèles (`calcul_pension`, `data/reference/referents.yaml`) :
  cloné le 1er octobre, lu le 4 au commit `ec5a871`. Ce jour-là, la page de
  la DREES, lue par WebFetch quand `curl` recevait une page anti-robot,
  disait que CALIPER « a été réécrit en R » et que son code était celui-là.
- *Ce qui était périmé.* Le bloc « Reprise » de l'action demandait encore de
  « relire la page de la DREES sur CALIPER, quand son serveur répondra » ; le
  registre des sources rangeait `drees_caliper` et `drees_calcul_pension` en
  `a_explorer`. Les deux lignes passent en `explore`, datées du 4 octobre,
  avec ce qu'elles ont donné et ce qui en reste ; la reprise ne garde de
  CALIPER que son communiqué de 2021, dont le dépôt n'a pas l'adresse.
- *La mesure du jour.* Sur le GitLab, par `git ls-remote` et un clone sans
  contenu, rien n'étant exécuté : `main` est toujours à `ec5a871`, du
  20 janvier 2023 ; `dev`, `racl` et `3-cas-types-du-cor` portent des
  commits que `main` n'a pas (12, 7 et 11), tous de 2022, non lus.
  `scripts/fetch/sonder_sources.py` : le GitLab répond, le site de la DREES
  toujours pas. L'accès déclaré de `drees_caliper`, `session`, est donc
  démenti ; il reste en l'état, aucune classe de
  `docs/exploration_sources.md` ne disant « WebFetch seul », et Chromium
  n'ayant pas été essayé.
- *Ce que le GitLab ne règle pas.* Il ne rend pas à CALIPER ce qui faisait
  son prix : sa validation sur les pensions réelles de l'EIR 2004 (chantier
  138.14) demande des données qu'on ne lit qu'au CASD. Et `calcul_pension`
  est figé avant la réforme de 2023, dans la famille de TRAJECTOiRE : un
  accord avec lui ne vaut qu'une confirmation. La liste des simplifications
  de CALIPER, que sa ligne du registre des sources promettait à
  `docs/limites/`, n'y a pas été confrontée.
