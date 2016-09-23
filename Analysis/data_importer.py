'''
	this script is used as data importer
	both for annotation & sample import in MongoDB database
'''

import argparse

import json

# from mongo_store import SampleClient, AnnotationClient
from mongo_store import SampleClient, AnnotationClient

def import_file(file_path, sample_client, debug=True):
	with open(file_path, 'rb') as txtfile:
		if debug:
			print "Full file path: %s" % (file_path)
			# print "Take a look at the file\n %s" % (txtfile, )
		txtfile_string = txtfile.read()
		input_json = json.loads(txtfile_string)
		# print len(input_json)
		# print input_json[0]
		for content in input_json.keys():
			# import sys
			# sys.exit(input_json.keys())
			# print input_json[content].keys()
			sample_client.store_one(input_json[content])
		print "Import successed!"

def import_annotation(file_path, platform_id, anno_type, annotation_client, debug=True):
	with open(file_path, 'rb') as txtfile:
		if debug:
			print "Full file path: %s" % (file_path)
		txtfile_string = txtfile.read()
		annotation_json = json.loads(txtfile_string)
		for entrez_gene_id in annotation_json.keys():
			# if debug:
			# 	print "Entrez gene id: %s" % (entrez_gene_id, )
			# 	print annotation_json[entrez_gene_id]
				# exit()
			probe_array = annotation_json[entrez_gene_id]['probe_ids']
			symbol = annotation_json[entrez_gene_id]['symbol']
			# Update corresponding record
			annotation_client.update_record_by_entrez_gene_id(anno_type, entrez_gene_id, platform_id, probe_array, symbol)


if __name__ == '__main__' :
	# we're running as a main command line script
	parser = argparse.ArgumentParser(description='Import microarray data from downloaded GEO files for a specific dataset.')
	parser.add_argument('--data-type',
						help='The data type of imported data. Either gene or sample',
						dest='data_type',
						metavar='annotation/sample',
						required=True,
						type=str)
	parser.add_argument('--file-name',
						help='The file that is going to be imported',
						dest='file_name',
						metavar='Comma separated file',
						required=True,
						type=str)
	
	parser.add_argument('--annotation-type',
						help='Type of annotation',
						dest='anno_type',
						metavar='RNA/protein/microRNA/dna_methylation',
						required=True,
						type=str)	
	
	parser.add_argument('--platform-id',
						help='The platform ID in GEO for the annotation',
						dest='platform_id',
						# metavar='',
						# required=True,
						type=str)	

	parser.add_argument('--debug', dest='debug', action='store_true')
	parser.set_defaults(debug=False)	
	
	args = parser.parse_args()
	
	sample_client = SampleClient()
	annotation_client = AnnotationClient()



	# get current directory
	import os
	current_dir = os.path.dirname(os.path.realpath(__file__))
	''' file path in windows '''
	# file_path = current_dir + '\\' + args.file_name
	''' file path in ubuntu '''
	file_path = current_dir + "/" + args.file_name

	print "complete file path %s" % (file_path, )
	# read the files (csv, txt etc.) in a directory
	if args.file_name is None or args.data_type is None:
		parser.print_help()
	else:
		if args.data_type not in ['annotation', 'sample']:
			print "Wrong data type"
			parser.print_help()
		elif args.data_type == 'annotation' :
			if args.platform_id is None or args.anno_type is None:
				print "Please type input platform ID and annotation type"
				parser.print_help()
			else:
				platform_id = args.platform_id
				anno_type = args.anno_type
				print "Processing: %s" % (args.file_name, )
				# import_file(file_path, platform_id, import_client)
				import_annotation(file_path, platform_id, anno_type, annotation_client, args.debug)
		else :
			print "Processing: %s" % (args.file_name, )
			import_file(file_path, sample_client)
	# insert the data into corresponding place in MongoDB
