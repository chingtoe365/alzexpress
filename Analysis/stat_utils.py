"""
	This script stores the statistics calculations needed throughtout the analyse
"""
import pandas as pd
import numpy as np

def get_absolute_log_fold_change(x, *args):
	"""
		Calculate the abs(log2(mean(group1) / mean(group2)))
			Expressed in R
	"""
	groups = args[0]
	debug = args[1]

	# if debug:
	# 	print "The array you're going to get abs log fold change is %s" % (x, )
	# 	print "The group variable shows %s" % (groups, )

	groups = np.array(groups)
	x = np.array(x)

	group0 = np.where(groups == 0)
	group1 = np.where(groups == 1)

	value0 = x[group0]
	value1 = x[group1]

	mean0 = np.nanmean(value0)
	mean1 = np.nanmean(value1)
	
	result = mean1 - mean0
	# result = np.log2(mean1 / mean0)
	# result = np.log2((mean1 - mean0) / mean0)
	
	return result


def get_log_fold_change_separate(evals, groups):
	"""
		Calculate the abs(log2(mean(group1) / mean(group2))) separately for each sample
			Expressed in R
	"""

	groups = np.array(groups)
	evals = np.array(evals)

	group0 = np.where(groups == 0)
	group1 = np.where(groups == 1)

	value0 = evals[group0]
	value1 = evals[group1]

	mean0 = np.nanmean(value0)
	mean1 = np.nanmean(value1)
	
	result = mean1 - mean0
	# result = np.log2(mean1 / mean0)
	# result = np.log2((mean1 - mean0) / mean0)
	
	return result

def calculate_fold_change_for_table(table, classes, debug=False) :
	
	table = pd.DataFrame.transpose(table)

	fold_change_pd_series = table.apply(get_absolute_log_fold_change, args=([classes, debug]))
	
	return list(fold_change_pd_series)


if __name__ == "__main__":
	test_df = pd.DataFrame(
		{
			"s1" : [None,2,3,4], 
			"s2" : [1.3,2.5,1.3,6.4],
			"s3" : [15.2,6.4,8.4,7.9],
			"s4" : [8.7,9.6,8.4,1.5],
			"s5" : [3,3.2,15,3.2]
		})
	test_class = [1,1,0,0,1]
	s = calculate_fold_change_for_table(test_df, test_class, True)
	print s

