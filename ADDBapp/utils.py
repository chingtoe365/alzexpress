# Helper functions defined here
import re

import pandas as pd

import numpy as np

def extract_single_from_list_in_dataset_dict(dataset_dict):
	''' 
		turn [element, ] to 'element' before storing into the database  
	'''
	for key in dataset_dict.keys():
			if len(dataset_dict[key]) == 1 and key not in KEYS_WITH_FLEXIBLE_LENGTH:
				dataset_dict[key] = dataset_dict[key][0]
	return dataset_dict



def combine_multiple_filters_to_query(filters):
	query = {}
	# projector = {"_id" : 1, "expression_value" : 1, "probe_id" : 1}
	for f in filters:
		newDict = generate_query_by_single_inputs(f[0], f[1], f[2])
		# import pdb; pdb.set_trace()
		
		if newDict.keys()[0] in query.keys():
			# import pdb; pdb.set_trace()
			query[newDict.keys()[0]].update(newDict[newDict.keys()[0]])
		else:
			query.update(newDict)
		# import pdb; pdb.set_trace()
	# return [query, projector]
	return query


def generate_query_by_single_inputs(filterBy, relation, keyword) :
	# import pdb; pdb.set_trace()
	
	if "exist" in relation:
		if "!" in relation:
			query = {filterBy : {"$exists" : "False" }}
		else:
			query = {filterBy : {"$exists" : "True" }}
	elif "regex" in relation:
		if "!" in relation:
			query = {filterBy : {"$not" : re.compile(keyword) }}
		else:
			# import pdb; pdb.set_trace()
			query = {filterBy : {"$regex" : str(keyword) }}
			# import pdb; pdb.set_trace()
	elif "in" in relation:
		query = {filterBy : {relation : keyword }}
	else :
		query = {filterBy : {relation : int(keyword) }}
	return query

def get_element_by_indexes(indexArray, array):
	return [array[index] for index in xrange(len(array)) if index in indexArray]


def filtered_duplicate_by(df, metric):
	"""
		First sort by descending order, and then group by symbol, then select the first occurence
		Then select the indexes (probe names)
	"""
	# import pdb; pdb.set_trace();
	# filtered_probes = list(df.sort(metric, ascending=False).groupby('symb', as_index=False).first().index())
	# probe_df = pd.DataFrame(df.index, columns=['probe'], index=df.index)
	# df = pd.concat([probe_df, df], axis=1)
	filtered_df = df.sort(metric, ascending=False).groupby('symb', as_index=False).first()
	# print filtered_df
	return filtered_df



def split_feature_input_to_list(feature_str):
	delimer = "\r\n"
	return feature_str.split(delimer)


def extract_gene_symbol_from_protein_name(protein_name):
	symb_search = re.search(r'(.+\()(.+)(\).+)', protein_name)
	if not symb_search:
		return symb_search.group(2)
	else:
		return None