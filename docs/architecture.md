# Architecture du dépôt

*Version 5.5, décidée par le propriétaire le 25 septembre 2026. Ce document
dit l'état de l'architecture : il reste vrai tant qu'aucune décision ne le
change, et la liste de ses changements est en bas (« Les versions »). Il est
tiré de la note de décision
[`docs/decisions/0001-architecture.md`](decisions/0001-architecture.md), la
« note 0001 », gelée, qui garde en plus ses récits : pourquoi cette
architecture (son § 1), et comment elle a été éprouvée (son § 14). La
numérotation est la sienne. Les chiffres datés qu'elle donne sont ici des
ancres, qu'une sonde recalcule, ou des renvois à elle ou au tableau de bord
(§ 9.3).*

*Comment le lire.* Une session courte lit L'essentiel, le § 13 et l'annexe C.
Où en est le dépôt, ce qui ne va pas encore et ce qui reste à faire ne
s'écrivent pas ici : c'est le tableau de bord (§ 9.1).

## L'essentiel

Le dépôt calcule des retraites françaises : sous le droit en vigueur (le
scénario 1, qui sert d'étalon) et sous la proposition (les scénarios 2 à 6),
pour une personne (le site) comme pour la population (la page Coût), des
carrières commencées en 1930 aux départs de 2070.

**Neuf principes, au cœur du noyau (§ 13.1)**

1. **Tout le droit des retraites est dans le périmètre.** Ce qui n'est pas
   encore calculé est déclaré comme tel dans la carte des règles, jamais
   ignoré en silence.
2. **Une information a un seul endroit.** Tout le reste y renvoie ou en est
   fabriqué.
3. **La référence est le texte qui crée le droit, tel que la caisse
   l'applique.** Viennent ensuite les exemples officiels, puis les autres
   modèles et résultats publics (OpenFisca, les barèmes de l'IPP, Destinie de
   l'INSEE, TRAJECTOiRE de la DREES, les cas types du COR…), chacun sur ce
   qu'il couvre, puis notre modèle. Aucun ne fait autorité sur la loi : on ne
   s'écarte de l'un d'eux que si la législation, telle que la caisse
   l'applique, montre qu'il se trompe, et la fiche en garde la preuve.
   La proposition n'a pas de texte en vigueur : sa référence est son propre
   texte, puis les notes de décision.
4. **Une implémentation fait foi : aujourd'hui, le Python.** Les autres, dont
   le JavaScript du site, en sont la copie étape par étape, écrite à la main
   ou produite d'une source commune. Toutes s'échangent les mêmes données entre
   étapes, et les témoins garantissent qu'elles donnent les mêmes chiffres.
5. **Le temps est explicite.** Chaque version d'une règle dit à quelles
   situations elle s'applique, par des bornes sur des dates nommées. Les
   versions d'une règle forment un partage, sans trou ni chevauchement qui ne
   soit déclaré (« sans droit », exception).
6. **Les règles se combinent par des relations déclarées** — plafond,
   exception, priorité, dépendance, choix du plus favorable, cumul, ordre —,
   datées comme elles, et jamais par des conditions cachées dans le code.
7. **La personne est une chronologie datée, dans un réseau de personnes
   liées.** Ce qu'on ne sait pas est présumé, et la présomption est affichée ;
   ce que la loi décide à défaut est écrit dans la règle.
8. **Le moteur acquiert, puis liquide.** Pour chaque demande, il construit le
   relevé des droits qu'elle fait valoir, puis il liquide. Un échéancier
   appelle ce calcul aux seuls événements qui ouvrent, révisent ou
   transforment un droit ; il fait vivre chaque pension à chaque événement,
   pour chaque personne concernée.
9. **Chaque scénario est un univers de droit.** Le droit réel en est un.
   Chaque scénario de la proposition en est un autre, posé sur lui en couches
   qui retirent, remplacent ou ajoutent des règles, et relié à lui par des
   règles de transition déclarées.

**Trois règles de conduite.**

- Restructurer ne change aucun résultat.
- Rien de ce qui porte une information ne se perd : tout se déplace, et un
  fichier ne se retire que si son contenu existe ailleurs à l'identique.
- Ce qu'on apprend n'est jamais bloqué. Une source entre toujours, ce
  qu'elle révèle est déclaré, et seuls une régression ou un problème caché
  arrêtent un envoi (§ 9.2).

Le noyau (§ 13) ne change que par une décision écrite et validée. Y ajouter un
champ facultatif n'en demande pas. Les listes de valeurs et les dates nommées
vivent à côté du noyau : on les allonge, elles aussi, sans décision.

**Où va quoi**

| Pour… | on écrit dans… |
|---|---|
| une version parue au *Journal officiel* | si seule une valeur change : la table datée du paramètre. Sinon : la fiche de la règle (version, textes, exemples, ligne d'historique), ses deux fonctions et `reformes.yaml` ; les témoins changent dans un commit à part |
| corriger notre lecture d'un texte | la version existante, sur place ; son historique dit l'effet sur les témoins (§ 4.10) |
| une décision de justice qui change le droit appliqué | une version nouvelle, qui cite la décision (§ 4.10) |
| dire comment deux règles se combinent | une fiche de relation, datée |
| une date qu'une règle lit et que le vocabulaire n'a pas | le vocabulaire des dates, sans décision, si elle entre dans l'une des quatre sortes (§ 4.2) |
| une série (prix, salaires, démographie, mortalité) | `data/reference/macro` ou `data/reference/mortalite`, et sa source dans `data/sources.yaml` |
| décrire un régime | le fichier du régime |
| prendre en compte une situation personnelle | un fait ou un lien de la chronologie, avec sa présomption par défaut, puis le gabarit d'un domaine (§ 11) |
| modéliser un comportement (partir au taux plein…) ou une population | le pilote, hors du moteur |
| écrire un scénario de la proposition | son univers de droit : ses couches et ses règles de transition. Une variante est une couche de paramètres |
| confronter le modèle à un autre modèle public | le registre des autres modèles, qui ne garde que leurs sorties (§ 3.4) |
| interroger un simulateur officiel | à la main, dans le budget de ce simulateur ; la réponse devient un exemple officiel cité (§ 3.5) |
| trancher une divergence entre deux sources | la fiche, avec la preuve de chaque lecture et ce qui a tranché (§ 3.3) |
| noter un choix de modélisation | une note de décision |
| ajouter ou retirer un registre ou un mécanisme de contrôle | d'abord une note de décision (§ 13.4) |
| corriger une vue fabriquée (la veille, les limites, l'inventaire) | jamais la vue : la fiche, puis on régénère |
| changer une adresse du site, un paramètre d'adresse ou une variable de thème | d'abord une note de décision : c'est la surface publique (annexe C) |
| raconter ce qui a été fait | le message de commit |
| savoir où l'on en est, ce qui ne va pas encore, ce qui reste à faire | le tableau de bord, fabriqué (§ 9.1) ; la feuille de route n'y ajoute que ce que la carte ne sait pas dire |
| une source nouvelle : un texte, un exemple, une série, une remarque | le registre des sources, où elle entre toujours ; ce qu'elle révèle, déclaré là où il va (§ 9.2) |
| changer le texte du site | le site, en JavaScript seulement |

---

## 2. Le périmètre : tout le droit des retraites

Chaque domaine ci-dessous sera couvert. La colonne du milieu dit où en est le
dépôt, que le tableau de bord détaille (§ 9.1) ; celle de droite, ce que la
couverture demande à l'architecture.

| Domaine | Aujourd'hui | Ce que la couverture demande |
|---|---|---|
| Régimes, droits propres | <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->91<!--/--> lignes d'inventaire : <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=modelise)-->35<!--/--> modélisées, <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=partiel)-->39<!--/--> partielles, <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=hors_champ)-->15<!--/--> hors champ, <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=routage)-->2<!--/--> routages | compléter les partielles ; ouvrir les hors champ (Alsace-Moselle, fonctionnaires de Mayotte, anciens régimes coloniaux, ORTF, Crédit foncier…) |
| Enfants | un nombre ; naissances présumées aux <!--chiffre:valeur(data/reference/vocabulaire/valeurs.yaml:listes.presomptions.valeurs.naissance_des_enfants.valeur)-->30<!--/--> ans de l'assuré | naissances et adoptions datées, et la date prévue d'une naissance ; qui élève l'enfant ; interruptions d'activité ; accord des parents, parents de même sexe, retrait de l'autorité parentale |
| Périodes assimilées | en partie (chômage, maladie, maternité, AVPF…) ; apprentissage, stages, sportifs de haut niveau, TUC, congé de naissance non appliqués | chaque période datée, avec son motif ; validations rétroactives |
| Temps partiel | quotité non saisie | quotité de chaque période ; surcotisation |
| Départs anticipés | carrière longue, catégories actives, militaires : oui ; parents de trois enfants de la fonction publique : non ; handicap : hors modèle | tous, dont incapacité permanente, pénibilité, amiante |
| Invalidité, inaptitude | hors modèle | périodes d'invalidité, pension d'invalidité et sa conversion, retraite pour invalidité des fonctionnaires, inaptitude |
| Réversion | hors modèle | conjoints successifs datés, décès, ressources, partage entre ex-conjoints, règles de chaque régime, orphelins |
| Plusieurs départs, cumul emploi-retraite, seconde pension, retraite progressive | hors modèle : une seule liquidation, à une date | un départ par régime ; activité après le départ ; fraction de pension ; pension définitive |
| Rachats, versements, surcotisation | hors modèle | actes datés de l'assuré, avec leur coût |
| Carrières hors de France | absentes | périodes par pays et par convention ; totalisation et prorata ; pensions étrangères |
| Minimum vieillesse (ASPA) | barème d'une personne seule, sans condition de ressources | ressources, résidence et composition du foyer ; récupération sur la succession |
| Prélèvements sur les pensions | taux plein (<!--chiffre:mesure(prelevement_pension)-->9,1<!--/--> %) pour tous | revenu fiscal du foyer, pour les exonérations et les taux réduits |
| Revalorisation après le départ | faite (action 112) | s'y ajoutent les mesures qui visent les pensions déjà versées et les composantes temporaires |
| Droit futur, droit passé non retrouvé | le dernier texte, appliqué tel quel ; des barèmes « prêtés » aux années sans texte | versions supposées, déclarées comme telles |

Trois conséquences.

- **Le formulaire grandit par blocs facultatifs.** Les questions de base
  restent ; chaque domaine ajoute un bloc qu'on n'ouvre que si l'on est
  concerné. Ce qui n'est pas saisi est présumé (§ 5.6).
- **La proposition doit trancher chaque domaine,** et chaque droit en cours
  à la bascule (une réversion attendue, une retraite progressive, une
  invalidité pas encore convertie). Ce sont des décisions politiques : la
  carte en tient la liste (§ 8).
- **La page Coût suit.** Chaque domaine ajoute sa dépense ; la réversion, en
  particulier, rapproche le périmètre du modèle de celui de la dépense DREES,
  à laquelle la page se compare.

---

## 3. Les références et la preuve

### 3.1 La hiérarchie

1. **Le texte qui crée le droit**, tel que la caisse l'applique : loi, décret,
   arrêté, accord national interprofessionnel (Agirc-Arrco), statuts approuvés
   (caisses libérales), et les décisions de justice qui l'interprètent ou le
   changent ; son application se lit dans les circulaires de la caisse. C'est
   la définition même du scénario 1.
2. **Les exemples chiffrés officiels** (Cnav, service-public, caisses), qui se
   rejouent : `tests/temoins/exemples_officiels.yaml`.
3. **Les autres modèles et résultats publics**, chacun sur ce qu'il couvre
   (§ 3.4).
4. **Le modèle.**

Quand la caisse, le texte et le juge ne lisent pas la même chose, la fiche
garde les lectures et dit laquelle le scénario 1 retient.

Pour les scénarios 2 à 6, la hiérarchie est plus courte : le texte de la
proposition (`README.md` aujourd'hui), puis les notes de décision qui le
précisent domaine par domaine (§ 8), puis le modèle.

### 3.2 La preuve

Tout ce qui décide d'un résultat porte sa preuve, et une machine la vérifie :

- **un texte du *Journal officiel* ou de LEGI** : son identifiant, sa
  version, et la citation exacte qui fonde la lecture. Un script retrouve la
  citation mot pour mot dans cette version, dans l'index de la DILA ;
- **un texte hors du *Journal officiel*** (accord, statuts, circulaire, fiche
  service-public, publication) : sa référence, son adresse, sa date de
  lecture, et une copie datée. La copie reste dans `data/brut/`, que git
  ignore, quand la source en interdit la rediffusion ; son empreinte, elle,
  est versionnée. Le script retrouve la citation dans la copie ;
- **une valeur d'une table datée** : son fichier source et son empreinte. Le
  script de certification contrôle chaque valeur. Il le fait déjà pour les
  séries du dépôt (note 0001, § 14.8).

Une lecture sans preuve n'est pas une lecture : « une déduction n'est pas une
lecture ; une mémoire n'est pas une source », dit déjà `CLAUDE.md`. Ce qu'un
script ne peut pas vérifier, le sens d'un texte, s'écrit dans la fiche à côté
de sa citation, pour qu'un lecteur le contrôle d'un coup d'œil.

### 3.3 Trancher une divergence

Deux sources, deux registres, ou le code et un texte, peuvent se contredire :
pendant la migration comme après. On procède toujours de même :

1. on énonce le point exactement : la règle, la version, la valeur, les
   dates ;
2. on réunit chaque lecture avec sa preuve (§ 3.2) ;
3. la hiérarchie tranche (§ 3.1) : le texte tel que la caisse l'applique
   l'emporte sur l'exemple officiel, l'exemple sur les autres modèles, et tous
   sur le nôtre ;
4. la fiche garde les lectures, leurs preuves et ce qui a tranché ; le tableau
   de bord le montre ;
5. si aucune source ne tranche (deux circulaires qui se contredisent, un texte
   que la caisse n'applique pas encore), le point reste ouvert, et déclaré. Le
   scénario 1 suit ce que la caisse applique quand c'est documenté ; sinon, le
   résultat montre le doute. Jamais de choix en silence ;
6. pendant la migration, trancher ne change aucun résultat dans le même
   commit. Si la lecture retenue déplace des chiffres, c'est un commit à part,
   avec le diff de ses témoins.

Aucune architecture ne garantit zéro erreur : les textes sont ambigus, les
sources se trompent, des données manquent. Celle-ci garantit autre chose :
aucune affirmation sans preuve vérifiable, aucune divergence tranchée sans
écrire pourquoi, et toute erreur retrouvable et corrigeable, parce que chaque
chiffre remonte à son texte.

### 3.4 Les autres modèles

Aucun modèle ne fait autorité sur la loi. Chacun confirme ou contredit, sur
ce qu'il couvre, et un écart se tranche par la preuve (§ 3.3). Un registre,
`data/reference/referents.yaml`, tient pour chacun :

- ce qu'il couvre (régimes, règles, années), et la version confrontée ;
- ce dont il dépend : deux modèles qui partagent une source ne comptent que
  pour une confirmation ;
- comment on le confronte : des paramètres à comparer, un calcul à rejouer,
  des résultats publiés à retrouver ;
- ses conditions d'usage. Un code sous GPL, EUPL ou AGPL s'exécute à part, et
  seules ses sorties entrent au dépôt, qui est sous licence Apache. Un
  simulateur officiel ne se balaie pas sans l'accord de la caisse ;
- les écarts trouvés, et qui avait raison, preuve à l'appui.

Une version de fiche est **établie** quand elle est lue dans son texte (§ 3.2)
et confirmée par au moins une source indépendante : un exemple officiel, un
modèle indépendant, un résultat publié. Le tableau de bord compte ces
confirmations (§ 9.1).

Les sources recensées, par usage. Leur version et leur étendue au jour du
recensement, le 25 septembre 2026, sont dans la note 0001 (§ 3.4 et 14.9) ;
le registre des autres modèles les tiendra à jour.

| Usage | Source | Ce qu'elle apporte | Ce dont elle dépend |
|---|---|---|---|
| paramètres | les barèmes de l'IPP (Licence Ouverte) | leurs fichiers sur les retraites, dont une partie cite son texte | c'est la source des paramètres d'OpenFisca-France-Pension et de TRAJECTOiRE : un accord entre eux ne compte qu'une fois |
| indépendants | `modele-ti` de l'Urssaf (publicodes, MIT) | cotisations, trimestres, points de la CNAVPL, de la Cipav et du RCI ; une partie des règles cite sa source | indépendant |
| pension entière | Destinie 2, de l'INSEE (GPL) | régime général, fonctionnaires de l'État et des collectivités, indépendants, Agirc-Arrco, réversion, minimum vieillesse ; le droit jusqu'à sa dernière mise à jour | règles et paramètres pour l'essentiel indépendants de l'IPP |
| cas types, régimes spéciaux et libéraux | TRAJECTOiRE, de la DREES (EUPL) | un second code, en mode cas types | paramètres de l'IPP |
| pension entière, profils simples | OpenFisca-France-Pension (AGPL) | les familles de régimes qu'il couvre (§ 3.5), sur des paramètres figés | paramètres de l'IPP |
| agrégats | les données de la DREES (EIR, EACR), puis les cas types du COR | montants par génération, effectifs, taux de remplacement | la DREES recalcule les cas types du COR avec TRAJECTOiRE |
| exemples ponctuels | les simulateurs officiels anonymes : âge légal, carrière longue, réversion… | le droit tel que la caisse l'applique | indépendants ; leurs conditions d'usage limitent l'extraction |
| une autre transcription des textes | Catala (Apache 2.0) : les conditions d'âge de départ, codées pour les aides au logement | les mêmes articles, lus par d'autres, à confronter aux nôtres | indépendant |
| le droit d'avant 2013 | PENSIPP, de l'IPP (sans licence) | les règles du régime général et de la fonction publique de 1946 à 2011, millésime par millésime | paramètres de l'IPP ; se lit, ne se copie pas |
| les prélèvements sur les pensions | LexImpact, sur OpenFisca-France (AGPL) | la CSG, la CRDS et la CASA selon le revenu fiscal du foyer, là où le modèle applique <!--chiffre:mesure(prelevement_pension)-->9,1<!--/--> % à tous | OpenFisca-France |

Toute source garde sa place, même vieillie ou dépendante d'une autre : elle
vérifie, elle comble un manque, et son écart se tranche par la preuve. Le
registre dit seulement ce qu'elle vaut comme confirmation. Catala l'a déjà
montré dans les deux sens, sur l'âge légal d'une génération : sa règle
s'écartait du texte qu'elle recopie, et ce texte n'était plus le droit, que
le modèle applique (le cas, chiffré à sa date : note 0001, § 3.4).

**Les licences, en pratique.** Le code du dépôt est sous licence Apache 2.0 ;
le site et la documentation sous CC BY-SA 4.0 ; chaque donnée suit la licence
de sa source. Une licence régit du code et des fichiers, pas des faits : un
montant, une date, un texte de loi ne sont à personne. Trois cas :

- **les licences permissives** (Apache pour Catala, MIT pour `modele-ti`,
  Licence Ouverte pour les barèmes de l'IPP et l'open data des caisses) : on
  peut copier, en citant la source et la licence, et pour la Licence Ouverte
  la date de mise à jour ;
- **les licences à réciprocité** (GPL pour Destinie 2, EUPL pour TRAJECTOiRE,
  AGPL pour OpenFisca et LexImpact) : on les exécute à part, et on ne garde
  que leurs sorties. Copier leur code, ou leurs fichiers de paramètres, ferait
  passer le dépôt sous leur licence. Qui modifie un code AGPL et le sert en
  ligne doit en publier la source ;
- **sans licence** (PENSIPP) : on le lit et on le cite, on ne le copie pas.
  L'exécuter ou le réutiliser demande l'accord de l'IPP.


### 3.5 Les simulateurs officiels, sans se faire bloquer

Les simulateurs des caisses disent le droit tel qu'elles l'appliquent : c'est
la source la plus précieuse, et la mieux gardée. Leurs conditions limitent
l'usage à la consultation (Agirc-Arrco), à un usage personnel (CNRACL, MSA),
à l'extraction d'une partie non substantielle (Assurance retraite, service des
retraites de l'État), ou interdisent toute rediffusion (info-retraite).
L'Assurance retraite protège ses pages par un reCAPTCHA « contre les logiciels
automatiques ». La règle, fixée par le propriétaire le 25 septembre 2026,
est d'en tirer le plus possible sans jamais solliciter les caisses : ni
demande d'exemples ou de jeux d'essai, ni demande d'accord, ni demande de
documents au titre du droit d'accès. Quatre voies, dans cet ordre :

1. **Ce qu'ils publient déjà, librement réutilisable.**
   - L'open data de l'Assurance retraite, sous Licence Ouverte ; les
     statistiques du service des retraites de l'État, sur data.gouv.fr.
   - Les fiches de service-public.fr, sous Licence Ouverte.
   - Les circulaires et leurs exemples chiffrés.
   - Les fiches « Traitements algorithmiques » que la loi oblige les
     administrations à publier (article L312-1-3 du code des relations entre
     le public et l'administration).
2. **Interroger à la main, peu et bien.** Une personne saisit les cas de
   bascule que fabrique la carte (§ 4.1), un par borne : chaque saisie teste
   une règle à l'endroit où elle change. Chaque réponse entre comme exemple
   officiel, ponctuel et cité : le simulateur, la date, la saisie, le
   résultat. Un budget par simulateur, tenu dans le registre, garde l'ensemble
   loin d'une extraction substantielle.
3. **Comparer une carrière réelle.** Le propriétaire compare la sienne à
   « Mon estimation retraite », et des volontaires peuvent faire de même s'ils
   y consentent : c'est l'usage personnel que les conditions permettent.
   Aucune donnée personnelle n'entre dans le dépôt, seulement l'écart trouvé et
   la règle qu'il met en cause.
4. **Jamais d'automate**, même lent : pas de captcha contourné, pas de
   robot. Un robots.txt permissif ne lève pas des conditions
   d'utilisation qui l'interdisent.

**OpenFisca, précisément.** Le moteur du dépôt n'est pas OpenFisca. OpenFisca
y sert deux fois :

- **OpenFisca-France** fournit des séries que le *Journal officiel* ne rend pas
  directement : le plafond de la Sécurité sociale de certaines années, le point
  d'indice d'avant 1996, le SMIC d'avant 1997 et d'après 2017, le barème du
  minimum garanti ;
- **OpenFisca-France-Pension** est une seconde implémentation, rejouée sur des
  profils simples dans les familles qu'il couvre : régime général,
  pension civile (État et CNRACL), Arrco d'avant 2019, Agirc, Ircantec. Les
  confrontations ont trouvé des erreurs des deux côtés : les nôtres sont
  corrigées, et là où l'erreur est la sienne, le dépôt suit la loi (leur
  compte à sa date : note 0001, § 3.5).

Chaque fiche de règle porte sa correspondance avec chacun de ces modèles
(variable, paramètre, ou « aucune »), et tout écart y est justifié par une
preuve. La comparaison ne se limite plus à quelques profils : elle s'étend,
paramètre après paramètre, à tous ceux qui existent des deux côtés, et d'abord
aux barèmes de l'IPP, lus à leur source plutôt que dans la copie d'OpenFisca.
Un cliquet compte les paramètres pas encore comparés ; un écart trouvé est
déclaré dans la fiche, et ne bloque rien (§ 9.2).

---

## 4. Le temps

C'est le cœur du scénario 1. Les règles changent sans cesse, et un droit se
juge à la version de la règle qui lui est applicable.

### 4.1 Ce qu'une version dit d'elle-même

- **Ses textes.** Chacun est désigné par un identifiant stable (LEGIARTI ou
  LEGITEXT, JORFTEXT ou JORFARTI, ELI, ECLI pour une décision de justice) et
  porte sa date d'entrée en vigueur. À défaut seulement, il est désigné par sa
  référence et son lieu de publication, déclarés comme tels : accord publié
  hors du *Journal officiel*, statuts d'une caisse, règlement, loi du pays,
  article d'un code abrogé que l'index ne contient pas.
- **Sa date de publication** : celle du texte qui la fait naître. Quand elle
  cite plusieurs textes, elle désigne celui-là (`nee_de`) : une version de 2011
  qui cite encore l'article de 2004 n'était pas connue en 2004. C'est l'axe de
  ce qui était publié, et à quelle date (§ 4.9). Tant que la date du *Journal
  officiel* n'est pas renseignée, on prend l'entrée en vigueur de ce texte. La
  date à laquelle une version est entrée dans le dépôt, git la connaît : on ne
  l'écrit pas.
- **Son statut.**
  - *Lue* : elle repose sur un texte lu.
  - *Supposée* : le texte du passé n'a pas été retrouvé, ou celui de l'avenir
    n'est pas écrit. Elle énonce alors son hypothèse et sa fiabilité.
    L'hypothèse peut ne porter que sur une borne. L. 351-3 fait ainsi entrer
    une règle en vigueur « à une date fixée par décret, et au plus tard le 1er
    novembre 2026 ».

  Une version lue peut en outre être **inapplicable** : son texte est en
  vigueur, mais il attend un décret, qu'elle déclare requis. Tant que ce
  décret n'est pas publié à la date d'observation, la version qu'elle suspend
  continue de s'appliquer, comme la caisse le fait pour l'écrêtement du
  minimum garanti. Être inapplicable dépend donc de la date d'observation : ce
  n'est pas un statut figé.

  Une version que le modèle ne sait pas encore calculer n'est pas
  inapplicable : sa fiche est dans l'état *approchée* (§ 6.1), et
  l'approximation y est écrite avec son effet.
- **Ses bornes.** Chaque date qui la rend applicable a son intervalle [début,
  fin) (§ 4.2). C'est le seul endroit où s'écrivent ces dates : la date d'effet
  d'un texte, sa fin, les pensions qu'il vise s'y traduisent toutes. Un décret
  de juillet 2024 fixe des âges pour des pensions dès le 1er septembre 2023 :
  cela s'écrit en borne sur la date d'effet de la pension, borne qui commence
  avant la publication.
- **Ce qu'elle vise.** Soit les pensions qui prennent effet dans ses bornes.
  Soit les pensions déjà servies, pour les échéances comprises dans ses bornes
  (la loi du 14 avril 2023 le fait pour certains points agricoles). Cela dit
  quelle étape l'applique : la liquidation, ou la vie de la pension (§ 7.4).
- **Sa durée**, pour un effet temporaire : un malus de trois ans.
- **Ses unités et ses arrondis** (§ 4.6).
- **Son contenu.**
  - Ce qu'elle accorde ou exige, et à qui.
  - Sous quelles conditions, y compris celles qui comparent deux dates de la
    personne, comme l'enfant né avant la radiation.
  - Ses défauts légaux (§ 5.6).
  - Les paramètres qu'elle lit, chacun avec la date qui décide de sa valeur :
    l'année de la génération, celle de l'ouverture du droit ou celle du revenu.
    Destinie, le modèle de l'INSEE, a dû corriger en 2011 un barème lu sur la
    génération au lieu de l'année d'ouverture des droits.
- **Ses exemples officiels**, ou la déclaration qu'on n'en a trouvé aucun.

Les versions d'une même règle forment un **partage**. Pour toute combinaison
possible de ces dates, une version et une seule s'applique ; le vocabulaire
(§ 4.2) dit quelles combinaisons ne le sont pas, comme un enfant né après la
date d'effet de la pension. Un test parcourt la grille des dates, et il
fabrique du même coup les cas de bascule, juste avant et juste après chaque
borne. Les deux erreurs suivent la logique de Catala, le langage de l'Inria qui
écrit la loi en code :

- **aucune version** qui s'applique est une erreur, sauf si la fiche déclare
  « sans droit » pour ces dates, et dit pourquoi ;
- **deux versions** qui s'appliquent sont une erreur, sauf si l'une se déclare
  exception de l'autre ; trancher un tel conflit est un acte
  d'interprétation, qui revient à la lecture des textes, pas au code.

Le partage doit tenir **à chaque date d'observation** (§ 4.9), pas seulement
aujourd'hui. Une version close parce qu'une autre lui succède ne l'est qu'une
fois celle-ci publiée : avant, on ignorait qu'elle finirait. La version qui
ferme une borne se déduit d'ordinaire des bornes : c'est l'une de celles qui
commencent là, et la borne vaut dès que l'une d'elles est connue. On ne
l'écrit (`fermee_par`) que lorsque ce n'est pas le cas. Une version sans texte
(supposée, « sans droit ») est connue à toute date d'observation. Le test
vérifie le partage à chaque date où une version paraît. Une version
inapplicable ne crée pas de chevauchement : elle laisse la place à celle
qu'elle suspend.

Les tables datées disent de même **jusqu'où leur dernière valeur est connue
valable** (OpenFisca-France l'écrit `last_value_still_valid_on`) : au-delà, la
valeur reprise est une hypothèse, et le résultat le dit. Chaque valeur porte
aussi sa date de publication, quand on la connaît (§ 4.9).

### 4.2 Les dates qui décident

Une date qui décide est une date de la chronologie, ou une date qu'une fiche
calcule à partir d'elle.

Il y en a **quatre sortes**, et cette liste est fermée : elle ne s'allonge que
par une note de décision. Les dates elles-mêmes sont tenues dans un fichier de
vocabulaire, `data/reference/vocabulaire/dates.yaml`, chacune avec son nom (`enfant.naissance`, `conjoint.deces`,
`liquidation.date_effet`…). On y en ajoute sans décision, pourvu qu'elles
relèvent d'une des quatre sortes. Chaque date vaut pour l'assuré comme pour
une personne liée, désignée par le lien qui l'y rattache : la naissance de
l'enfant, le décès du conjoint.

| Sorte | Les dates | Exemples |
|---|---|---|
| **la date d'un fait** | naissance, réelle ou prévue ; adoption ; décès ; entrée dans un métier ou un régime ; titularisation ; sortie d'un régime (radiation, cessation) ; décision médicale (invalidité, inaptitude, consolidation) ; début ou fin d'une période ; chaque jour d'une période, l'année d'un revenu ; un acte de la personne (demande, option, renonciation, rachat) ou de la caisse (notification) | fonction publique : quatre trimestres par enfant né avant 2004, deux pour un enfant né depuis ; RATP : régime fermé aux recrutés à partir du 1er septembre 2023 ; L. 351-3 : les enfants nés depuis le 1er janvier 2026, « ainsi que […] les enfants nés avant cette date dont la naissance était censée intervenir à compter de cette date » ; chômage non indemnisé : quatre trimestres au plus pour les périodes d'avant 2011, six depuis ; Ircantec : la validation, faite sur demande pour qui a été radié avant 1990 |
| **la date d'un lien** | début ou fin d'une union, d'une filiation, d'une éducation, d'une aide | réversion d'un fonctionnaire : deux années de services au moins entre le mariage et la cessation d'activité, ou un mariage d'au moins quatre années, ou un enfant issu du mariage (L. 39 CPCMR) ; au régime général, la réversion se partage entre ex-conjoints « au prorata de la durée respective de chaque mariage » (L. 353-3 CSS) |
| **la date d'une liquidation** | la date d'effet de la pension dans ce régime ; celle d'une autre liquidation, désignée par son régime, son motif et sa nature ; l'échéance d'une pension servie | formule de calcul, valeur du point ; la première pension de vieillesse de base, dont dépendent les règles de cumul ; points agricoles : arrérages dus depuis le 1er septembre 2023, pour des pensions prises avant |
| **une date dérivée**, calculée par une fiche à partir des autres | la génération ; un âge atteint ; le jour où des conditions sont réunies ; la date où un droit est acquis | âge légal, réforme de 2023 et sa suspension ; régimes spéciaux : les décrets de 2023 gardent les anciennes règles à qui les remplissait déjà ; Agirc-Arrco : la majoration pour enfants dépend de l'année d'acquisition des points ; décret n° 2011-2103 : l'année où est atteinte la durée de quinze ans « applicable antérieurement » |

Le vocabulaire dit aussi quelles combinaisons ne se présentent pas (un enfant
né après la date d'effet de la pension). Une date dérivée a sa fiche, qui la
calcule sous une version nommée (§ 7.5).

Deux versions d'une même règle peuvent se lire sur des dates différentes. La
majoration de durée d'assurance de 1972 et de 1975 se lit à la date d'effet de
la pension, celle de 2010 aussi à la naissance de l'enfant. Une version peut
aussi en lire plusieurs à la fois (annexe A).

### 4.3 Les droits maintenus

Un droit supprimé reste acquis à qui remplissait ses conditions à temps :
l'agent recruté à la RATP avant le 1er septembre 2023 garde le régime
spécial ; les bonifications de conduite de la SNCF se sont fermées à qui
entrait après 2008, pas aux autres. Ces maintiens s'écrivent comme des bornes
de version (« entré avant le… », « conditions réunies avant le… »), jamais
comme des exceptions dans le code.

### 4.4 Les droits créés après coup

Depuis le 1er septembre 2023, les TUC des années 1980 valident des
trimestres. Le dépôt le notait déjà : « le droit applicable à une année de
carrière a changé quarante ans après cette année-là ». La version entre en
vigueur en 2023 et couvre des faits des années 1980 : ses dates ne se suivent
pas, et le moteur doit savoir rejouer ce cas.

### 4.5 Les pensions déjà liquidées

Une pension est fixée par les règles de sa date d'effet. Elle ne bouge ensuite
que par une **liste fermée d'exceptions**. Chacune est portée par une version
qui dit ses dates, et si des rappels sont dus ou un indu répété :

- les revalorisations (le modèle les applique depuis l'action 112 : gel de
  2014, cinq coefficients selon le montant en 2020) ;
- une mesure qui vise expressément les pensions déjà versées ;
- une révision, automatique ou sur demande ;
- une suspension, une réduction ou un ajout dus à un fait postérieur : le
  cumul avec des revenus, une nouvelle union pour certaines réversions, l'aide
  d'une tierce personne ;
- une annulation ;
- un plancher, comparé à une liquidation qui n'a pas eu lieu (§ 7.3) ;
- une composante temporaire qui s'éteint, comme le malus de l'Agirc-Arrco,
  que le modèle écarte aujourd'hui parce qu'il ne calcule qu'une pension
  annuelle unique.

### 4.6 Unités, arrondis, ancrages

La chronologie garde la date au jour quand elle est connue. Chaque version dit
trois choses, qui changent elles aussi d'une version à l'autre :

- dans quelle unité elle compte : jour, mois, trimestre, semestre, année ;
- comment elle arrondit : « une année entamée comptant entière », au
  trimestre supérieur… ;
- depuis quand elle compte : des trimestres civils, ou des trimestres courus
  depuis le jour où les conditions sont réunies.

Deux approximations d'aujourd'hui tombent ainsi : la pension qui part le mois
de l'anniversaire au lieu du 1er du mois suivant, et une règle de septembre
2026 appliquée dès janvier.

### 4.7 Les hypothèses

Les départs simulés vont jusqu'en 2070, et des textes anciens n'ont pas été
retrouvés. Une version *supposée* le dit, avec son hypothèse (« le dernier
texte reste en vigueur », « le barème de 2011 vaut avant ») et sa fiabilité.
Les hypothèses sur l'économie (croissance, emploi, prix) sont traitées de
même. Le résultat liste toutes les hypothèses qu'il a utilisées. La suspension
de la réforme de 2023, qui court jusqu'au 1er janvier 2028, en est le premier
cas.

### 4.8 Les univers de droit

Un **univers** est une suite de jeux de versions dans le temps, reliés par des
règles de transition. Chaque scénario en est un :

- **le droit réel** (scénario 1) ;
- **la proposition rétroactive** (scénarios 2 et 4) : une autre loi, appliquée
  depuis l'origine, « comme si la règle avait toujours existé » ;
- **la proposition prospective** (scénarios 3 et 5) : le droit réel jusqu'à la
  bascule, puis une règle de transition — la valorisation des droits acquis —
  et la nouvelle loi ;
- **la proposition libérale** (scénario 6) : le compte rétroactif du
  scénario 4 jusqu'à la bascule, puis ses propres règles.

Un univers s'écrit comme une **couche nommée**, posée sur le droit réel, qui
reste intact. Une couche fait six choses :

- **garder** des fiches ;
- **ajouter** une fiche ou une relation : le compte notionnel, la
  capitalisation, la garantie vieillesse n'existent pas dans le droit réel ;
- **remplacer** une version ;
- **neutraliser** des fiches ;
- **changer** un paramètre ;
- **ajouter** une règle de transition.

Chaque opération vise une fiche nommée, ou un **sélecteur** : une étape, un
domaine, une face, un régime, la contributivité. OpenFisca écrit ainsi ses
réformes : une réforme peut ajouter, remplacer, mettre à jour ou neutraliser
une variable, et modifier des paramètres.

Les couches se composent, comme les scénarios se définissent déjà : le
scénario 4 est le 2 plus la part patronale, le 5 est le 3 plus la même part.
Les réglages du site sont des couches de plus, et le droit supposé (§ 4.7)
aussi : on peut toujours en changer l'hypothèse.

- Les couches **s'empilent dans l'ordre que l'univers déclare**, pas chaque
  couche : la même couche « part patronale » se pose sur le scénario 2 pour
  faire le 4, et sur le 3 pour faire le 5. Chacune agit sur le résultat de
  celles d'en dessous. Deux couches qui touchent la même fiche sans ordre
  déclaré sont refusées par un test.
- Une couche dit **depuis quand** elle agit, et sur quelle date elle le lit :
  la date d'effet de la pension, la date d'un fait, ou l'échéance.
- Une fiche **neutralisée** n'accorde rien, et les relations qui la visent
  passent à leur possibilité suivante (§ 6.4). Si toutes le sont, la relation
  n'accorde rien : c'est voulu, ce n'est pas une erreur.
- Une couche peut **ne valoir que pour un calcul** : la liquidation fictive
  « au contributif seul » de la bascule. Ce calcul est celui que nomme la
  transition qui emploie la couche. L'univers déclare, comme pour les autres,
  où elle se pose dans sa pile, d'ordinaire juste sous la transition ; le
  calcul voit toutes les couches d'en dessous.
- **Aucune règle ne passe d'un univers à l'autre en silence.** Pour chaque
  univers de la proposition, un test liste les fiches du droit réel qu'aucune
  couche ne garde, ne remplace ni ne neutralise, par leur nom ou par un
  sélecteur. Ce sont les domaines sans décision (§ 8). Une fiche ajoutée
  demain au droit réel y apparaît d'elle-même, au lieu de se glisser sans
  qu'on le voie dans les scénarios 2, 4 et 6.
- La pile se résout quand on fabrique les données, qui gardent les dates de
  publication : la date d'observation filtre les versions au moment du calcul
  (§ 4.9). Les réglages du site n'y ajoutent que des paramètres et des
  neutralisations.

La valorisation des droits acquis est **une fiche comme les autres**, avec ses
choix déclarés (âge de conversion, décote neutralisée, proratisation,
revalorisation) et ses tests. C'est une liquidation fictive globale, qui lit
le relevé et l'état arrêtés à la bascule — y compris une retraite progressive,
une réversion attendue ou une invalidité en cours. Le relevé montre ensuite,
ligne par ligne, ce que la bascule garde, convertit ou retire : le scénario 3,
par exemple, retire les avantages non contributifs. Cela se lit sans rien
écrire de plus : une ligne gardée se retrouve telle quelle, une ligne
convertie par sa filiation, une ligne retirée par la couche qui la
neutralise. C'est une explication, pas
une preuve, car la valeur d'un trimestre n'est pas additive : la preuve est la
fiche de valorisation et ses tests.

### 4.9 La situation et l'observation

Toute question se pose à deux dates :

- **la date de situation**, à laquelle on arrête les droits ;
- **la date d'observation**, qui fixe l'état du droit connu : ce qui était
  publié à cette date.

Elles coïncident presque toujours, mais pas dans deux cas :

- **Par défaut, l'observation est fixe.** On la choisit en fabriquant les
  données, et toutes les liquidations voient le même droit. Une loi
  rétroactive s'applique alors d'emblée, depuis sa date d'effet.
- **Dans l'échéancier, elle peut glisser.** Chaque événement observe alors le
  droit publié à sa date, et la publication d'une loi rétroactive devient un
  événement, avec ses rappels ou son indu (§ 7.4). On peut ainsi refaire un
  calcul tel qu'il aurait été fait avant une loi rétroactive, et reconstituer
  ce qui a été versé. Les modèles de l'INSEE (Destinie) et de l'IPP (PENSIPP)
  savent appliquer « la législation d'une année donnée » ; les bases de
  données temporelles appellent cela deux axes indépendants.

Les versions, et les valeurs des tables datées, portent donc leur date de
publication (§ 4.1). Le journal de l'échéancier porte lui aussi les deux axes :
chaque entrée dit quand elle a été inscrite, et sur quelle période elle vaut
(§ 7.4).

Chaque résultat publié — une page, une simulation partagée, un relevé — porte
en outre les **empreintes** de la carte des règles, du code et des données qui
l'ont produit (§ 13.3). Les témoins les gardent à part, hors de ce qu'on
compare au bit près : sinon chaque commit les réécrirait tous, et aucune
réorganisation ne passerait (§ 12).

### 4.10 Une réforme, une correction, une décision de justice

- **Une réforme** est un ensemble de versions nouvelles, datées ensemble ;
  `reformes.yaml` les relie.
- **Une correction de notre lecture** n'est pas une version : le droit n'a pas
  changé, notre transcription était fausse. Elle modifie la version existante,
  et l'historique de la fiche la note avec son effet sur les témoins.
- **Une décision de justice qui change le droit appliqué** est une version
  comme une autre : une question prioritaire de constitutionnalité qui abroge,
  un arrêt qui écarte un texte contraire au droit européen. Elle cite la
  décision par son ECLI. Ses bornes sont celles que la décision fixe, ou à
  défaut celles où la caisse l'applique, et elle dit si elle vaut pour les
  pensions déjà liquidées. Une décision qui ne fait qu'interpréter est une
  lecture : la fiche la garde avec les autres (§ 3), et dit si le scénario 1
  la suit.

---

## 5. Les personnes et leurs faits

### 5.1 Un réseau de personnes

La réversion dépend de la carrière d'un conjoint ; l'ASPA et les prélèvements
dépendent des ressources du foyer ; certaines règles lisent même une troisième
personne (le nouveau conjoint du survivant, l'autre parent d'un orphelin, la
personne aidée). La chronologie porte donc un **réseau de personnes**, chacune
avec ses propres faits. Elles sont reliées deux à deux par des **liens typés
et datés** : union (mariage, PACS, concubinage), filiation, adoption,
éducation, aide. Chaque lien porte son rôle, son intervalle et, s'il le faut,
le régime qui le lit. N'importe quelle personne peut être celle dont on calcule
les droits : le conjoint décédé, pour une réversion. Toute date d'un fait ou
d'un lien d'une personne liée peut décider (§ 4.2).

Sur ce point, on s'écarte volontairement d'OpenFisca : il regroupe des
individus dans des entités fixes (familles, foyers), alors qu'une vie de
retraite fait et défait les liens — mariages, divorces, décès.

Chaque fait dit **d'où il vient** :

- déclaré, par la personne ou par un relevé déposé ;
- présumé ;
- simulé, par le pilote (§ 7.7).

Deux choses ne sont pas des faits de la chronologie, parce qu'elles n'y
auraient pas de date d'inscription et échapperaient à la règle d'information
(§ 7.3) :

- ce qu'une règle inscrit en cours de calcul va au journal, signé de la
  règle (§ 7.4) ;
- un résultat connu sans être calculé entre là où il aurait été calculé
  (§ 5.5).

Un fait est **connu**, par défaut, à mesure qu'il se produit : un événement à
sa date, une période jour après jour. Un fait appris plus tard le dit
(`connu_le`) : une période déclarée après coup, un relevé corrigé. C'est cette
date que lit la règle d'information (§ 7.3).

### 5.2 Des périodes

Chacune a un début et une fin :

- **activité** : métier, statut, grade et corps, régime, revenu, quotité,
  pays et territoire ; plusieurs activités peuvent se cumuler ;
- **périodes assimilées**, avec leur motif : chômage indemnisé ou non,
  maladie, maternité, accident du travail, invalidité, service militaire,
  apprentissage, stage, TUC, aide à un proche, congé parental, congé de
  naissance… ;
- **périodes à l'étranger** : pays, convention applicable ;
- **résidence**, pour les droits qui l'exigent ;
- **après un départ** : activité en cumul, retraite progressive.

### 5.3 Des événements et des actes

Chaque **événement** a une date : naissance (et, s'il le faut, la date où
elle était prévue), décès, recrutement, titularisation, radiation, décision
médicale (invalidité, inaptitude, incapacité, consolidation, handicap, avec
leur taux), exposition professionnelle.

Un **acte** est un événement que la personne choisit : demande, option,
renonciation, rachat, versement, accord des parents. Il porte son délai et
dit s'il est irrévocable. Un départ est l'acte de demander sa pension dans un
régime, à une date, pour un motif. La caisse a aussi ses actes, comme la
notification d'une décision.

### 5.4 Les ressources et les pensions d'ailleurs

Ressources et foyer fiscal, patrimoine : ce sont des faits datés. Une pension
étrangère, elle, est une liquidation observée (§ 5.5), avec son âge
d'ouverture. Chaque règle qui additionne des
ressources nomme son **assiette**, dans une fiche, parce que chaque texte
additionne autre chose.

Tout montant porte **sa monnaie** : anciens francs, francs, euros, franc CFP.
Les changements de monnaie sont des versions comme les autres, et les
conversions se font en un seul endroit.

### 5.5 Les résultats observés

Un résultat peut être connu sans être calculé : la pension d'un conjoint
décédé, une pension étrangère, les trimestres d'un relevé de carrière qui
font foi. Il entre **là où il aurait été calculé**, avec l'origine
« observé », et nulle part ailleurs (principe 2) :

- une pension observée est une liquidation du journal (§ 7.4), inscrite par
  un événement « liquidation observée ». Une pension étrangère qui arrive
  trois ans après le départ est un événement de plus : il révise l'écrêtement
  du minimum contributif, qui la compte (L. 173-2) ;
- des trimestres qui font foi sont des lignes du relevé (§ 7.6).

Le relevé des droits et le résultat le signalent.

### 5.6 Les présomptions, et ce que la loi décide à défaut

- **Une présomption** remplace un fait inconnu. Elle a un nom, une valeur et
  une raison, que le vocabulaire porte (`presomptions`, dans
  `data/reference/vocabulaire/valeurs.yaml`), et le fait qu'elle pose le dit
  (C.1). Les présomptions d'aujourd'hui deviennent les valeurs par défaut, si
  bien que les résultats ne bougent pas tant que rien de nouveau n'est
  saisi :
  - enfants nés aux <!--chiffre:valeur(data/reference/vocabulaire/valeurs.yaml:listes.presomptions.valeurs.naissance_des_enfants.valeur)-->30<!--/--> ans de l'assuré ;
  - radiation au 1er janvier suivant ;
  - agent présumé en activité ;
  - pas d'accord des parents ;
  - validation de l'Ircantec présumée demandée.
- **Un défaut légal** n'est pas une présomption : c'est la loi qui décide
  quand la personne n'a rien fait. Il s'écrit dans la version de la règle,
  parce qu'il change avec elle. Au régime général, les trimestres d'éducation
  vont à la mère à défaut d'accord depuis 2010. Depuis 2013, ils se partagent
  par moitié entre deux parents de même sexe (L. 351-4, annexe A).
- **Pour chaque règle qui dépend d'un fait inconnu**, la fiche choisit :
  présumer, demander, ou calculer les deux cas et montrer l'écart. Les écarts
  se calculent un fait à la fois, les autres restant présumés, et jamais en
  combinant tous les cas : quatre faits inconnus font cinq calculs, pas seize.
- **En population**, une présomption devient un tirage, pas une moyenne : les
  minima et les plafonds ne sont pas linéaires.
- Le résultat liste les présomptions qu'il a utilisées.

### 5.7 D'où viennent les faits

- **Le formulaire** : les questions de base, puis un bloc facultatif par
  domaine.
- **Le relevé de carrière déposé** : l'année, le régime, le revenu porté au
  compte et les trimestres retenus, rien de plus — ni le mois, ni la part de
  primes, ni le statut de cadre.
- **Les présomptions** pour le reste.

---

## 6. La carte des règles

### 6.1 Une fiche par dispositif

Un fichier par règle, dans `data/reference/regles/`. Une règle est un
**dispositif** : ce qu'un même ensemble d'articles accorde ou exige. Ses
réécritures successives forment ses versions, et aussi l'article qui la
remplace pour les faits nouveaux, comme L. 12 bis après L. 12 b. Deux
dispositifs qui visent le même objet — les trimestres d'enfants du régime
général et ceux de la fonction publique — font deux fiches d'un même domaine.

Une fiche porte d'abord ce qui est **obligatoire** :

- son identifiant : stable, jamais tiré d'un numéro d'article, jamais
  renommé ; une fiche qui disparaît est dépréciée, et renvoie à celle qui la
  remplace ;
- son intitulé, son domaine, l'étape du moteur qui l'applique, les régimes
  concernés ;
- ce qu'elle **lit** et ce qu'elle **écrit** : les faits, les lignes du relevé
  et les résultats dont elle a besoin, et ceux qu'elle produit ;
- sa **face** : un droit, une cotisation ou un financement (§ 7.4, 7.6) ; une
  fiche de financement désigne les fiches qu'elle paie ;
- son **état** : conforme, transcrite, approchée, manquante, pas encore
  modélisée ;
- ses **versions** (§ 4.1).

Le reste est **facultatif**, avec une valeur par défaut. Il devient
obligatoire quand la fiche en a besoin :

- ce qu'elle lit **sous hypothèse**, un résultat qui vient plus loin (§ 7.5),
  et la liste finie des possibilités qu'elle évalue ;
- ses **approximations**, chacune avec son effet connu, ou « non mesuré » ;
  obligatoires dans l'état « approchée », et c'est d'elles que se fabriquent
  les limites du tableau de bord (§ 9.1) ;
- ses **présomptions** ;
- ses **invariants** : les bornes qu'une valeur ne peut pas franchir (un taux
  entre 0 et 1, une durée positive), que les tests vérifient ;
- ses **sources lues** : la date de lecture, la prochaine relecture et les
  lectures divergentes. Les questions ouvertes vont là, où une vue les lit,
  jamais dans un commentaire ;
- ses **cas de bascule**, fabriqués depuis les bornes ;
- son **code** : la fonction Python, sa jumelle JavaScript, les tests ;
  obligatoire dès que la fiche n'est plus « pas encore modélisée » ;
- sa **correspondance avec les autres modèles** (§ 3.4), et les écarts
  justifiés ;
- son **historique** : les récits qui la concernent, repris des registres.

Le minimum reste court : une fiche nouvelle s'écrit en une page, et les tests
disent ce qui lui manque à mesure qu'elle mûrit.

### 6.2 Les relations, fiches à part entière

Dans l'histoire du dépôt, bien des règles dépendent d'une autre (leur part,
à sa date : note 0001, § 14.1). Ces liens ont leur propre fiche, avec leurs
versions. La priorité entre régimes pour les trimestres d'enfants existait
déjà dans la loi du 3 janvier 1975 (article 16), et elle a changé plusieurs
fois depuis 1985 (note 0001, § 6.2). L'ordre entre la surcote et le minimum
contributif a changé au 1er avril 2009.

Une fiche de relation dit :

- sa sorte ;
- les fiches qu'elle relie, et leur rôle (générale ou exception, prioritaire
  ou subsidiaire, ce que le plafond borne) ;
- l'étape où elle s'applique, ou l'échéancier ;
- son rang dans cette étape ;
- ses versions.

La dépendance n'a pas de fiche à elle : elle se déclare dans ce que la fiche
lit (§ 6.1). Les autres sortes rencontrées dans le dépôt :

| Relation | Exemple |
|---|---|
| **plafond** ou **enveloppe partagée**, consommée dans un ordre déclaré | l'écrêtement du minimum contributif ; les trimestres réputés cotisés d'une carrière longue |
| **exception** : une règle en remplace une autre quand ses conditions sont remplies | la catégorie active avance l'âge d'ouverture |
| **priorité** entre régimes | les trimestres d'enfants vont d'abord au régime spécial |
| **dépendance** au résultat d'une autre règle, d'un autre régime ou d'une autre personne | la réversion, calculée sur les droits du conjoint |
| **choix du plus favorable**, avec sa méthode déclarée, la même dans les deux moteurs, et le nombre de calculs qu'elle s'autorise | les deux décomptes de la décote |
| **cumul** ou **non-cumul** | les bonifications, plafonnées ensemble depuis 2023 |
| **séquence** entre périodes | des enveloppes consommées dans l'ordre de la carrière |
| **ordre de composition** | la cascade des avantages : AVPF, puis trimestres d'enfants, puis minima… |
| **ordre des événements d'une même date** | le décès avant la réversion qu'il ouvre |

Chaque étape applique ses relations dans l'ordre que les fiches déclarent.
C'est ce que Catala, le langage conçu à l'Inria pour écrire la loi en code,
rend explicite. C'est aussi ce que `calculer` cache aujourd'hui dans ses
conditions (leur compte, à sa date : note 0001, § 1), et le dépôt l'a appris
à ses dépens : « l'ordre n'est pas indifférent […], et le modèle en prenait
deux à l'envers ».

### 6.3 Les transformations

Certaines règles transforment des droits déjà inscrits :

- la conversion des points d'un régime fermé dans son successeur (l'Arrco en
  1999, l'Agirc dans l'Agirc-Arrco en 2019) ;
- les droits figés d'un régime qui s'éteint ;
- le rétablissement d'un fonctionnaire au régime général ;
- l'annulation d'un droit ;
- la réattribution de trimestres d'une personne à une autre. Depuis le 1er
  septembre 2023, les trimestres d'enfants d'un parent condamné pour un crime
  contre l'enfant, « dont la pension n'a pas encore été liquidée, sont
  attribués à l'autre parent » (L. 351-4) ;
- la valorisation des droits acquis à la bascule.

Ce sont des fiches de **transformation**. Chacune s'applique dans l'étape qui
produit les lignes qu'elle transforme, après elles : le rétablissement à
« coordonner les affiliations », la réattribution des trimestres d'enfants à
« compter les durées », la conversion des points à « acquérir les droits », la
valorisation à la bascule en dernier. Elles produisent de nouvelles lignes du
relevé, sans effacer les anciennes, au nom de la personne qui en bénéficie. Ces lignes
gardent leur **filiation** : la personne, le régime et l'année d'origine, dont
dépend par exemple la majoration de l'Agirc-Arrco, ou la liquidation d'où
elles viennent. La valorisation des droits acquis lit ainsi, au journal, la
liquidation fictive que la transition a inscrite à la bascule, et écrit les
lignes du capital.

### 6.4 Neutraliser une règle

Toute fiche peut être **neutralisée** dans un univers : c'est ainsi qu'on
mesure ce qu'une règle apporte (la cascade des avantages non contributifs, le
calcul « au contributif seul » de la bascule). L'ordre des neutralisations est
déclaré, comme celui des relations.

Neutraliser une fiche ne suffit pas toujours à mesurer ce qu'elle apporte.
Les relations qui la visent passent à leur possibilité suivante : neutraliser
la bonification de la fonction publique ne retire pas les trimestres de
l'enfant, la priorité entre régimes les reporte au régime général. On mesure
alors un transfert, pas un apport. Pour mesurer l'apport, on neutralise
aussi les possibilités vers lesquelles la relation se reporte. Sinon, le
résultat dit qu'il mesure un transfert.

### 6.5 Ce qu'elle remplace

La fiche rassemble ce qui est aujourd'hui dispersé :

- la ligne de `veille.yaml`, que les fiches ont reprise à la phase 2 ;
- les bascules de `frontiere_contributive.yaml` ;
- les commentaires d'en-tête des tables de `data/reference/legislation/` ;
- les récits de `limites.md` et les notes de la feuille de route qui la
  concernent ;
- les commentaires juridiques du code.

Les registres actuels deviennent des **vues fabriquées** à partir des fiches :

- ce qu'il faut relire (la veille) ;
- ce qui est approché, ce qui reste à faire (le tableau de bord, § 9.1) ;
- ce qui a changé de face (la frontière contributive) ;
- la couverture de chaque régime (l'inventaire).

### 6.6 Ne rien oublier : les textes comme liste de contrôle

La carte part des textes, pas de la mémoire.

- **Les articles.** Depuis l'index LEGI du dépôt, on dresse la liste des
  articles qui touchent les retraites : code de la sécurité sociale, code des
  pensions civiles et militaires, code rural, décrets des régimes. On la
  complète des accords Agirc-Arrco et des statuts des caisses. Chaque
  **rédaction** d'un article est rattachée à une version de fiche, ou déclarée
  sans effet sur elle, avec le mot à mot qui le montre.
- **Les situations.** Même chose pour les situations que décrivent les fiches
  service-public et les circulaires des caisses.
- **Le contrôle.** Un cliquet tient le compte des rédactions et des
  situations qui n'ont aucun statut : ni rattachées, ni sans effet, ni « à
  rattacher », ni « à examiner ». Ce nombre ne peut que décroître, et le
  cliquet devient un refus quand il atteint zéro. Le script qui apporte les
  rédactions nouvelles de l'index les inscrit « à examiner », datées : une loi
  nouvelle ne fait donc jamais monter le cliquet, elle allonge ce qui reste à
  faire (§ 9.2). Le dépôt fait déjà ainsi pour les réformes, avec
  `reformes.yaml`.
- **Où elle vit.** Depuis la phase 2, la liste des rédactions est dans
  `data/reference/textes/` : son périmètre déclaré (`perimetre.yaml`, où se
  tient le cliquet), la liste elle-même (`redactions.csv`), et ce que
  `python scripts/textes.py --inscrire` y apporte de l'index. Le statut d'une
  rédaction ne s'y écrit pas : il se lit dans les fiches qui la citent
  (`src/retraite_notionnelle/noyau/textes.py`). Les situations des fiches
  service-public et des circulaires attendent encore leur liste.

La liste a déjà servi, et elle a montré ce que la mémoire laisse passer :
pour écrire l'annexe A, on a comparé mot à mot, dans l'index LEGI, les
rédactions successives de trois articles, et trouvé ce que les fiches d'une
version précédente avaient manqué. La note 0001 (§ 6.6) le raconte,
rédaction par rédaction.

### 6.7 Ce que les tests exigent de la carte

- chaque règle du code a sa fiche, et chaque fiche a son code ou l'état
  « pas encore modélisée » ;
- les versions de chaque fiche et de chaque relation forment un partage, aux
  « sans droit » et exceptions déclarés près ;
- chaque version a au moins un exemple officiel, ou déclare n'en avoir trouvé
  aucun ; un exemple passe, ou porte son écart connu ;
- chaque borne de version produit deux cas de test, juste avant et juste
  après ;
- ce que les fiches lisent et écrivent ne forme aucun cycle, hors les
  lectures sous hypothèse, qui déclarent leurs possibilités ;
- chaque relation désigne des fiches qui existent ;
- chaque fiche peut être neutralisée sans casser le calcul, et dit ce qu'elle
  écrit alors ;
- chaque texte est cité par un identifiant stable, ou, à défaut, par sa
  référence de publication déclarée (§ 4.1) ;
- chaque citation se retrouve mot pour mot dans la version qu'elle cite, et
  chaque source hors du *Journal officiel* a sa copie datée ou son empreinte
  (§ 3.2) ;
- chaque écart à un autre modèle cite sa preuve (§ 3.3) ;
- une étape ne lit d'une autre que les données qu'elles échangent : les
  frontières entre modules, que la DREES a vues « tendre à s'effacer » dans
  son propre modèle, sont tenues par un test ;
- une valeur qu'un moteur ne connaît pas l'arrête : une sorte de fait, un
  motif, une nature ajoutés sans décision (§ 13.3) ne sont jamais traités en
  silence comme une autre ;
- pour chaque univers de la proposition, la liste des fiches du droit réel
  sans décision (§ 4.8) est fabriquée, et la carte la montre.

---

## 7. Le moteur

### 7.1 Des moteurs jumeaux, des étapes qui s'échangent des données

Une implémentation fait foi, aujourd'hui le Python ; le JavaScript est sa
copie pour le site. Les deux ont la même structure, étape par étape et
fonction par fonction, avec les mêmes noms : recopier une règle devient un
geste local. Les versions, les relations et les paramètres sont des données,
écrites une fois et lues par les deux moteurs.

Les étapes portent un nom, pas un numéro : en insérer une ne renumérote rien.
Elles s'échangent des **données** au format JSON, les mêmes dans les deux
moteurs, décrites chacune par un schéma. Le schéma d'une étape s'écrit à la
phase qui la crée, avant tout code. Chaque étape se teste donc seule, se
compare seule entre Python et JavaScript, et pourrait un jour n'être écrite
qu'une fois. C'est la porte de sortie si la recopie devient trop lourde :
Catala, par exemple, produit du Python et du JavaScript à partir d'un même
texte, et publie ainsi une bibliothèque de droit français. Le jour venu, une
étape pourra y passer seule, sans toucher aux autres, et le principe 4 n'aura
pas à changer.

### 7.2 Acquérir

Le scénario 1 quitte `scenarios/actuel.py` pour
`src/retraite_notionnelle/droit/` (et `moteur/js/droit/`), une étape par
module. Pour une demande, quatre étapes construisent le **relevé des droits**
qu'elle fait valoir :

- **préparer la chronologie** : compléter par les présomptions, normaliser
  les dates ;
- **coordonner les affiliations** : rétablissement, interpénétration,
  successions de régimes, liquidation unique des régimes alignés, carrières
  hors de France ;
- **compter les durées** : assurance, cotisée, services ; périodes
  assimilées, enfants et la priorité entre régimes qui les répartit, rachats ;
  plafonds annuels et enveloppes ;
- **acquérir les droits** : points, salaires portés au compte, cotisations.

Le relevé ne se construit pas une fois pour toutes : il dépend de la demande.
La fiche des trimestres d'enfants de la fonction publique lit la date d'effet
de la pension, et d'autres fiches lisent une autre liquidation (§ 4.2). Il
s'arrête à la date d'effet ; ce qui suit l'événement qui appelle le calcul y
est présumé (§ 7.3).

Ces étapes lisent la chronologie du réseau et le journal de l'échéancier
(§ 7.4). Une période assimilée peut venir d'une pension servie : l'invalidité.
Un droit peut s'éteindre par une liquidation : « aucun droit ne peut être
acquis dans un régime de retraite de base après la liquidation d'une seconde
pension de vieillesse » (L. 161-22-1-2, pour les premières pensions prises à
compter de 2027).

L'acquisition parcourt tout le réseau dans l'ordre des dates. Une
transformation déclenchée chez une personne liée écrit ses lignes au nom de la
personne qui en bénéficie, avec leur filiation.

Pour montrer « vos droits » sans demande, à une date de situation, on
construit le relevé d'une demande supposée à cette date. Les lignes qui
dépendent de la date de départ y sont *en attente* (§ 7.6).

### 7.3 Liquider

`liquider(demande, état, contexte)` est une **fonction pure**, qui ne lit rien
d'autre que ses trois entrées. Pour une demande, elle fait l'acquisition
(§ 7.2), puis trois étapes :

- **ouvrir le droit** : âge légal, carrière longue, catégories actives,
  militaires, invalidité, inaptitude, incapacité permanente, handicap,
  amiante, droits maintenus ; taux plein ;
- **liquider chaque régime** : annuités, points, forfait ou capital ; décote,
  surcote, proratisation ; fraction de la retraite progressive, que sa fiche
  tire de la quotité de l'activité gardée ; pension par
  fractions, chacune liquidée sous la version de sa période (le régime des
  cultes en a trois : avant 1979, de 1979 à 1997, depuis 1998) ; prorata
  international ;
- **compléter tous régimes** : minimum contributif et son écrêtement, qui lit
  dans l'état toutes les pensions, françaises et étrangères (L. 173-2) ;
  minimum garanti ; majorations pour enfants ; surcote parentale.

Ses trois entrées :

- **La demande** dit :
  - la personne ;
  - les régimes ;
  - la date d'effet ;
  - l'événement qui l'appelle, et sa date ;
  - le **motif** : vieillesse, invalidité, inaptitude, carrière longue,
    réversion… ;
  - la **nature** : provisoire (retraite progressive), définitive, seconde (la
    pension créée en 2023 pour qui retravaille), fictive ;
  - selon le cas : la liquidation qu'une révision reprend, dont elle garde la
    nature, et la date d'où elle vaut ; le défunt d'une réversion.
- **L'état** est le journal de l'échéancier et la chronologie du réseau, lus
  à la date de l'événement (§ 7.4).
- **Le contexte** dit :
  - l'univers (§ 4.8), dont la fabrication des données a résolu la pile ;
  - la date d'observation (§ 4.9), fixe, ou celle de l'événement dans
    l'échéancier ; elle filtre les versions au moment du calcul ;
  - pour un calcul sous hypothèse, l'hypothèse (§ 7.5).

**La règle d'information.** Des faits et de l'état, `liquider` ne lit que ce
qui est connu à la date de l'événement qui l'appelle : une liquidation ne voit
pas l'avenir, et la révision qui suivra aura quelque chose à réviser. Si la
date d'effet est plus tardive que la demande, l'intervalle est présumé, et une
révision le reprend.

La date d'effet arrête le relevé et, avec les autres dates qui décident
(§ 4.2), choisit les versions. Le motif et la nature changent la décote, la
revalorisation, la réversion et les règles de cumul : les versions peuvent les
lire.

`liquider` peut **s'appeler elle-même** sur des demandes fictives :

- chaque possibilité d'un calcul sous hypothèse (§ 7.5) ;
- un plancher ;
- la pension dont un défunt « eût bénéficié » ;
- la valorisation des droits acquis à la bascule.

Une liquidation d'essai ne va pas au journal. Une liquidation fictive qui
fonde un droit y va, avec sa nature : celle qui valorise les droits acquis à
la bascule, que la transformation lit ensuite pour écrire les lignes du
capital (§ 6.3).

**La réversion n'est pas une étape.** C'est `liquider` pour le survivant, de
motif « réversion », dans les régimes du défunt. Elle lit dans l'état la
liquidation, réelle ou fictive, du défunt, et le partage déjà figé entre ses
ex-conjoints. Le survivant choisit sa date d'effet dans les limites du texte :
au régime général, le premier jour d'un mois, au plus tôt celui qui suit le
décès si la demande vient dans l'année (R. 353-7). Les pensions d'orphelin se
calculent de même.

### 7.4 L'échéancier

Un **échéancier** parcourt les événements dans l'ordre des dates. Chaque
**événement** porte :

- sa date ;
- sa sorte ;
- les personnes concernées ;
- ce qu'il vise : un régime, une liquidation, une allocation ;
- son origine : un acte, le pilote qui le simule, une observation, une règle
  qui l'induit, ou la publication d'une version.

**Aux événements qui ouvrent, révisent ou transforment un droit**, il appelle
`liquider` : un départ, une pension définitive, une seconde pension, une
réversion, une révision (dont un changement de quotité ou de ressources qui
modifie un droit), une annulation, une transformation (dont la bascule d'un
univers). Le vocabulaire dit, pour chaque sorte d'événement, s'il appelle
`liquider`, et avec quel motif et quelle nature. La demande se construit à
partir de l'événement : la personne et ce qu'il vise, le motif et la nature de
sa sorte, et la date d'effet que l'acte choisit, dans les limites qu'une fiche
déclare (R. 353-7 pour une réversion). Les personnes concernées sont celles
que les liens lus par les fiches rattachent à l'événement, jusqu'à la distance
que ces fiches déclarent : le réseau a donc une borne.

**Puis, à chaque événement**, et à chaque date où une composante commence ou
finit, il applique deux étapes qui ne liquident rien. Il les applique dans cet
ordre, après les liquidations du jour, sur toutes les pensions d'un
bénéficiaire ou d'un foyer, tous régimes et droits dérivés compris :

- **faire vivre** : revalorisations, mesures sur les pensions versées,
  composantes qui s'éteignent. La revalorisation de 2020 dépendait du total de
  toutes les pensions reçues, droits dérivés compris : elle ne peut se
  calculer régime par régime ;
- **foyer et net** : l'ASPA, ouverte sur demande, revue à chaque événement
  parce qu'elle voit toutes les ressources, dont la réversion, et récupérée
  sur la succession au décès ; les prélèvements selon le revenu du foyer.

Une fiche qui lit un état antérieur le déclare comme une date qui décide. La
revalorisation de 2020 lisait ainsi le total des pensions « le mois précédent
celui auquel intervient la revalorisation » (loi n° 2019-1446, article 81).
Une revalorisation ne relance jamais la liquidation.

Quatre règles complètent l'échéancier :

- **Les événements d'une même date** se suivent dans l'ordre qu'une relation
  déclare.
- **Une règle peut inscrire un événement**, et le signe. Les revalorisations
  sont des événements que leurs fiches inscrivent à leurs dates ; la bascule
  d'un univers, un événement que sa règle de transition inscrit à la sienne.
  Un événement induit inscrit d'avance attend au journal, avec sa condition,
  et sa fiche peut l'annuler. La pension d'invalidité est remplacée à l'âge légal par la pension
  de vieillesse pour inaptitude. Mais l'assuré qui travaille garde sa pension
  d'invalidité tant qu'il ne demande rien (L. 341-16).
- **La publication** d'une version qui vise des pensions déjà versées est un
  événement, quand l'observation glisse (§ 4.9), avec ses rappels ou son indu.
- **L'état est un journal** : on y ajoute, on n'efface jamais. Chaque entrée
  porte deux dates : son inscription (l'événement qui l'a écrite, et sa date)
  et sa période d'effet. Deux lectures en découlent :
  - l'état à une date est tout ce qui a été inscrit au plus tard ce jour-là ;
  - ce qui est servi pour une période se lit, pour chaque composante, sur la
    dernière entrée de sa lignée dont l'effet la couvre.

  Une composante a un identifiant stable. L'entrée qui la révise la remplace
  (`remplace`) : c'est dans cette lignée que la plus récente l'emporte. Une
  composante s'éteint à la fin de son effet, ou par une entrée qui la remplace
  sans montant (une suspension, un décès). Le journal garde aussi les
  décisions figées (le partage d'une réversion, le régime qui reçoit les
  trimestres d'un enfant) et les sorties des deux étapes qui ne liquident rien.

  Toute entrée dont l'effet commence avant son inscription donne un rappel ou
  un indu : une révision, une loi publiée après sa date d'effet, une pension
  étrangère connue tard. Pour chaque échéance passée, c'est la différence entre
  ce qui est dû sous l'entrée nouvelle, revalorisations refaites, et ce qui a
  été servi. Une révision qui ne vaut que pour l'avenir reprend, elle aussi,
  les revalorisations appliquées depuis le début de la composante :
  l'accroissement d'une réversion partagée ne repart pas du montant de sa
  liquidation.

Un second départ, la pension définitive après une retraite progressive, la
révision d'un minimum ou d'une réversion, l'accroissement d'une réversion
partagée au décès d'un ex-conjoint ne sont donc pas des cas particuliers : ce
sont des événements de plus.

Le résultat n'est pas un nombre mais une **pension en composantes datées** :
base, majorations, minima, malus temporaire, capital versé une fois. Chaque
composante est rattachée à sa fiche, et dit son bénéficiaire. Elle dit aussi
si elle est servie ou seulement calculée : la pension entière d'une retraite
progressive, dont seule une fraction est versée. Elle dit enfin si elle est
en attente, comme un minimum contributif qui attend une pension étrangère,
et de quoi. À chaque échéance, une composante porte ses payeurs et
leurs parts, et dit si elle est contributive, selon les fiches de financement
alors en vigueur : le payeur d'une pension servie peut changer pendant qu'on
la touche.

### 7.5 L'ordre des calculs, les hypothèses, les dates calculées

- L'ordre se déduit de ce que chaque fiche lit et écrit, et des ordres de
  composition que les relations déclarent ; un test refuse les cycles, hors
  les lectures sous hypothèse.
- Parfois une règle a besoin d'un résultat qui vient plus loin. La priorité
  des trimestres d'enfants va, en dernier recours, au régime « qui servirait
  la pension la plus élevée ». Le rétablissement dépend des services comptés
  ensemble. Le moteur calcule alors **sous hypothèse**. La relation déclare :
  - ses possibilités ;
  - les étapes qu'elle rejoue ;
  - l'unité sur laquelle elle décide (l'enfant) ;
  - son critère de cohérence ;
  - le départage que le texte donne.

  Le moteur évalue chaque possibilité par une liquidation d'essai et garde
  celle que la règle désigne. Sa décision est figée au journal, où la
  liquidation d'un autre régime, le même jour, la lit. Aucune possibilité
  cohérente, ou plusieurs sans départage déclaré, c'est une erreur, comme un
  conflit de versions. Deux hypothèses ne s'emboîtent pas sans budget déclaré.
- **Une date calculée l'est sous une version nommée de la fiche qui la
  calcule**, jamais sous la version qu'elle sert à choisir. Le décret
  n° 2011-2103 fixe la durée de services exigée d'un fonctionnaire selon
  « l'année au cours de laquelle est atteinte la durée de services de quinze
  ans applicable antérieurement » : la date se calcule sous l'ancienne règle.
  Un calcul sous hypothèse donnerait ici un résultat faux.
- Le moteur n'efface jamais un résultat produit : il le révise par une entrée
  nouvelle du journal.

### 7.6 Le relevé des droits

Chaque ligne porte :

- la personne qui en bénéficie ;
- le fait et sa date ;
- la règle, sa version et son texte ;
- le droit : quantité, unité, régime ;
- sa **face** : droit, cotisation ou financement. Pour un financement attaché
  à l'acquisition (l'État qui paie les trimestres d'une année), elle porte
  aussi ses payeurs et leurs parts ;
- sa **nature** :
  - *ferme* ;
  - *conditionnelle*, avec la condition qui reste ouverte (un retour dans un
    régime interpénétré annule un rétablissement) ;
  - *en attente*, quand elle dépend de la date de départ ou d'un événement
    (une réversion) ;
- sa **filiation**, pour une ligne issue d'une transformation : la ligne, la
  liquidation ou la personne d'origine ;
- son origine : calculée, ou observée, quand un relevé de carrière fait foi ;
- les présomptions utilisées et la fiabilité.

Le relevé s'arrête à une date de situation, sous un état du droit observé
(§ 4.9). Il sert au calcul, aux tests, à la proposition, et au site : « vos
droits, et d'où ils viennent ».

### 7.7 Le pilote

Hors du moteur, un **pilote** fixe ce que le droit ne décide pas.

- **Les comportements** : partir au taux plein, à l'âge légal, le plus tard
  possible. Le moteur ne devine rien : le pilote l'interroge, au besoin
  plusieurs fois (le point fixe des cas types d'aujourd'hui). Puis il inscrit
  la date de départ comme un acte, dans chaque univers et à chaque date
  d'observation : un même assuré ne part pas forcément au même âge sous deux
  droits différents. Quand il ne lui faut qu'une date d'ouverture ou de taux
  plein, il n'interroge que l'étape « ouvrir le droit ».
- **Les populations** : des cas types pondérés aujourd'hui ; des tirages, des
  couples et des décès simulés demain, comme dans un modèle de
  microsimulation (Destinie à l'INSEE), sans changer le moteur.
- **Les cascades** de neutralisations.
- **Les paramètres qui dépendent d'une population.** Le mécanisme qu'un
  système notionnel ajoute le plus volontiers est un coefficient d'équilibre
  appliqué aux pensions. Sa valeur se tire de l'agrégat de toute une
  population, du même univers. Il vient donc du pilote, déclaré comme tel, et
  entre dans l'univers comme un paramètre daté. Il ne vient jamais du moteur.
  `moteur/js/cout.js` calcule déjà ce coefficient, et dit : « Le modèle le
  calcule ; il ne l'applique jamais. » L'appliquer un jour ne changera pas le
  moteur. S'il se reporte d'une année sur l'autre, le pilote devra le calculer
  année par année, dans l'ordre.

### 7.8 Le budget de calcul

Le temps de calcul se mesure par carrière, une fois les données chargées :
pour le scénario 1 et pour les six scénarios, dans chacun des deux moteurs.
Les références sont celles du 25 septembre 2026, que la note 0001 donne
(§ 7.8).

Le coût à venir ne tient ni à l'échéancier ni au calcul sous hypothèse en
eux-mêmes, mais à trois multiplications, que les règles ci-dessus ferment :

- reliquider à des événements qui n'ouvrent aucun droit, des dizaines de
  fois plus cher (la mesure, à sa date : note 0001, § 7.8) ;
- emboîter des hypothèses ;
- énumérer sans borne dans un choix du plus favorable.

Chaque témoin compte donc ses appels de `liquider`, liquidations d'essai
comprises, et un test refuse qu'il dépasse le nombre déclaré. Chaque phase
refait la mesure dans les deux moteurs, et celle de la suite de tests ; une
phase qui les dégrade s'arrête le temps de les ramener. Le paquet du site se
découpe par domaine et se charge à la demande : le premier chargement ne
grossit pas quand les domaines s'ajoutent.

---

## 8. La proposition, la page Coût, le site

- **La proposition** est faite d'univers de droit (§ 4.8). Pour chaque domaine
  couvert, et pour chaque droit en cours à la bascule, une note de décision
  dit ce qu'elle garde, ce qu'elle convertit et ce qu'elle supprime. La carte
  liste ce qui n'a pas encore de décision : les fiches du droit réel qu'aucune
  couche ne vise (§ 4.8), et les droits en cours à la bascule, comme une
  retraite progressive.
- **La page Coût** passe le même moteur sur une population, par le pilote
  (§ 7.7). Elle tourne aujourd'hui dans le navigateur : le pilote de ses cas
  types est donc écrit dans les deux langages. Une microsimulation de toute la
  population n'y tiendrait pas : la page lirait alors des agrégats fabriqués à
  l'avance. Les faces du relevé et des composantes disent qui paie quoi.
- **Le site** ne contient que la présentation, écrite une fois, en
  JavaScript. Le résultat montre les présomptions, les hypothèses et le relevé
  des droits. Les réglages du site sont des couches de paramètres et de
  neutralisations, appliquées au calcul dans les deux moteurs.
- **Ce que d'autres utilisent** — les adresses du site, les paramètres d'une
  simulation dans l'adresse, les variables de thème qu'un hôte redéfinit — est
  la surface publique (annexe C). `docs/integration-partiliberalfrancais.md`
  promet déjà à un hôte que ces adresses « ne changeront pas sans que ce
  fichier le dise ».

---

## 9. Savoir où l'on en est

### 9.1 Le tableau de bord

Une seule page, `docs/etat.md`, répond à trois questions : où en est-on, ce
qui ne va pas encore, ce qui reste à faire. Un script la fabrique à chaque
changement, depuis la carte des règles, les témoins, les mesures du pilote et
le registre des sources. Personne ne l'écrit à la main (principe 2). Une
correction ne demande donc aucun geste de plus : elle change une fiche, et le
tableau suit.

**L'avancement** se lit sur trois axes.

- **Le droit couvert.** Les fiches par état (conforme, transcrite, approchée,
  manquante, pas encore modélisée), par domaine et par régime. Deux poids
  disent ce que cela représente :
  - les retraités de chaque caisse, que l'enquête EACR de la DREES donne déjà
    au dépôt ;
  - la part de la dépense, que le COR donne pour un domaine hors modèle comme
    la réversion.

  Le dénominateur est la liste de contrôle des textes (§ 6.6) : l'avancement
  se mesure contre la loi, pas contre ce qu'on a pensé à noter.
- **La confiance.** Les versions lues et les versions supposées ; pour
  chacune, le nombre de sources indépendantes qui la confirment (§ 3.4) : un
  exemple officiel, un autre modèle, des résultats publiés ; les écarts
  ouverts avec d'autres modèles ; les relectures à jour.
- **La réorganisation.** La phase en cours (§ 11), les règles du code qui ont
  leur fiche, les registres devenus des vues.
- **Le coût du travail**, mesuré lui aussi :
  - le temps de la suite rapide et de la suite complète ;
  - ce qu'une session doit lire pour chaque sorte de tâche, en lignes ;
  - le nombre de fichiers qu'une modification touche, et combien sont de la
    prose écrite à la main, relevés sur l'historique git.

  Chacun a son budget. La suite rapide tient sous deux minutes. Une règle se
  change dans sa fiche, ses deux fonctions et ses tests ; les vues se
  régénèrent. Aucune prose ne s'écrit à la main hors de la fiche et du message
  de commit. Une phase qui dégrade un budget s'arrête le temps de le ramener,
  comme pour le calcul (§ 7.8).

Ce qui est mécanique, un script le fait : comparer les rédactions d'un
article, vérifier une citation, tester un partage, confronter à un autre
modèle, fabriquer le tableau. Une session ne lit un texte que pour décider.
C'est là que se gagnent le temps et les tokens, sans rien retrancher à la
qualité : le script vérifie tout, à chaque fois, ce qu'une relecture ne
ferait qu'une fois.

Quand chaque ligne du relevé citera sa fiche (phases 4 et 5), un chiffre les
résumera : la part des pensions simulées qui ne passent que par des règles
conformes, cas types pesés par les effectifs. Et comme la page est refaite à
chaque commit, son histoire est dans git : l'avancement devient une courbe, et
non plus une impression.

**Les limites** sont toutes celles que la carte déclare : approximations,
versions supposées, présomptions, domaines hors modèle. Chacune a son effet :

- mesuré par le pilote, qui neutralise ou fait varier la règle sur les cas
  types pesés ;
- ou « non mesuré », et le mesurer devient une tâche.

Elles se classent par effet et par nombre de personnes touchées. Chaque
résultat du site liste en plus les limites par lesquelles il est passé,
puisque ses lignes citent leurs fiches.

**Ce qui reste à faire** se tire de la carte :

- les fiches qui ne sont pas conformes, et les approximations à lever ou à
  mesurer ;
- les textes à rattacher ou à relire, et les relectures en retard ;
- les sources à exploiter, et les saisies à faire dans les simulateurs
  officiels, dans leur budget (§ 3.5) ;
- les versions sans exemple officiel ;
- les décisions que la proposition n'a pas prises (§ 8) ;
- les phases qui restent.

Chaque tâche dit ce qu'elle améliorerait, en personnes touchées et en effet
quand on les connaît. Elle dit aussi qui peut la faire : une session, ou le
propriétaire (une décision politique, une validation, un geste sur GitHub).
La feuille de route ne garde que ce que la carte ne sait pas dire :
l'outillage, le site, les décisions.

Le tableau n'a pas attendu la carte : dès la phase 0, il se fabriquait depuis
les registres. Depuis la phase 2, il lit la carte des règles et la liste de
contrôle des textes, sans avoir changé de questions ; les registres qui ne sont
pas encore des vues le complètent : l'inventaire et les effectifs, les
exemples officiels, les réformes, les sources à explorer, la feuille de route.
Une maquette l'a montré avant la phase 0 (note 0001, § 14.7) ;
`scripts/tableau_de_bord.py` en est tiré. Le coût du travail, qui se relève
sur l'historique git, périmerait la page à chaque commit : il s'affiche à la
demande (`--cout`), hors de `docs/etat.md`.

### 9.2 Ce qu'on apprend n'est jamais bloqué

Une source peut corriger le dépôt : un texte, une circulaire, un exemple
officiel, une série, une version nouvelle d'OpenFisca, une remarque de
lecteur. Rien ne doit l'empêcher d'entrer, pas même le tableau de bord.

- **Une source entre toujours.** Elle est inscrite au registre des sources,
  reçue, puis examinée. Ce qu'elle révèle est déclaré là où il va : une limite
  dans une fiche, un texte à rattacher, une lecture divergente, un écart à un
  autre modèle. Le tableau le montre le jour même.
- **Un test arrête une régression, jamais une découverte.** Il bloque :
  - un résultat qui change sans le diff de ses témoins ;
  - un problème caché : une règle du code sans fiche, un chiffre nu dans une
    prose d'état ;
  - une contradiction : deux versions qui se chevauchent.

  Il ne bloque pas un écart déclaré.
- **Un exemple officiel que le modèle ne reproduit pas entre quand même**, à
  l'état « écart connu », avec la valeur que donne le modèle et l'explication.
  Dans `tests/temoins/exemples_officiels.yaml`, c'est un champ `ecart_connu`,
  qui nomme la fiche déclarant l'écart, et que le tableau de bord
  liste. Le test vérifie que le modèle rend la valeur déclarée : s'il rend la
  valeur publiée, l'écart est corrigé et sa déclaration se retire. L'inverse
  reste interdit : un exemple qui passait ne devient pas « écart connu » en
  silence. Ce serait une régression, et le diff la montre.
- **Les cliquets ne comptent que ce qui n'est pas déclaré**, jamais les
  problèmes connus. Une loi nouvelle ajoute des rédactions à l'index : le
  script qui les apporte les inscrit « à examiner », datées, et aucun cliquet
  ne bouge (§ 6.6).
- **La règle d'arrêt arrête le code, pas l'inscription** (§ 13.4). Un constat
  qui n'entre pas dans le noyau est déclaré avant même que la note soit
  écrite.

Le nombre de problèmes connus peut donc monter : c'est ce qu'on sait de plus,
pas une régression. Le tableau montre les deux, ce qu'on sait manquer et ce
qu'on a corrigé.

### 9.3 Les documents

- **`docs/architecture.md`** : ce document, l'état de l'architecture, avec son
  numéro de version et la liste de ses changements.
- **Les décisions** : `docs/decisions/`, une note courte par choix. La
  première, `0001-architecture.md`, est l'architecture telle qu'elle a été
  décidée, gelée, avec ses récits : pourquoi cette architecture, et comment
  elle a été éprouvée. Ce document en tire l'état, et c'est lui qui vit
  ensuite.
- **L'état** : `docs/methodologie.md` (ce que le moteur calcule, étape par
  étape) et le tableau de bord (§ 9.1).
- **Les archives** : `docs/archives/`, gelées et conservées intégralement : le
  journal et les actions faites de la feuille de route, les récits de
  `limites.md`, l'histoire git de `CLAUDE.md`, le journal de veille.
- **La feuille de route** : ce que la carte ne sait pas dire (§ 9.1).
- **`CLAUDE.md`** : une page, qui renvoie ici. Si un autre outil pilote un jour
  les sessions, un fichier d'entrée à son nom renvoie à la même page.

Les chiffres qui décrivent le dépôt lui-même (lignes, nombre de tests) sortent
de la prose ; un script les affiche à la demande :
`python scripts/tableau_de_bord.py --cout`.

---

## 10. Les tests

1. **Rapides**, ceux qu'on relance en travaillant (moins de deux minutes
   visées) : les règles — exemples officiels et cas de bascule — et les
   étapes, chacune seule.
2. **Complets** : les témoins, joués par les deux moteurs, et les agrégats de
   la page Coût. Les témoins comprennent des simulations, des pages, et des
   **suites d'événements** : un départ, puis un second ; un décès, puis une
   réversion.
3. **Contrôles** : la confrontation aux autres modèles, la certification des
   données, la prose, la carte des règles (§ 6.7). Aucun ne refuse ce qui est
   déclaré (§ 9.2).

Tout tourne sur GitHub à chaque envoi sur `main`, par
`.github/workflows/tests.yml`, dont le verdict se lit dans l'onglet Actions ;
en local, le premier niveau se lance seul, par `python -m pytest -m rapide`.
`tests/conftest.py` range chaque fichier de tests dans son niveau ; un fichier
qu'il ne nomme pas est rapide, puisque c'est d'ordinaire celui d'une règle.
`python -m pytest`, sans rien choisir, joue les trois : c'est le défaut, la
suite qu'on passe avant d'envoyer sur `main`. Les deux tests les plus longs,
les chiffres ancrés et les témoins, sont découpés (leur durée, à sa date : la
note 0001, § 10). Les témoins se découpent par domaine et par étape. Les vues
et les fichiers fabriqués se régénèrent ; ils ne se fusionnent jamais à la
main.

---

## 11. Le chemin

Les phases 0 à 8 réorganisent sans changer un seul résultat ; les domaines
viennent ensuite, un par un.

| Phase | Contenu | Résultats |
|---|---|---|
| 0 | ce document et la note 0001 ; le tableau de bord, depuis les registres d'aujourd'hui ; tests sur GitHub ; suite rapide | inchangés |
| 1 | documentation rangée par nature, contrôle de conservation | inchangés |
| 2 | carte des règles et des relations, depuis les registres existants ; vocabulaire des dates ; contrats de l'annexe C en schémas validés par les tests ; cliquets des textes posés ; le tableau de bord passe à la carte | inchangés |
| 3 | chronologie datée et réseau de personnes, présomptions actuelles par défaut | inchangés |
| 4 | acquisition en étapes et relevé des droits | inchangés |
| 5 | liquidation en fonction pure, journal, échéancier, pilote | inchangés |
| 6 | un fichier par régime ; les interrupteurs deviennent des renvois aux fiches | inchangés |
| 7 | la proposition réécrite en univers de droit | inchangés |
| 8 | texte du site écrit une fois | inchangés |
| 9 et suivantes | un domaine à la fois | changent, commit par commit |

Trois règles tiennent le chemin :

- **Jamais deux sources pour une information.** Ce qui passe dans une fiche
  devient une vue fabriquée dans le même commit. Le pire serait une migration
  arrêtée à mi-chemin, avec l'ancien registre et la fiche vivant côte à côte.
- **Chaque phase vaut seule**, si le chemin s'arrêtait après elle.
- **Le noyau d'abord.** Les phases 2 à 5 et 7 le mettent en place ; les phases
  6 et 8 peuvent attendre sans rien bloquer.

Chaque domaine suit le même gabarit :

- fiches et relations ;
- faits de la chronologie ;
- fonctions dans l'étape ;
- exemples officiels ;
- bloc du formulaire ;
- dépense de la page Coût ;
- décision de la proposition.

L'ordre se fixe par le nombre de personnes concernées, mesuré sur les sources
publiques au moment de choisir. En première lecture, à confirmer par cette
mesure :

1. les dates des enfants ;
2. les périodes assimilées manquantes ;
3. l'invalidité et l'inaptitude ;
4. la réversion ;
5. les départs multiples et la vie après le départ ;
6. les carrières hors de France ;
7. les départs anticipés particuliers ;
8. les rachats ;
9. les régimes hors champ.

---

## 12. Rien de cassé, rien de perdu

**Rien de cassé**

- Une phase de réorganisation (0 à 8) doit reproduire au bit près les
  simulations témoins, les pages et les exemples officiels ; sinon, elle ne
  passe pas.
- Un changement de résultat se fait dans un commit à part, avec le diff de ses
  témoins.
- Un repère git (tag) marque le départ de chaque phase.
- Une seule session déplace des fichiers à la fois ; les autres travaillent
  dans d'autres zones.

**Rien de perdu**

- Rien de ce qui porte une information ne se perd : tout est déplacé, et
  l'annexe B dit où.
- Un fichier ne se retire que si son contenu existe ailleurs à l'identique,
  vérifié. C'est le cas de `web/pages.py` et de `web/gabarit.py`, à la
  phase 8.
- Un script de conservation vérifie que chaque paragraphe des documents et
  chaque entrée des registres d'aujourd'hui se retrouvent dans le nouveau
  rangement. Il se retire après la phase 8, quand plus rien ne se déplace.
  C'est `scripts/conservation.py` : `--depuis HEAD` vérifie un déplacement
  avant qu'on le commite, et un test tient, contre une référence figée
  (`tests/temoins/conservation.json`), les récits, les notes de décision, les
  archives et les entrées des registres.
- L'historique git garde le reste.

---

## 13. La stabilité : ce qui ne bouge pas, et comment on change le reste

### 13.1 Le noyau

Il ne change qu'avec une décision écrite, validée par le propriétaire du
dépôt. Il comprend :

- **les neuf principes** ;
- **neuf contrats de données**, écrits à l'annexe C avec leurs valeurs par
  défaut, et en schémas dans `data/reference/contrats/` :
  - la **chronologie**, faits et liens ;
  - la **fiche**, règle ou relation, et ses **versions** ;
  - la **table datée** d'un paramètre ou d'une série ;
  - la **couche** et l'**univers** ;
  - la **ligne** du relevé ;
  - la **liquidation** et ses composantes ;
  - l'**événement** ;
  - l'**entrée du journal** ;
  - la **surface publique** ;
- **deux règles d'exécution** :
  - le journal est l'état, où l'on ajoute sans effacer, et chaque entrée y
    porte deux dates, son inscription et son effet ;
  - une étape ne lit d'une autre que des données décrites par un schéma ;
- **les étapes, nommées**, les trois entrées de `liquider` (§ 7.3) et la règle
  d'information : une liquidation ne lit rien de ce qui est connu après
  l'événement qui l'appelle ;
- **les quatre sortes de dates qui décident** (§ 4.2) ;
- **la hiérarchie des références**.

Les listes de valeurs n'en font pas partie : sortes de faits, d'événements et
de relations, motifs, natures, statuts, faces, origines, et le vocabulaire des
dates nommées. Elles vivent dans des fichiers de vocabulaire,
`data/reference/vocabulaire/`, qui s'allongent sans décision (§ 13.3).

### 13.2 Le reste

Évolue sans décision, tant qu'il entre dans le noyau :

- ajouter une règle, une version, une relation, un paramètre, une série, une
  date nommée, une sorte de fait ou d'événement, une présomption, un régime,
  un univers, un domaine, un champ facultatif ;
- renommer un fichier ou une fonction ;
- réorganiser l'intérieur d'une étape.

### 13.3 Comment le noyau change

- **La règle additive.** Ajouter un champ facultatif dont la valeur par défaut
  laisse les témoins identiques, ou une valeur à une liste, ne demande pas de
  décision. Renommer, retirer ou changer le sens d'un champ ou d'une valeur en
  demande une. Un moteur qui rencontre une valeur qu'il ne connaît pas
  s'arrête (§ 6.7) : c'est ce qui rend l'ajout sans risque.
- Chaque contrat porte un numéro de version (`schema_version`).
- Un changement du noyau demande trois choses :
  - une note dans `docs/decisions/` : le problème, les solutions écartées, la
    migration ;
  - un script qui convertit tout l'existant d'un coup ;
  - des témoins identiques.
- Ce document porte un numéro de version et la liste de ses changements.
- **La carte a une empreinte**, calculée sur ses fichiers. Son journal est
  fabriqué à partir des historiques des fiches : un test exige, pour chaque
  changement, sa ligne d'historique, avec les périodes et les résultats
  touchés. Un repère git marque les versions qu'on cite. Aucun compteur n'est
  partagé : deux sessions qui changent deux fiches ne touchent pas le même
  fichier. On garde ainsi la discipline d'OpenFisca-France, qui refuse de
  fusionner un changement sans son entrée au journal, mais pas son numéro qui
  monte : ici, les sessions en parallèle s'y heurteraient toutes, comme elles
  se heurtent aujourd'hui dans la feuille de route.
- Les identifiants ne se renomment jamais : on déprécie, on ne casse pas.
  OpenFisca-France change de version majeure à chaque changement qui casse
  ce qui s'appuie sur lui, et son journal parle sans cesse de renommage
  (les comptes, à leur date : note 0001, § 13.3).

### 13.4 La règle d'arrêt

Si un cas n'entre pas dans le noyau, on s'arrête et on écrit la note avant de
coder. On ne contourne jamais le noyau : c'est le contournement qui a produit
les interrupteurs par période des fichiers de régimes, et des registres nés
presque un par jour (leur compte, à sa date : note 0001, § 1 et 13.4). De
même, un registre ou un mécanisme de contrôle n'entre dans le dépôt, et n'en
sort, que par une note.

### 13.5 Ce qui entre maintenant, ce qui attend sans refonte

Le noyau se fixe maintenant pour ce qu'on ne pourrait pas ajouter plus tard
sans reprendre les fiches et les deux moteurs : le sens des contrats, les deux
dates du journal, les entrées de `liquider`, les sortes de dates. Le reste
s'ajoute au fil des domaines, sans décision, par la règle additive, avec une
valeur par défaut qui laisse les témoins identiques.

**Maintenant** :

- les neuf contrats et leurs valeurs par défaut ;
- les quatre sortes de dates ;
- les étapes nommées et les entrées de `liquider` ;
- le partage des versions et son test ;
- la pile des couches.

**Réservé, codé plus tard sans rien refondre** :

- l'axe d'observation : les dates de publication se remplissent peu à peu ;
  la fabrication des données les garde, et l'observation filtre les versions
  au calcul, fixe par défaut, glissante dans l'échéancier ;
- les événements autres que le départ (décès, union, quotité, ressources,
  majorité, publication, événements induits), et les motifs et natures autres
  que « vieillesse » et « définitive ». Seule « fictive » sert tôt, car le
  modèle s'en sert déjà pour valoriser les droits acquis ;
- le réseau de personnes au-delà des enfants ;
- les lectures sous hypothèse : les approximations d'aujourd'hui restent en
  place, déclarées comme telles, jusqu'au domaine qui les remplace ;
- les enveloppes, cumuls et séquences : leur format est fixé, le code migre au
  fil des phases 4 à 6 ;
- le pilote par univers, les couples et les tirages : ils changent les
  résultats, et viennent donc avec les domaines ;
- les listes de contrôle des textes et la confrontation complète aux autres
  modèles :
  des cliquets posés à la phase 2, puis resserrés.

**En JavaScript**, seulement ce que le site fait tourner : le calcul, les
couches de réglage et le pilote de la page Coût. Le site observe à la date de
fabrication des données, et ne résout pas les couches d'univers : la
fabrication l'a fait.

---

## Annexe A — Deux fiches d'exemple : les trimestres des enfants

Écrites le 25 septembre 2026, à partir de ce que le dépôt contenait ce
jour-là — `majoration_duree_assurance.csv` et son en-tête, les entrées de
`veille.yaml` et de `frontiere_contributive.yaml`, le code et les tests — et
des rédactions d'articles lues mot à mot dans l'index LEGI. Les bornes sont
des intervalles [début, fin) ; `null` veut dire « sans borne ». Celles que le
modèle donne à l'année restent à relire au jour près. Elles servent de
gabarit : une fiche cite ses textes par identifiant, écrit ses bornes en
intervalles, jamais en prose, et range ses questions ouvertes dans `sources`,
où une vue les lit.

### A.1 La fonction publique, en entier

```yaml
id: enfants_fonction_publique
schema_version: 1
intitule: >-
  Trimestres des enfants dans la fonction publique : bonification de L. 12 b,
  majoration de L. 12 bis, bonification de L. 12 b ter
domaine: enfants
etape: compter_les_durees
regimes: [fonction_publique, regimes_speciaux]
face: droit
etat: approchee               # deux approximations, plus bas
lit: [enfant.naissance, enfant.mere, recrutement, radiation, liquidation.date_effet]
ecrit: [trimestres_duree, trimestres_services]
# la priorité entre régimes (R. 173-15 : un seul régime accorde, le régime
# spécial d'abord) est une fiche de relation, qui vise celle-ci
dates_qui_decident: [enfant.naissance, liquidation.date_effet]

versions:   # un partage, à chaque date d'observation
  - id: l12b_avant_1964
    statut: supposee
    hypothese: le texte d'avant le code de 1964 n'a pas été relu ; on lui prête la règle de 1964
    fiabilite: faible
    bornes:
      enfant.naissance: [null, 2004-01-01]
      liquidation.date_effet: [null, 1964-12-01]
    contenu:
      droit: 4 trimestres par enfant, en services et en durée
      beneficiaire: la mère
    exemples: aucun trouvé

  - id: l12b_1964
    statut: lue
    textes:
      - {id: LEGIARTI000006362901, article: R. 13, en_vigueur: 1964-12-01}
      - {id: LEGIARTI000006362695, article: L. 12, en_vigueur: 1982-07-14}  # première rédaction de l'index
    nee_de: LEGIARTI000006362901
    bornes:
      enfant.naissance: [null, 2004-01-01]
      liquidation.date_effet: [1964-12-01, 2004-01-01]
    contenu:
      droit: 4 trimestres par enfant, en services et en durée
      beneficiaire: la mère (« en faveur des femmes fonctionnaires »)
    exemples: aucun trouvé

  - id: l12b_2004
    statut: lue
    textes:
      - {id: LEGIARTI000006362696, article: L. 12, en_vigueur: 2004-01-01}
      - {id: LEGIARTI000006362902, article: R. 13, en_vigueur: 2004-01-01}
    nee_de: LEGIARTI000006362696
    bornes:
      enfant.naissance: [null, 2004-01-01]
      liquidation.date_effet: [2004-01-01, 2011-01-01]
    contenu:
      droit: 4 trimestres par enfant né en service
      beneficiaire: >-
        l'un ou l'autre parent, après une interruption d'activité continue
        d'au moins deux mois, dans les seuls congés du statut
    exemples: aucun trouvé

  - id: l12b_2011_decret
    statut: lue
    textes:
      - {id: LEGIARTI000023449727, article: R. 13, en_vigueur: 2011-01-01}
      - {id: LEGIARTI000006362696, article: L. 12, en_vigueur: 2004-01-01}
    nee_de: LEGIARTI000023449727
    bornes:
      enfant.naissance: [null, 2004-01-01]
      liquidation.date_effet: [2011-01-01, 2011-07-01]
    contenu:
      droit: 4 trimestres par enfant né avant la radiation
      beneficiaire: >-
        l'un ou l'autre parent, après une interruption d'activité (la loi) ou
        une interruption ou une réduction (le décret)
    exemples: aucun trouvé

  - id: l12b_2011
    statut: lue
    textes:
      - {id: LEGIARTI000023096747, article: L. 12, en_vigueur: 2011-07-01}
      - {id: LEGIARTI000023449727, article: R. 13, en_vigueur: 2011-01-01}
    nee_de: LEGIARTI000023096747
    bornes:
      enfant.naissance: [null, 2004-01-01]
      liquidation.date_effet: [2011-07-01, null]
    contenu:
      droit: 4 trimestres par enfant né avant la radiation
      beneficiaire: >-
        l'un ou l'autre parent, après une interruption ou une réduction
        d'activité ; le congé de maternité du code de la sécurité sociale est
        admis
    exemples: [sp_f37311_bonification_avant_2004]    # pension de mai 2026

  - id: l12bis
    statut: lue
    textes:
      - {id: LEGIARTI000006362697, article: L. 12 bis, en_vigueur: 2004-01-01}
    bornes:
      enfant.naissance: [2004-01-01, null]
      liquidation.date_effet: [2004-01-01, 2026-09-01]
    contenu:
      droit: 2 trimestres par enfant, en durée seulement
      beneficiaire: la mère, si elle a accouché après son recrutement
    exemples: aucun trouvé

  - id: l12bter
    statut: lue
    textes:
      - {id: LEGIARTI000053280361, article: L. 12 (b ter), en_vigueur: 2025-12-31}
      - {id: LEGIARTI000053280367, article: L. 12 bis, en_vigueur: 2025-12-31}
      - {id: LEGITEXT000053265238, article: "loi n° 2025-1403, article 104", en_vigueur: 2025-12-31}
      - {id: LEGITEXT000054586750, article: "décret n° 2026-699 (CNRACL, FSPOEIE)", en_vigueur: 2026-08-01}
    nee_de: LEGIARTI000053280361
    bornes:
      enfant.naissance: [2004-01-01, null]
      liquidation.date_effet: [2026-09-01, null]
    contenu:
      droit: 2 trimestres par enfant, dont 1 en services
      beneficiaire: la mère, si elle a accouché après son recrutement
    exemples: [sp_f37311_bonification_depuis_2004]   # pension de mai 2038 ;
                                                     # l'exemple date d'avant le b ter,
                                                     # son total vaut pour les deux

textes_sans_effet:   # rédactions lues mot à mot, qui ne changent pas la fiche
  - {id: LEGIARTI000006362903, article: R. 13, en_vigueur: 2006-05-12, motif: renvoi mis à jour (article 40 bis)}
  - {id: LEGIARTI000020532497, article: R. 13, en_vigueur: 2009-04-19, motif: renvois au code de la défense}
  - {id: LEGIARTI000051969102, article: R. 13, en_vigueur: 2025-10-01, motif: renvois au code général de la fonction publique}
  - {id: LEGIARTI000030949157, article: L. 12, en_vigueur: 2015-07-30, motif: b inchangé}
  - {id: LEGIARTI000037200561, article: L. 12, en_vigueur: 2018-07-15, motif: b inchangé}
  - {id: LEGIARTI000047926152, article: L. 12, en_vigueur: 2023-08-03, motif: b inchangé}
  - {id: LEGIARTI000047452833, article: L. 12, en_vigueur: 2023-09-01, motif: b inchangé}

approximations:
  - {version: l12bter, ecart: le modèle date à l'année et applique la version dès janvier 2026, effet: non mesuré}
  - {version: [l12b_2004, l12b_2011_decret, l12b_2011], ecart: les conditions d'interruption ou de réduction d'activité sont présumées remplies par la mère, effet: non mesuré}
  - {regime: regimes_speciaux, ecart: les conditions de la fonction publique leur sont prêtées, effet: non mesuré}

presomptions:     # celles d'aujourd'hui, qui deviennent les valeurs par défaut
  enfant.naissance: aux 30 ans de l'assuré
  interruption_d_activite: remplie par la mère seule
  radiation: au 1er janvier suivant la dernière année de services

sources:
  lu_le: 2026-09-25
  prochaine_relecture: 2027-03-31
  lectures_divergentes:
    - >-
      Du 1er janvier au 30 juin 2011, R. 13 admet déjà « une interruption ou
      une réduction de l'activité », alors que L. 12 ne dit « interrompu ou
      réduit » que pour les pensions prenant effet à compter du 1er juillet
      2011 (loi n° 2010-1330, article 118 II). À trancher par la circulaire du
      service des retraites de l'État.
  frontiere_contributive: >-
    Le registre marque encore le b ter « non appliqué », alors que le code
    l'applique depuis le 22 septembre 2026 : la vue fabriquée le corrigera.

code:
  python: >-
    scenarios/actuel.py : MajorationsPourEnfants,
    ScenarioActuel._majoration_pour_enfants, _bonification_ouverte
  javascript: >-
    moteur/js/regimes.js : MajorationsPourEnfants ;
    moteur/js/scenario-actuel.js : bonificationOuverte
  parametres: data/reference/legislation/majoration_duree_assurance.csv
  tests: [tests/test_priorite_enfants.py, tests/test_scenarios_meres.py]

referents:
  openfisca_france_pension:
    equivalent: variable nombre_enfants (un nombre, sans dates)
    confrontation: aucune ; les profils de l'oracle sont sans enfant
  destinie_2: à confronter (réversion et enfants y sont modélisés)

historique:       # repris des registres ; les originaux restent en archive
  - >-
    La fonction publique recevait la majoration du régime général, huit
    trimestres par enfant ; corrigé (en-tête de majoration_duree_assurance.csv).
  - 2026-09-21 — le b ter est lu et porté (veille.yaml).
  - >-
    2026-09-22 — bonification et majoration séparées : 1,2 % de pension
    rendus au droit (commit 49cb9e5).
  - >-
    2026-09-25 — l'index LEGI, lu mot à mot : R. 13 a six rédactions, dont
    trois ne changent que des renvois ; la version de 2011 se coupe en deux,
    au 1er janvier (le décret) et au 1er juillet (la loi).
```

### A.2 Le régime général, en résumé

```yaml
id: mda_regime_general
schema_version: 1
intitule: Majoration de durée d'assurance pour enfants (L. 351-4 CSS)
domaine: enfants
etape: compter_les_durees
regimes: [regime_general, artisans, commercants, salaries_agricoles]
face: droit
etat: approchee
dates_qui_decident: [liquidation.date_effet, enfant.naissance]
versions:
  - id: sans_droit_avant_1972
    statut: lue
    bornes: {liquidation.date_effet: [null, 1972-01-01]}
    contenu: {droit: aucun, raison: la majoration naît de la loi n° 71-1132}
  - id: mda_1972
    statut: lue
    textes:
      - {id: LEGITEXT000006068397, article: "loi n° 71-1132 (article L. 342-1 de l'ancien code, hors de l'index)", en_vigueur: 1972-01-01}
    bornes: {liquidation.date_effet: [1972-01-01, 1975-01-01]}
    contenu: {droit: 4 trimestres par enfant, beneficiaire: la mère d'au moins deux enfants}
    exemples: aucun trouvé
  - id: mda_1975
    statut: lue
    textes:
      - {id: LEGITEXT000006068508, article: loi n° 75-3, en_vigueur: 1974-07-01}  # date de l'index
      - {id: LEGIARTI000006742625, article: L. 351-4, en_vigueur: 1985-12-21}
      - {id: LEGIARTI000006742626, article: L. 351-4, en_vigueur: 2001-12-26}
    nee_de: LEGITEXT000006068508
    bornes: {liquidation.date_effet: [1975-01-01, 2003-12-30]}
    contenu:
      droit: 8 trimestres par enfant élevé neuf ans avant ses seize ans
      beneficiaire: la mère
    exemples: aucun trouvé
  - id: mda_2003
    statut: lue
    textes:
      - {id: LEGIARTI000006742627, article: L. 351-4, en_vigueur: 2003-08-22}
      - {id: LEGIARTI000006736529, article: D. 351-1-7, en_vigueur: 2003-12-30}
    nee_de: LEGIARTI000006742627
    bornes: {liquidation.date_effet: [2003-12-30, 2010-04-01]}
    hypothese: >-
      sur la borne de début : on la prend à l'entrée en vigueur du décret ;
      les pensions que la loi n° 2003-775 vise sont à relire
    fiabilite: moyenne
    contenu:
      droit: >-
        un trimestre à la naissance ou à l'adoption, puis un à chaque
        anniversaire jusqu'aux seize ans de l'enfant, huit au plus
      beneficiaire: la mère qui en a assumé la charge effective et permanente
    exemples: aucun trouvé
  - id: mda_2010_enfants_nes_avant
    statut: lue
    textes:
      - {id: LEGIARTI000021537916, article: L. 351-4 et dispositions transitoires de la loi n° 2009-1646, en_vigueur: 2009-12-28}
    bornes:
      liquidation.date_effet: [2010-04-01, null]
      enfant.naissance: [null, 2010-01-01]
    contenu:
      droit: 8 trimestres par enfant
      beneficiaire: la mère
      defauts_legaux: {education: la mère}
    exemples: [sp_f16336_mda_deux_enfants, cnav_2017_01_mda_trois_enfants]   # pensions de mai 2026
  - id: mda_2010
    statut: lue
    textes:
      - {id: LEGIARTI000021537916, article: "L. 351-4 (loi n° 2009-1646, pensions prenant effet à compter du 2010-04-01)", en_vigueur: 2009-12-28}
    bornes:
      liquidation.date_effet: [2010-04-01, null]
      enfant.naissance: [2010-01-01, null]
    contenu:
      droit: 4 trimestres au titre de la maternité et 4 au titre de l'éducation
      beneficiaire: la mère pour la maternité ; l'éducation au choix des parents
      defauts_legaux: {education: "à défaut d'accord des parents, la mère"}
    exemples: aucun trouvé

textes_a_rattacher:   # rédactions qui changent le droit, pas encore coupées en versions
  - {id: LEGIARTI000027432121, en_vigueur: 2013-05-19, change: "entre deux parents de même sexe, la majoration d'éducation se partage par moitié"}
  - {id: LEGIARTI000033713911, en_vigueur: 2016-12-25, change: le tuteur de l'enfant est admis}
  - {id: LEGIARTI000047453184, en_vigueur: 2023-04-16, change: la mère garde au moins deux trimestres d'éducation ; quatre trimestres si l'enfant meurt avant quatre ans}
  - {id: LEGIARTI000047456714, en_vigueur: 2023-09-01, change: les trimestres d'un parent condamné pour un crime contre l'enfant vont à l'autre parent}
  - {id: LEGIARTI000053280393, en_vigueur: 2025-12-31, change: "le IX est abrogé pour les pensions prenant effet à compter du 1er septembre 2026 ; la carrière longue relève désormais de L. 351-1-1 3°"}
textes_a_relire:
  - {id: LEGIARTI000006742626, en_vigueur: 2001-12-26, question: "les conditions passent au décret : lequel, et change-t-il le droit ?"}
  - {id: LEGIARTI000051289761, en_vigueur: 2025-02-28, question: un renvoi au code rural est retiré du IX (loi n° 2025-199)}
textes_sans_effet:
  - {id: LEGIARTI000022267455, en_vigueur: 2010-05-08, motif: renvoi au code rural et de la pêche maritime}
  - {id: LEGIARTI000036391746, en_vigueur: 2018-01-01, motif: renvoi retiré (L. 634-3-2)}
  - {id: LEGIARTI000037063369, en_vigueur: 2018-06-14, motif: renvoi mis à jour (L. 653-2)}
  - {id: LEGIARTI000045136636, en_vigueur: 2022-02-09, motif: renvoi d'alinéa}

approximations:
  - {version: mda_2003, ecart: "le modèle sert huit trimestres d'un coup", effet: "les mères dont un enfant a moins de sept ans à la date d'effet ; non mesuré"}
  - {textes: textes_a_rattacher, ecart: pas encore modélisés, effet: "aucun sur les résultats d'aujourd'hui, qui présument la mère seule bénéficiaire"}
presomptions:
  enfant_eleve_neuf_ans: présumé
  accord_des_parents: aucun (le défaut légal s'applique)
sources:
  lu_le: 2026-09-25
  prochaine_relecture: 2027-03-31
  a_relire:
    - les dispositions transitoires de la loi n° 2009-1646 pour les enfants nés avant 2010
    - le décret d'application de la loi n° 2003-775, et les pensions qu'elle vise
    - >-
      l'index date la loi n° 75-3 du 1er juillet 1974, et son article 11 renvoie à
      « L. 342-1 modifié » : la borne du 1er janvier 1975, reprise du modèle, est à relire
```

Ce que les deux fiches montrent :

- **Les versions se lisent sur deux dates, et forment un partage à chaque date
  d'observation.** Pour la fonction publique, la naissance de l'enfant choisit
  entre L. 12 b et L. 12 bis ; la date d'effet de la pension choisit la
  rédaction de R. 13 et l'entrée en vigueur du b ter. Un programme le vérifie
  à chaque date où une version paraît, et fabrique les cas de bascule
  (note 0001, § 14.5) : `src/retraite_notionnelle/noyau/partage.py`, que le
  contrôle de la carte joue sur chaque fiche.
- **Une borne ne ferme une version que lorsque sa suivante est connue.** Avant
  la loi du 30 décembre 2025, la version `l12bis` valait aussi pour les
  pensions prenant effet après le 1er septembre 2026. Rien de plus ne
  s'écrit : la version qui ferme une borne est celle qui commence là, et le
  programme le déduit.
- **Le passé qu'on n'a pas lu est dit.** Avant 1964, la version est supposée,
  et elle le déclare, avec sa fiabilité.
- **Défaut légal et présomption ne se confondent plus,** et le défaut légal
  change avec la version. Que l'éducation aille à la mère à défaut d'accord,
  c'est la loi de 2010 ; qu'il n'y ait pas eu d'accord, c'est une présomption.
- **La relation est déclarée.** La priorité entre régimes n'est plus une
  condition cachée dans le code : elle a sa fiche.
- **Les présomptions gouvernent aujourd'hui le résultat.** Les tests
  déplacent la naissance de la mère pour placer l'enfant avant ou après 2004 ;
  un exemple officiel a dû être réécrit de la même façon. Avec des naissances
  datées, les deux se lisent directement.
- **OpenFisca ne peut pas trancher ici.** Il connaît un nombre d'enfants, pas
  leurs dates : la référence est le texte et les exemples, et Destinie 2 reste
  à confronter.
- **La liste des textes trouve ce que la mémoire avait laissé.** Chaque
  rédaction est rattachée à une version, déclarée sans effet, ou comptée
  comme restant à rattacher. Pour le régime général, des rédactions qui
  changent le droit attendent encore (ses `textes_a_rattacher`, en A.2), et
  le décret de 2003 accordait les trimestres un par un, à chaque
  anniversaire de l'enfant. La fiche le montre au lieu de le laisser
  dormir.

---

## Annexe B — Où va chaque fichier d'aujourd'hui

**La documentation**

| Aujourd'hui | Demain |
|---|---|
| `CLAUDE.md` | une page qui renvoie ici ; l'histoire git en archive |
| `README.md` | inchangé : c'est le texte de la proposition, sa référence (§ 3) |
| `docs/feuille_de_route.md` | ce que la carte ne sait pas dire (l'outillage, le site, les décisions) ; les actions faites et le journal en archive ; ce qui touche une règle, recopié dans sa fiche |
| `docs/limites.md` | les sections d'état : les limites du tableau de bord, fabriquées ; les récits : en archive, et recopiés dans les fiches concernées |
| `docs/methodologie.md` | l'état du moteur, réorganisé par étapes |
| (nouveau) `docs/etat.md` | le tableau de bord, fabriqué à chaque changement (§ 9.1) |
| `docs/fraicheur.md` | une note de décision ; le contrôle des chiffres, allégé |
| `docs/veille_droit.md` | la procédure de veille, raccourcie |
| `docs/regimes.md`, `docs/chiffrage_plf.md`, `docs/chiffrage_plf.csv` | inchangés : déjà produits par script |
| `docs/frontiere_contributive.md`, `docs/avantages_non_contributifs.md` | des vues, fabriquées à partir des faces et des neutralisations des fiches |
| `docs/integration-partiliberalfrancais.md` | inchangé ; ses adresses stables sont la surface publique (annexe C) |
| les autres fichiers de `docs/` | inchangés, chacun déclaré état ou récit |

**Les données**

| Aujourd'hui | Demain |
|---|---|
| `data/reference/legislation/veille.yaml` | ses entrées dans les fiches ; son journal en archive ; ses sources à consulter dans la procédure |
| `data/reference/legislation/frontiere_contributive.yaml` | ses bascules dans les versions et les faces des fiches ; le fichier devient une vue |
| `data/reference/legislation/*.csv` | les tables datées, inchangées, avec deux colonnes facultatives de plus : la date de publication, la dernière valeur connue valable ; les fiches y renvoient |
| `data/reference/legislation/reformes.yaml`, `data/reference/regimes/pivots.yaml` | inchangés, reliés aux versions |
| `data/reference/regimes/*.yaml` (les fichiers de régimes) | un fichier par régime ; les interrupteurs deviennent des renvois aux fiches |
| `data/reference/regimes/_schema.yaml` | réduit : les champs de cas particuliers deviennent des fiches |
| `data/reference/regimes/inventaire.yaml` | une vue de couverture, fabriquée |
| `data/reference/macro/`, `data/reference/mortalite/`, `data/sources.yaml` | inchangés : les séries, en tables datées, et leurs sources |
| `data/sources_a_explorer.yaml` | le registre des sources : toute source y entre, avec son statut et ce qu'elle a produit (§ 9.2) |
| (nouveau) `data/reference/referents.yaml` | le registre des autres modèles publics : couverture, dépendances, conditions d'usage, écarts trouvés (§ 3.4) |
| `data/reference/site/affirmations.yaml` | inchangé, relié aux fiches |
| `data/reference/prose/zones.yaml` | simplifié : un régime (état, récit, produit) par fichier |
| `data/derive/`, `data/brut/` | inchangés : fabriqué, et sources brutes |

**Le code**

| Aujourd'hui | Demain |
|---|---|
| `src/retraite_notionnelle/scenarios/actuel.py` | découpé en étapes dans `src/retraite_notionnelle/droit/` ; ses commentaires suivent leur code |
| `src/retraite_notionnelle/scenarios/notionnel.py`, `moteur/` (compte, conversion, capitalisation, fusion, indexation, âge de référence), `garantie.py`, `restitution.py` | les fiches et les couches des univers de la proposition (phase 7) |
| `src/retraite_notionnelle/carriere.py` | la chronologie datée et le réseau de personnes (phase 3) ; `web/releve_lu.py` continue de l'alimenter |
| `src/retraite_notionnelle/calendrier.py` | inchangé : le mois et ses arrondis (§ 4.6) |
| `src/retraite_notionnelle/revalorisation.py` | l'étape « faire vivre » |
| `src/retraite_notionnelle/remuneration.py` | les cotisations de l'acquisition, et le net de l'étape « foyer et net » |
| `src/retraite_notionnelle/avantages.py`, `frontiere.py` | les cascades de neutralisations du pilote, et les vues de la frontière contributive |
| `src/retraite_notionnelle/castypes.py` | son point fixe passe au pilote |
| `src/retraite_notionnelle/cout.py`, `donnees/` | le pilote de population et la page Coût |
| `src/retraite_notionnelle/config.py` | ses décisions de modélisation deviennent des paramètres de couche ou des notes de décision |
| `src/retraite_notionnelle/simulateur.py` | l'échéancier, et l'entrée des univers |
| `src/retraite_notionnelle/web/pages.py`, `web/gabarit.py` | retirés à la phase 8 : leur rendu est déjà comparé à l'identique à celui de `pages.js` et `gabarit.js` (`tests/js/comparer-pages.mjs`) |
| `moteur/js/` | le même découpage que le Python, fichier pour fichier ; `scenario-actuel.js` découpé dans `moteur/js/droit/` |
| `moteur/donnees.json`, `moteur/style.css` | fabriqués, comme aujourd'hui ; le paquet se découpe par domaine |
| `scripts/` | inchangés ; `scripts/fetch/` reste l'outillage de récupération et de certification |

**Les tests**

| Aujourd'hui | Demain |
|---|---|
| `tests/temoins/` | inchangés, puis découpés par domaine : c'est le filet |
| `tests/temoins/exemples_officiels.yaml` | inchangé, plus un état par exemple : passe, ou écart connu (§ 9.2) |
| `tests/` | rangés en trois niveaux : rapides, complets, contrôles (§ 10) |

---

## Annexe C — Les neuf contrats de données

Ce sont les formes que le noyau fixe (§ 13.1). Chaque contrat porte un
`schema_version`. Depuis la phase 2, chacun est un schéma, dans
`data/reference/contrats/`, que `src/retraite_notionnelle/noyau/contrats.py`
applique et que `tests/test_contrats.py` tient à ces tables. Ce qui est fixé,
c'est ce que chaque champ porte.

Le validateur distingue deux constats. Un champ inconnu, une valeur hors du
vocabulaire, un type faux sont des erreurs : un moteur s'y arrêterait, et les
tests les refusent. Un champ obligatoire absent est un manque : la donnée
n'est pas encore mûre, le tableau de bord le compte, et rien n'est bloqué.

Un champ facultatif a une valeur par défaut, qui laisse les résultats
d'aujourd'hui identiques ; on en ajoute d'autres sans décision (§ 13.3). Les
listes de valeurs (sortes, motifs, natures, statuts, faces, origines) vivent
dans les fichiers de vocabulaire. Celles qu'on lit ici sont celles
d'aujourd'hui, et elles s'allongent sans décision.

### C.1 La chronologie : le fait et le lien

**La chronologie**, ce qu'une étape passe à la suivante (§ 7.1)

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `faits` | les faits de toutes les personnes du réseau | aucun |
| `liens` | les liens qui les relient | aucun |

**Le fait**

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id` | identifiant stable | — |
| `personne` | la personne du réseau | — |
| `sorte` | aujourd'hui : période d'activité, période où l'emploi s'interrompt (avec son motif), période assimilée, période à l'étranger, résidence, cessation d'activité, naissance (réelle ou prévue), adoption, décès, recrutement, titularisation, radiation, décision médicale, exposition, ressources, acte de la personne (demande, option, renonciation, rachat, versement, accord) ou de la caisse (notification) | — |
| `debut`, `fin` | dates au jour ; une période vaut [début, fin), et `fin` est vide pour un événement | — |
| `attributs` | selon la sorte : métier, statut, grade et corps, régime, revenu, quotité, motif, pays, taux… | — |
| `montant` | un montant et sa monnaie | la monnaie de la date |
| `territoire` | métropole, un département ou une collectivité d'outre-mer, un pays | métropole |
| `origine` | déclaré, présumé, simulé ; ce qu'une règle inscrit va au journal (C.8) | déclaré |
| `presomption` | pour un fait présumé, le nom de la présomption qui le pose (§ 5.6) | — |
| `connu_le` | la date où le fait est connu (§ 5.1) | à mesure qu'il se produit |
| `fiabilite` | niveau de la donnée | — |

**Le lien**

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id`, `de`, `vers` | les deux personnes | — |
| `sorte` | aujourd'hui : union, filiation, adoption, éducation, aide, tutelle | — |
| `forme` | pour une union : mariage, PACS, concubinage | — |
| `roles` | le rôle de chacun (mère, père, conjoint, aidant, tuteur…) | — |
| `debut`, `fin` | dates au jour ; la fin dit sa cause (divorce, décès) | — |
| `regime` | le régime qui lit ce lien, s'il est seul à le lire | tous |
| `origine`, `presomption` | comme pour un fait | déclaré |

### C.2 La fiche et ses versions

**La fiche**, pour une règle comme pour une relation

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id` | identifiant stable, jamais renommé ; `remplacee_par` si elle est dépréciée | — |
| `intitule`, `domaine`, `regimes` | — | — |
| `etape` | le nom de l'étape qui l'applique, ou l'échéancier | — |
| `face` | droit, cotisation, financement ; pour un financement, les fiches qu'elle paie | droit |
| `etat` | conforme, transcrite, approchée, manquante, pas encore modélisée | — |
| `lit`, `ecrit` | faits, liens, lignes du relevé, entrées du journal, résultats | — |
| `lit_sous_hypothese` | les résultats qui viennent plus loin, et leurs possibilités | aucun |
| `dates_qui_decident` | des dates nommées du vocabulaire | — |
| `suit` | les événements qu'elle suit, les liens qu'elle lit, et jusqu'à quelle distance | aucun |
| `neutralisee` | ce qu'elle écrit quand un univers la neutralise | rien |
| `versions` | un partage, à chaque date d'observation (ci-dessous) | — |
| `approximations` | chacune avec sa version et son effet, ou « non mesuré » | aucune |
| `presomptions`, `invariants` | — | aucun |
| `sources` | lue le, prochaine relecture, lectures divergentes, questions à relire | — |
| `textes_sans_effet`, `textes_a_rattacher`, `textes_a_relire` | les rédactions lues qui ne la changent pas, celles qui la changent sans être encore coupées en versions, et celles dont l'effet reste à lire | aucun |
| `code`, `referents`, `historique` | fonctions et tests ; correspondance avec chaque autre modèle, et écarts justifiés (§ 3.4) ; récits | — |

Une **relation** porte en plus :

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `sorte` | aujourd'hui : plafond, enveloppe, exception, priorité, choix, cumul, non-cumul, séquence, ordre de composition, ordre des événements d'une même date | — |
| `fiches` | les fiches reliées, avec leur rôle | — |
| `rang` | le rang d'application dans l'étape | — |
| `methode` | pour un choix : comment on retient le plus favorable, la même dans les deux moteurs, et le nombre de calculs qu'elle s'autorise | — |
| `hypothese` | pour une lecture sous hypothèse : possibilités, étapes rejouées, unité de décision, critère de cohérence, départage, budget | aucune |

**La version**

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id` | identifiant immuable | — |
| `statut` | lue, supposée | lue |
| `hypothese`, `fiabilite` | pour une version supposée, ou pour une borne supposée | — |
| `textes` | pour chacun : identifiant stable (ou référence de publication déclarée), article, entrée en vigueur, publication, citation exacte, date de lecture ; hors du *Journal officiel*, une copie datée ou son empreinte (§ 3.2) | publication : vide |
| `nee_de` | le texte qui la fait naître : la version est connue à sa publication | son seul texte ; sans texte, connue à toute date d'observation |
| `requis` | les textes sans lesquels elle est inapplicable (son décret) : tant qu'ils ne sont pas publiés à la date d'observation, la version qu'elle suspend continue | aucun |
| `bornes` | un intervalle [début, fin) par date qui décide : le seul endroit où s'écrivent ses dates | — |
| `fermee_par` | pour une fin de borne, la version qui la ferme ; la borne ne vaut qu'une fois celle-ci connue | l'une des versions qui commencent là |
| `vise` | les pensions qui prennent effet, ou les pensions servies ; l'étape qui l'applique en découle | pensions qui prennent effet |
| `duree` | pour un effet temporaire | — |
| `exception_de` | la version qu'elle prime, s'il y a chevauchement | — |
| `contenu` | droit accordé ou exigé, bénéficiaire, conditions, défauts légaux, paramètres lus, chacun avec sa date qui décide | — |
| `unites` | unité, arrondi, ancrage | — |
| `exemples` | les exemples officiels, chacun qui passe ou qui porte son écart connu (la valeur du modèle, l'explication), ou « aucun trouvé » | — |

### C.3 La table datée

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id` | le paramètre ou la série | — |
| `unite`, `monnaie` | — | — |
| `indexee_par` | la date qui décide de sa valeur : l'année du revenu, la génération, la date d'effet, l'échéance… | — |
| `valeurs` | pour chacune : sa date d'application, sa source, sa date de publication, et l'empreinte du fichier source | publication : vide |
| `valable_jusqu_au` | jusqu'où la dernière valeur est connue valable ; au-delà, la reprendre est une hypothèse | — |
| `origine` | texte, série publiée, autre modèle (lequel), prolongement supposé | — |

### C.4 La couche et l'univers

**La couche**

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id`, `nom` | identifiant stable | — |
| `operations` | garder, ajouter une fiche ou une relation, remplacer une version, neutraliser, changer un paramètre, ajouter une transition ; chacune vise une fiche nommée ou un sélecteur (étape, domaine, face, régime, contributivité) | — |
| `depuis` | la date qu'elle lit pour agir (date d'effet, date d'un fait, échéance), et sa valeur | l'origine |
| `portee` | l'univers, ou un seul calcul : celui que nomme la transition qui l'emploie | l'univers |

**L'univers**

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id`, `nom` | le scénario | — |
| `couches` | la pile, dans l'ordre, le droit réel en bas, couches d'un seul calcul comprises : chacune voit celles d'en dessous | le droit réel seul |
| `observation` | la date d'observation par défaut | la date de fabrication des données |
| `parametres_du_pilote` | les paramètres qui dépendent d'une population, déclarés comme tels (§ 7.7) | aucun |

### C.5 La ligne du relevé

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id`, `personne` | la ligne, et la personne qui en bénéficie | — |
| `fait`, `date` | le fait qui ouvre le droit, et sa date | — |
| `fiche`, `version`, `texte` | la règle appliquée | — |
| `droit` | quantité, unité, régime | — |
| `face` | droit, cotisation, financement | droit |
| `payeurs` | pour un financement attaché à l'acquisition : payeurs et parts | le régime |
| `contributive` | oui ou non | oui pour ce qui est cotisé |
| `nature` | ferme ; conditionnelle (et la condition ouverte) ; en attente (de quoi) | ferme |
| `filiation` | la ligne, la liquidation ou la personne d'origine, pour une transformation | vide |
| `origine` | calculée, observée | calculée |
| `presomptions`, `fiabilite` | — | — |

### C.6 La liquidation

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `demande` | personne, régimes, date d'effet, événement qui l'appelle et sa date, motif, nature ; pour une révision, la liquidation reprise, dont elle garde la nature, et la date d'où elle vaut ; pour une réversion, le défunt | motif vieillesse, nature définitive |
| `contexte` | univers (sa pile résolue), date d'observation (qui filtre les versions au calcul), hypothèse | droit réel, date de fabrication, aucune |
| `composantes` | base, majorations, minima, composantes temporaires, capital : chacune avec un identifiant stable, sa fiche, sa version, son bénéficiaire, son montant et sa monnaie, son début et sa fin ; servie ou seulement calculée ; ferme, ou en attente, et de quoi | servie, ferme |
| `payeurs`, `contributive` | par composante et par échéance | le régime ; oui |
| `lignes_consommees` | les lignes du relevé qu'elle a utilisées ; aucune pour une liquidation provisoire ou fictive ; une révision remplace celles de la liquidation qu'elle reprend | — |
| `decisions` | ce qu'elle fige pour d'autres liquidations : le partage d'une réversion, le régime qui reçoit les trimestres d'un enfant | aucune |
| `origine` | calculée, ou observée (une pension étrangère, la pension connue d'un défunt) | calculée |

### C.7 L'événement

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id`, `date` | — | — |
| `sorte` | aujourd'hui : départ, pension définitive, seconde pension, réversion, révision, annulation, transformation (dont la bascule), revalorisation, décès, union et fin d'union, changement de quotité ou de ressources, début ou fin d'une période, décision médicale, demande d'allocation, liquidation observée, début ou fin d'une composante, majorité d'un orphelin, publication d'une version. Le vocabulaire dit, pour chaque sorte, si elle appelle `liquider`, et avec quel motif et quelle nature | départ |
| `personnes` | les personnes concernées | — |
| `vise` | un régime, une liquidation, une allocation | — |
| `origine` | acte, simulé, observé, induit (fiche), publication | acte |
| `condition` | pour un événement induit inscrit d'avance : sa condition, et la fiche qui peut l'annuler | aucune |
| `rang` | l'ordre dans la journée, selon la relation qui le déclare | — |

### C.8 L'entrée du journal

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `id` | — | — |
| `inscrite` | l'événement qui l'a écrite, et sa date | — |
| `effet` | la période sur laquelle elle vaut, [début, fin) | — |
| `contenu` | un événement traité ou en attente ; une liquidation ; une composante, y compris celles des étapes qui ne liquident rien (revalorisation, ASPA, récupération sur la succession, net) ; une décision figée | — |
| `remplace` | l'entrée qu'elle révise : une composante et ses révisions forment une lignée | aucune |
| `annule` | l'événement en attente qu'elle annule | aucun |

Le journal se lit de deux façons, et de deux seulement :

- l'état à une date : tout ce qui a été inscrit au plus tard ce jour-là ;
- ce qui est servi pour une période : pour chaque composante, la dernière
  entrée de sa lignée dont l'effet couvre la période.

Rien ne s'y efface.

### C.9 La surface publique

| Champ | Ce qu'il porte | Défaut |
|---|---|---|
| `adresses` | les adresses du site : `#/simuler`, `#/simuler?…`, `#/cout`, `#/risque`, `#/partager`, `#/cas-types`, `#/avantages`, `#/methode`, et celles qui restent lues après une refonte (`#/trajectoire`, `#/donnees`, `#/?…`) | — |
| `entree` | les paramètres d'une simulation dans l'adresse (`naissance`, `sexe`, `statut`, `debut`, `liquidation`…, la liste que le site écrit), chacun avec son format | un paramètre ajouté a une valeur par défaut, qui laisse les anciennes adresses donner le même résultat |
| `sortie` | ce qu'une simulation rend : les pensions de chaque scénario en composantes, le relevé, les présomptions, les hypothèses, les empreintes | — |
| `theme` | les variables de thème (couleurs, polices) qu'un hôte peut redéfinir ; les sélecteurs internes n'en font pas partie | — |

### Les deux règles d'exécution

- **Le journal est l'état.** On y ajoute, on n'efface jamais, et chaque entrée
  porte son inscription et son effet (C.8).
- **Une étape ne lit d'une autre que des données décrites par un schéma.** Le
  schéma s'écrit à la phase qui crée l'étape, avant tout code, et il évolue
  par la règle additive, comme les contrats.

---

## Les versions

- **5.6**, 26 septembre 2026 : la phase 3 ajoute à la chronologie (C.1),
  par la règle additive (§ 13.3), ce qui la fait passer d'une étape à
  l'autre — son enveloppe, ses faits et ses liens — et le nom de la
  présomption qui pose un fait ; une période y vaut [début, fin), comme les
  bornes des versions. Les présomptions d'aujourd'hui entrent au
  vocabulaire, chacune avec sa valeur et sa raison (§ 5.6).

- **5.5**, 25 septembre 2026 : la suite complète reste le défaut de
  `python -m pytest`, et se passe avant tout envoi sur `main` ; la suite
  rapide est celle qu'on relance en travaillant (§ 10). Le propriétaire l'a
  décidé après la phase 0, plutôt que de faire de la suite rapide le défaut :
  tout part sur `main` sans relecture, et ce qui se lance avant l'envoi doit
  tout voir.
- **5.4**, 25 septembre 2026 : l'usage des simulateurs officiels devient une
  règle, qui ne sollicite jamais les caisses (§ 3.5). C'est la version
  décidée ; la phase 0 en tire ce document.
- **5.3** : toutes les sources gardées, leurs licences précisées, et comment
  tirer le plus des simulateurs officiels sans se faire bloquer (§ 3.4 et
  3.5).
- **5.2** : la preuve et la façon de trancher une divergence (§ 3.2 et 3.3) ;
  le principe 3 élargi aux autres modèles publics (§ 3.4), à la demande du
  propriétaire.
- **5.1** : le tableau de bord et la règle « ce qu'on apprend n'est jamais
  bloqué » (§ 9), sans toucher au noyau.
- Ce qui précède, et les épreuves qui ont façonné l'architecture : note 0001,
  § 14.
