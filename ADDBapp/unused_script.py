def upload(request):
	# if this is a POST request we need to process the form data
	# create a form instance and populate it with data from the request:
	form = fileUploadForm()
	message = ""
	if request.method == 'POST':
		form = fileUploadForm(request.POST, request.FILES)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			uploadType = request.POST['uploadType']
			f = request.FILES['fileUpload']
			# handle_uploaded_file(f)
			wholeFileStr = ""
			for chunk in f.chunks():
				# # for debugging
				wholeFileStr = wholeFileStr + chunk
			# # uploading, size limit < 16MB
			jsonObj = json.loads(wholeFileStr)
			# db = client.addb
			if uploadType == 'samples':
				table = db_client.db['samples']
			else:
				table = db_client.db['anno']
			# import pdb; pdb.set_trace()
			for key in jsonObj.keys():
				# import pdb; pdb.set_trace()
				table.insert(jsonObj[key])
				# db.samples.insert(jsonObj[key])
			# db.samples.insert(jsonObj)
			# # User GridFS to store large file, but not JSON documents, sadly
			# db = client.addb
			# fs = gridfs.GridFS(db)
			# a = fs.put(wholeFileStr, filename=f.name)
			# message = fs.get(a).read()
			message = "Upload successful"
			
	# if a GET (or any other method) we'll create a blank form
	return render(request, 'read_data.html', {
		'form' : form,
		'message' : message
	})
