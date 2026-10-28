# L'onglet « Issues » de Chrome : une alerte corrigée, l'autre déclarée

**Le 28 octobre 2026, la demande.** Le propriétaire : « regarde le site
internet dans un navigateur et regarde les commentaires de la console je crois
qu'il y a un souci », puis la capture de l'onglet « Issues » de Chrome :
« Non-standard `autocomplete` attribute value », un élément visé.

## Ce qui a été vu

- **La console est vide.** Les neuf pages en ligne, à 375 et 1 280 points ;
  les anciennes adresses en `#/…` ; le simulateur calculé, la carrière derrière
  le `#` ; chaque bouton cliqué et chaque dépliant ouvert ; un réseau lent : ni
  message, ni exception, ni requête en échec. Le site en ligne est celui de
  `main`, fichier pour fichier.
- **L'onglet « Issues » portait deux alertes**, que le Chromium sans interface
  de Playwright ne lève pas — il n'a pas l'autoremplissage, qui les calcule —,
  mais que le Chromium entier, celui des tests des écrans, lève :
  - `FormEmptyIdAndNameAttributesForInputError` : la zone de texte de secours
    de chaque barre de partage (`textarea.repli`, `barrePartage`, dans
    `gabarit.js`), sans `id` ni `name` — trois sur Coût, quatre sur Droits non
    cotisés, douze sur Le saviez-vous ?, quatre sur Partager ;
  - `FormInputHasWrongButWellIntendedAutocompleteValueError` : la date de
    naissance, `autocomplete="bday"`, sur l'accueil et le simulateur. C'est
    celle de la capture.
- **`bday` est la bonne valeur.** La norme HTML la donne à une date de
  naissance entière, le critère 1.3.5 des WCAG (RGAA 11.13) la demande, et
  `test_les_champs_qui_decrivent_la_personne_sont_reconnaissables` la tient.
  L'autoremplissage de Chrome ne connaît que `bday-day`, `bday-month` et
  `bday-year` (`kStandardizedAttributes`, dans
  `components/autofill/core/common/autocomplete_parsing_util.cc`), et dit « non
  standard » toute valeur inconnue où se lit « bday ». Sans elle, il ne
  remplirait pas mieux le champ.
- **Lighthouse ne compte ni l'une ni l'autre** : son audit `inspector-issues`
  ne retient que le contenu mixte, les cookies, les blocages d'origine et la
  politique de sécurité. Les notes de l'action ne bougent pas.

## Ce qui est fait

- **Le test d'abord.** Le pilote des écrans (`tests/js/ecrans.mjs`) écoute
  l'onglet (`Audits.issueAdded`) et décrit chaque alerte dès qu'elle arrive —
  une page que le routeur recalcule remplace ses nœuds —, par son type et
  l'élément visé, écrit en sélecteur ;
  `test_aucune_page_ne_porte_d_alerte_dans_l_onglet_issues` refuse toute alerte
  qu'`ALERTES_ADMISES` ne déclare pas avec sa raison. Vu rouge sur les quatre
  pages des barres de partage.
- **Le correctif** : la zone de texte porte `name="message"`. Aucune page ne
  pose de barre de partage dans un formulaire : rien ne l'envoie. Les quatre
  pages et les huit rendus de page qui changent ne changent que de ce nom.
- **`bday` reste**, seule alerte admise, sur l'accueil, le simulateur et ses
  résultats, aux cinquante visites du pilote.

## Ce qui reste

- Rien pour l'onglet. Le vider tout à fait demanderait d'ôter `bday`, au prix
  du critère 1.3.5 : choix au propriétaire, non fait.

## En passant : pytest 9.2.0

- **Paru le 27 octobre 2026 à 21 h 30 UTC**, après la dernière suite verte de
  GitHub, qui installe la dernière version, il refuse tout conteneur dans un
  `pytest.approx` — un dictionnaire dans un tuple —, quand les versions d'avant
  ne refusaient qu'un tuple dans un tuple.
  `test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation`
  (`test_avantages.py`) comparait ainsi d'un bloc le total des départs anticipés
  et sa ventilation : il les compare l'un après l'autre. C'était le seul échec
  de la suite rapide ; la suite complète de GitHub dira s'il en reste ailleurs.
