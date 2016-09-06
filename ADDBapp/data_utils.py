"""
Data utilities
"""
import pandas as pd
import numpy as np

def scale_normalize(x):
	"""
		Normalize column values (each probe) for heatmap figure
	"""
	x = np.array(x)
	mean = np.nanmean(x)
	sd = np.nanstd(x)

	new_x = (x - mean) / sd

	new_x = new_x / np.nanmax(abs(new_x))
	# print new_x

	return new_x




def normalize_heatmap_row_expression(table):
	"""
		row - sample
		column - probe
	"""
	normalized_series = table.apply(scale_normalize)

	return normalized_series


if __name__ == "__main__":
	test_df = pd.DataFrame(
		{
			"s1" : [None,2,3,4], 
			"s2" : [1.3,2.5,1.3,6.4],
			"s3" : [15.2,6.4,8.4,7.9],
			"s4" : [8.7,9.6,8.4,1.5],
			"s5" : [3,3.2,15,3.2]
		})
	
	print test_df

	s = normalize_heatmap_row_expression(test_df)
	print s
	# print type(s)
	# print s[0]