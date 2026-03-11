SetPosition = {
    infowindow: null,
    map: null,
    mc: null,
    geocoder: null,
    marker: null,
	position: null,
    zoom: 6,
	address: 'Kharkov Ukraine',
	converter_url: null,
	position: {'latitude': null, 'longitude': null},
	
	validate: function(o) {
			var coordinate = o.id.substring(3);
	
			var id_degree = 'id_'+coordinate;
			var degree = $('#'+id_degree).val();

		    if (degree) {
				$.ajax({
					url: SetPosition.converter_url,
					type: 'GET',
					dataType: 'JSON',
					data: {	'input': degree },
					success: function(doc) {
						if (doc.status != "OK") {
							SetPosition.set_status(coordinate, 'error');
							return;
						}
						
						var id_sign = 'btn_'+coordinate.substring(0,3)+'_sign';
						doc.sign = $('#'+id_sign)[0].innerHTML;
						var float_degree = doc.d * 1.0;
						if (!SetPosition.valid_coordinate(doc.d, coordinate)) {
							SetPosition.set_status(coordinate, 'error');
						} else {
							SetPosition.position[coordinate] = SetPosition.get_coordinate(doc);
							SetPosition.showCoordinates(coordinate, doc);
							SetPosition.set_status(coordinate, 'success');
							SetPosition.moveMarker();
						}
						
					}
				})
		    } else {
				SetPosition.set_status(coordinate, 'warning');
			}
	
	},
	
	valid_coordinate: function(degree, coordinate) {
		degree = degree * 1.0;
		if (degree <= 90.0) return true;
		if ((degree <= 180.0) && (coordinate=='longitude')) return true;
		return false;
	},
	
	get_coordinate: function(d) {
		degree = d.d * 1.0;
		sign = d.sign;
		if (sign=='S' || sign=='W') degree = -degree;
		return degree;
	},
	
	set_status: function(coordinate, status) {
		var statuses = ['success','error','warning'];
		var panel= $("#id_"+coordinate+"_block");
		var className = panel[0].className;
		if (className.indexOf(status) > -1) return;
		var el_classes = className.split(' ');
		new_classes = new Array();
		for (var i=0;i<=el_classes.length;i++) {
			if (statuses.indexOf(el_classes[i]) == -1) new_classes[new_classes.length] = el_classes[i];	
		}
		new_classes[new_classes.length] = status;
		panel[0].className = new_classes.join(' ');
	},
	
	showCoordinates: function(coordinate, data) {
		$('#id_'+coordinate).val(data.dm);
	},
	
	get_coordinate_dir: function(o) {
		var coordinate = 'lat';
		if (o.id.indexOf('_lon_') > 0) coordinate = 'lon';
		return coordinate;
	},
	
	toggleChar: function(o, s) {
		var ch = s[0];
		if (o.innerHTML==s[0]) {
			ch = s[1];	
		}
		o.innerHTML = ch;
	},
	
	toggleSign: function(o) {
		var coordinate = SetPosition.get_coordinate_dir(o);
		var id_input = 'btn_'+coordinate+'_sign';
		SetPosition.toggleChar(o, coordinate=='lat' ? 'NS' : 'EW');
		var el_hidden = document.getElementById(id_input);
		el_hidden.value = o.innerHTML;
	},
	
	moveMarker: function() {
		if ((SetPosition.position['latitude'] != null) && (SetPosition.position['longitude'] != null)) {
			if (SetPosition.map) {
				var position = SetPosition.get_position();
				SetPosition.map.set_position(position);
				SetPosition.map.moveMarkerTo();
				SetPosition.map.map.setCenter(position);
				SetPosition.map.map.setZoom(6);
			}	
		}
	},
	
	get_position: function() {
		if (SetPosition.valid_position()) {
			return new google.maps.LatLng(SetPosition.position['latitude'], 
										SetPosition.position['longitude']);
		} else return null;
	},
	
	valid_position: function() {
		if ((SetPosition.position['latitude'] == null) || (SetPosition.position['longitude'] == null)) {
			return false;
		}	
		return true;
	},
	
	set_position: function(position) {
		$('#id_latitude').val(SetPosition.D_to_DM(position.lat()));
		$('#id_longitude').val(SetPosition.D_to_DM(position.lng()));
	},
	
	address_to_position: function(address) {
		var position = null;
		SetPosition.map.geocoder.geocode( { 'address': address}, function(results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
				position = results[0].geometry.location;
				SetPosition.set_position(position);
			} 
		});
	},
	
	D_to_DM: function(degree) {
		// get minutes
		var degree_int = Math.floor(degree);
		var minutes = (degree - degree_int) * 60.0;
		// format string
		var minutes_str = Math.round(minutes*1000)/1000;
		return degree_int + '° '+ minutes_str
	}
	
    //rc['dm'] = "%d° %.3f\'" % (int(Deg),
                               //minutes_from_degree(Deg))
	//def minutes_from_degree(d):
        //f = d - int(d)
        //return f*60						   
}
