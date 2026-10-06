# Version du 6 octobre 2026 : une version par fichier

Une version de ce document ne s'écrit plus en tête de sa liste, et son
en-tête n'en nomme plus aucune : chacune a son fichier, sous
`docs/architecture/versions/`, nommé de sa date et de son sujet, qui s'ouvre
sur son titre (§ 9.3, annexe B). Deux sessions qui en ajoutent une chacune
n'écrivent plus au même endroit (action 149, à la demande du propriétaire,
qui mène plusieurs sessions en parallèle). Une version ne porte plus de
numéro : deux sessions prendraient ensemble le suivant, compteur commun que
le § 13.3 refusait déjà à la carte ; elle se cite par sa date et son sujet.
Les premières, de 5.1 à 5.37, gardent le leur, en bas du document, telles
qu'elles ont été écrites. `scripts/conservation.py` gèle chaque version dès
son fichier écrit, et un test tient le rangement.
