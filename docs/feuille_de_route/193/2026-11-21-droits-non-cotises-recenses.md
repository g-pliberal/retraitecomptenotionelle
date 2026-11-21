# Action 193 : quatre droits non cotisés de plus sur la page, la réversion servie en partie

*Le 21 novembre 2026, une session a écrit la correction ; une autre l'a
relue sous Opus (Fable indisponible ce soir-là ; le propriétaire l'a voulu
ainsi), puis publiée avant les pages fabriquées depuis les fiches
(`2026-11-21-pages-depuis-les-fiches.md`).*

**Le défaut.** La page « Droits non cotisés » se disait complète, mais le
moteur servait quatre dispositifs qu'elle ne nommait pas, et marquait
« absent » la majoration de réversion que la fiche `reversion` sert.

**Ce qui change.**

- **Quatre lignes neuves** dans `avantages_non_contributifs.yaml`, à l'état
  « intégré », le coût marqué « PAS ENCORE MESURÉ » : l'avantage social
  vieillesse des soignants conventionnés (D. 645-2 du code de la sécurité
  sociale) ; le départ immédiat des fonctionnaires parents de trois enfants,
  de 1965 à 2011 (L. 24, I, 3° du code des pensions ; loi n° 2010-1330,
  article 44) ; la majoration de durée des hospitaliers de catégorie active
  (loi n° 2003-775, article 78) ; le taux plein sans la durée requise de
  certains assurés (L. 351-8 du code de la sécurité sociale), dont les cinq
  fiches `taux_plein_*` tiennent en une ligne. Aucun montant n'est écrit pour
  l'ASV : aucune source publiée ne sépare la part de l'Assurance maladie.
- **La réversion, la majoration forfaitaire pour enfant à charge et la
  majoration de réversion** sont dites « servi en partie » : au conjoint que
  la saisie déclare, dans les régimes dont une fiche porte la réversion. Un
  champ neuf, `servi_en_partie`, le dit ; le paquet le porte.
- **La liste n'est plus dite close** : la page, le document et l'en-tête de
  l'inventaire disent « tel que le dépôt l'a recensé ».
- **Le test de l'inventaire s'étend aux fiches de règles** : toute fiche
  appliquée qui sert un avantage (enfants, minima, périodes assimilées,
  départ anticipé, réversion, et les familles `taux_plein_*`, `asv_*`,
  `majoration_duree_*`, `bonification_*`…) renvoie à sa ligne, ou se déclare
  `hors_inventaire` avec sa raison. Vingt-huit fiches déjà servies ont été
  rattachées ; la réversion du FSPOEIE, publiée le même soir, l'a été au
  passage des pages fabriquées.

Aucun témoin de simulation ne bouge ; la page compte 53 dispositifs, dont
46 en vigueur, au lieu de 49 et 43. Le budget de mots de la page dépliée
passe de 7 470 à 7 650.

**Ce qui reste.** Les droits en vigueur que le moteur ne sert pas encore, que
leurs fiches marquent `pas_encore_modelisee` ou `manquante` : le minimum de
pension des IEG, l'assurance vieillesse des aidants, la majoration de durée
de l'aidant d'un adulte handicapé, entre autres ; ils attendent la réponse
du propriétaire. Le coût des quatre lignes neuves, à mesurer.
