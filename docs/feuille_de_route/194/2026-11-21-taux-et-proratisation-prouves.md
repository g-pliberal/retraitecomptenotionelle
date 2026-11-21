# Action 194 : le taux et la proratisation, trois parties prouvées

Le 21 novembre 2026. Session sur Opus 5.5, comme Gilles l'a choisi pour ces
briefs (le dépôt voudrait Fable 5.2) ; un point consulté auprès d'une session
Fable 5.2. Posée sur la décote prouvée, non publiée à son début : à publier
après elle.

## Ce qui est fait

**Le découpage** (rangement, aucun résultat ne bouge) : la fiche
`taux_plein_et_proratisation` a quatre versions à la date d'effet :
`avant_l_ordonnance_de_1982` (supposée, la période du régime), `cent_cinquante`
[1983-04-01, 2004) (R. 351-6 de 1985, article 70-5 du décret n° 45-179),
`decret_de_2004` [2004, 2026) (la table du II pour les nés avant 1948, la durée
requise ensuite ; le décret n° 2007-614 a levé la borne de 2008 avant qu'elle ne
joue), `decret_de_2025` depuis 2026 (le II supprimé, maintenu par R. 351-39 pour
les plus de 75 ans au 1er janvier 2026, donc tous les nés avant 1948). La
version de 2026 dans LEGI a perdu la ligne de 1947 ; le décret publié la garde.

**Une grandeur sur un relevé entier** (`tests/test_oracle.py`) : les cas
`releve_entier` mesurent aussi `pension_base_sur_sam`, `taux_liquidation`,
`trimestres_valides`. Test posé à la main : 0,5 × 147 / 156.

**Trois grilles indépendantes**, 58 cas
(`grille_taux_et_proratisation_cent_cinquante`, 13 ; `_decret_de_2004`, 33 ;
`_decret_de_2025`, 12). La carte compte 22 parties prouvées.

## Comment la grille s'est faite

Une session sans le code (`/mnt/project-files/justesse/2026-11-21-taux-et-proratisation-prouves/aveugle/`)
a reçu 40 cas (naissance, date d'effet, salaires au plafond), le plafond et le
SMIC, les index LEGI et JORF ; elle a trouvé seule ses textes et proposé 20 cas.
Un guetteur fanotify, qui note le processus, n'a vu aucune lecture de sa part
dans les copies du dépôt ni dans le dossier partagé.

## Les écarts

- L'année de l'effet : elle retient, à la lettre, le salaire des trimestres
  clos validant jusqu'à quatre trimestres ; la caisse (circulaire 2004/29, point
  2121) limite le compte aux trimestres civils clos, sa seconde lecture. Retenu
  celle de la caisse, chiffrée dans l'énoncé.
- Deux cas avec surcote, hors grille.
- Quatre cas d'une pension prise longtemps après l'âge du taux plein, sans
  activité depuis : la session indépendante, et une session Fable 5.2 de
  mémoire, ne comptent depuis 2004 que les trimestres accomplis (R. 351-7) ;
  le moteur majore chaque trimestre écoulé. Un fil dédié a lu la caisse : la
  circulaire 2004/20 (point 11, la majoration « est indépendante du fait
  d'avoir exercé ou non une activité professionnelle ») et l'exposé Cnav
  d'avril 2026 (« par trimestre écoulé ») donnent raison au moteur
  (`/mnt/project-files/ecarts/2026-11-21-majoration-apres-taux-plein-pas-d-ecart.md`).
  La grille retient la caisse, et chiffre l'autre lecture dans l'énoncé.

## Coût

Quatre commits par-dessus la décote, 12 fichiers ; une session aveugle de
quinze minutes, une consultation Fable ; deux heures et demie en tout.
