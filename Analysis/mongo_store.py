from pymongo import MongoClient
from parameters import DB_HOST, DB_PORT, \
	CATEGORY_IN_INTEREST, ALL_PLATFORMS

from data_utils import extract_single_from_list_in_dataset_dict

class SampleClient():
	"""
	A client to wrap the mongo database for storing samples
	"""
	def __init__(self):
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		self.db = client['sample']

	def count_datsets(self) :
		return len(self.db.collection_names())

	def count_samples(self, collection):
		return self.db[collection].count()
	
	def get_platform_id(self, dataset):
		return self.db[dataset].find_one()["platform_id"]
	
	def get_platform_name(self, dataset):
		return self.db[dataset].find_one()["platform_name"]

	def get_platform_type(self, platform_name):
		return [x for x in ALL_PLATFORMS if x in platform_name.lower()][0]

	# def get_all_dataset_name(self) :
	# 	return self.db.collection_names()

	def get_data_type(self, dataset):
		return self.db[dataset].find_one()["data_type"]

	def get_tissue(self, dataset):
		return self.db[dataset].find_one()["tissue"]

	def get_probe_id_list(self, dataset):
		return self.db[dataset].find_one()["probe_id"]

	def get_all_categories_in_dataset(self, dataset) :
		'''
			Structure of the return list
			
			[{'region' : 'PFC'},{'region' : 'HI'},{'gender' : 'M'},{'gender' : 'F'}]
		'''
		queried_dataset = self.db[dataset]
		category_list = []
		for category in CATEGORY_IN_INTEREST:
			unique_values_in_this_category = queried_dataset.distinct(category)
			for value in unique_values_in_this_category :
				category_list.append({category: value})
		return category_list

	def fetch_sample_records_in_one_category(self, category, dataset):
		return self.db[dataset].find({category.keys()[0] : category.values()[0]}, {'disease_state' : 1, 'expression_value' : 1, 'age' : 1, 'gender' : 1})
	
	# def fetch_sample_record_expression_in_one_category(self, category, dataset):
	# 	return self.db[dataset].find({category.keys()[0] : category.values()[0]}, {'expression_value' : 1, '_id' : 0})


	def store_one(self, dataset_dict):
		''' 
			Insert a single sample into the database
		'''
		# print dataset_dict.keys()

		dataset_dict = extract_single_from_list_in_dataset_dict(dataset_dict)
		
		# print dataset_dict['dataset_accession']
		
		dataset_accession = dataset_dict['dataset_accession']
		query = {
			"sample_accession" : dataset_dict['sample_accession']
		}
		# all_collection = self.get_all_dataset_name()

		# if dataset_accession not in all_collection:
		# 	self.db.create_collection(dataset_accession)
		
		db_collection = self.db[dataset_accession]
		return db_collection.update(query, {'$set' : dataset_dict}, upsert=True)

class AnnotationClient():
	"""
	A client to wrap the mongo database for storing annotations
	"""
	def __init__(self):
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		self.db = client['annotation']

	def get_collection_for_data_type(self, data_type):
		
		return self.db[data_type].find()

	def get_all_gene_entrez_id_and_symbol(self, anno_type) :
		
		return self.db[anno_type].find({}, {'entrez_gene_id' : 1, 'symbol' : 1, '_id' : 0})

	def store_one(self, anno_type, feature_dict):
		''' 
			Insert a single sample into the database
		'''
		query = {
			"entrez_gene_id" : feature_dict['entrez_gene_id']
		}
		db_collection = self.db[anno_type]
		
		return db_collection.update(query, {'$set' : feature_dict}, upsert=True)

	def get_all_probe_ids_by_platform(self, anno_type, platform_id):
		
		records = self.db[anno_type].find(
			{platform_id : {'$exists' : 1}}, 
			{platform_id : 1, "symbol" : 1, "_id" : 0})

		return records

	def get_record_by_entrez_gene_id(self, anno_type, entrez_gene_id):
		return self.db[anno_type].find_one({
				'entrez_gene_id' : entrez_gene_id
			})

	def update_record_by_entrez_gene_id(self, anno_type, entrez_gene_id, platform_id, probe_array, symbol):
		return self.db[anno_type].update({
				'entrez_gene_id' : str(entrez_gene_id)
			}, {
				'$set' : {
					platform_id : probe_array,
					'symbol' : symbol
				}
			}, upsert=True)
		# exit()

class TestStatClient():
	"""
	A client to wrap the mongo database for storing test statistics
	"""
	def __init__(self):
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		self.db = client['teststat']

	# def get_all_probes(self, collection, dataset):
	# 	return self.db[collection].find_one(
	# 		{
	# 			"dataset_accession" : dataset
	# 		}
	# 	).keys().remove("dataset_accession")	

	# def get_all_symbols(self, collection, dataset):
	# 	record = self.db[collection].find_one({"dataset_accession" : dataset})
	# 	self.db
	# 	return 
	def get_all_datasets(self, collection):
		return self.db[collection].distinct('dataset_accession')

	def get_records_without_expression_value(self, collection, dataset):
		return self.db[collection].find({
				'dataset_accession' : dataset
			}, {
				'_id' : 0,
				'eval' : 0,
				'dataset_accession' : 0 
			})

	def get_sample_count(self, collection):
		return self.db[collection].find_one({
				'sample_count' : 1
			}, {
				'_id' : 0,
				'sample_count' : 0
			})

	def get_all_stat_records(self, collection):
		"""
			Get all statistic records by excluding records of sample_count and disease_state
		"""
		return self.db[collection].find({
				'sample_count' : {'$exists' : 0},
				'disease_state' : {'$exists' : 0}
			})

	def get_all_stat_records_for_dataset(self, collection, dataset):
		"""
			Get all statistic records by excluding records of sample_count and disease_state
		"""
		return self.db[collection].find({
				'dataset_accession' : dataset
			})

	def get_disease_state(self, collection):
		return self.db[collection].find_one({
				'disease_state' : 1
			})

	def update_meta_sample_count(self, collection, meta):
		return self.db[collection].update({
				'sample_count' : 1
				}, 
				{
					'$set' : meta,
				},
				upsert=True
		)

	def update_meta_disease_state(self, collection, meta):
		return self.db[collection].update({
				'disease_state' : 1
				}, 
				{
					'$set' : meta,
				},
				upsert=True
		)


	def update_fold_change_only(self, collection, document):
		return self.db[collection].update_one({
				'_id' : document['_id']
			},{
				'$set' : {
					'fc' : document['fc']
				}
			})

	# def insert_record(self, collection, record):
	# 	"""
	# 		Insert stat record in collection named after: 
	# 			datatype/tissue/category/comparison/
	# 		Each record looks like:
	# 		{
	# 			'dataset_accession' : 'GSE5281',
	# 			'190_s_at' : {
	# 				'symb' : 'APOE',
	# 				'lt' : -1.1,
	# 				'lp' : 0.0456,
	# 				'tt' : -2.5,
	# 				'tp' : 0.006 
	# 			}
	# 			'45_a_at' :{}
	# 			...
	# 		}
	# 	"""
		
	# 	return self.db[collection].update({
	# 			'dataset_accession' : record['dataset_accession']
	# 			}, 
	# 			{
	# 				'$set' : record,
	# 			},
	# 			upsert=True
	# 	)

	def insert_record(self, collection, record):
		"""
			Insert stat record in collection named after: 
				datatype/tissue/category/comparison/
			Each record looks like:
			{
				'dataset_accession' : 'GSE5281',
				'pid' : '190_s_at',
				'symb' : 'APOE',
				'lt' : -1.1,
				'lp' : 0.0456,
				'tt' : -2.5,
				'tp' : 0.006,
				'eval' : [23.23,2.23,.....]
			}
		"""
		
		return self.db[collection].update({
					'dataset_accession' : record['dataset_accession'],
					'pid' : record['pid']
				}, 
				{
					'$set' : record,
				},
				upsert=True
		)

	def update_multi(self, collection, query, record):
		return self.db[collection].update(query, 
			{
				'$set' : record,
			}
		)


class MetaStatClient():
	"""
	A client to wrap the mongo database for storing test statistics
	"""
	def __init__(self):
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		self.db = client['metastat']

	def insert_meta_analysis_record(self, collection, record):
		"""
			Insert stat record in collection named after: 
				datatype/tissue/category/comparison/
			Each record looks like:
			{
				'pid': 190_s_at',
				'symb' : 'APOE',
				'p' : 0.0456,
				'eff' : '++---?',
				'sig' : '!!!-!?',
				'deg' : true
			}
		"""
		
		return self.db[collection].update({
				'symb': record['symb'],
				}, 
				{
					'$set' : record,
				},
				upsert=True
		)