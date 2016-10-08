from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from .utils import combine_multiple_filters_to_query, filtered_duplicate_by, \
				split_feature_input_to_list, extract_gene_symbol_from_protein_name

from data_utils import normalize_heatmap_row_expression

from .forms import featureSelectionForm

from graph_data import generate_series_from_list, generate_scatterplot_series, \
						generate_volcanoplot_series

from url_data import generate_mulivariable_series_from_list, \
					from_symbol_to_entrez_gene_id, \
					from_single_symbol_to_string_id, \
					generate_string_id_get_query_from_list

from parameters import ALL_PLATFORMS, ALL_REGIONS

import pandas as pd
import numpy as np

# from django.utils import simplejson

from views_constants import *

def home(request):
	return render(request, 'home.html')

def upload(request):
	return "This page is depreciated" 

def summary(request):
	sample_proportion_dict_list = []
	region_proportion_dict_list = []
	gender_proportion_dict_list = []
	region_dict = {}
	male_count = 0
	female_count = 0
	for region in ALL_REGIONS:
		region_dict[region] = 0
	all_datasets = sample_client.get_all_datasets()
	for dataset in all_datasets:
		sample_proportion_dict_list.append({
				'name' : dataset.encode('utf-8'),
				'y' : sample_client.count_samples(dataset)
			})
		male_count += sample_client.count_gender_samples(dataset, 'M')
		female_count += sample_client.count_gender_samples(dataset, 'F')
		for region in ALL_REGIONS:
			region_dict[region] += sample_client.count_region_samples(dataset, region)

	gender_proportion_dict_list = [
		{
			'name' : 'Male',
			'y' : male_count
		},
		{
			'name' : 'Female',
			'y' : female_count
		}
	]

	for region in ALL_REGIONS:
		region_proportion_dict_list.append({
			'name' : region,
			'y' : region_dict[region]
		})

	return render(request, 'summary.html', {
		'sample_proportion' : sample_proportion_dict_list,
		'gender_proportion' : gender_proportion_dict_list,
		'region_proportion' : region_proportion_dict_list
	})


def dataset_summary(request, dataset):
	# Set returned variables
	region_proportion_dict_list = []
	gender_proportion_dict_list = []
	region_dict = {}

	male_count = sample_client.count_gender_samples(dataset, 'M')
	female_count = sample_client.count_gender_samples(dataset, 'F')
	all_regions = list(sample_client.get_all_regions(dataset))
	all_regions = [x.encode("utf-8") for x in all_regions]
	for region in all_regions:
		region_dict[region] = sample_client.count_region_samples(dataset, region)

	gender_proportion_dict_list = [
		{
			'name' : 'Male',
			'y' : male_count
		},
		{
			'name' : 'Female',
			'y' : female_count
		}
	]

	for region in all_regions:
		region_proportion_dict_list.append({
			'name' : region,
			'y' : region_dict[region]
		})

	# Top 10 features
	


	return render(request, 'dataset_summary.html', {
		# 'sample_proportion' : sample_proportion_dict_list,
		'dataset' : dataset,
		'regions' : all_regions,
		'gender_proportion' : gender_proportion_dict_list,
		'region_proportion' : region_proportion_dict_list
	})

def summary_volcano(request, dataset, region):
	# Set returned variables
	print dataset
	print region
	collection_name = "RNA_brain_region-" + region + "_AD-vs-Control"
	# Vocano plots

	fold_change_p_value_list = list(test_stat_client.get_all_pval_fold_change_for_this_dataset(collection_name, dataset))
	print len(fold_change_p_value_list)
	fold_change_p_value_df = pd.DataFrame(fold_change_p_value_list)
	deg_series, normal_series, deg_features, normal_features = generate_volcanoplot_series(fold_change_p_value_df)
	
	deg_count = len(deg_series)
	molecule_count = deg_count + len(normal_series)

	return render(request, 'dataset_summary_volcano.html', {
		'dataset' : dataset,
		'volcano_deg_data_series' : deg_series,
		'volcano_normal_data_series' : normal_series,
		'volcano_deg_features' : deg_features,
		'volcano_normal_features' : normal_features,
		'deg_count' : deg_count,
		'molecule_count' : molecule_count
	})

def query(request):
	"""
		This page is to display query feature statistics
	"""
	# initialize form
	form = featureSelectionForm()
	# query output for displaying
	output = []
	# preset variables
	string_id_series = []
	# Mongo query to be defined
	query = ''
	if request.method == 'POST' :
		form = featureSelectionForm(request.POST)
		if form.is_valid():
			# Presumed variables
			# collection_name = "RNA_brain_gender-F_AD-vs-Control"
			# feature_symbols_in_interest = ['APOE', 'BIN1', 'CLU']
			# way_to_choose_probe = "fold change"
			### Get variables from POST
			collection_name = "%s_%s_%s-%s_%s" % (request.POST["dataType"],
													request.POST["tissue"],
													request.POST["category"],
													request.POST["group"],
													request.POST["comparison"])
			"""
				We should split POST["featureInput"] here
			"""
			# import pdb; pdb.set_trace();
			feature_symbols_in_interest = split_feature_input_to_list(request.POST["featureInput"])

			way_to_choose_probe = request.POST["probeSelectionMethod"]

			test_stat_output_dict = {}

			all_datasets = test_stat_client.get_all_datasets(collection_name)

			test_statistics = list(test_stat_client.get_all_for_this_category(collection_name))

			test_statistics = pd.DataFrame(test_statistics)

			for dataset in all_datasets:
				# Filter 1 - dataset accession & features in interest
				if request.POST["dataType"] == "RNA":
					filt_ind = (test_statistics['dataset_accession'] == dataset) & (test_statistics['symb'].isin(feature_symbols_in_interest))
				elif request.POST["dataType"] == "protein":
					symbol_series = test_statistics['symb'].apply(extract_gene_symbol_from_protein_name)
					filt_ind = (test_statistics['dataset_accession'] == dataset) & (symbol_series.isin(feature_symbols_in_interest))

				test_stat_df = test_statistics[filt_ind]

				# Filter 2 - remove duplicates
				"""
					Here we provide options for user to choose how to select a probe when 
					multiple probes are corresponding to one feature
				"""

				if way_to_choose_probe == "fold change":
					test_stat_df = filtered_duplicate_by(test_stat_df, 'fc')

				elif way_to_choose_probe == "limma p value" : 
					test_stat_df = filtered_duplicate_by(test_stat_df, 'lp')

				elif way_to_choose_probe == "t test p value" :
					test_stat_df = filtered_duplicate_by(test_stat_df, 'tp')

				if test_stat_df.empty:
					all_datasets.remove(dataset)
					continue
				# Split dataframe for stat table display and graph display
				# stat_table = test_stat_df.drop(['eval', 'dsl'], axis=1)
				stat_table = test_stat_df.drop(['eval'], axis=1)
				# import pdb; pdb.set_trace()
				stat_table['entrez_gene_id'] = stat_table.apply(from_symbol_to_entrez_gene_id, axis=1)
				stat_table['string_id'] = from_single_symbol_to_string_id(stat_table['symb'])
				string_id_series = stat_table['string_id']
				
				# import pdb; pdb.set_trace()

				stat_table_output = stat_table.to_dict(outtype='records')

				# import pdb; pdb.set_trace()
				test_stat_output_dict.update({dataset : stat_table_output})



			return render(request, 'feature_stat.html',
						{
							'dataset_names' : all_datasets,
							'test_stat' : test_stat_output_dict,
							'way_to_choose_probe' : way_to_choose_probe,
							'datatype' : request.POST["dataType"],
							'tissue' : request.POST["tissue"],
							'category' : request.POST["category"],
							'group' : request.POST["group"],
							'comparison' : request.POST["comparison"],
							'features' : generate_mulivariable_series_from_list(feature_symbols_in_interest),
							'string_url_id_component' : generate_string_id_get_query_from_list(string_id_series)
						})
	else:		
		return render(request, 'query.html', {
			'form' : form
		})


def detail(request):
	"""
		This page is to display detailed queried feature statistics
	"""

	dataset = request.GET.get('dataset', '')
	datatype = request.GET.get('datatype', 'RNA')
	tissue = request.GET.get('tissue', 'brain')
	category = request.GET.get('category', 'region')
	group = request.GET.get('group', 'PFC')
	comparison = request.GET.get('comparison', 'AD-vs-Control')
	feature_symbols_in_interest = request.GET.get('features', '').split(' ')
	collection_name = "%s_%s_%s-%s_%s" % (datatype,
											tissue,
											category,
											group,
											comparison)
	"""
		We should split POST["featureInput"] here
	"""
	# import pdb; pdb.set_trace();
	# feature_symbols_in_interest = split_feature_input_to_list(request.POST["featureInput"])

	way_to_choose_probe = request.GET.get('way_to_choose_probe', 'fold change')

	all_datasets = test_stat_client.get_all_datasets(collection_name)

	test_statistics = list(test_stat_client.get_all_for_this_category(collection_name))

	disease_state_list = test_stat_client.get_disease_state_list(collection_name)

	test_statistics = pd.DataFrame(test_statistics)

	# Filter 1 - dataset accession & features in interest
	filt_ind = (test_statistics['dataset_accession'] == dataset) & (test_statistics['symb'].isin(feature_symbols_in_interest))
	test_stat_df = test_statistics[filt_ind]

	# Filter 2 - remove duplicates
	"""
		Here we provide options for user to choose how to select a probe when 
		multiple probes are corresponding to one feature
	"""

	if way_to_choose_probe == "fold change":
		test_stat_df = filtered_duplicate_by(test_stat_df, 'fc')

	elif way_to_choose_probe == "limma p value" : 
		test_stat_df = filtered_duplicate_by(test_stat_df, 'lp')

	elif way_to_choose_probe == "t test p value" :
		test_stat_df = filtered_duplicate_by(test_stat_df, 'tp')

	# Split dataframe for stat table display and graph display
	stat_table = test_stat_df.drop(['eval', 'dsl'], axis=1)
	stat_graph_exprs = test_stat_df[['symb', 'eval']]
	stat_graph_ds = disease_state_list[dataset]

	# import pdb; pdb.set_trace()
	stat_table['entrez_gene_id'] = stat_table.apply(from_symbol_to_entrez_gene_id, axis=1)			

	ds_1_count = sum(stat_graph_ds)
	ds_0_count = len(stat_graph_ds) - sum(stat_graph_ds)

	stat_graph_ds_1 = [True if x == 1 else False for x in stat_graph_ds]
	stat_graph_ds_0 = [True if x == 0 else False for x in stat_graph_ds]
	# stat_graph_ds_0 = stat_graph_ds == 0

	heatmap_feature_count = test_stat_df.shape[0]
	heatmap_sample_count = len(stat_graph_ds)
	heatmap_df_row_count = heatmap_sample_count * heatmap_feature_count

	
	# import pdb;pdb.set_trace
	# Generate a expression table (row as feature)
	expression_table = pd.DataFrame(list(stat_graph_exprs['eval']))

	
	# import pdb;pdb.set_trace();
	# Transpose table before sorting by disease state
	expression_table = pd.DataFrame.transpose(expression_table)

	# Get new expression table sorted by disease state
	expression_table = expression_table[stat_graph_ds_1].append(expression_table[stat_graph_ds_0], ignore_index=True)

	### Normalize row expression
	expression_table_normalized = normalize_heatmap_row_expression(expression_table)
	
	# Get minimum and maximum value of expression
	exprs_min = np.nanmin(expression_table_normalized.values)
	exprs_max = np.nanmax(expression_table_normalized.values)


	heatmap_dataset_df = pd.DataFrame({
			'0' : sorted(range(0, heatmap_sample_count) * heatmap_feature_count),  # sample_x
			'1' : range(0, heatmap_feature_count) * heatmap_sample_count,	# feature_y
			'2' : [val for row in expression_table_normalized.values.tolist() for val in row] #expression_z
		})

	# Remove NANs in heatmap data series
	not_nan_index = np.invert(np.isnan(heatmap_dataset_df['2']))
	heatmap_dataset_df = heatmap_dataset_df[not_nan_index]
	# Prepare one dimentional scatter plot

	# Final output
	# Scatter plot
	state_1_data_series = generate_scatterplot_series(range(0, ds_1_count), 0, expression_table)
	state_0_data_series = generate_scatterplot_series(range(ds_1_count, ds_1_count+ds_0_count), 1, expression_table)	
	state_1_name = "AD"
	state_0_name = "Control"
	# Heatmap
	heatmap_feature_list = [x.encode('utf-8') for x in list(stat_graph_exprs['symb'])]
	heatmap_sample_ds_list = ['AD'] * ds_1_count + ['Control'] * ds_0_count
	heatmap_datasets = heatmap_dataset_df.values.tolist()
	heatmap_extremes = [exprs_min, exprs_max]
	# Statistic table
	stat_table_output = stat_table.to_dict(outtype='records')

	return render(request, 'feature_stat_detail.html',
				{
					'dataset_name' : dataset,
					'test_stat' : stat_table_output,
					'feature_list' : heatmap_feature_list,
					'sample_state_list' : heatmap_sample_ds_list,
					'heatmap_datasets' : heatmap_datasets,
					'heatmap_extremes' : heatmap_extremes,
					'state_1_data_series' : state_1_data_series,
					'state_0_data_series' : state_0_data_series,
					'state_1_name' : state_1_name,
					'state_0_name' : state_0_name,
				})


def meta(request):
	"""
		This page is to display detailed queried feature statistics
	"""

	datatype = request.GET.get('datatype', 'RNA')
	tissue = request.GET.get('tissue', 'brain')
	category = request.GET.get('category', 'region')
	group = request.GET.get('group', 'PFC')
	comparison = request.GET.get('comparison', 'AD-vs-Control')
	feature_symbols_in_interest = request.GET.get('features', '').split(' ')
	collection_name = "%s_%s_%s-%s_%s" % (datatype,
											tissue,
											category,
											group,
											comparison)
	"""
		We should split POST["featureInput"] here
	"""
	# import pdb; pdb.set_trace();
	# feature_symbols_in_interest = split_feature_input_to_list(request.POST["featureInput"])

	# way_to_choose_probe = request.GET.get('way_to_choose_probe', 'fold change')

	records = list(meta_stat_client.get_all_records(collection_name))
	records_all_teststat = list(test_stat_client.get_all_records(collection_name))
	record_sample_count = test_stat_client.get_all_sample_count(collection_name)
	record_disease_state = test_stat_client.get_all_disease_state(collection_name)
	record_all_datasets = test_stat_client.get_all_datasets(collection_name)

	# Turn into dataframe
	records = pd.DataFrame(records)
	records_all_teststat = pd.DataFrame(records_all_teststat)

	# Select features in interest
	filt_ind = records['symb'].isin(feature_symbols_in_interest)
	records_queried = records[filt_ind]

	records_queried['entrez_gene_id'] = records_queried.apply(from_symbol_to_entrez_gene_id, axis=1)
				

	# Select top 10 by meta-p-value
	records_top_10 = records.sort('pval', ascending=True).iloc[0:9, ]

	records_top_10['entrez_gene_id'] = records_top_10.apply(from_symbol_to_entrez_gene_id, axis=1)
	
	# Get meta info for this collection
	meta_df = pd.DataFrame(record_sample_count, index=['sample_count'], columns=record_all_datasets)
	meta_df = pd.DataFrame.transpose(meta_df)
	meta_df['state_1_count'] = pd.Series(record_disease_state).apply(sum)
	meta_df['state_0_count'] = meta_df['sample_count'] - meta_df['state_1_count']
	symbol_count_list = []
	
	for dataset in record_all_datasets:
		symb_count = records_all_teststat[records_all_teststat['dataset_accession'] == dataset].shape[0]
		symbol_count_list.append(symb_count)

	meta_df['feature_count'] = symbol_count_list
	meta_df['dataset_accession'] = meta_df.index
	
	union_feature_count = records.shape[0]
	check_all_presence = lambda x : '?' not in x['eff']
	# import pdb;pdb.set_trace();
	
	intersect_feature_count = sum(records.apply(check_all_presence, axis=1))
	

	# Output queried records to dictionary
	meta_stat_queried = records_queried.to_dict(outtype='records')
	meta_stat_top_10 = records_top_10.to_dict(outtype='records')
	meta_info = meta_df.to_dict(outtype='records')
	# import pdb;pdb.set_trace();

	return render(request, 'meta_stat.html',
				{
					'meta_stat_queried' : meta_stat_queried,
					'meta_stat_top_10' : meta_stat_top_10,
					'collection_name' : collection_name,
					'meta_info' : meta_info,
					'union_feature_count' : union_feature_count,
					'intersect_feature_count' : intersect_feature_count
				})

