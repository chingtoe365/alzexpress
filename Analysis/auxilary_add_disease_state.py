from mongo_store import TestStatClient, SampleClient, AnnotationClient, MetaStatClient

from data_utils import extract_expression_table_by_sample_records, \
	get_disease_state_by_sample_records, expression_table_preprocessing, \
	get_feature_probe_symbol_dict_list, organize_test_stats

from stat_utils import calculate_fold_change_for_table

from call_r import calculate_limma_and_t, meta_analysis_by_pval_combi

from parameters import TISSUE_IN_INTEREST, DATA_TYPE_IN_INTEREST

import argparse

import progressbar

import pandas as pd
import numpy as np

def prepare_stat_record_and_insert(dataset, collection_name, disease_state_list, store=False):
	
	"""
		Prepare a record for the insertion into db
	"""

	query = {
		'dataset_accession' : dataset
	}
	new_stat_record = {
		'dsl' : disease_state_list
	}
	if store:
		test_stat_client.update_multi(collection_name, query, new_stat_record)

	return True

def variable_prepare(dataset, sample_client):
	"""
		Get basic meta-information for a particular dataset
	"""
	
	# Get data type for dataset
	data_type = sample_client.get_data_type(dataset)
	# Get tissue of dataset
	tissue = sample_client.get_tissue(dataset)

	# Get all category groups
	categories = sample_client.get_all_categories_in_dataset(dataset)

	return data_type, tissue, categories


def calculate_and_store_stat(datasets, sample_client, annotation_client, test_stat_client, debug=False, store=True):
	for dataset in datasets :
		print "Calculating stats of dataset %s ..." % (dataset, )

		# Prepare variables for later usage
		data_type, tissue, categories = variable_prepare(dataset,
												sample_client)
		print "Variables prepared"

		
		# Calculate stats cat by cat
		for category in categories :
			print "Processing %s in the %s group" % (category.keys()[0], category.values()[0], )
			
			# fetch the expression table for each category in the dataset
			sample_records_list = list(sample_client.fetch_sample_records_in_one_category(category, dataset))

			# count samples
			sample_count = len(sample_records_list)

			if debug:
				print "Sample count: %s" % (len(sample_records_list), )


			""" 
				we should add a loop for comparison here when other comparisons are added in (eg. AD vs. MCI, Control vs. MCI., PD vs. AD ....)
			"""
			disease_state_list = get_disease_state_by_sample_records(sample_records_list)
			
			if debug:
				"Length of disease state list : %s" % (len(disease_state_list), )
			
			if len(np.unique(disease_state_list)) != 2:
				print "Samples in this category group don't include two conditions!"
				print "disease state list", disease_state_list
				# Skip the calculation in this situation
				continue

			
			collection_name = "%s_%s_%s-%s_%s-vs-%s" % (data_type, 
														tissue, 
														category.keys()[0], 
														category.values()[0],
														"AD", # change when more comparison added
														"Control") # change when more comparison added
			print "Stats will be stored in collection name: %s" % (collection_name)
		
			### First update meta infor for each category group in teststat
			if store:
				disease_state_meta = {'AD' : 1, 'CNL' : 0, dataset : disease_state_list}
				test_stat_client.update_meta_disease_state(collection_name, disease_state_meta)

			# prepare_stat_record_and_insert(dataset,
			# 								collection_name,
			# 								disease_state_list,
			# 								store)
			
			print "Finished calculation of %s in the %s group" % (category.keys()[0], category.values()[0], )


if __name__ == "__main__" :
	"""
		This util add missing disease_state_list into teststat db
	"""

	datasets = ['GSE33000', 'GSE36980', 'GSE5281', 'GSE44772', 'GSE48350']
	# Define all clients
	test_stat_client = TestStatClient()
	sample_client = SampleClient()
	annotation_client = AnnotationClient()

	calculate_and_store_stat(datasets, sample_client, annotation_client, test_stat_client, debug=True, store=True)