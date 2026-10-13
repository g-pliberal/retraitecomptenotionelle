# Étape 1, ranger le document : la licence lue, la fiche au manifeste, le miroir sur la branche du propriétaire

**La licence.** budget.gouv.fr refuse le cloud ; le propriétaire a lu ses
mentions légales dans le navigateur de son téléphone et en a envoyé trois
captures, de 15 h 27 et 15 h 28. Rubrique « Réutilisation des contenus et
liens » : « Sauf mention explicite de propriété intellectuelle détenue par des
tiers, les contenus de ce site sont proposés sous licence ouverte Etalab
2.0 », libres de reproduction et de redistribution « sous réserve de
mentionner leur source, leur date de dernière mise à jour et ne pas induire en
erreur des tiers ». La rubrique « Crédits photos » réserve les images des
articles ; le jaune n'en porte pas, et son texte ne mentionne aucune propriété
intellectuelle de tiers (ni « © », ni « droits réservés », ni
« reproduction »).

**La fiche du manifeste**, `sre_jaune_pensions_2027`, juste après celle de
l'édition 2026 : la page des jaunes 2027 pour `url` ; pour `document`,
`file-download/34465`, déduit du nom sous lequel le téléphone a enregistré le
fichier et du modèle de l'édition 2026 (`file-download/31546`) ; pour
`fichier_local`, ce nom même, `34465.pdf`, celui que le site lui donne ;
l'empreinte de la copie ; la rediffusion `libre`, clause, lecture et mention
citées ; `statut_integration: a_faire`, et pour `cible` les deux premiers
fichiers que l'action 159 visera. Le nombre de jeux du manifeste, ancré dans
`docs/methodologie.md`, est passé de 213 à 214.

**La release.** Le workflow `documents-apportes.yml`, lancé par la session à
15 h 31 (exécution 38405657830), a reçu 403 sur la page comme sur le fichier, à
la requête simple puis par Chromium : budget.gouv.fr refuse aussi les machines
de GitHub. Le dépôt à la main sur la release restait possible, depuis un
navigateur, le jeton d'une session n'écrivant pas les releases.

**Le miroir.** Le propriétaire a fait valoir que le fichier était déjà dans le
dépôt, sur la branche `jaune-2027`, et que cela revenait au même. C'est vrai :
GitHub le sert à tous (`raw.githubusercontent.com`, 200, 11 964 640 octets,
même empreinte), et la licence permet de le rediffuser. Le `miroir` de la fiche
est donc cette adresse, et `source_locale.py --recuperer` a écrit
`data/brut/34465.pdf` depuis elle, empreinte vérifiée. Deux conséquences : la
branche se garde tant qu'aucun autre miroir ne la remplace, l'Assemblée quand
elle servira le jaune, ou la release ; et le workflow ne cherche plus à publier
le document, `--publier` ne prenant que les jeux sans autre miroir que la
release, si bien que sa course mensuelle n'échouera pas sur lui.

**Ce qui change dans le plan.** Apprendre à `sre_jaune_pensions.py` l'édition
2027 passe à l'étape 2, les bonifications, qui en a besoin la première.

**Ce qui reste.** Les étapes 2 à 9, en parallèle. Quand l'Assemblée servira le
jaune : comparer son fichier à l'empreinte, en faire le miroir, et supprimer la
branche `jaune-2027`, ce que seul le propriétaire peut faire.
