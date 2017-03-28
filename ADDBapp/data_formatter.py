"""
This is to format the tables
"""
import pandas as pd
import numpy as np

from .utils import filtered_duplicate_by, \
				extract_gene_symbol_from_protein_name

def get_deg_tables_from_collection(collection_names, meta_collections, meta_stat_client, test_stat_client):
	"""
		Extract DEG tables from collections requested
	"""
	comm_deg_df = pd.DataFrame()

	DEG_num_list = []

	unique_symbol_num_list = []

	for collection in collection_names:
		if collection in meta_collections:
			# If this collection is found in meta stats, use it
			# Count DEG numbers
			all_meta_stat = list(meta_stat_client.get_all_records(collection))
			meta_stat_df = pd.DataFrame(all_meta_stat)


			# change dataframe index to symbol
			# If it's a collection for protein, change symbol names
			if 'protein' in collection:
				meta_stat_df['index_temp'] = list(meta_stat_df['symb'].apply(extract_gene_symbol_from_protein_name))
			else:
				meta_stat_df['index_temp'] = list(meta_stat_df['symb'])
			# import pdb;pdb.set_trace();
			
			# Remove empty temp symbols
			meta_stat_df = meta_stat_df[np.invert(meta_stat_df['index_temp'] == '')]
			# Assign it to index
			meta_stat_df.index = list(meta_stat_df['index_temp'])
			
			unique_symbol_num_list.append(meta_stat_df.shape[0])

			deg_df = meta_stat_df[meta_stat_df['bfp'] <= 0.05]

			DEG_num_list.append(deg_df.shape[0])
			
			# Prepare common genes
			deg_df = pd.DataFrame(deg_df['bfp'])
			deg_df.columns = [collection]
			# print deg_df.index.is_unique

			comm_deg_df = pd.concat([comm_deg_df, deg_df], axis=1)
			# import pdb;pdb.set_trace();
			
		else:
			# If this collection is not found in meta stat collection, use only stat collection 
			# Count DEG numbers
			all_stat = list(test_stat_client.get_all_records(collection))
			stat_df = pd.DataFrame(all_stat)
			# import pdb;pdb.set_trace()

			# change dataframe index to symbol
			# If it's a collection for protein, change symbol names
			if 'protein' in collection:
				stat_df['index_temp'] = list(stat_df['symb'].apply(extract_gene_symbol_from_protein_name))
			else:
				stat_df['index_temp'] = list(stat_df['symb'])
			# print deg_df.iloc[0:10,]
			# print deg_df.iloc[0:3, ]
			
			# Remove empty temp symbols
			stat_df = stat_df[np.invert(stat_df['index_temp'] == '')]
			
			# remove duplicates
			stat_df = filtered_duplicate_by(stat_df, by='lp', group_index=['index_temp'])
			
			# Assign it to index
			stat_df.index = list(stat_df['index_temp'])
			
			unique_symbol_num_list.append(stat_df.shape[0])

			deg_df = stat_df[stat_df['lp'] <= 0.05]

			DEG_num_list.append(deg_df.shape[0])
			
			# Prepare common genes
			deg_df = pd.DataFrame(deg_df['lp'])
			deg_df.columns = [collection]
			
			new_comm_df = pd.concat([comm_deg_df, deg_df], axis=1)

			comm_deg_df = pd.concat([comm_deg_df, deg_df], axis=1)


	return comm_deg_df, DEG_num_list, unique_symbol_num_list
