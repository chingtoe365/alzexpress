"""
Some test for annotation matching
"""
from mongo_store import SampleClient, AnnotationClient

def build_dict(seq, platform):
	"""
		converts a list of annotation entries into a dictionary of probe_id as key and symbol as value
		From
		[{'rosetta': [xxx, xxx], 'symbol' : 'symbol_name'}, {}, {}]
		To
		{'probe id 1' : 'symbol', 'probe id 2' : 'symbol', ...}
	"""
	new_dict = {}

	for item in seq:
		for probe in item[platform]:
			key_value = probe
			new_dict[key_value] = item['symbol']
	return new_dict

def get_feature_probe_symbol_dict_list(anno_type, probe_id_list, platform_id, anno_client):
	all_probe_ids = list(anno_client.get_all_probe_ids_by_platform(anno_type, platform_id))
	
	# covert probe gene list to easy-handle format
	all_probe_ids_dict = build_dict(all_probe_ids, platform_id)
	
	"""
		Get corresponding gene symbol of each probe
		If not probe not found in dict (not in anno db) then filter it out
		dict list should look like this:
		{
			'129_at_x' : 'ABC',
			'89_at_x' : 'BCD',
			...
		}
	"""
	
	feature_probe_symbol_dict = {p : all_probe_ids_dict[p] for p in probe_id_list if p in all_probe_ids_dict.keys()}
	

	import pdb;pdb.set_trace();
	
	old_count = len(probe_id_list)
	new_count = len(feature_probe_symbol_dict.keys())

	if new_count < old_count :
		print "Warning: Annotation missing for %s probes" % (old_count - new_count, )
	
	return feature_probe_symbol_dict

if __name__ == "__main__":
	anno_client = AnnotationClient()
	sample_client = SampleClient()

	test_dataset = "GSE36980"

	probe_id_list = sample_client.get_probe_id_list(test_dataset)
	feature_probe_symbol_dict = get_feature_probe_symbol_dict_list("RNA", probe_id_list, "GPL6244", anno_client)

