library(limma)
# limma_calculator <- function(df, class_lst) {
limma_calculator <- function(df, class_lst, age, gender) {
    group = as.factor(class_lst)
    design = model.matrix(~0 + age + gender + group)
    fit = lmFit(t(df), design)
    contrast.matrix = makeContrasts("group1 - group0", levels = design)

    fit2i = contrasts.fit(fit, contrast.matrix)
    fit2i = eBayes(fit2i)

    result = list(t_score=as.numeric(fit2i$t), p_value=as.numeric(fit2i$p.value))

    return(result) 
}
# limma_calculator <- function(df, class_lst, age, gender) {
	
# 	### function to calculate limma scores
#     # print(df[1:4, 1:4])
#     # print(typeof(df[1,1]))
#     # df = as.matrix(df)
#     # print(df[1:4, 1:4])
#     group = as.factor(class_lst)
#     # design = model.matrix(~-1 + group)
#     design = model.matrix(~0 + group + age + gender)
#     # print("OK")
#     # apply(df, 2, function(x){
#     #         print(which(!is.numeric(x)))
#     #     })
#     # print(df[2,1])
#     # print(df[!is.numeric(df)])
#     # print(df[1])
#     fit = lmFit(df, design)
#     # print("OK")
#     # print(fit)
#     # whether it's group0 - group1 OR group1 - group0??
#     contrast.matrix = makeContrasts("group1 - group0", levels = design)
#     # print("OK")
#     # print(contrast.matrix)
#     fit2i = contrasts.fit(fit, contrast.matrix)
#     fit2i = eBayes(fit2i)

#     # drop age and gender as factors if any
#     # For RNA sequencing data no need to do so
#     # to_drop_ind = c()
#     # # to_drop_ind = c(length_of_stats-1, length_of_stats)
#     # # length_of_stats = length(fit2i$t)    
#     # if(any(rownames(df)=="age")){
#     #     to_drop_ind = c(to_drop_ind, which(rownames(df)=="age"))
#     # }
#     # if(any(rownames(df)=="gender")){
#     #     to_drop_ind = c(to_drop_ind, which(rownames(df)=="gender"))   
#     # }
#     # print(to_drop_ind)
#     # if(length(to_drop_ind)>0){
#     #     result = list(t_score=as.numeric(fit2i$t)[-to_drop_ind], p_value=as.numeric(fit2i$p.value)[-to_drop_ind])    
#     # }else{
#     #     result = list(t_score=as.numeric(fit2i$t), p_value=as.numeric(fit2i$p.value))
#     # }
#     result = list(t_score=as.numeric(fit2i$t), p_value=as.numeric(fit2i$p.value))

#     return(result) 
# }

t_calculator <- function(df, class_lst) {
	
	### function to calculate t statistics
		# columns of df stands for samples
		# rows of df stands for featurs
	
    # ### Drop age and gender if any ###
    # to_drop_ind = c()
    # # to_drop_ind = c(length_of_stats-1, length_of_stats)
    # # length_of_stats = length(fit2i$t)    
    # if(any(rownames(df)=="age")){
    #     to_drop_ind = c(to_drop_ind, which(rownames(df)=="age"))
    # }
    # if(any(rownames(df)=="gender")){
    #     to_drop_ind = c(to_drop_ind, which(rownames(df)=="gender"))   
    # }
    # # to_drop_ind = c(which(rownames(df)=="age"), which(rownames(df)=="gender"))
    # if(length(to_drop_ind)>0){
    #     df = df[-to_drop_ind, ]
    # }
    
    df_0 = df[, class_lst == 0]
	df_1 = df[, class_lst == 1]
	sti = row.ttest.stat(df_0, df_1)
	pval = 2 * (1 - pt(abs(sti), df = (length(class_lst) - 2)))
	# drop age and gender as factors
    
    result = list(t_score=sti, p_value=pval)

	return(result) 
}

# t_calculator_2 <- function(df, class_lst) {
	
# 	### function to calculate t statistics
# 		# columns of df stands for samples
# 		# rows of df stands for featurs

# 	resultmat = apply(df, 1, function(x) {
# 			df_1 = x[class_lst == 1]
# 			df_0 = x[class_lst == 0]
# 			ttestres = t.test(df_1, df_0)
# 			t = ttestres$statistic
# 			pval = ttestres$p.value
# 			res = c(t, pval)
# 			names(res) = c("t", "pval")
# 			return(res)
# 		})

# 	result = list(t_score=resultmat["t", ], p_value=resultmat["pval", ])
# 	return(result) 
# }


row.ttest.stat <- function (mat1, mat2) 
{
    n1_list <- apply(mat1, 1, function(x) sum(!is.na(x)))
    n2_list <- apply(mat2, 1, function(x) sum(!is.na(x)))
    n_list <- n1_list + n2_list
    m1 <- rowMeans(mat1, na.rm = TRUE)
    m2 <- rowMeans(mat2, na.rm = TRUE)
    v1 <- rowVars(mat1, na.rm = TRUE)
    v2 <- rowVars(mat2, na.rm = TRUE)
    vpool <- (n1_list - 1)/(n_list - 2) * v1 + (n2_list - 1)/(n_list - 2) * v2
    tstat <- sqrt(n1_list * n2_list/n_list) * (m2 - m1)/sqrt(vpool)
    return(tstat)
}


rowVars <- function (x, na.rm = TRUE) 
{
    sqr = function(x) x * x
    n = rowSums(!is.na(x))
    n[n <= 1] = NA
    return(rowSums(sqr(x - rowMeans(x, na.rm = na.rm)), na.rm = na.rm)/(n - 
        1))
}

meta_analysis_p_value_combine <- function (df, signDf, BHth = 0.05) 
{   
    listres = vector("list", 8)
	nrep = df[nrow(df), ]
    fullFeatureLength = nrow(df) - 1
    commonFeatureBoolean = apply(df[1:fullFeatureLength, ], 1, function(x){
                return(all(!is.na(x)))
            })
    # commonFeatureIndex = which(commonFeatureBoolean)
    commonFeatureLength = sum(commonFeatureBoolean)

	tsco = apply(df[1:fullFeatureLength, ], 1, function(x){
			nbreptot = sum(nrep[!is.na(x)])
			weight = sqrt(nrep[!is.na(x)]/nbreptot)
			x = x[!is.na(x)]
	        vec = qnorm(1 - x)
	        stattestg = sum(weight[1:length(weight)] * vec[1:length(vec)], 
	            na.rm = TRUE)	
	        return(stattestg)
		})

    # print(tsco[1:4])

    pval = 2 * (1 - pnorm(abs(tsco)))

    # print(pval[1:4])

    effect = apply(signDf, 1, function(x){
    		y = sapply(x, function(z){
    				if(is.na(z)){
    					return('?')
    				}else if(z>0){
    					return('+')
    				}else if(z<0){
    					return('-')
    				}else{
    					return('!')
    				}
    			})
    		return(paste(y, collapse=""))
    	})
    
    # print(effect[1:4])

    bhAdjustPval = p.adjust(pval, method = "BH", n=fullFeatureLength)
    bfAdjustPval = p.adjust(pval, method = "bonferroni", n=fullFeatureLength)    

    # Calculate adjusted pvalue after duplicates filtered
    commBhAdjustPval = p.adjust(pval[commonFeatureBoolean], method = "BH", n=commonFeatureLength)
    commBfAdjustPval = p.adjust(pval[commonFeatureBoolean], method = "bonferroni", n=commonFeatureLength)

    # bhDegs = bhAdjustPval <= BHth
    # bfDegs = bfAdjustPval <= BHth
    # bhAdjustDegs = commBhAdjustPval <= BHth
    # bfAdjustDegs = commBfAdjustPval <= BHth

    sigcal = function(x, meth, leng){
        y = sapply(x, function(z){
                padj = p.adjust(z, method = meth, n=leng)
                if(is.na(padj)){
                    return('?')
                }else if(padj <= BHth){
                    return('!')
                }else{
                    return('-')
                }
            })
        return(paste(y, collapse=""))
    }
   
    # bhSig = apply(df[1:(nrow(df)-1), ], 1, sigcal, meth="BH", leng=fullFeatureLength)
    bfSig = apply(df[1:(nrow(df)-1), ], 1, sigcal, meth="bonferroni", leng=fullFeatureLength)
    # commBfSig = apply(df[1:(nrow(df)-1), ], 1, sigcal, meth="BH", leng=commonFeatureLength)
    # commBfSig = apply(df[1:(nrow(df)-1), ], 1, sigcal, meth="bonferroni", leng=commonFeatureLength)
    # print(length(tsco))
    # print(length(pval))
    # print(length(bhAdjustPval))
    # print(length(bfAdjustPval))
    # print(length(commBhAdjustPval))
    # print(length(commBfAdjustPval))
    # print(length(bfSig))
    # print(length(effect))

    listres[[1]] = tsco
    listres[[2]] = pval
    listres[[3]] = bhAdjustPval
    listres[[4]] = bfAdjustPval    
    listres[[5]] = commBhAdjustPval
    listres[[6]] = commBfAdjustPval
    # listres[[7]] = bhDegs
    # listres[[8]] = bfDegs
    # listres[[9]] = bhAdjustDegs
    # listres[[10]] = bfAdjustDegs
    # listres[[11]] = bhSig
    listres[[7]] = bfSig
    # listres[[13]] = commBfSig
    # listres[[14]] = commBfSig
    listres[[8]] = effect

    # result_df = as.data.frame(listres)
    # print(result_df[1:4, ])

    names(listres) = c("TScore", "PValue", 
                    "BhAdjustPval", "BfAdjustPval", "CommonBhAdjustPval", "CommonBfAdjustPval", 
                    #"BhDegs", "BfDegs", "CommonBhDegs", "CommonBfDegs",
                    # "BhSignificance", "CommonBhSignificance", "CommonBfSignificance",
                    "BfSignificance", 
                    "Effect")
    return(listres)
}