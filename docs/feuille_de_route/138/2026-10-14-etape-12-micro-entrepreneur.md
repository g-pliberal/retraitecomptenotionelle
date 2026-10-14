# Étape 12, deuxième partie : le micro-entrepreneur saisi par son chiffre d'affaires, et le chemin de la Cipav

**Le 14 octobre 2026, la demande.** Session de nuit, la seule sur les pages et
la saisie : le micro-entrepreneur par son chiffre d'affaires et le chemin de la
Cipav, rang moyen du classement du 9 octobre (`2026-10-09-classement-par-poids.md`),
« les deux côtés, par la saisie » : l'utilisateur reconstituait son revenu sans
l'abattement, et le registre le disait de modele-ti (`referents.yaml`, chantier
« 138.12 »).

**Ce que dit le droit, lu le jour même** (journal de veille du 14 octobre ;
fiche neuve `micro_social_abattement`). L. 613-7, II : « Les prestations […]
sont calculées sur la base de leur chiffre d'affaires ou de leurs recettes
après application d'un taux d'abattement de 71 % », pour la vente, « de 50 % »
pour les services commerciaux ou artisanaux, « de 34 % » pour les recettes
libérales ; les mêmes que le micro-fiscal (CGI, 50-0 et 102 ter, dès 2007).
D. 613-4, b : la section de la Cipav, 34 % d'abattement, 23,2 % de taux global.
Service-public (F23369) nomme les professions que la Cipav garde.

**Ce qui est fait.**

- *La saisie, dans les deux moteurs* (`saisie.py`, `saisie.js`) : un champ
  `micro`, `ACTIVITES_MICRO` — vide, le revenu déjà abattu, le sens d'avant,
  que toutes les adresses existantes gardent ; `vente`, `services`, `liberal`,
  `cipav`. Une ligne de micro-entrepreneur lit alors son revenu comme un
  chiffre d'affaires mensuel ; `Saisie.abattu` l'abat au seuil du modèle, dans
  `parcours` et `emploi_retraite_declare`, et route la Cipav vers
  `profession_liberale` (CNAVPL et Cipav). `niveaux` garde le nombre saisi,
  pour que la bascule d'unité le traduise sans l'abattre ; en net, le chiffre
  d'affaires passe tel quel, ni brut ni net. Le refus d'un revenu hors des
  bornes du modèle les redit en chiffre d'affaires. L'adresse porte `micro`
  quand il est dit ; une activité dite sans ligne de micro-entrepreneur ne
  change rien et ne se refuse pas.
- *Les pages* (`pages.js`) : le menu « Micro-entrepreneur, vous saisissez »
  sous les périodes, présent dès qu'une période ou l'activité après le départ
  est de micro-entrepreneur ; le champ « Chiffre d'affaires mensuel » ou
  « Recettes mensuelles », « abattu de 71 % » ; la bascule net/brut qui laisse
  le chiffre d'affaires tel quel, l'avertissement de conversion qui ne le
  compte pas ; par la pension, le revenu trouvé dit aussi le chiffre
  d'affaires, et le lien de reprise l'écrit dans les champs qui le relisent.
- *Mesuré* : 2 000 € de ventes par mois, né en 1975, de 2009 à 2039, profil
  plat, valent la pension d'un revenu saisi de 580 € (2 894 € par an au
  scénario 1), au lieu de celle de 2 000 € (12 594 €) que la même saisie
  donnait avant ; 2 000 € de recettes à la Cipav, celle d'un libéral à
  1 320 € (7 306 €).
- *Les témoins* : quatre simulations (`micro_entrepreneur_vente`, `_services`
  en net, `_liberal` en multiples, `_cipav`), que le portage retrouve au bit
  près sur les 808 ; deux pages, `simuler_micro_entrepreneur`, au formulaire
  figé entier, et `simuler_micro_entrepreneur_par_pension`. Quatre tests dans
  `test_web_saisie.py`. Au registre, le point de modele-ti passe à `repris` ;
  les fiches du régime et du statut le disent.

**Ce qui reste.**

1. *Le revenu qui valide les trimestres* : service-public le prend au
   versement — 12,3 % × 43,45 % pour la vente en 2026, soit 0,299 du chiffre
   d'affaires —, le modèle au revenu abattu (0,29). L'écart du registre le
   porte ; le texte qui le fixe reste à lire.
2. *La cotisation des comptes notionnels* : celle du commerçant reproduit le
   taux global de la vente, par construction ; celles des services, du
   libéral et de la Cipav s'en écartent, à mesurer contre D. 613-4 et ses
   versions.
3. *Une activité par carrière* : le champ vaut pour toutes les périodes de
   micro-entrepreneur ; une carrière qui change d'activité se saisit en revenu
   abattu.
4. *Le menu ne paraît qu'après un premier calcul* : le formulaire est rendu, et
   rien ne le montre au choix du statut ; le script de la page pourrait le
   faire.
5. *Les bornes du modèle* : 0,1 fois le salaire moyen au moins, soit 1 226 €
   de ventes par mois ; un petit micro-entrepreneur est refusé, comme un petit
   revenu l'était.
6. *L'abattement minimal de 305 €* n'est pas opposé.
