pheno = ...[[1]]@phenoData@data
exprstable = ...[[1]]@exprsData@exprs
age = sapply(pheno[, xx], AgeExtract)
gender = sapply(pheno[, xx], GenderExtract)
samples = rownames/colnames(exprstable)
...age.sorted = age[match(rownames/colnames(exprstable), samples)]
...gender.sorted = gender[match(rownames/colnames(exprstable), samples)]
...result = age_gender_normalize(exprstable, ...age.sorted, ...gender.sorted)
