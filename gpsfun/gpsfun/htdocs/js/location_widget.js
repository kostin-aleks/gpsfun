MapWidget = {
    map: null,
    geocoder: null,
    marker: null,
	position: null,
    zoom: 6,
	address: 'Kharkov Ukraine',
	text_position_object: null,
	
	
    init: function() {
		MapWidget.position = new google.maps.LatLng(50, 36.2);
		var myOptions = {
			zoom: MapWidget.zoom,
			center: MapWidget.position,
			scaleControl: true,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};

		MapWidget.map = new google.maps.Map($("#map_canvas")[0],
									  myOptions);

		MapWidget.geocoder = new google.maps.Geocoder();
		
		google.maps.event.addListener(MapWidget.map, 'click', function(event) {
			MapWidget.move_marker_here(event.latLng);
			});
		//google.maps.event.addListener(MapWidget.map, 'mousemove', function (event) {
			//MapWidget.showMouseLocation(event);
		//});

    },
	
	move_marker_here: function(position) {
		MapWidget.set_position(position);
		MapWidget.moveMarkerTo();
		if (MapWidget.text_position_object) {
			MapWidget.text_position_object.set_position(position);
		}
	},
    
    show: function() {
		MapWidget.init();
		MapWidget.addMarker();
	},
	
    createIcons: function() {
	MapWidget.default_marker = new google.maps.MarkerImage("/static/img/green_bulb.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);

	MapWidget.shadow = new google.maps.MarkerImage("/static/img/shadow-bulb.png",
	    new google.maps.Size(39.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
    },    
        
    addMarker: function() {					      
		MapWidget.marker = new google.maps.Marker({
			position: MapWidget.position, 
			map: MapWidget.map,
			title: 'title',
			pid: 1,
			site: 'site',
			site_code: 2,
			icon: MapWidget.default_marker,
			shadow:  MapWidget.shadow
			});  
			
		MapWidget.map.setCenter(MapWidget.position);
    },
    
    moveMarkerTo: function() {
		MapWidget.marker.setPosition(MapWidget.position);
	},
	
    removeMarker: function() {
		MapWidget.marker = null;
	},
    
    set_position: function(position) {
		MapWidget.position = position;
	},
	
    codeAddress: function(address) {
		MapWidget.geocoder.geocode( { 'address': address}, function(results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
			MapWidget.map.setCenter(results[0].geometry.location);
			MapWidget.map.setZoom(6);
			MapWidget.set_position(results[0].geometry.location);
			MapWidget.moveMarkerTo();
			} 
		});
    },
}
