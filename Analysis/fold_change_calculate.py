from mongo_store import TestStatClient, SampleClient, AnnotationClient, MetaStatClient

from data_utils import extract_expression_table_by_sample_records, \
	get_disease_state_by_sample_records, expression_table_preprocessing, \
	get_feature_probe_symbol_dict_list, organize_test_stats

from stat_utils import calculate_fold_change_for_table

from call_r import calculate_limma_and_t, meta_analysis_by_pval_combi, \
					age_gender_normalize

from parameters import TISSUE_IN_INTEREST, DATA_TYPE_IN_INTEREST

import argparse

import progressbar

import pandas as pd
import numpy as np

def prepare_stat_record_and_insert(dataset, collection_name, probe_id_list, fold_change, store=False):
	
	"""
		Prepare a record for the insertion into db
	"""

	print "Stroring test statistics..."

	n_processed = 0
	n_pairs = len(probe_id_list)
	bar = progressbar.ProgressBar(maxval=n_pairs,
								widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()
	count = 0
	for probe in probe_id_list :
		
		fc = fold_change[count]
		new_stat_record = {
				'dataset_accession' : dataset,
				'pid' : probe,
				'fc' : fc,
		}
		if store:
			test_stat_client.insert_record(collection_name, new_stat_record)

		n_processed += 1
		bar.update(n_processed)
		count = count + 1

	bar.finish()
	
	print "Finished test statistics storing!"

	return True

def calculate_and_store_statistic_of_given_table(table, disease_state, debug=False):
	"""
		stats to calculate:
			fold change
			limma z score
			limma p value
			normal t-test z score
			normal t-test p value
		stats to added
			loocv SVM accuracy
	"""
	table = pd.DataFrame.transpose(table)
	
	if debug:
		"Table glimpse : %s" % (table.iloc[0:2, 0:2])
	
	# Calculate fold change
	fold_change = calculate_fold_change_for_table(table, disease_state, debug)

	if debug:
		print "Length of fold change list : %s" % (len(fold_change), )

	return fold_change


def variable_prepare(dataset, sample_client, annotation_client):
	"""
		Get basic meta-information for a particular dataset
	"""
	
	# Get data type for dataset
	data_type = sample_client.get_data_type(dataset)
	# Get tissue of dataset
	tissue = sample_client.get_tissue(dataset)

	"""
		Keep using this before renew of annotation db
	"""
	# # Get platform name
	# platform_name = sample_client.get_platform_name(dataset)
	# # Get platform type
	# platform_type = sample_client.get_platform_type(platform_name)
	
	"""
		Use this after renewal of annotation db
	"""
	# Get platform id
	platform_id = sample_client.get_platform_id(dataset)

	# Get probe id list
	probe_id_list = sample_client.get_probe_id_list(dataset)
	# Get corresponding feature symbol list
	feature_probe_symbol_dict = get_feature_probe_symbol_dict_list(probe_id_list, platform_id, annotation_client)
	# feature_probe_symbol_dict = get_feature_probe_symbol_dict_list(probe_id_list, platform_type, annotation_client)

	# Get all category groups
	categories = sample_client.get_all_categories_in_dataset(dataset)

	return data_type, tissue, probe_id_list, feature_probe_symbol_dict, categories


def calculate_and_store_stat(datasets, sample_client, annotation_client, test_stat_client, debug=False, store=True):
	for dataset in datasets :
		print "Calculating stats of dataset %s ..." % (dataset, )

		# Prepare variables for later usage
		data_type, tissue, probe_id_list, feature_probe_symbol_dict, categories = variable_prepare(dataset,
																									sample_client,
																									annotation_client)
		print "Variables prepared"
		if debug:
			print "Meta info of this datset"
			print "Data type : %s" % (data_type, )
			print "Tissue : %s" % (tissue, )
			print "Probe & symbol count : %s" % (len(feature_probe_symbol_dict.keys()), )
			print "To calculate category groups: %s" % (categories, )
		
		# Calculate stats cat by cat
		for category in categories :
			print "Processing %s in the %s group" % (category.keys()[0], category.values()[0], )
			
			# fetch the expression table for each category in the dataset
			sample_records = sample_client.fetch_sample_records_in_one_category(category, dataset)
			sample_records_list = list(sample_records)

			# count samples
			sample_count = len(sample_records_list)
			
			if debug:
				print "Sample count: %s" % (len(sample_records_list), )

			age_list = [x['age'] for x in sample_records_list]
			gender_list = [x['gender'] for x in sample_records_list]
			
			# age_list = []
			# gender_list = []
			# for record in sample_records:
			# 	# get age list
			# 	age_list.append(record['age'])
			# 	# get gender list
			# 	gender_list.append(record['gender'])

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

			print "Extracting expression table"

			# expression_value_list = list(sample_client.fetch_sample_record_expression_in_one_category(category, dataset))

			expression_table = extract_expression_table_by_sample_records(sample_records_list, debug)

			expression_table.columns = probe_id_list
			print "Expression table extracted"

			if debug:
				print expression_table.iloc[1:2, 1:2]
	
			fold_change = calculate_and_store_statistic_of_given_table(expression_table,  
																	disease_state_list,
																	debug)
			print "Statistics calculated"
			# Store result in database
			"""
				Extension: when more comparison added, name variable should adjust here
			"""
			collection_name = "%s_%s_%s-%s_%s-vs-%s" % (data_type, 
														tissue, 
														category.keys()[0], 
														category.values()[0],
														"AD", # change when more comparison added
														"Control") # change when more comparison added
			print "Stats will be stored in collection name: %s" % (collection_name)
		
			### First update meta infor for each category group in teststat

			prepare_stat_record_and_insert(dataset,
											collection_name,
											probe_id_list,
											fold_change,
											store)
			
			print "Finished calculation of %s in the %s group" % (category.keys()[0], category.values()[0], )

if __name__ == "__main__" :
	"""
		the pre-calculation and anaylsis of DEGs is done from command line. 
	"""
	parser = argparse.ArgumentParser(description='Calculate statistics of given datasets')

	parser.add_argument('--method', 
						dest='method', 
						choices=['meta', 'sep'], 
						default='sep')

	parser.add_argument('--datasets', 
						metavar='N', 
						type=str, 
						nargs='+',
						help='datasets to process')

	parser.add_argument('--data-type',
						dest='data_type',
						metavar='RNA/miRNA/methylation/protein',
						type=str)

	parser.add_argument('--tissue',
						dest='tissue',
						metavar='brain/blood',
						type=str)

	parser.add_argument('--group-category',
						dest='group_category',
						metavar='gender/region/age',
						type=str)	

	parser.add_argument('--group-name',
						dest='group_name',
						metavar=' M/F/PFC/HI/..',
						type=str)

	parser.add_argument('--state-1',
						dest='state_1',
						metavar='AD',
						type=str)
	
	parser.add_argument('--state-0',
						dest='state_0',
						metavar='CNL',
						type=str)

	parser.add_argument('--debug', dest='debug', action='store_true')
	parser.set_defaults(debug=False)	

	parser.add_argument('--store', dest='store', action='store_true')
	parser.set_defaults(store=False)
	
	args = parser.parse_args()

	print args.method
	print args.datasets

	if args.method == 'meta':
		if args.datasets is not None:
			parser.error('Mismatch of chosen method and subsequent arguments, make sure you select the right method!')
		elif args.data_type is None:
			parser.error('Data type missing! Example: --data-type=RNA')
		elif args.tissue is None:
			parser.error('Tissue missing! Example: --tissue=brain')		
		elif args.group_category is None:
			parser.error('Group category missing! Example: --group_category=gender')		
		elif args.group_name is None:
			parser.error('Group name missing! Example: --group_name=F')		
		elif args.state_1 is None:
			parser.error('State 1 missing! Example: --state_1=AD')
		elif args.state_0 is None:
			parser.error('State 0 missing! Example: --state_0=Control')

		# Define all clients
		test_stat_client = TestStatClient()
		meta_stat_client = MetaStatClient()

		collection_name = "%s_%s_%s-%s_%s-vs-%s" % (args.data_type, 
													args.tissue, 
													args.group_category, 
													args.group_name,
													args.state_1,
													args.state_0)

		print "Stat collection to do meta-analysis: %s" % (collection_name, )

		execute_meta_analysis(collection_name, test_stat_client, meta_stat_client, debug=args.debug, store=args.store)

		print "Meta-analysis finished!"


	elif args.method == 'sep':
		if args.data_type is not None or args.tissue is not None or args.group_category is not None or args.group_name is not None or args.state_0 is not None or args.state_1 is not None:
			parser.error('Mismatch of chosen method and subsequent arguments, make sure you select the right method!')
		elif args.datasets is None :
			parser.error('You haven\'t provided any datasets!')

		# Define all clients
		test_stat_client = TestStatClient()
		sample_client = SampleClient()
		annotation_client = AnnotationClient()

		''' 
			when doing updates this variable can be specified to new datasets manually
			That's why I leave it in main
		'''
		# Initialize and get all datasets 
		# datasets = sample_client.get_all_dataset_name()
		# datasets = ["GSE5281", "GSE44772"] # GSE36980 annotation missing
		datasets = args.datasets
		# datasets = ["test"] # GSE36980 annotation missing

		print "Datasets to be calculated: %s" % (datasets, )
		calculate_and_store_stat(datasets, sample_client, annotation_client, test_stat_client, debug=args.debug, store=args.store)
		print "Separate datasets calculation finished!"

	else:
		parser.error('Wrong methods! Assign "meta" or "sep" to --method')


