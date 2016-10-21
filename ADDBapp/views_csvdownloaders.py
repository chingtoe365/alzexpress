import requests
import csv

from data_formatter import get_deg_tables_from_collection

from .utils import check_nan_in_a_row

from django.http import HttpResponse

from views_constants import *

import pandas as pd


def download_cross_study_deg_csv(request, collecton_string):
	"""
		This page is to display cross study results
	"""

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')

	collection_names = collection_string.split('+')

	file_name = 'Common_DEGs_in_' + ' and '.join(collection_names) + '.csv'
	
	response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'

	comm_deg_stat_list = []

	# Get collection names
	meta_collections = meta_stat_client.get_all_collections()
	stat_collections = test_stat_client.get_all_collections()

	comm_deg_df, DEG_num_list, unique_symbol_num_list = get_deg_tables_from_collection(collection_names, meta_collections, meta_stat_client, test_stat_client)
		

	# Filter out those records with at least one NaN (They do not appear in all collections) 
	# Add one column to indicate NaN number
	
	comm_deg_df['no_nan'] = comm_deg_df.apply(check_nan_in_a_row, axis=1)
	
	# import pdb;pdb.set_trace();
	
	# Select those without nan and drop indicator column
	comm_deg_df = comm_deg_df[comm_deg_df['no_nan']].drop(['no_nan'], axis=1)

	comm_deg_stat_list = comm_deg_df.values.tolist()
	common_deg_names = list(comm_deg_df.index)

	writer = csv.writer(response)
	writer.writerow([''] + collection_names)
	for i in range(0, len(comm_deg_stat_list)):
		# writer.writerow(common_deg_names[i] + comm_deg_stat_list[i])
		row = [common_deg_names[i]] + comm_deg_stat_list[i]
		writer.writerow(row)

	return response

def download_csv_for_meta_queried_features(request, collection_name, feature_string):
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	
	file_name = 'Meta_analysis_for_' + collection_name + '_for_querired_features.csv'
	
	response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'

	columns = ['Feature', 'Meta t-score', 'Meta p-value', 'Adjusted p-value (BH)', 'Adjusted p-value (Bonferroni)', 'Adjusted p-value (BH, common features)', 'Adjusted p-value (Bonferroni, common features)', 'Significance', 'Effect']
	field_to_use = ['symb', 'tsco', 'pval', 'bhp', 'bfp', 'cbhp', 'cbfp', 'bfsig', 'eff']
	
	feature_symbols_in_interest = feature_string.split('+')
	records = list(meta_stat_client.get_all_records(collection_name))
	records = pd.DataFrame(records)
	filt_ind = records['symb'].isin(feature_symbols_in_interest)
	records_queried = records[filt_ind]
	records_queried = records_queried[field_to_use]
	meta_stat_queried = records_queried.values.tolist()
	
	writer = csv.writer(response)
	writer.writerow(columns)
	for i in range(0, len(meta_stat_queried)):
		# writer.writerow(common_deg_names[i] + comm_deg_stat_list[i])
		# row = [common_deg_names[i]] + comm_deg_stat_list[i]
		writer.writerow(meta_stat_queried[i])

	return response

def download_csv_for_all_meta_stat(request, collection_name):
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	
	file_name = 'Meta_analysis_for_' + collection_name + '.csv'
	
	response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'

	columns = ['Feature', 'Meta t-score', 'Meta p-value', 'Adjusted p-value (BH)', 'Adjusted p-value (Bonferroni)', 'Adjusted p-value (BH, common features)', 'Adjusted p-value (Bonferroni, common features)', 'Significance', 'Effect']
	field_to_use = ['symb', 'tsco', 'pval', 'bhp', 'bfp', 'cbhp', 'cbfp', 'bfsig', 'eff']
	# feature_symbols_in_interest = feature_string.split('+')
	records = list(meta_stat_client.get_all_records(collection_name))
	records = pd.DataFrame(records)
	records = records[field_to_use]
	# filt_ind = records['symb'].isin(feature_symbols_in_interest)
	# records_queried = records[filt_ind]
	meta_stat = records.values.tolist()
	
	writer = csv.writer(response)
	writer.writerow(columns)
	for i in range(0, len(meta_stat)):
		# writer.writerow(common_deg_names[i] + comm_deg_stat_list[i])
		# row = [common_deg_names[i]] + comm_deg_stat_list[i]
		writer.writerow(meta_stat[i])

	return response

def download_csv_for_separate_stat(request, dataset, region):
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')

	# collection_names = collection_string.split('+')

	file_name = 'Fold_change_and_p_value_for_' + dataset + '_in_' + region + '.csv'
	
	response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'


	data_type = sample_client.get_data_type(dataset)
	tissue = sample_client.get_tissue(dataset)
	collection_name = data_type + "_" + tissue + "_region-" + region + "_AD-vs-Control"
	# Vocano plots
	columns = ['Probe ID', 'Symbol', 'Fold Change', 'Limma p-value']
	field_to_use = ['pid', 'symb', 'fc', 'lp']
	fold_change_p_value_list = list(test_stat_client.get_all_pval_fold_change_for_this_dataset(collection_name, dataset))
	fold_change_p_value_df = pd.DataFrame(fold_change_p_value_list)
	fold_change_p_value_df.drop(['_id'], axis=1, inplace=True)
	fold_change_p_value_df = fold_change_p_value_df[field_to_use]
	stat = fold_change_p_value_df.values.tolist()
	
	
	writer = csv.writer(response)
	writer.writerow(columns)
	for i in range(0, len(stat)):
		# writer.writerow(common_deg_names[i] + comm_deg_stat_list[i])
		# row = [common_deg_names[i]] + comm_deg_stat_list[i]
		writer.writerow(stat[i])

	return response