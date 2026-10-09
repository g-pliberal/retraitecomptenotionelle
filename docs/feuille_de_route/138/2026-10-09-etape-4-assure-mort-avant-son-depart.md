# Étape 4, quatrième partie : la réversion d'un assuré mort avant son départ

**Le 9 octobre 2026, la demande.** Le propriétaire : « Réversion d'un assuré
mort avant son départ (R. 353-6), puis le partage entre ex-conjoints et le
remariage. » C'est le point suivant de « Ce qui reste » (note « plafond du
ménage ») : la saisie refusait un décès avant le départ, « la réversion d'une
pension que l'assuré n'a pas encore liquidée n'est pas calculée ».

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre ;
fiches `reversion` et `reversion_fonction_publique`).

- *Le régime général.* R. 353-6, dans ses deux rédactions (1985, puis 2011) :
  quand le titulaire de droits « décède antérieurement » à l'âge du taux plein,
  la réversion « est calculée en fonction du montant de la pension qui aurait
  été allouée au de cujus au titre de l'inaptitude au travail ». La Cnav
  (exposé « Retraite de l'assuré décédé », 6 mars 2026) : 54 % de la retraite
  que l'assuré « aurait pu obtenir », au taux de 50 % « quel que soit l'âge de
  l'assuré au moment du décès », la durée « arrêtée au dernier jour du
  trimestre civil qui précède le décès », l'année du point de départ de la
  réversion négligée au salaire annuel moyen, les majorations pour enfants
  examinées à ce point de départ ; la circulaire n° 2005-17, § 211 à 218, dit
  les règles de quelle date valent pour quoi.
- *Les autres régimes.* « Le coefficient de minoration n'est pas applicable aux
  pensions de réversion lorsque la liquidation de la pension dont le
  fonctionnaire aurait pu bénéficier intervient après son décès » (L. 14, I, du
  code des pensions, depuis 2004), que la CNRACL, les ouvriers de l'État, les
  IEG, la SNCF, la RATP et la CRPCEN écrivent mot pour mot ; L. 38 sert la
  moitié de la pension « qu'il aurait pu obtenir au jour de son décès ». Les
  complémentaires reversent les points acquis, sans coefficient.
- *Une lecture divergente* : R. 353-6 nomme aussi « le pensionné » mort avant
  l'âge du taux plein ; la Cnav reverse au pensionné le montant de sa retraite,
  décote comprise. Le modèle suit la caisse.
- *Destinie 2* (`Reversion.cpp`, au commit `4c1d34b`) calcule de même une
  pension théorique sans âge minimal, aux taux pleins, et garde la pension d'un
  régime déjà liquidé.

**Ce qui est fait.**

- *Le modèle* (deux moteurs) : l'échéancier, quand le décès précède le départ
  déclaré, liquide la pension que l'assuré eût obtenue — une liquidation
  fictive, de motif `reversion`, sur la carrière arrêtée au premier jour du
  trimestre civil du décès (`Carriere.arretee_au_deces`), inscrite au journal
  sous le décès, sans composantes. Cette carrière porte `au_deces` : aucune
  décote dans les régimes en annuités, aucun coefficient dans les régimes en
  points. La réversion lit ses pensions, aux euros de l'année du décès, avec
  ses durées pour le minimum ; la cessation d'activité que lisent les
  conditions de mariage de la fonction publique, des IEG et de l'Ircantec est
  le décès. La ligne de réversion le dit (`avant_le_depart`).
- *La saisie* (deux moteurs) accepte le décès avant le départ, et refuse ce qui
  ne tient pas : un décès avant la naissance, avant le début de la carrière, ou
  avant le mariage que le modèle présume à vingt-sept ans quand sa date n'est
  pas dite.
- *La page* : « À votre décès, en mai 2024, avant votre départ, » et la phrase
  qui dit que la réversion porte sur la pension que l'assuré aurait obtenue à
  son décès, sans décote ; elle montre toujours la pension du départ déclaré,
  comme si l'assuré vivait.
- *Le budget de calcul* compte la liquidation au décès comme un départ de plus.
- *Les fiches* : `reversion` cite R. 353-6 dans chaque version, remplace par ce
  qui reste l'approximation qui déclarait le cas absent, et porte la lecture
  divergente ; `reversion_fonction_publique` cite L. 14 ; `reversion_agirc_arrco`
  et `reversion_ircantec` disent les points reversés sans coefficient ; le
  registre, au chantier 138.4 ; les limites et le tableau de l'architecture.
- *Les tests* (`test_reversion.py`) : la liquidation fictive au taux plein, la
  durée arrêtée au trimestre, la même carrière décotée d'un vivant, le
  fonctionnaire au taux de 75 %, sa condition de mariage lue au décès, la
  saisie, la page ; deux témoins de simulation, `reversion_deces_avant_le_depart`
  et `reversion_fonctionnaire_mort_en_activite`, les deux moteurs au bit près.

**Les mesures.** Aucune pension des six scénarios ne bouge, ni aucune des
dix-neuf réversions des témoins, qui gagnent le champ `avant_le_depart`. La
mère de trois enfants morte à cinquante-quatre ans en mai 2024, avec 157
trimestres de 172, laisse 18 106,67 euros de pension du régime général au taux
plein, quand la même carrière d'une vivante serait décotée à 14 711,67 euros
(taux de 40,6 %) ; son veuf reçoit, à ses cinquante-cinq ans, 10 755,36 euros
du régime général, majoration de 10 % comprise, et 3 938,37 euros de
l'Agirc-Arrco. Le fonctionnaire mort au même âge laisse une pension civile de
20 899,63 euros au taux de 75 %, au lieu de 15 674,72 décotée ; sa veuve en
reçoit la moitié dès juin 2024, et la moitié de son RAFP.

**Ce qui reste.**

1. *De l'étape 4, dans l'ordre* : le partage entre ex-conjoints et le remariage
   — le nouveau conjoint devient une personne de la chronologie, avec une union
   datée — ; L. 353-5 et D. 355-1 ; les majorations forfaitaires d'avant 1995
   et 1982.
2. *De R. 353-6* : les règles de la date d'effet de la réversion (majorations
   pour enfants, surcote, salaire annuel moyen des polypensionnés), et, pour un
   décès de juillet 2004 à juin 2011, le nombre d'années et la durée de la
   génération qui avait soixante ans l'année du décès ; la pension d'un régime
   déjà servie au décès, avant le départ déclaré, que le modèle recalcule ; un
   exemple chiffré publié, que la fiche attend.
