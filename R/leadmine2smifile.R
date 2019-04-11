#!/usr/bin/env Rscript
#############################################################################
library(readr)
library(data.table)

args <- commandArgs(trailingOnly=T)
if (length(args)>0)
{
  message((ifile <- args[1]))
} else {
  message("ERROR: Syntax: leadmine2smifile.R TSVFILE")
  quit()  
}

drugs_leadmine <- read_delim(ifile,  "\t", escape_double=F, trim_ws=T)
setDT(drugs_leadmine)
setnames(drugs_leadmine, old=c("DocName", "ResolvedForm"), new=c("id", "smiles"))
#
drugs_smi <- drugs_leadmine[!is.na(drugs_leadmine$smiles), c("smiles","OriginalText")]
drugs_smi <- unique(drugs_smi)
setnames(drugs_smi, old=c("OriginalText"), new=c("name"))
message(sprintf("Unique drug smiles: %d", length(unique(drugs_smi$smiles))))
#
# Aggregate by same smiles.
drugs_smi <- drugs_smi[,  .(names = paste(name, collapse="; ")), by="smiles"]
drugs_smi <- drugs_smi[order(nchar(drugs_smi$smiles))]
writeLines(format_tsv(drugs_smi, col_names=F), stdout())
#
