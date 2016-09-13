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

def prepare_stat_record_and_insert(dataset, collection_name, sample_count, probe_id_list, feature_probe_symbol_dict, limma_result_dict, t_result_dict, fold_change, expression_table, store=False):
	
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
		if probe in feature_probe_symbol_dict.keys():
			symbol = feature_probe_symbol_dict[probe][0]
		else :
			symbol = ''
		limma_t = limma_result_dict['t_score'][count]
		limma_p = limma_result_dict['p_value'][count]
		ttest_t = t_result_dict['t_score'][count]
		ttest_p = t_result_dict['p_value'][count]
		fc = fold_change[count]
		evalue = list(expression_table[probe])
		new_stat_record = {
				'dataset_accession' : dataset,
				'pid' : probe,
				'symb' : symbol,
				'lt' : limma_t,
				'lp' : limma_p,
				'tt' : ttest_t,
				'tp' : ttest_p,
				'fc' : fc,
				'eval' : evalue
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

	# Call R to calculate limma & t test
	limma_result_dict, t_result_dict = calculate_limma_and_t(table, disease_state, debug)
	
	# Calculate fold change
	fold_change = calculate_fold_change_for_table(table, disease_state, debug)

	if debug:
		print "Length of fold change list : %s" % (len(fold_change), )

	return limma_result_dict, t_result_dict, fold_change


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
	
			# Pre-processing of expression table
			"""
				After discussion we decided to do statistics for all features before removing duplicates
			"""
			## 1. NaN value
			## 2. Probe duplicates

			# """
			# 	Pre-processing : Remove effect of age and gender
			# """

			# # expression_table, stayed_index = age_gender_normalize(expression_table, age_list, gender_list)

			# # disease_state_list = list(np.array(disease_state_list)[stayed_index])
			
			# processed_table, refined_gene_symbol_list = expression_table_preprocessing(expression_table, gene_symbol_list, disease_state_list)
			limma_result_dict, t_result_dict, fold_change = calculate_and_store_statistic_of_given_table(expression_table,  
																							disease_state_list,
																										debug)
			print "Statistics calculated"
			# Store result in database
			"""
				Extension: when more comparison added, name variable should adjust here
			"""
			region_name = category.values()[0]
			
			if category.values()[0] == "SFG":
				for region_name in ["PFC", "SFG", ]:

					collection_name = "%s_%s_%s-%s_%s-vs-%s" % (data_type, 
																tissue, 
																category.keys()[0], 
																region_name,
																"AD", # change when more comparison added
																"Control") # change when more comparison added
					print "Stats will be stored in collection name: %s" % (collection_name)
				
					### First update meta infor for each category group in teststat
					if store:
						sample_count = {dataset : sample_count}
						test_stat_client.update_meta_sample_count(collection_name, sample_count)				
						disease_state = {'AD' : 1, 'CNL' : 0, dataset : disease_state_list}
						test_stat_client.update_meta_disease_state(collection_name, disease_state)

					prepare_stat_record_and_insert(dataset,
													collection_name,
													sample_count,
													probe_id_list,
													feature_probe_symbol_dict,
													limma_result_dict,
													t_result_dict, 
													fold_change,
													expression_table,
													store)
				
				print "Finished calculation of %s in the %s group" % (category.keys()[0], category.values()[0], )

def execute_meta_analysis(collection_name, test_stat_client, meta_stat_client, debug=False, store=True):
	
	# Fetch stats and organize it into required format for meta-analysis function in R
	pval_df, tsco_df = organize_test_stats(collection_name, test_stat_client, debug=debug)

	feature_length = tsco_df.shape[0]
	symbol_list = list(pval_df.index[0:feature_length])

	if debug:
		print feature_length
		print symbol_list[0:3]

	# Execute meta-analysis
	meta_analysis_result_dict = meta_analysis_by_pval_combi(pval_df, tsco_df, debug=debug)

	# Turn to dataframe before store
	meta_result_df = pd.DataFrame(meta_analysis_result_dict)

	if debug:
		print meta_result_df.iloc[0:3, ]

	# Turn meta result dict to storable format
	for i in range(0, meta_result_df.shape[0]):
		new_meta_record = {
			# 'pid': p,
			'symb' : symbol_list[i],
			'tsco' : meta_result_df['TScore'][i],
			'pval' : meta_result_df['PValue'][i],
			'bhp' : meta_result_df['BhAdjustPval'][i],
			'bfp' : meta_result_df['BfAdjustPval'][i],
			'cbhp' : meta_result_df['CommonBhAdjustPval'][i],
			'cbfp' : meta_result_df['CommonBfAdjustPval'][i],
			# 'bhdeg' : meta_result_df['BhDegs'][i],
			# 'bfdeg' : meta_result_df['BfDegs'][i],
			# 'cbhdeg' : meta_result_df['CommonBhDegs'][i],
			# 'cbfdeg' : meta_result_df['CommonBfDegs'][i],
			# 'bhsig' : meta_result_df['BhSignificance'][i],
			'bfsig' : meta_result_df['BfSignificance'][i],
			# 'cbhsig' : meta_result_df['CommonBhSignificance'][i],
			# 'cbfsig' : meta_result_df['CommonBfSignificance'][i],
			'eff' : meta_result_df['Effect'][i]
		}
		if debug:
			print new_meta_record

		# Store the result if needed
		if store:
			meta_stat_client.insert_meta_analysis_record(collection_name, new_meta_record)

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


