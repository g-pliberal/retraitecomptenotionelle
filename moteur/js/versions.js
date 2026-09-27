/**
 * La version d'une fiche qui s'applique à une situation (docs/architecture.md,
 * § 4.1).
 *
 * Jumeau de `src/retraite_notionnelle/noyau/versions.py`. Les versions d'une
 * fiche forment un partage de ses dates qui décident, contrôlé sur chaque
 * fiche : pour des dates données, une version et une seule s'applique, aux
 * exceptions déclarées près. Le paquet porte les fiches que le moteur lit,
 * préparées par le Python : leurs dates qui décident, et chaque version avec
 * ses bornes, son texte et ses paramètres. Les dates y sont écrites
 * AAAA-MM-JJ, et deux dates écrites ainsi se comparent comme deux textes.
 */

/**
 * La version d'une fiche préparée qui s'applique à ces dates,
 * `{date nommée: "AAAA-MM-JJ"}` ; `null` si aucune ne s'applique. Une date qui
 * manque, ou que la fiche ne déclare pas, arrête le calcul ; quand deux
 * versions s'appliquent, celle qui se déclare l'exception de l'autre
 * l'emporte. Voir `applicable` du Python.
 */
export function applicable(fiche, dates) {
  const noms = fiche.dates_qui_decident;
  const donnees = Object.keys(dates);
  if (donnees.length !== noms.length || !noms.every((nom) => nom in dates)) {
    throw new Error(`${fiche.id} : dates qui décident ${JSON.stringify([...noms].sort())}, `
      + `reçu ${JSON.stringify(donnees.sort())}`);
  }
  const valent = fiche.versions.filter((version) => noms.every((nom) => {
    const [debut, fin] = version.bornes[nom] ?? [null, null];
    const jour = dates[nom];
    return !((debut !== null && jour < debut) || (fin !== null && jour >= fin));
  }));
  const restent = valent.filter(
    (version) => !valent.some((autre) => autre.exception_de === version.id),
  );
  if (restent.length > 1) {
    throw new Error(`${fiche.id} : ${restent.map((v) => v.id).join(", ")} s'appliquent `
      + "toutes à ces dates, et le partage n'en admet qu'une");
  }
  return restent.length ? restent[0] : null;
}
