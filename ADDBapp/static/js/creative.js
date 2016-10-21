// Some scripts for every page load
$(function(){
	$('.string-link').hide();
	$('.feature-annotation').hover(function(){
		// console.log("mouse in");
		$(this).children(".string-link").show();
	}, function(){
		// console.log("mouse out");
		$(this).children(".string-link").hide();
	// });	
	});
	

	$('.cross-study-query-form label').append('<div class=\"checkbox-mask\"></div>');
	$('.cross-study-query-form label').click(function(){
		// alert('#' + $(this).parent('label').attr('for'));
		inputId = '#' + $(this).attr('for');
		inputObj = $(inputId);
		// console.log(inputObj);
		// var checkedStatus = inputObj.checked;
		checkedStatus = inputObj.prop("checked");
		console.log(checkedStatus);
		if(!checkedStatus){
			// inputObj.attr('checked', true);
			inputObj.checked = true;
			$(this).children('.checkbox-mask').addClass('glyphicon glyphicon-ok-circle');
			// $(this).children('.checkbox-mask').css('background-color', 'white');
		}
		else{
			// inputObj.attr('checked', false);
			inputObj.checked = false;
			$(this).children('.checkbox-mask').removeClass('glyphicon glyphicon-ok-circle');
			// $(this).children('.checkbox-mask').css('background-color', 'transparent');
		}
	});

	$('.cross-study-query-form input[type=submit]').val('Check common DEGs');

	// activate data table for deg table in cross study
	$('.data-table').DataTable();
})

// http://string-db.org/api/tsv/resolveList?identifiers=trpA%0DtrpB&species=511145