# Exécute TRAJECTOiRE (DREES) sur les cas types du COR et sur les carrières que
# `trajectoire.py` décrit.
#
#     Rscript trajectoire.R <dossier des entrées> <dossier des sorties>
#
# Ce script appartient au dépôt ; TRAJECTOiRE n'y entre pas. Il s'installe à
# part (paquet R `trajectoire`, https://git.drees.fr/drees_code_public/modeles/trajectoire,
# licence EUPL-1.2), et ce script n'en appelle que les fonctions et les fichiers
# livrés avec lui. Seules les sorties entrent au dépôt, figées dans
# `tests/temoins/trajectoire.json`.
#
# Deux exécutions, dans le même processus :
#
# 1. LES CAS TYPES DU COR, tels que TRAJECTOiRE les calcule : le script que le
#    paquet livre pour cela (`inst/scripts/casTypesCOR.R`, que
#    `lancerCasTypesCor()` source) est évalué expression par expression, tel
#    quel, à trois choses près, que l'on vérifie avant de les faire : il n'est
#    pas rechargé depuis ses sources (`devtools::load_all()`, qui suppose le
#    dossier du paquet, est sauté : le paquet installé est déjà chargé) ; les
#    générations sont celles d'`options.json` au lieu de 1940 à 2000 ; une seule
#    hypothèse de croissance du salaire moyen par tête (SMPT) au lieu des quatre
#    du COR. Il s'arrête avant le rapport et le classeur (`rmarkdown::render`,
#    `openxlsx::write.xlsx`, `browseURL`). Le script calcule chaque âge de
#    départ, de l'âge d'ouverture (ou de la carrière longue) à l'âge
#    d'annulation de la décote, par trimestre ; on garde, pour chaque cas type
#    et chaque génération, le premier âge au taux plein qu'il marque
#    (`ageMinTxPlein`).
# 2. LES CARRIÈRES DU DÉPÔT, écrites par `trajectoire.py` en tables d'entrée de
#    `calculePension()` (dtId, dtIdAnEtat, dtIdAnCaisseFonctionnaire,
#    dtIdNumeroEnfant), sous les paramètres que l'exécution 1 a prolongés.
#
# Aucune donnée confidentielle : le mode « cas types » se passe de l'EIC et de
# l'EIR, et `telecharger = FALSE` lit les barèmes livrés avec le paquet.
#
# Le répertoire de travail est un dossier temporaire, marqué `.here` : le
# paquet écrit son `_config.yaml` à la racine du projet que `here` trouve, et ce
# ne doit être ni le dépôt ni le dossier du modèle.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 2) {
  stop("usage : Rscript trajectoire.R <entrees> <sorties>")
}
entrees <- normalizePath(arguments[1], mustWork = TRUE)
sorties <- arguments[2]
dir.create(sorties, showWarnings = FALSE, recursive = TRUE)
sorties <- normalizePath(sorties, mustWork = TRUE)

travail <- file.path(tempdir(), "trajectoire")
dir.create(travail, showWarnings = FALSE)
setwd(travail)
writeLines("cache: _cache", "_config.yaml")
file.create(".here")

suppressPackageStartupMessages({
  library(data.table)
  library(trajectoire)
})
logger::log_threshold(logger::WARN)
# `lancerModele()` compare la graine avant et après chaque étape : elle doit
# exister.
set.seed(20261005L)

reglages <- jsonlite::fromJSON(file.path(entrees, "options.json"))
generations <- as.integer(reglages$generations)
hyp_smpt <- as.numeric(reglages$hypSmpt)

# ---------------------------------------------------------------------------
# 1. Les cas types du COR, par le script du paquet
# ---------------------------------------------------------------------------

script <- system.file("scripts", "casTypesCOR.R", package = "trajectoire", mustWork = TRUE)
expressions <- parse(script, keep.source = FALSE)
texte <- function(e) paste(deparse(e, width.cutoff = 500L), collapse = "\n")
est_boucle_smpt <- function(e) {
  is.call(e) && identical(e[[1]], as.name("for")) && identical(e[[2]], as.name("hypSmpt_"))
}
# Les trois substitutions portent sur des expressions que l'on reconnaît : si le
# script change, l'exécution s'arrête au lieu de faire autre chose.
stopifnot(
  sum(vapply(expressions, function(e) identical(e, quote(devtools::load_all())), TRUE)) == 1,
  sum(vapply(expressions, function(e) startsWith(texte(e), "generations <- "), TRUE)) == 1,
  sum(vapply(expressions, est_boucle_smpt, TRUE)) == 1,
  sum(vapply(expressions, function(e) startsWith(texte(e), "nomFichier <- "), TRUE)) == 1
)
cas_types <- new.env(parent = asNamespace("trajectoire"))
for (e in expressions) {
  if (identical(e, quote(devtools::load_all()))) next
  if (startsWith(texte(e), "nomFichier <- ")) break
  if (startsWith(texte(e), "generations <- ")) {
    e <- call("<-", as.name("generations"), generations)
  }
  if (est_boucle_smpt(e)) e[[3]] <- hyp_smpt
  eval(e, envir = cas_types)
}
resultats_cor <- get("resFinal", envir = cas_types)
retenus <- resultats_cor$dtIdPensionnes[ageMinTxPlein %in% TRUE, id]

# Les entrées que le script a données à `calculePension()`, pour la dernière
# (et seule) hypothèse de SMPT.
entrees_cor <- list(
  dtId = get("dtId", envir = cas_types),
  dtIdAnEtat = get("dtIdAnEtat", envir = cas_types),
  dtIdAnCaisse = get("dtIdAnCaisse", envir = cas_types),
  dtIdAnCaisseFonctionnaire = get("dtIdAnCaisseFonctionnaire", envir = cas_types)
)
parametres <- get("parametres", envir = cas_types)
param_modele <- get("paramModele", envir = cas_types)

# ---------------------------------------------------------------------------
# 2. Les carrières du dépôt
# ---------------------------------------------------------------------------

lire <- function(nom) {
  fread(file.path(entrees, paste0(nom, ".csv")), encoding = "UTF-8")
}
mois <- function(texte) as.anneeMois(as.character(texte))
dt_id <- lire("dtId")
dt_id[, `:=`(dateNaissance = mois(dateNaissance), dateLiq = mois(dateLiq))]
dt_an_etat <- lire("dtIdAnEtat")
dt_fonc <- lire("dtIdAnCaisseFonctionnaire")
dt_enfants <- lire("dtIdNumeroEnfant")
resultats_depot <- calculePension(
  dtId = dt_id,
  dtIdNumeroEnfant = dt_enfants,
  dtIdAnEtat = dt_an_etat,
  dtIdAnCaisseFonctionnaire = if (nrow(dt_fonc)) dt_fonc else NULL,
  parametres = parametres,
  paramModele = param_modele
)

# ---------------------------------------------------------------------------
# Les sorties
# ---------------------------------------------------------------------------

ecrire <- function(table, nom) {
  table <- copy(as.data.table(table))
  # Les dates de TRAJECTOiRE comptent les mois depuis janvier 1970 ; une table
  # réunie par `rbindlist` en perd parfois la classe : on les écrit « AAAA-MM ».
  for (colonne in names(table)) {
    valeurs <- table[[colonne]]
    if (inherits(valeurs, "anneeMois") || (startsWith(colonne, "date") && is.numeric(valeurs))) {
      set(table, j = colonne,
          value = ifelse(is.na(valeurs), NA_character_,
                         format(as.anneeMois(as.integer(valeurs)))))
    }
  }
  fwrite(table, file.path(sorties, paste0(nom, ".csv")))
}
colonnes <- function(table, voulues) intersect(voulues, names(table))
sortir <- function(resultats, ids, suffixe) {
  garder <- function(table, voulues) {
    table <- as.data.table(table)[id %in% ids]
    table[, colonnes(table, voulues), with = FALSE]
  }
  ecrire(garder(resultats$dtIdPensionnes, c(
    "id", "casType", "generation", "ageLiq", "dateNaissance", "sexe", "nbEnfant",
    "ageMort", "categCSG", "dateLiqCaissePrincipale", "caissePrincipale",
    "typeLiquidation", "typeDepart", "AOD", "AAD", "dureeRequise",
    "dureeValideeTousRegimes", "aSurcoteDansCaissePrincipale",
    "aDecoteDansCaissePrincipale", "nbTrimDecoteCaissePrincipale",
    "nbTrimSurcoteCaissePrincipale", "aMinPension", "pensionLiqEurosConstants",
    "pensionLiqSmpt", "txRemplacementNet", "txRemplacementNetSmpt",
    "txRemplacementCdv", "txRemplacementNetCdv", "txAnnuite", "txRecuperation",
    "txPrestation", "dureeRetraiteRelativeDureeCotisation", "ageMinTxPlein")),
    paste0("pensionnes_", suffixe))
  ecrire(garder(resultats$dtIdCaisse, c(
    "id", "caisse", "dateLiq", "pension", "pensionAvantMinEtMajo", "majorationEnfant",
    "ajoutMinimum", "taux", "tauxDecote", "tauxSurcote", "nbTrimDecote",
    "nbTrimSurcote", "pensionNette")), paste0("caisses_", suffixe))
  ecrire(garder(resultats$dtIdCaisseBase, c(
    "id", "caisse", "dateLiq", "prorat", "dureeValideeTousRegimes",
    "dureeCotiseTousRegimes", "dureeValidee", "dureeCotisee", "dureeGratuite",
    "dureeRequise", "dureeRequiseProrat", "AOD", "AAD", "MDAenfantPourTaux",
    "MDAenfantPourProrat", "nbTrimBonification", "typeDepart", "dateTauxPlein")),
    paste0("bases_", suffixe))
  ecrire(garder(resultats$dtIdCaisseSalaireReference, c("id", "caisse", "salaireReference")),
         paste0("salaires_reference_", suffixe))
  ecrire(garder(resultats$dtIdCaisseFonctionnaire, c(
    "id", "caisse", "majoBonifFonc", "AOD", "AAD", "dureeRequise",
    "categFonctionPublique", "typeBonif", "typeMDAFonc", "primesDansCotiseBase")),
    paste0("fonctionnaires_", suffixe))
  ecrire(garder(resultats$dtIdAnCaisse, c(
    "id", "annee", "caisse", "remuneration", "nbTrimCotise", "nbTrimValide",
    "nbTrimGratuit", "montantAvpf")), paste0("annees_", suffixe))
  ecrire(garder(resultats$dtIdAnCaisseComplementaire, c(
    "id", "annee", "caisse", "nbMois", "nbPtCotise", "nbPtGratuit", "nbPt")),
    paste0("points_", suffixe))
  ecrire(garder(resultats$dtIdRacl, c("id", "dateLiqRacl")), paste0("racl_", suffixe))
  ecrire(garder(resultats$dtIdCaisseModulationTemporaire, c("id", "caisse", "taux", "duree")),
         paste0("modulations_", suffixe))
}
sortir(resultats_cor, retenus, "cor")
sortir(resultats_depot, unique(dt_id$id), "depot")

# Les entrées des cas types du COR retenus : la carrière que le script du paquet
# a construite, d'où `trajectoire.py` écrit la requête du dépôt.
extraire <- function(table, voulues) {
  table <- as.data.table(table)[id %in% retenus]
  table[, colonnes(table, voulues), with = FALSE]
}
ecrire(extraire(entrees_cor$dtId, c(
  "id", "casType", "sexe", "dateNaissance", "generation", "dateLiq", "ageLiq",
  "ageMort", "nbEnfant", "categCSG")), "entrees_cor_id")
ecrire(extraire(entrees_cor$dtIdAnEtat, c(
  "id", "annee", "etatTravail", "dureeEnMois", "remuneration", "salaireRelatif",
  "smpt")), "entrees_cor_etats")
ecrire(extraire(entrees_cor$dtIdAnCaisse, c(
  "id", "annee", "caisse", "nbTrimGratuit", "nbTrimCotise", "montantAvpf")),
  "entrees_cor_caisses")
ecrire(extraire(entrees_cor$dtIdAnCaisseFonctionnaire, c(
  "id", "annee", "caisse", "primes", "nbTrimValideFonc")), "entrees_cor_fonctionnaires")
# L'âge d'ouverture, l'âge d'annulation de la décote et la durée requise que le
# paquet lit, par génération et catégorie : la législation qu'il porte.
ecrire(parametres$ageDuree, "parametres_age_duree")
# Les paramètres qui expliquent un écart de montant sans relancer R : la chaîne
# de revalorisation des salaires du salaire annuel moyen (en pour cent par an)
# et le plafond, les taux d'acquisition des points de l'Arrco et de l'Agirc
# (moyens et minimaux), les valeurs d'achat et de service des points, la
# revalorisation des pensions de la fonction publique, l'assiette de l'AVPF et
# le salaire qui valide un trimestre.
annees <- 1960:2035
par_annee <- Reduce(function(x, y) merge(x, y, by = "annee", all = TRUE), list(
  as.data.table(parametres$revaloSam)[, .(annee, revaloSam)],
  as.data.table(parametres$pss)[, .(annee, pss)],
  as.data.table(parametres$salaireValidant)[, .(annee, salaireValidant)],
  as.data.table(parametres$smicAVPF)[, .(annee, smicAVPF)],
  as.data.table(parametres$paramCotis)[, .(
    annee, txCotARRCOsalempl_t1, txCotMIN_ARRCOsalempl_t1, txCotARRCOsalempl_t2,
    txCotMIN_ARRCOsalempl_t2, txCotAGIRCsalempl_TB, txCotMIN_AGIRCsalempl_TB)]
))
ecrire(par_annee[annee %in% annees], "parametres_annuels")
ecrire(as.data.table(parametres$valeurPtAcquisition)[
  caisse %chin% c("Arrco", "Agirc", "Agirc-Arrco", "Rafp") & annee %in% annees],
  "parametres_valeur_achat")
ecrire(as.data.table(parametres$valeurPtService)[
  caisse %chin% c("Arrco", "Agirc", "Agirc-Arrco", "Rafp") & dateLiq >= anneeMois(2010, 1) &
    dateLiq <= anneeMois(2035, 12), .(date = dateLiq, caisse, valeurPtService)],
  "parametres_valeur_service")
ecrire(as.data.table(parametres$revalo)[
  caisse %chin% c("SRE", "CNRACL") & dateValeurPension >= anneeMois(2010, 1) &
    dateValeurPension <= anneeMois(2035, 12), .(date = dateValeurPension, caisse, revalo)],
  "parametres_revalorisation_fonction_publique")

versions <- list(
  R = paste(R.version$major, R.version$minor, sep = "."),
  trajectoire = as.character(packageVersion("trajectoire")),
  data.table = as.character(packageVersion("data.table")),
  logger = as.character(packageVersion("logger")),
  readxl = as.character(packageVersion("readxl")),
  plateforme = R.version$platform
)
writeLines(jsonlite::toJSON(versions, auto_unbox = TRUE, pretty = TRUE),
           file.path(sorties, "versions.json"))
