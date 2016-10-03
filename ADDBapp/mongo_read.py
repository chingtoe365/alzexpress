from pymongo import MongoClient
from parameters import DB_HOST, DB_PORT, \
	CATEGORY_IN_INTEREST, ALL_PLATFORMS

from utils import extract_single_from_list_in_dataset_dict

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

	def count_gender_samples(self, collection, gender):
		return self.db[collection].find({
				'gender' : gender
			}).count()

	def count_region_samples(self, collection, region):
		return self.db[collection].find({
				'region' : region
			}).count()

	def get_all_datasets(self):
		collections = self.db.collection_names()
		returned_list = [x for x in collections if 'GSE' in x]
		return returned_list

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

	def get_all_regions(self, dataset):
		return self.db[dataset].distinct('region')
		
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

	def fetch_sample_records_in_all_cateogies(self, dataset):
		"""
			Get all sample records in given datasets
			Would be exclusively AD & CNL at this state 
		"""
		### TODO ###
		# Include other disease state as well
		return self.db[dataset].find({'$or' : {'disease_state' : 'AD', 'disease_state' : 'CNL'}})

	def fetch_sample_records_in_one_category(self, category, dataset):
		"""
			Get sample records in given datasets for given group
			Would be exclusively AD & CNL 
		"""
		### TODO ###
		# Include other disease state as well
		return self.db[dataset].find({
			category.keys()[0] : category.values()[0], 
			'$or' : {'disease_state' : 'AD', 
					'disease_state' : 'CNL'}
			})

	def store_one(self, dataset_dict):
		''' 
			Insert a single sample into the database
		'''
		dataset_dict = extract_single_from_list_in_dataset_dict(dataset_dict)
		
		dataset_accession = dataset_dict['dataset_accession']
		query = {
			"sample_accession" : dataset_dict['sample_accession']
		}
		all_collection = self.get_all_dataset_name()

		if dataset_accession not in all_collection:
			self.db.create_collection(dataset_accession)
		
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

	def get_all_gene_entrez_id_and_symbol(self) :
		
		return self.db['gene'].find({}, {'entrez_gene_id' : 1, 'symbol' : 1, '_id' : 0})

	def store_one(self, feature_dict):
		''' 
			Insert a single sample into the database
		'''
		query = {
			"entrez_gene_id" : feature_dict['entrez_gene_id']
		}
		db_collection = self.db['gene']
		
		return db_collection.update(query, {'$set' : feature_dict}, upsert=True)

	def get_all_probe_ids_by_platform(self, annotation_type, platform):
		
		records = self.db[annotation_type].find(
			{platform : {'$exists' : 1}}, 
			{platform : 1, "symbol" : 1, "_id" : 0})

		return records

	def get_entrez_gene_id_from_symbol(self, symbol):
		return self.db['gene'].find_one({
				'symbol' : symbol
			})

class TestStatClient():
	"""
	A client to wrap the mongo database for storing test statistics
	"""
	def __init__(self):
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		self.db = client['teststat']

	def get_all_records(self, collection):
		return self.db[collection].find()

	def get_all_datasets(self, collection):
		return self.db[collection].distinct('dataset_accession')

	def get_one_dataset_record(self, collection, dataset):
		return self.db[collection].find_one({
				'dataset_accession' : dataset
			})

	def get_all_sample_count(self, collection):
		return self.db[collection].find_one({
				'sample_count' : 1
			}, {
				'sample_count' : 0, '_id' : 0
			})	

	def get_all_disease_state(self, collection):
		"""
			Should update when more disease comparison added in
		"""
		return self.db[collection].find_one({
				'disease_state' : 1
			}, {
				'disease_state' : 0, '_id' : 0, 'AD' : 0, 'CNL' : 0
			})

	# def get_all_features(self, collection):
	# 	return self.db[collection].find({
	# 			''
	# 		})
	def get_all_for_this_category(self, collection):
		return self.db[collection].find({'dataset_accession' : {
				'$exists' : True
			}})

	def get_all_pval_fold_change_for_this_dataset(self, collection, dataset):
		return self.db[collection].find({
				'dataset_accession' : dataset
			},{
				'pid' : 1, 'symb' : 1, 'lp' : 1, 'fc' : 1
			})

	def get_disease_state_list(self, collection):
		return self.db[collection].find_one({
				'disease_state' : 1
			})

	def insert_record(self, collection, record):
		"""
			Insert stat record in collection named after: 
				datatype/tissue/category/comparison/
			Each record looks like:
			{
				'dataset_accession' : 'GSE5281',
				'190_s_at' : {
					'symb' : 'APOE',
					'lt' : -1.1,
					'lp' : 0.0456,
					'tt' : -2.5,
					'tp' : 0.006 
				}
				'45_a_at' :{}
				...
			}
		"""
		
		return self.db[collection].update({
				'dataset_accession' : record['dataset_accession']
				}, 
				{
					'$set' : record,
				},
				upsert=True
		)

class MetaStatClient():
	"""
	A client to wrap the mongo database for storing test statistics
	"""
	def __init__(self):
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		self.db = client['metastat']

	def get_all_records(self, collection):
		return self.db[collection].find()

	def insert_meta_analysis_record(self, collection, record):
		"""
			Insert stat record in collection named after: 
				datatype/tissue/category/comparison/
			Each record looks like:
			{
				'dataset_accession' : dataset,
				'pid' : probe,
				'symb' : symbol,
				'lt' : limma_t,
				'lp' : limma_p,
				'tt' : ttest_t,
				'tp' : ttest_p,
				'fc' : fc,
				'eval' : evalue,
				'dsl' : disease_state_list
			}
		"""
		
		return self.db[collection].update({
				'pid': record['pid'],
				}, 
				{
					'$set' : record,
				},
				upsert=True
		)