library(MASS)

age_gender_normalize <- function(expression_table, age, gender){
    # newtable = log(table, 2)
    newtable = expression_table
    # Store all column names (variable names) first
    var_names = colnames(newtable)
    # Change column names of table to predictable names
    colnames(newtable) = paste("var", 1:ncol(newtable), sep="")
    # age = unlist(age)
    # gender = unlist(gender)

    gender[gender=="M"] = 1
    gender[gender=="F"] = 2
    gender = as.numeric(gender)
    age = as.numeric(age)
    
    newtable = as.data.frame(newtable, stringsAsFactors=FALSE)
    newtable['AGE'] = age
    newtable['GENDER'] = gender

    # Remove samples with null age value
    stayed_samples_index = which(!is.na(age) & !is.na(gender))

    newtable = newtable[stayed_samples_index, ]
    # newtable = newtable[!is.na(age), ]
    # newtable = newtable[!is.na(gender), ]

    # print(newtable[1:4,1:4])
    
    # stayed_samples_index = stayed_samples_index - 1

    correctedValueVec =sapply(1:(ncol(newtable)-2), function(x){
        var.this = paste("var", x, sep="")
        exprsVals = newtable[, x]
        fit = rlm(get(var.this) ~ AGE + GENDER, data=newtable, na.action=na.exclude, maxit=500)
        # fit = rlm(newtable[, x], newtable[, c("AGE", "GENDER")], na.action=na.exclude, maxit=100)
        correctedExpValWithoutNA = fit$coefficients[1] + fit$residuals
        # print(correctedExpValWithoutNA)
        # print(exprsVals)
        # stop()
        exprsVals[!is.na(exprsVals)] = correctedExpValWithoutNA
        # print(correctedExpVal)
        # print(paste(x, "done!", sep=" "))
        if ((x %% 1000 == 0) & (x >= 1000)){
            print(paste(x, ' probes processed', sep=""))
        }
        return(exprsVals)
    })
    # correctedExpVal = array()
    # for(i in 1:(ncol(newtable)-2)){
    #     var.this = paste("var", i, sep="")
    #     fit = rlm(get(var.this) ~ AGE + GENDER, data=newtable, na.action=na.exclude, maxit=100)
    #     # fit = rlm(newtable[, x], newtable[, c("AGE", "GENDER")], na.action=na.exclude, maxit=100)
    #     correctedExpVal = c(correctedExpVal, fit$coefficients[1] + fit$residuals)
    #     print(paste(i, "completed"))
    # }

    correctedTable = matrix(correctedValueVec, ncol=(ncol(newtable) - 2))
    colnames(correctedTable) = var_names
    # rownames(correctedTable) = rownames(newtable)[stayed_samples_index]

    return_list = list(correctedTable, stayed_samples_index)
    names(return_list) = c("corrected_table", "stayed_samples_index")

    return(return_list)
}