''' Some utility functions to deal with data '''
import pandas as pd
import numpy as np

import progressbar

# from mongo_store import AnnotationClient

from parameters import KEYS_WITH_FLEXIBLE_LENGTH

def convert_unicode_to_none_for_array(array) :
	return [None if type(x) is unicode else x for x in array]

def turn_paired_array_into_dict(value_list, probe_id_list, debug=False):
# def turn_value_array_to_dict_with_gene_symbol(value_list, probe_id_list, debug=False):
	value_dict = {}
	
	for probe_id in probe_id_list:
		value = value_list[probe_id_list.index(probe_id)]
		value_dict.update({probe_id : value})
	
	if debug:
		print "A peek of value dictionary : %s" % (value_dict) 
	
	return value_dict
	# return [{x : int(value_list[probe_id_list.index(x)])} for x in probe_id_list]

def build_dict(seq, platform):
	"""
		converts a list of annotation entries into a dictionary of probe_id as key and symbol as value
		From
		[{'rosetta': [xxx, xxx], 'symbol' : 'symbol_name'}, {}, {}]
		To
		{'probe id 1' : 'symbol', 'probe id 2' : 'symbol', ...}
	"""
	new_dict = {}

	for item in seq:
		for probe in item[platform]:
			key_value = probe
			new_dict[key_value] = item['symbol']
	return new_dict

def turn_paired_arrays_into_dict(seq1, seq2):
	
	if len(seq1) != len(seq2) :
		print "Error! probe list length not equal to symbol list length!"

	length = len(seq1)

	return_dict = {}

	for i in range(0, length-1):
		new_dict = {
			seq1[i] : seq2[i]
		}
		return_dict.update(new_dict)

	return return_dict

def extract_single_from_list_in_dataset_dict(dataset_dict):
	''' 
		turn [element, ] to 'element' before storing into the database  
	'''
	for key in dataset_dict.keys():
		if len(dataset_dict[key]) == 1 and key not in KEYS_WITH_FLEXIBLE_LENGTH:
			dataset_dict[key] = dataset_dict[key][0]
	return dataset_dict

def get_feature_probe_symbol_dict_list(anno_type, probe_id_list, platform_id, anno_client):
	all_probe_ids = list(anno_client.get_all_probe_ids_by_platform(anno_type, platform_id))
	
	# covert probe gene list to easy-handle format
	all_probe_ids_dict = build_dict(all_probe_ids, platform_id)
	
	"""
		Get corresponding gene symbol of each probe
		If not probe not found in dict (not in anno db) then filter it out
		dict list should look like this:
		{
			'129_at_x' : 'ABC',
			'89_at_x' : 'BCD',
			...
		}
	"""
	feature_probe_symbol_dict = {p : all_probe_ids_dict[p] for p in probe_id_list if p in all_probe_ids_dict.keys()}
	
	old_count = len(probe_id_list)
	new_count = len(feature_probe_symbol_dict.keys())

	if new_count < old_count :
		print "Warning: Annotation missing for %s probes" % (old_count - new_count, )
	
	return feature_probe_symbol_dict

# def extract_expression_table_by_sample_records(sample_records, probe_id_list, debug=False) :
# 	expression_list = []
# 	# store disease state
# 	disease_state_list = []
	
# 	n_processed = 0
# 	n_pairs = len(sample_records)
# 	bar = progressbar.ProgressBar(maxval=n_pairs,
# 								widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
# 	bar.start()
# 	for record in sample_records :
# 		expression_value_list = record["expression_value"]
# 		# Turn any character in the list to None
# 		expression_value_list = [x if type(x) is int or type(x) is float else None for x in expression_value_list]

# 		sample_expression_dict = turn_value_array_to_dict_with_gene_symbol(expression_value_list, probe_id_list, debug)
		
# 		expression_list.append(sample_expression_dict)

# 		n_processed += 1
# 		bar.update(n_processed)

# 	bar.finish()
	
# 	if debug:
# 		print "Length of expression list : %s" % (len(expression_list), )

# 	output = pd.DataFrame(expression_list)
# 	return output


"""
	A quicker way to get expression table
"""

def extract_expression_table_by_sample_records(sample_records, debug=False) :
	expression_list = []
	# store disease state
	disease_state_list = []

	n_processed = 0
	n_pairs = len(sample_records)
	bar = progressbar.ProgressBar(maxval=n_pairs,
								widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()
	for record in sample_records :
		expression_value_list = record["expression_value"]
		# Turn any character in the list to None
		expression_value_list = [x if type(x) is int or type(x) is float else None for x in expression_value_list]

		# sample_expression_dict = turn_value_array_to_dict_with_gene_symbol(expression_value_list, probe_id_list, debug)
		
		expression_list.append(expression_value_list)

		n_processed += 1
		bar.update(n_processed)

	bar.finish()
	
	if debug:
		print "Length of expression list : %s" % (len(expression_list), )

	output = pd.DataFrame(expression_list)
	return output

	
def get_disease_state_by_sample_records(sample_records, debug=True):
	"""
		currently just comparing AD with Control
		will add AD vs. MCI & Control vs. MCI later
	"""
	disease_state = []
	for record in sample_records:
		disease_state_str = record["disease_state"]
		if disease_state_str == "AD":
			disease_state.append(1)
		elif disease_state == "CNL" : 
			disease_state.append(0)
		else:
			print "Other disease state detected: %s" % (disease_state, )
			disease_state.append(-1)
			# continue
	return disease_state

def expression_table_preprocessing(table, gene_symbol_list, disease_state_list, remove_duplicate_by="fold_change" ,debug=True):
	"""
		this preprocessing function handles
				-- Duplicates of probes
			We provide only one way of selection at this stage
				---- the one with highest fold change
			Following ways of removing duplicates are to add:
				-- averaging
				-- highest p-value 			
	"""
	if debug:
		print "4 x 4 preview of unprocessed table: %s" % (table.iloc[0:3, 0:3], )
		print "Preview of gene symbol list %s" % (gene_symbol_list[0:4], )

	chosen_probes = []
	chosen_symbols = []

	unique_symbol_list = list(set(gene_symbol_list))
	np_gene_symbol_list = np.array(gene_symbol_list)
	
	for ugs in unique_symbol_list:
		matched_indexes = np.where(np_gene_symbol_list == ugs)
		if len(matched_indexes) > 1:
			leave_one_only_table = table[matched_indexes]
			fold_change_values = leave_one_only_table.apply(get_absolute_log_fold_change, args=(disease_state_list, ))
			chosen_probe = fold_change_values.idxmax()
			chosen_probes.append(chosen_probe)
		else:
			chosen_probe = table.columns.values[matched_indexes][0]
			chosen_probes.append(chosen_probe)
	chosen_symbols = unique_symbol_list
	table_without_duplicate = table[np.array(chosen_probes)]
	return table_without_duplicate, chosen_symbols


# def calculate_statistic_for_each_gene(gene_meta, expression):

def organize_test_stats(collection_name, test_stat_client, debug=False):
	"""
		This function turn teststat record to desirable format for meta-analysis
		which look something like this:
				study1	study2	study3
		gene1	xxx		xxx		xxx
		gene2	xxx		xxx		xxx
		gene3	xxx		xxx		xxx
		...
		sample_count	xxx		xxx		xxx
	"""

	# symbol_list = []
	sample_count = []

	# Get all dataset in this collection
	studies = test_stat_client.get_all_datasets(collection_name)

	# Get all records for this collection
	all_records = list(test_stat_client.get_all_stat_records(collection_name))

	# Get sample count dataframe
	sample_count_list = [test_stat_client.get_sample_count(collection_name)]

	if debug:
		print len(all_records)

	# Convert records and sample_count to dataframe
	records = pd.DataFrame(all_records)
	sample_count_df = pd.DataFrame(sample_count_list, index=['sampleCount'])

	fields_to_get = ['dataset_accession', 'lp', 'lt', 'symb', 'pid']
	# Slim the dataFrame
	records = records[fields_to_get]

	p_val_dict = {}
	t_sco_dict = {}

	for study in studies:
		# Get record for a particular dataset in a particular collection
		record = records[records['dataset_accession'] == study]

		if debug:
			print record.iloc[0:3]
			# print record['symb'][0] == ''
			# print type(record['symb'][0])

		# Filter out null symbols
		record = record[record['symb'] != '']
		
		if debug:
			print record.iloc[0:3]

		# Filter out duplicated probes with limma p-value (select highest)
		record = record.sort('lp').groupby('symb').first()
		
		if debug:
			print record.iloc[0:3]
			
		# Get series of limma p and limma t
		p_val_list_single_study = record['lp']
		t_sco_list_single_study = record['lt']

		p_val_dict.update({study : p_val_list_single_study})
		t_sco_dict.update({study : t_sco_list_single_study})

	pval_df = pd.DataFrame(p_val_dict)
	tsco_df = pd.DataFrame(t_sco_dict)

	# Empty indexes in case of duplicates which R does not allow to exists
	# pval_df.index = range(0, pval_df.shape[0])
	# tsco_df.index = range(0, tsco_df.shape[0])

	# if debug:
	# 	print pval_df[0:3]
	# 	print tsco_df[0:3]
	
	# symbol_list = list(records['symb'])
	# probe_id_list = list(records['pid'])
	# Append sample count row in pval_df
	# sample_count_df = pd.DataFrame([sample_count])
	
	if debug:
		print sample_count_df
		print pval_df.iloc[0:3]
		print tsco_df.iloc[0:3]

	pval_df = pval_df.append(sample_count_df)

	if debug:
		print pval_df.iloc[0:3]
		
	return pval_df, tsco_df # , probe_id_list, symbol_list



if __name__ == "__main__":
	pdf, tdf, pidlst, symlst = organize_test_stats(collection_name, test_stat_client, debug=False)