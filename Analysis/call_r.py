import numpy as np
from pandas import *
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import pandas.rpy.common as com

def calculate_limma_and_t(table, disease_state, age, gender, debug=False):
	'''
		Pass variables to R
	'''

	# eliminate null age & gender samples
	N = len(age)
	to_keep_indexes = [i for i in range(N) if age[i] != None and gender[i] != None]
	# boo_for_df = [True if age[i] != None and gender[i] != None else False for i in range(N)]
	
	if debug: 
		print "no debug"
		# import pdb;pdb.set_trace()
	
	table = table[table.columns[to_keep_indexes]]

	disease_state = np.array(disease_state)[to_keep_indexes].tolist()
	
	age = np.array(age)[to_keep_indexes].tolist()
	gender = np.array(gender)[to_keep_indexes].tolist()

	# Convert pandas.dataFrame to R dataframe
	rdf = com.convert_to_r_matrix(table)
	ro.globalenv['table'] = rdf
	# ro.globalevn['symbols'] = symbols
	ro.globalenv['class'] = ro.IntVector(disease_state)
	ro.globalenv['age'] = ro.IntVector(age)
	ro.globalenv['gender'] = ro.IntVector(gender)
	
	
	'''
		Call statistic calculator functions
	'''
	
	ro.r('source("./R/stats.r")')
	
	'''
		Execute limma & ttest calculator
	'''
	ro.r('probe_names <- rownames(table)')
	ro.r('table <- as.data.frame(matrix(as.numeric(table), nrow=nrow(table)))')
	ro.r('rownames(table) <- probe_names')
	ro.r('limma_result <- limma_calculator(table, class, age, gender)')
	ro.r('ttest_result <- t_calculator(table, class)')

	'''	
		Load data from R into Python
	'''

	limma_result_dict = com.load_data('limma_result')
	ttest_result_dict = com.load_data('ttest_result')

	return limma_result_dict, ttest_result_dict



def meta_analysis_by_pval_combi(df_pval, df_tsco, debug=False):
	# Convert pandas.dataFrame to R dataframe
	pvaltable = com.convert_to_r_dataframe(df_pval)
	tscotable = com.convert_to_r_dataframe(df_tsco)

	ro.globalenv['pvaltable'] = pvaltable
	ro.globalenv['tscotable'] = tscotable

	'''
		Call statistic calculator functions
	'''
	
	ro.r('source("./R/stats.r")')
	
	'''
		Execute limma & ttest calculator
	'''

	ro.r('meta_analysis_result <- meta_analysis_p_value_combine(pvaltable, tscotable)')

	'''	
		Load data from R into Python
	'''

	meta_analysis_result_dict = com.load_data('meta_analysis_result')
	
	return meta_analysis_result_dict


def age_gender_normalize(exprs_table, age_lst, gender_lst):
	'''
		Pass variables to R
	'''

	# Convert pandas.dataFrame to R dataframe
	rdf = com.convert_to_r_matrix(exprs_table)
	
	ro.globalenv['expression_table'] = rdf
	ro.globalenv['age'] = age_lst
	ro.globalenv['gender'] = gender_lst
	
	'''
		Call preprocessing functions
	'''
	
	ro.r('source("./R/preprocessing.r")')
	
	'''
		Execute preprocessing
	'''

	ro.r('result <- age_gender_normalize(expression_table, age, gender)')

	'''	
		Load data from R into Python
	'''

	expression_table = com.load_data('result$corrected_table')
	stayed_index = com.load_data('result$stayed_samples_index')

	return expression_table, stayed_index


if __name__ == '__main__':
	table = pandas.DataFrame({"a" : [1,23,42,2,2,1,2],
						"b" : [2,3,2,4,1,4,5],
						"c" : [3,4,5,4,3,3,2]})
	age = [45,3,2,89, 3,2,3]
	gender = [1,2,2,2,1,1,2]
	disease_state = [0,1,1,0,0,1,1]
	# import pdb;pdb.set_trace()
	limmaresult, ttestresult = calculate_limma_and_t(table, disease_state, age, gender, True)
	print test