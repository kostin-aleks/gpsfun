RateFilter = {
    change_subjects_url: '/geocaching/su/change/subjects/',
    
    reload_subjects: function (obj){
	var target = $('#ratefilter_subjects')[0];
	if (target) {
	    $.ajax({
			url: RateFilter.change_subjects_url,
			type: 'GET',
			dataType: 'JSON',
			data: {	'country': obj.value },
			success: function(doc) {
				if (doc.status != "OK") { return; }
				var target = $('#ratefilter_subjects')[0];
				target.options.length = 0;
				var first_option = new Option('all', 'ALL', true, false);
				target.options[0] = first_option;
				
				for (var i=0;i<doc.regions.length;i++) {
				 var item = doc.regions[i]; 			    
				 item.name = gettext(item.name);
				 doc.regions[i] = item;
				}
 
				doc.regions.sort(function(a,b){if(a.name==b.name) {return 0;} else {return a.name < b.name ?-1:1}})
				for (var i=0;i<doc.regions.length;i++) {
				 target.options[target.options.length] = new Option(doc.regions[i].name, doc.regions[i].code, false, false)
				}
			}
		})
	}
    }
}


