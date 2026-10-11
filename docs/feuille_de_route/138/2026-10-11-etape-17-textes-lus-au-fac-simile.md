# Étape 17, suite : quatre textes que l'index ne garde qu'en notice, lus au fac-similé du Journal officiel

**Le 11 octobre 2026, au soir : depuis le poste du propriétaire, Légifrance
sert les Journaux officiels numérisés que l'index n'a pas, et deux fiches de
l'étape 17 en reçoivent leurs textes.**

- *La demande.* Le propriétaire, dans une session de bureau : « fais le
  point 6, les textes sur Légifrance » — la loi n° 49-244 et le décret du
  2 mars 1948, que la fiche `pension_maximale_regime_general` attendait pour le
  maximum de 1949 à 1974, et le décret n° 65-315, que la fiche
  `taux_plein_anciens_deportes_internes` ne lisait que dans sa circulaire, avec
  le décret n° 70-342 qu'elle citait pour les salariés agricoles.
- *L'accès.* Légifrance refuse `curl`, et s'ouvre dans le navigateur de
  l'application. Un texte d'avant 1990 n'y a que sa notice et le Journal
  officiel du jour en version papier numérisée, de quatorze à trente-quatre
  mégaoctets, derrière un accès protégé : le Journal porte des données
  nominatives, et chaque téléchargement demande une petite addition, que le
  propriétaire a résolue lui-même, quatre fois. Les quatre fichiers restent
  dans `data/brut/jo/`, que git ignore ; les fiches n'en citent que les
  articles. Gallica, qui sert aussi le Journal officiel, oppose maintenant à
  `curl` et à son API une page de contrôle.
- *Le maximum des pensions.* Le décret n° 48-361 du 2 mars 1948 (JO du 3 mars,
  p. 2236) ne fixe aucun maximum de pension : il porte la rémunération maximum
  soumise à cotisation à 228 000 F par an. La loi n° 49-244 (JO du 25 février
  1949, p. 2019, article 2) borne « à titre exceptionnel, pour l'année 1949 »
  toute pension ou rente de vieillesse revalorisée à « 40 p. 100 du chiffre
  limite » : 91 200 F, le premier montant du barème de la Cnav, qui se trouve
  ainsi lu. Elle ne majore pas la borne pour l'ajournement au-delà de
  soixante-cinq ans, que le modèle applique de 1949 à 1971 sur la foi de la
  circulaire n° 2/72, qui ne la dit qu'à partir de 1972 : l'écart est déclaré
  dans la fiche, pour des assurés nés avant 1907. Les deux versions gardent
  leur statut `supposee` : une version lue née d'une loi publiée le 25 février
  et appliquée au 1er janvier serait inconnue du partage pendant ces semaines-là,
  et les années 1950 à 1971 restent sans texte lu.
- *Les anciens déportés et internés.* Le décret n° 65-315 (JO du 24 avril 1965,
  p. 3200) insère dans le premier alinéa de L. 332 les anciens déportés et
  internés titulaires de la carte : la version de 1965 est confirmée par son
  texte. Le décret n° 70-342 (JO du 19 avril 1970, p. 3751) ouvre aux salariés
  agricoles « la révision de leur pension de vieillesse à compter du 1er mai
  1965 » : la date que le modèle leur sert déjà, mais sur leur demande, qu'il
  présume faite. Reste la date des artisans et des commerçants.
- *La veille.* Le serveur de la DILA refusant ses incréments, L. 161-17-2 et
  L. 161-17-3 sont relus sur Légifrance : toujours en vigueur depuis le
  31 décembre 2025, sans version à venir (fiche `fin_de_la_suspension_2028`).
- *Ce qui reste.* Les décrets du maximum de 1950 à 1971 et la loi
  n° 48-1306 du 23 août 1948 ; s'ils disent comme la loi de 1949, ne plus
  majorer le maximum par l'ajournement avant 1972, en Python puis en
  JavaScript. Aucun résultat ne bouge aujourd'hui.
