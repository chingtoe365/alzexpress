UpdateAnnoList <- function(anno, type, probecol)
{
	for(ind in 1:nrow(anno))
	{
		geneEntryInd = which(unlist(lapply(annoList, function(x){
				x$entrez_gene_id == anno[ind, "Entrez.Gene"]
			})))
		if(length(geneEntryInd) > 0)
		{
			# if this gene exist in current anno List
			if(is.na(match(type, names(annoList[geneEntryInd][[1]]))))
			{
				annoList[geneEntryInd][[1]] <<- c(annoList[geneEntryInd][[1]], list(as.character(anno[ind, probecol])))
				names(annoList[geneEntryInd][[1]])[length(annoList[geneEntryInd][[1]])] <<- type
			}else{
				# if the probe of this platform exist in current gene
				annoList[geneEntryInd][[1]][type][[1]] <<- c(annoList[geneEntryInd][[1]][type][[1]], as.character(anno[ind, probecol]))
			}
		}
		else
		{
			newGene = list(anno[ind, "Entrez.Gene"], as.character(anno[ind, "Symbol"]), as.character(anno[ind, probecol]))
			names(newGene) = c("entrez_gene_id", "symbol", type)
			annoList <<- c(annoList, list(newGene))
		}
		if(ind %% 100 == 0 && ind >=100){
			print(paste(ind, "genes attached"))
		}
	}
}