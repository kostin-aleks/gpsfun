SelectLocation = {
	get_waypoint_address_url: null,
	
	map_object: null,
	position_input: null,
	
    city_selector: function(country, region, city) {
        $.ajax({
				url: SelectLocation.get_waypoint_address_url,
				type: 'GET',
				dataType: 'JSON',
				data: {	'country': country,
						'region': region,
						'city': city,
					   },
				success: function(doc) {
					if (doc.status != "OK") {
						return;
					}
				   if (SelectLocation.map_object) {
						SelectLocation.map_object.codeAddress(doc.address);
						if (SelectLocation.position_input) {
							 SelectLocation.position_input.address_to_position(doc.address);
						}						
				   }
				},
			})
    }
	
   
}



