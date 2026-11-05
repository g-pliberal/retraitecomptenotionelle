# Étape 3, suite : le simulateur du COR à l'archive du web, une seule capture, le fichier déjà lu

**Le 5 novembre 2026, la demande.** « On peut tout faire », depuis le poste,
qui atteint l'archive du web : les points 1 et 2 de « Ce qui reste » de la note
du 2 novembre, le dernier millésime du simulateur et la date de celui de
Challenges.

**Ce qui a été lu.** L'index de l'archive (CDX) pour toutes les adresses de
`www.cor-retraites.fr/simulateur/` ; ses pages de 2019 à 2026 ; son code
`js/script.js` de juillet 2021 et de mars 2025, et les fichiers `_nuxt/` de la
version de mars 2026 ; la documentation technique et la FAQ de 2021 et de 2024.

**Ce que la lecture a trouvé.**

- *Le fichier de données n'a qu'une capture*, du 3 octobre 2022. Son empreinte
  est celle de `cor_simulateur_2021` (`8196a3e4…`) : le COR servait ce jour-là
  le fichier que Challenges a repris.
- *Sa date* : le code de juillet 2021 renvoie au rapport annuel de novembre 2020
  (`node/545`), et la documentation technique est du 15 janvier 2021. Le nom
  « 2021 » est donc celui d'une mise à jour faite sur ce rapport ; rien ne dit
  si le fichier a changé entre janvier 2021 et octobre 2022.
- *Le dernier millésime n'est pas gardé.* Le code de mars 2025 renvoie au rapport
  de juin 2024 et lit toujours `fileProjection.json`, jamais recapturé. La
  version de mars 2026, récrite, lit `data/fileProjection.json`, jamais capturé.
  Ces deux adresses rendent aujourd'hui une page HTML, pas de données.

**Ce qui change.** La note de `cor_simulateur_2021` au manifeste. Ni témoin, ni
valeur, ni fichier : le COR interdit la reproduction sans son accord
(`rediffusion: interdite`), et rien n'est à déposer.

**Ce qui reste.** Le millésime de juin 2024, que seul le COR peut donner : un
courrier à son secrétariat général, que la note du 18 octobre sur la révision
de 2026 prévoit déjà pour une autre question. La version rouverte, à sa
réouverture.
