from django.http import HttpResponse

import json

import numpy as np
import pandas as pd

from views_constants import *

def get_top_tables(request):
	if request.method == 'POST':
		response_data = {}

		feature_filter_type = int(request.POST.get('feature_filter_type'))
		collection_name = request.POST.get('collection_name')

		records = list(meta_stat_client.get_all_records(collection_name))

		# Turn into dataframe
		records = pd.DataFrame(records)

		# print feature_filter_type
		# print type(feature_filter_type)
		if feature_filter_type == 2:
			print "2 a"
			# Common features
			# Filter out those without common adjusted p value
			records = records[np.invert(np.isnan(records['cbfp']))]

		print records.shape
		# Select top 10 by meta-p-value
		records_top_10 = records.sort('pval', ascending=True).iloc[0:9, ]
		records_top_10 = records_top_10.drop('_id', axis=1)

		# Outputing result in html table elements
		records_top_10 = records_top_10.to_dict(outtype='records')
		field_order = ['symb', 'tsco', 'pval', 'bhp', 'bfp', 'cbhp', 'cbfp', 'bfsig', 'eff']
		output = ''
		for row in records_top_10:
			output += '<tr>'
			for j in field_order:
				output += '<td>' + str(row[j]) + '</td>'
			output += '</tr>'
		# meta_stat_top_10 = records_top_10.to_dict(outtype='records')
		# meta_stat_top_10 = records_top_10.values.tolist()

		# print json.dumps(meta_stat_top_10)
		# response_data['content'] = meta_stat_top_10

		response_data['result'] = output

		# print json.dumps(response_data)

		return HttpResponse(
				json.dumps(response_data),
				content_type="application/json"
			)
	else:
		return HttpResponse(
				json.dumps("Forbidden request here"),
				content_type="application/json"
			)