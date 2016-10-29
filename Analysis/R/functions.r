ExtractBy <- function(arr, pattern, index)
{
	return(sapply(arr, function(x) 
		strsplit(as.character(x), pattern)[[1]][index]))
}

TrimFrontAndEndSpace <- function(stringArr)
{
	return(sapply(stringArr, function(x){
		splitRes = strsplit(as.character(x), "")[[1]]
		return(paste(splitRes[c(-1, -length(splitRes))], collapse=""))
	}))
}

ExtractByColon <- function(input) 
{
	input = as.character(input)
	return(TrimSpaces(strsplit(input, ":")[[1]][2]))
}

ExtractGender <- function(arr)
{
	res = as.character(arr)
	pat = "female"
	ind = grep(pat, res, ignore.case=T)
	res[ind] = "F"
	res[-ind] = "M"
	return(res)
}
library(stringr)
ExtractFromString <- function(stringArr)
{
	return(sapply(stringArr, function(x){
		s = as.character(x)
		loc_ind = str_locate(s, "AGE_\\d+")
		var_string = substring(s, loc_ind[1,1], loc_ind[1,2])
		res = strsplit(var_string, "_")[[1]][2]
		return(res)
	}))
}
AgeExtract <- function(input)
{
	inp = as.character(input)
	res = regexpr("\\d\\d+", inp)
	return(as.numeric(substring(inp, res[1], res[1] + attributes(res)$match.length - 1)))
}
GenderExtract <- function(input)
{
	inp = as.character(input)
	# pat = "F" #female
	if(grepl("female", inp, ignore.case=T))
	{
		return("F")
	}
	else if(grepl("F", inp, ignore.case=F))
	{
		return("F")
	}else{
		return("M")
	}
}
DiseaseStateExtract <- function(input)
{
	inp = as.character(input)
	AD_indicator = c("alzheimer", "AD", "disease: A", "Alzheimer's Disease", "status: AD")
	Healthy_indicator = c("normal", "control", "non-AD", "disease: N", "indiv", "Non-Demented", "status: CTL")
	MCI_indicator = c("mci", "status: MCI")
	PD_indicator = c("parkinson")
	BC_indicator = c("breast cancer")
	MS_indicator = c("multiple sclerosis")
	HD_indicator = c("Huntington's disease")
	Other_dementia_indicator = c("other_dementias")
	
	AD_check = any(sapply(AD_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))
	Healthy_check = any(sapply(Healthy_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))
	MCI_check = any(sapply(MCI_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))	
	PD_check = any(sapply(PD_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))	
	BC_check = any(sapply(BC_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))	
	MS_check = any(sapply(MS_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))
	HD_check = any(sapply(HD_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))
	Other_dementia_check = any(sapply(Other_dementia_indicator, function(x){
			grepl(x, inp, ignore.case=T)
			}))
	
	# special setting for gse48350
	
	# if(AD_check)
	# {
	# 	return("AD")
	# }
	# else
	# {
	# 	return ("CNL")
	# }

	##### general setting #########

	if(Healthy_check)
	{
		return("CNL")
	}
	else if(AD_check)
	{
		return("AD")
	}
	else if(MCI_check)
	{
		return("MCI")
	}
	else if(PD_check)
	{
		return("PD")
	}
	else if(BC_check)
	{
		return("BC")
	}
	else if(MS_check)
	{
		return("MS")
	}
	else if(HD_check)
	{
		return("HD")
	}
	else if(Other_dementia_check)
	{
		return("Other dementias")
	}else
	{
		return("Other State")
	}
}

NumberExtract <- function(input)
{
	# stop(input)
	inp = as.character(input)
	res1 = regexpr("\\d+\\.\\d+", inp)
	res2 = regexpr("\\d+", inp)
	if(is.na(input)){
		return(NA)
	}
	if(res1[1] > 0){
		res = res1
	}else{
		res = res2
	}
	return(as.numeric(substring(inp, res[1], res[1] + attributes(res)$match.length - 1)))
}
DirectExtract <- function(input)
{
	inp = as.character(input)
	return(inp)
}


TrimSpaces <- function(input)
{
	i = as.character(input)
	i = sub("^\\s+", "", i)
	i = sub("\\s+$", "", i)
	return(i)
}

RegionExtract <- function(input) 
{
	inp = as.character(input)
	if(grepl("prefrontal cortex", inp, ignore.case=T) | grepl("frontal cortex", inp, ignore.case=T)| grepl("frontal_cortex", inp, ignore.case=T) | grepl("PFC", inp, ignore.case=T))
	{ 
		return("PFC")
	}
	else if(grepl("superior frontal gyrus", inp, ignore.case=T))
	{
		return("SFG")
	}
	else if(grepl("medial temporal gyrus", inp, ignore.case=T) | grepl("middle temporal gyrus", inp, ignore.case=T))
	{
		return("MTG")
	}
	else if(grepl("hippocampus", inp, ignore.case=T))
	{
		return("HIP")
	}
	else if(grepl("primary visual cortex", inp, ignore.case=T))
	{
		return("PVC")
	}
	else if(grepl("posterior cingulate", inp, ignore.case=T) | grepl("posterior singulate", inp, ignore.case=T))
	{
		return("PC")
	}
	else if(grepl("entorhinal cortex", inp, ignore.case=T))
	{
		return("EC")
	}
	else if(grepl("cerebellum", inp, ignore.case=T))
	{
		return("CE")
	}	
	else if(grepl("visual cortex", inp, ignore.case=T))
	{
		return("VI")
	}	
	else if(grepl("temporal cortex", inp, ignore.case=T))
	{
		return("TC")
	}	
	else if(grepl("postcentral gyrus", inp, ignore.case=T) | grepl("post-central gyrus", inp, ignore.case=T))
	{
		return("POCG")
	}
	else{
		return("Error in identifying region")
	}
}

FromExpressionTableToList <- function(exprsTable, phenoTable, phenoVarArr, phenoVarNames, GEOseries, platform_name, platform_id, data_type, tissue)
{
	sampsInExp = colnames(exprsTable)
	probesInExp = rownames(exprsTable)
	# print(sampsInExp)
	result = vector("list", length(sampsInExp))
	sampsInPhen = rownames(phenoTable)
	# stop(sampsInPhen)
	neededPhenoTable = phenoTable[match(sampsInExp, sampsInPhen), ]
	count = 1
	for(sie in sampsInExp)
	{
		result[[count]] = list(GEOseries)
		result[[count]] = c(result[[count]], list(platform_name))
		result[[count]] = c(result[[count]], list(platform_id))
		result[[count]] = c(result[[count]], list(probesInExp))
		result[[count]] = c(result[[count]], list(data_type))
		result[[count]] = c(result[[count]], list(tissue))
		result[[count]] = c(result[[count]], list(exprsTable[, count]))
		# directExtractGroup = c("region", "pres", "sample_accession", "data_type", "organism")
		directExtractGroup = c("pres", "sample_accession", "organism")
		count2 = 1
		for(pv in phenoVarArr)
		{
			newAddedVal = neededPhenoTable[count, pv]
			# print(pv)
			# stop(newAddedVal)
			if(phenoVarNames[count2] == "age")
			{
				newAddedVal = AgeExtract(newAddedVal)
			}
			else if(phenoVarNames[count2] == "gender")
			{
				newAddedVal = GenderExtract(newAddedVal)
			}
			else if(phenoVarNames[count2] == "disease_state")
			{
				newAddedVal = DiseaseStateExtract(newAddedVal)
			}else if(phenoVarNames[count2] == "region"){
				region_full_name = as.character(newAddedVal)
				newAddedVal = RegionExtract(newAddedVal)
			}
			else if(!is.na(match(phenoVarNames[count2], directExtractGroup)))
			{
				newAddedVal = DirectExtract(newAddedVal)
				newAddedVal = TrimSpaces(newAddedVal)
			}
			# else if(length(grep(":", newAddedVal)) > 0)
			# {
			# 	newAddedVal = ExtractByColon(newAddedVal)
			# 	# newAddedVal = TrimSpaces(newAddedVal)
			# }
			else
			{
				newAddedVal = NumberExtract(newAddedVal)
			}
			result[[count]] = c(result[[count]], list(newAddedVal)) # as.character? as numeric? 
			count2 = count2 + 1
		}

		if(tissue == "brain"){
			# Add region_full_name field
			result[[count]] = c(result[[count]], list(region_full_name))
			names(result[[count]]) = c("dataset_accession", "platform_name", "platform_id", "probe_id", "data_type", "tissue", "expression_value", phenoVarNames, "region_full_name")
		}else{
			names(result[[count]]) = c("dataset_accession", "platform_name", "platform_id", "probe_id", "data_type", "tissue", "expression_value", phenoVarNames)
		}

		count = count + 1
	}

	names(result) = sampsInExp
	return(result)
}

FromAnnotationTableToList <- function(anno_table, entrez_gene_id_col, probe_id_col, symbol_col)
{
	# Remove probes with null entrez gene id
	anno_table = anno_table[!is.na(anno_table[, entrez_gene_id_col]), ]
	# Remove probes with null symbols
	anno_table = anno_table[!is.na(anno_table[, symbol_col]), ]
	# Create a json formatted list
	# example 7556 : [2,4,5]
	# Assign returned variable
	anno_list = list()
	# anno_list[[1]][[1]] = c(1,2,3)
	# anno_list[[1]][[2]] = "haha"
	# names(anno_list[[1]]) = c("probe_ids", "symbol")
	# names(anno_list) = c("test")
	for(i in 1:nrow(anno_table)){
		entrez_id = as.character(anno_table[i, entrez_gene_id_col])
		probe_id = as.character(anno_table[i, probe_id_col])
		symbol = as.character(anno_table[i, symbol_col])
		exists_or_not = match(entrez_id, names(anno_list))
		# print(is.na(exists_or_not))
		if(!is.na(exists_or_not)){
			# If entrez gene id already exists, append
			# print(anno_list[exists_or_not][[1]][["probe_ids"]])
			# new_array = c(anno_list[exists_or_not][[1]][["probe_ids"]], probe_id)
			new_array = c(anno_list[exists_or_not][[1]]$probe_ids, probe_id)
			# print(anno_list[exists_or_not][[1]][["probe_ids"]])
			# print(new_array)
			# print(probe_id)
			anno_list[exists_or_not][[1]]$probe_ids = NULL
			# print(anno_list[exists_or_not][[1]])
			# print(anno_list[exists_or_not][[1]])
			# anno_list[exists_or_not][[1]][["probe_ids"]] = new_array
			anno_list[exists_or_not][[1]]$probe_ids = new_array
			# print(anno_list[exists_or_not][[1]])
			# stop()
		}else{
			# If not exist, create
			# anno_list[[entrez_id]][["probe_ids"]] = c(probe_id)
			# anno_list[[entrez_id]][["symbol"]] = symbol
			anno_list[[entrez_id]]$probe_ids = c(probe_id)
			anno_list[[entrez_id]]$symbol = symbol
		}
	}
	# Remove initial thing
	# anno_list = anno_list[-1]
	return(anno_list)
}