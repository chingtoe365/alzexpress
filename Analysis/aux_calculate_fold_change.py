from mongo_store import TestStatClient, SampleClient, AnnotationClient, MetaStatClient

from stat_utils import calculate_fold_change_for_table, \
						get_log_fold_change_separate

import pandas as pd
import numpy as np

import progressbar

if __name__ == "__main__" :
	"""
		just to calculate the fold change again 
	"""

	regions = ['CE', 'EC', 'HIP', 'MTG', 'PC', 'PFC', 'POCG', 'PVC', 'SFG', 'TC', 'VI']

	collections = ["RNA_brain_region-" + x + "_AD-vs-Control" for x in regions]

	test_stat_client = TestStatClient()
	for collection in collections:
		ds_states = test_stat_client.get_disease_state(collection)
		datasets = test_stat_client.get_all_datasets(collection)

		print "Processing collection %s" % (collection, )

		for dataset in datasets:
			stat_records = list(test_stat_client.get_all_stat_records_for_dataset(collection, dataset))
			
			print "Processing dataset %s" % (dataset, )
			ds_state = ds_states[dataset]

			n_processed = 0
			n_pairs = len(stat_records)
			bar = progressbar.ProgressBar(maxval=n_pairs,
										widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
			bar.start()

			for record in stat_records:
				e_values = record['eval']
				record_id = record['_id']
				fold_change = get_log_fold_change_separate(e_values, ds_state)
				new_doc = {
					'_id' : record_id,
					'fc' : fold_change
				}
				# print new_doc
			 	test_stat_client.update_fold_change_only(collection, new_doc)

			 	n_processed += 1
				bar.update(n_processed)

			print "Finshed dataset %s" % (dataset, )
			bar.finish()



