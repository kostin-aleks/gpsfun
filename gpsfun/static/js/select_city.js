CityWidget = {
  
    change_country_url: null,
	change_region_url: null,    
	
	country_id: 'id_select_country',
	subject_id: 'id_select_subject',
	city_id: 'id_select_city',
	
	listener: null,
	
    init: function(country_id, subject_id, city_id) {
		CityWidget.country_id = country_id;
		CityWidget.subject_id = subject_id;
		CityWidget.city_id = city_id;
    },
    
    send_to_listener: function() {
		var country = document.getElementById(CityWidget.country_id);
		var region = document.getElementById(CityWidget.subject_id);
		var city = document.getElementById(CityWidget.city_id);
		
		if (CityWidget.listener) CityWidget.listener(country.value, region.value, city.value);
	},
	
    show_spinner: function() {
		$('#map_spinner').show();
    },
    
    hide_spinner: function() {
		$('#map_spinner').hide();
    },

    reload_subjects: function(o) {
		var country_iso = o.value;
		if (!country_iso) return;
		
		this.show_spinner();
		$.ajax({
				url: CityWidget.change_country_url,
				type: 'GET',
				dataType: 'JSON',
				data: {	'country': country_iso
					   },
				success: function(doc) {
					if (doc.status != "OK") {
						return;
					}
				   CityWidget.populate_regions(doc.regions);
				   CityWidget.send_to_listener();
				},
				complete: function() {
					CityWidget.hide_spinner();	
				}
			})
		
    },

	reload_cities: function(o) {
		var region_code = o.value;
		if (!region_code) return;
		var country_iso = '';
		var el_country = $('#'+CityWidget.country_id);		
		if (el_country) { var country_iso = el_country.val(); }
		if (!country_iso) return;
		CityWidget.show_spinner();
		$.ajax({
				url: CityWidget.change_region_url,
				type: 'GET',
				dataType: 'JSON',
				data: {	'country': country_iso,
						'region': region_code
					   },
				success: function(doc) {
					if (doc.status != "OK") {
						return;
					}
				   CityWidget.populate_cities(doc.cities);
				   CityWidget.send_to_listener();
				},
				complete: function() {
					CityWidget.hide_spinner();	
				}
			})
    },
	
	chosen_city: function(o) {
		CityWidget.send_to_listener();
	},
	
	clear_options: function(o, text_of_first) {
		if (!o) return;
		o.options.length = 0;
		var first_option = new Option(text_of_first, 'NONE', true, false);
		o.options[0] = first_option;	
	},
	
	populate_options: function(o, items) {
		if (items && items.length) {
			for (var i=0;i<items.length;i++) {
				var item = items[i]; 			    
				item.name = gettext(item.name);
				items[i] = item;
			}
	
			items.sort(function(a,b){if(a.name==b.name) {return 0;} else {return a.name < b.name ?-1:1}})
			for (var i=0;i<items.length;i++) {
				o.options[o.options.length] = new Option(items[i].name, items[i].code, false, false)
			}
		}
	},
	
    populate_regions: function(regions) {
		var target = document.getElementById(CityWidget.subject_id);
		
		CityWidget.clear_options(target, gettext('-- choose admin subject --')
		);
		
		CityWidget.clear_options(document.getElementById(CityWidget.city_id),
								 gettext('-- choose city --')
		);

		CityWidget.populate_options(target, regions);
	
	},
	
	populate_cities: function(cities) {
		var target = document.getElementById(CityWidget.city_id);
		CityWidget.clear_options(target, gettext('-- choose city --'));
		CityWidget.populate_options(target, cities);
	
	}	
   
}



