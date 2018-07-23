#!/usr/bin/env Rscript
#############################################################################
### CTTI = Clinical Trials Transformation Initiative
### AACT = Aggregate Analysis of ClinicalTrials.gov
### According to website (July 2018), data is refreshed monthly.
### https://aact.ctti-clinicaltrials.org/
#############################################################################
### See also: https://github.com/ctti-clinicaltrials/aact
#############################################################################
### descriptions_MeSH_disease_terms_leadmine.tsv from Go_NER.sh
### descriptions_MeSH_supp_disease_terms_leadmine.tsv from Go_NER.sh
#############################################################################
### MeSH XML files (desc2018.xml, supp2018.xml) downloaded from:
### https://www.nlm.nih.gov/mesh/.
### Converted to TSV by mesh_xml_utils.py.
#############################################################################
library(readr)
library(dplyr, quietly = T)
library(plotly, quietly = T)


###
# Corpus = Descriptions
# MeSH Diseases NER:
###
#MeSH disease terms:
desc_meshdisease_leadmine <- read_delim("data/descriptions_MeSH_disease_leadmine.tsv", "\t")
desc_meshdisease_leadmine <- dplyr::rename(desc_meshdisease_leadmine, nct_id = DocName)
#
ner <- desc_meshdisease_leadmine %>% group_by(EntityText) %>% summarise(n = n())
#
mesh_disease <- read_delim("data/mesh_disease.tsv", "\t")
mesh_disease <- dplyr::rename(mesh_disease, mesh_id = id)
ner <- merge(ner, mesh_disease, by.x="EntityText", by.y="term")
ner <- ner[order(-ner$n),]
rownames(ner) <- NULL
#
writeLines(sprintf("===\nTop MeSH disease terms counts:"))
writeLines(sprintf("%3d. %s: %-28s: %6d", 1:50, ner$mesh_id[1:25], ner$EntityText[1:25], ner$n[1:25]))
#
###
#MeSH supplemental disease terms:
desc_meshsuppdisease_leadmine <- read_delim("data/descriptions_MeSH_supp_disease_leadmine.tsv", "\t")
desc_meshsuppdisease_leadmine <- dplyr::rename(desc_meshsuppdisease_leadmine, nct_id = DocName)
#
ner <- desc_meshsuppdisease_leadmine %>% group_by(EntityText) %>% summarise(n = n())
#
mesh_supp_disease <- read_delim("data/mesh_supp_disease.tsv", "\t")
mesh_supp_disease <- dplyr::rename(mesh_supp_disease, mesh_id = id)
ner <- merge(ner, mesh_supp_disease, by.x="EntityText", by.y="term")
ner <- ner[order(-ner$n),]
rownames(ner) <- NULL
#
writeLines(sprintf("===\nTop MeSH supplemental disease terms counts:"))
writeLines(sprintf("%3d. %s: %-28s: %6d", 1:50, ner$mesh_id[1:25], ner$EntityText[1:25], ner$n[1:25]))
#
