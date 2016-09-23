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
	})
	// console.log("hello world");
	// // $('.feature-annotation').mouseover(function(){
	// // 	console.log("mouse in");
	// // 	$(this).children('a').before('<div class="string-link"><a>S</a></div>');
	// // }).mouseout(function(){
	// // 	console.log("mouse out");
	// // 	$(this).children('a').sibling('.string-link').remove();
	// // });	
	// $('.feature-annotation').hover(function(){
	// 	// console.log("mouse in");
	// 	$(this).children("a").before("<a class=\"string-link\" href=\"http://www.bbc.com\"></a>");
	// }, function(){
	// 	// console.log("mouse out");
	// 	$(this).children(".string-link").remove();
	// });	
})

// http://string-db.org/api/tsv/resolveList?identifiers=trpA%0DtrpB&species=511145