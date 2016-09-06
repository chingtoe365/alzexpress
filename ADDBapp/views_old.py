from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from .utils import combine_multiple_filters_to_query, filtered_duplicate_by

# from data_utils import convert_unicode_to_none_for_array

from parameters import ALL_PLATFORMS

import json

from .forms import sampleFilterForm
from .forms import fileUploadForm


import pandas as pd
import numpy as np

from views_constants import *

# from mongo_read import ADDBClient

# db_client = ADDBClient()

# from Analysis.mongo_read import SampleClient, AnnotationClient
# db_client = SampleClient()
# connection with Redis
# import redis
# r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Create your views here.

def index(request):
	return HttpResponse()

def home(request):
	return render(request, 'home.html') 


# from numpy import *

def query(request):
	# db = client.addb
	# get extra field count
	extra_field_count = request.GET.get('extra_field_count')
	if extra_field_count is None:
		# if none set to zero
		extra_field_count = 0
	# initialize form
	form = sampleFilterForm(extra=extra_field_count)
	# query output for displaying
	output = []
	# Mongo query to be defined
	query = ''
	if request.method == 'POST' :
		form = sampleFilterForm(request.POST)
		if form.is_valid():
			filters = []
			# collect all user input filters into a filter list
			for i in range(int(extra_field_count) + 1):
				filters.append((request.POST["filterBy_" + str(i)], request.POST["relation_" + str(i)], request.POST["keyword_" + str(i)]))
			# import pdb; pdb.set_trace()
			# make query out of the filter collection
			query = combine_multiple_filters_to_query(filters)
			# query the database
			cursor = db_client.db['samples'].find(query, {"_id" : 0, "expression_value" : 0, "probe_id" : 0})

			# read and append each collection to output	
			for doc in cursor:
				# import pdb; pdb.set_trace()
				output.append(doc)
			# result = json.dumps(resultJson, separators=(',', ':'))
				# result = data.find()
			# data = fs.find({"filename" : "gse5281.json.txt"}).read()
				# result = data.find({}, {"expression_value" : 0})
			# result = fs.find({}, {"expression_value" : -1})
			# fs = gridfs.GridFS(db)
			# a = fs.get(fs)
	return render(request, 'query.html', {
		'form' : form,
		'result' : output,
		'query' : query
		# 'redirectUrl' : redirectUrl
	})
	
import ast
from numpy import *
def featureQuery(request):
	# db = client.addb
	if request.method == 'POST':
		# import pdb; pdb.set_trace()
		# get gene list
		geneArr = request.POST['input-genes'].split('\r\n')
		ga = []
		for gene in geneArr : 
			ga.append({"symbol" : gene})
		annoQuery = {"$or" : ga}
		query = request.POST['sample-query']
		query = eval(query)
		cursor = db_client.db['samples'].find(query, {"dataset_accession" : 1, "platform_name" : 1, "expression_value" : 1, "probe_id" : 1, "sample_accession" : 1})
		# import pdb; pdb.set_trace()
		datasets = cursor.distinct("dataset_accession")
		# platforms = cursor.distinct("platform_name")
		# probe_id_list = {}
		# probe_id_list = dict.fromkeys(datasets)
		# matched_probe_id_list = {}
		# matched_probe_id_list = dict.fromkeys(datasets)
		expression_table = {}
		expression_table = expression_table.fromkeys(datasets)
		# extract probe IDs of selected genes/features from anno collection
		annoCursor = list(db_client.db['anno'].find(annoQuery, {"_id" : 0, "entrez_gene_id" : 0}))
		annoProbeDict = {}
		annoProbeDict2 = {}
		# allkey = reduce(lambda x, y: set.union(set(x.keys()), set(y.keys())), annoCursor)

		# extract probe id array for each dataset
		for ds in datasets :
			# get a particular sample within this dataset
			sampleSampleInDataset = db_client.db['samples'].find({"dataset_accession" : ds}).next()
			# platform name of this dataset
			platform_name = sampleSampleInDataset["platform_name"][0]
			# probe id array of this dataset
			probeIdArrayInDataset = sampleSampleInDataset["probe_id"]
			# check which platform this dataset use by its platform_name
			platform = [x for x in ALL_PLATFORMS if x in platform_name.lower()][0]
			# probe ids for genes in interest in different dataset
			annoProbeDict.update({ds : {}})
			for geneEntry in annoCursor:
				matchedProbeArray = [g for g in geneEntry[platform] if g in probeIdArrayInDataset]
				annoProbeDict[ds].update({geneEntry["symbol"][0] : matchedProbeArray})
			## update first level dict
			annoProbeDict2.update({ds : {}})
			# update the probe ids array
			# matchedProbeArrayInDataset = [ele for k in annoProbeDict[ds].keys() for ele in annoProbeDict[ds][k] if ele in probeIdArrayInDataset]
			matchedProbeArrayInDataset = [probeIdArrayInDataset.index(ele) for k in annoProbeDict[ds].keys() for ele in annoProbeDict[ds][k] if ele in probeIdArrayInDataset]
			annoProbeDict2[ds].update({'probe' : matchedProbeArrayInDataset})
			# update the symbol array
			matchedSymbolArrayInDataset = [k for k in annoProbeDict[ds].keys() for ele in annoProbeDict[ds][k] if ele in probeIdArrayInDataset]
			annoProbeDict2[ds].update({'symbol' : matchedSymbolArrayInDataset})
		
		''' extract expression table from sample queries '''
		# old way to extract values and form a table

		for doc in cursor :
			dataset = doc["dataset_accession"][0]
			if len(annoProbeDict2[dataset]['probe']) != 0 :
				# import  pdb; pdb.set_trace()
				# deal with null
				exprsValWithoutNull = [None if type(x) is unicode else x for x in doc["expression_value"]]			
				expressionArray = np.array(exprsValWithoutNull, dtype=np.float)
				if expression_table[dataset] is None :
					expression_table[dataset] = expressionArray[annoProbeDict2[dataset]['probe']] # not sure if this [] is needed
				else :
					expression_table[dataset] = np.vstack((expression_table[dataset], expressionArray[annoProbeDict2[dataset]['probe']])) # not sure if this [] is needed
		# 		# import  pdb; pdb.set_trace()
		# import  pdb; pdb.set_trace()

		# new way to do it
		# for doc in cursor :
		# 	dataset = doc["dataset_accession"][0]
		# 	if len(annoProbeDict2[dataset]['probe']) != 0 :
		# 		# deal with null
		# 		expression_value_without_null = convert_unicode_to_none_for_array(doc["expression_value"])
				
		# 		expression_array = pd.DataFrame([expression_value_without_null], columns=doc["probe_id"], index=doc['sample_accession'])
		# 		# expressionArray = np.array(expression_value_without_null, dtype=np.float)
		# 		if expression_table[dataset] is None :
		# 			expression_table[dataset] = expression_array[annoProbeDict2[dataset]['probe']] # not sure if this [] is needed
		# 		else :
		# 			# expression_table[dataset] = np.vstack((expression_table[dataset], expressionArray[annoProbeDict2[dataset]['probe']])) # not sure if this [] is needed
		# 			# expression_table[dataset] = expression_table[dataset].append(expression_array[annoProbeDict2[dataset]['probe']], columns=[expression_table[dataset].columns.values])
		# 			expression_table[dataset] = expression_table[dataset].append(expression_array[annoProbeDict2[dataset]['probe']])

		# import  pdb; pdb.set_trace()

	return render(request, 'featureQuery.html', {
		'expression_table' : expression_table
	})

def test(request):
	db = client.addb
	samp = db.samples.find({"_id" : '57248d25c6b9662864537ffe'}, {"age" : 1, "gender" : 1,"expression_value" : 1})
	# import  pdb; pdb.set_trace()	
	return HttpResponse(dir(samp))
def upload_handler(request):
	if request.method == 'POST':
		# return HttpResponseRedirect('..')
		filename = request.FILES['file']['name']
		return HttpResponse(filename)
		# if(file.multiple_chunks()){
		# 	data = file.chunks
		# }
  #       data = file.read()
  #      	return HttpResponse(data)
        # update_database(data)
		# form = UploadFileForm(reuqest.POST, request.FILES)
		# if form.is_valid():
			# return HttpResponseRedirect('/index')
	else:
		# form = UploadFileForm()
		return render(request, 'read_data.html', {
		'message' : 'Upload not successful'	
		})


def queried_feature_stat(request):
	"""
		This page is to display query feature statistics
	"""
	# Presumed variables
	collection_name = "RNA_brain_gender-F_AD-vs-Control"
	feature_symbols_in_interest = ['APOE', 'BIN1', 'CLU']
	way_to_choose_probe = "fold change"

	all_datasets = test_stat_client.get_all_datasets(collection_name)

	test_stat_output_dict = {}

	for dataset in all_datasets:
		test_statistics = test_stat_client.get_one_dataset_record(collection_name, dataset)
		# remove unnecessary info
		test_statistics.pop('dataset_accession', 0)
		test_statistics.pop('sample_count', 0)

		test_stat_df = pd.DataFrame(test_statistics)

		# count probes
		probe_count = test_stat_df.shape[0]
		# get probe names
		probe_names = list(test_stat_df.index)

		probe_in_interest = [probe_names[i] for i in range(0, probe_count) if test_stat_df.symb[i] in feature_symbols_in_interest]
		# Filter out those un-queried probes 
		test_stat_df = test_stat_df.loc[probe_in_interest]

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

		# Convert pd.dataframe to dict with every probe id as keys
		test_stat = test_stat_df.to_dict(orient='index')

		test_stat_output_dict.update({dataset : test_stat})

	return render_template('feature_stat.html',
							test_stat=test_stat_output_dict)



