CachesMap = {
    infowindow: null,
    map: null,
    mc: null,
    geocoder: null,
    markers: [],
    imageTR: null,
    imageVI: null,
    imageMS: null,
    imageMV: null,
    shadow: null,
    cache_info_url: null,
    change_country_url: null,
    region_caches_url: null,
    
    setInformationWindow: function (obj) {
	var df = Ajax.load_json(CachesMap.cache_info_url,
                            {'cache_pid': obj.pid,
                             'cache_site': obj.site,
                             });
	df.addCallback(function(doc) {
                           if (doc.status != "OK") {
                               return;
                           }
                           CachesMap.infowindow.setContent(doc.content);
			   CachesMap.infowindow.open(CachesMap.map, obj);
                       });
    
    },
    
	
    init: function() {
	var latlng = new google.maps.LatLng(50.0, 36.0);
	var myOptions = {
	    zoom: 6,
	    center: latlng,
	    scaleControl: true,
	    mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	setElementWidth("id_space", 98);
	CachesMap.map = new google.maps.Map($("#map_canvas")[0],
					              myOptions);
	var mcOptions = {gridSize: 50, maxZoom: 10};
    
	CachesMap.infowindow = new google.maps.InfoWindow({
	    content: "...",
	    size: new google.maps.Size(150,50)
	});
	CachesMap.mc = new MarkerClusterer(CachesMap.map, [], mcOptions);
	CachesMap.createIcons();
	CachesMap.geocoder = new google.maps.Geocoder();
	
	google.maps.event.addListener(CachesMap.map, 'click', function() {
	    CachesMap.infowindow.close();
        });
	google.maps.event.addListener(CachesMap.map, 'mousemove', function (event) {
	    CachesMap.showMouseLocation(event);
	});
	var all_option =  $('#id_types_all')[0];

    },
    
    createIcons: function() {
        CachesMap.imageTR = new google.maps.MarkerImage("/static/img/green_tr.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
	CachesMap.imageVI = new google.maps.MarkerImage("/static/img/blue_vi.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
        CachesMap.imageMS = new google.maps.MarkerImage("/static/img/green_ms.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
	CachesMap.imageMV = new google.maps.MarkerImage("/static/img/blue_mv.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);	
	CachesMap.shadow = new google.maps.MarkerImage("/static/img/shadow-bulb.png",
	    new google.maps.Size(39.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
    },
    
    iconByType: function(type_code) {
	    if (type_code=='TR') {
		return CachesMap.imageTR;
	    }
	    if (type_code=='VI') {
		return CachesMap.imageVI;
	    }
	    if (type_code=='MV') {
		return CachesMap.imageMV;
	    }
	    if (type_code=='MS') {
		return CachesMap.imageMS;
	    }
    },
    
    drawMap: function() {
	

	CachesMap.mc.addMarkers(CachesMap.markers);
    },
    
    changeRegions: function(obj) {
	var df = Ajax.load_json(CachesMap.change_country_url,
                            {'country': obj.value
                             });
	df.addCallback(function(doc) {
                           if (doc.status != "OK") {
                               return;
                           }
			   var target = $('#id_region')[0];
			   replaceChildNodes(target);
			   option_node = OPTION({'value': 'all'}, '-- all regions --');
			   connect(option_node, 'onclick', CachesMap, CachesMap.chooseAllRegions);
			   appendChildNodes(target, option_node);
		           forEach(doc.regions, function(item) {
				option_node = OPTION({'value': item.code}, item.name);
				appendChildNodes(target, option_node);
			    });
			   target.size = doc.regions.length+1;
			   CachesMap.markers = [];
			   CachesMap.mc.clearMarkers();
			   CachesMap.codeAddress(doc.address);
			   $('#id_count')[0].innerHTML = '';
                       });
    },
    
    loadCaches: function(o) {
        // region
	var obj = $('#id_region')[0];
	var selected = new Array();
	for (var i=0;i<obj.options.length;i++) {
	  if (obj.options[i].selected) selected.push(obj.options[i].value);
	}
	var region_selected = selected;
	// type
	obj = $('#id_type')[0];
	selected = new Array();
	for (var i=0;i<obj.options.length;i++) {
	  if (obj.options[i].selected) selected.push(obj.options[i].value);
	}
	var type_selected = selected;
	// related
	obj = $('#id_related')[0];
	selected = new Array();
	if (obj) {
	    for (var i=0;i<obj.options.length;i++) {
	      if (obj.options[i].selected) selected.push(obj.options[i].value);
	    }
	}
	var related_selected = selected;
	var df = Ajax.load_json(CachesMap.region_caches_url,
                            {'region': region_selected,
			    'type': type_selected,
			    'related': related_selected,
			    'country': $('#id_country').val()
                             });
	df.addCallback(function(doc) {
                           if (doc.status != "OK") {
                               return;
                           }
			    CachesMap.centerMap(doc.rect);
			   CachesMap.addMarkers(doc.caches);
			   
                       });
    },
    
    tuneInputs: function() {
	var selRegions = $('#id_region')[0];
	selRegions.size = selRegions.options.length+1;
    },
    
    addMarkers: function(caches_list) {
        $('#id_count')[0].innerHTML = '';
	CachesMap.markers = [];
	CachesMap.mc.clearMarkers();
	if (caches_list.length) {
	    showElement('import_data');
	} else {
	    hideElement('import_data');
	}
	if (!caches_list.length) return;
	
	var marker;
	for (var i=0;i<caches_list.length;i++) { 						      
	    marker = new google.maps.Marker({
		position: new google.maps.LatLng(caches_list[i].latitude_degree, caches_list[i].longitude_degree), 
		map: CachesMap.map,
		title: caches_list[i].name,
		pid: caches_list[i].pid,
		site: caches_list[i].site,
		icon: CachesMap.iconByType(caches_list[i].type_code),
		shadow:  CachesMap.shadow
	    });  
	    google.maps.event.addListener(marker, 'click', function () {
		//CachesMap.map.setCenter(this.position);
		CachesMap.setInformationWindow(this);
	    });
	    CachesMap.markers[CachesMap.markers.length] = marker;
	}
	CachesMap.mc.addMarkers(CachesMap.markers);
	$('#id_count')[0].innerHTML = gettext('found') + ': ' + caches_list.length;
	
    },
    
    centerMap: function(rectangle) {
	if ((rectangle.lat_min=='') || (rectangle.lat_max=='') || (rectangle.lng_min=='') || (rectangle.lng_max=='')) return;
	
	CachesMap.map.setCenter(new google.maps.LatLng(
	    ((rectangle.lat_max + rectangle.lat_min) / 2.0),
	    ((rectangle.lng_max + rectangle.lng_min) / 2.0)
	));
	
	CachesMap.map.fitBounds(new google.maps.LatLngBounds(
	    //bottom left
	    new google.maps.LatLng( rectangle.lat_min,  rectangle.lng_min),
	    //top right
	    new google.maps.LatLng( rectangle.lat_max,  rectangle.lng_max)
	));
    },
    
    codeAddress: function(address) {
	CachesMap.geocoder.geocode( { 'address': address}, function(results, status) {
	    if (status == google.maps.GeocoderStatus.OK) {
		CachesMap.map.setCenter(results[0].geometry.location);
		CachesMap.map.setZoom(6);
	    } 
	});
    },
    
    chooseAllRegions: function() {
	var target = $('#id_region')[0];
	CachesMap.loadCaches(target);
    },
    
    chooseAllTypes: function() {
	var target = $('#id_type');
	CachesMap.loadCaches(target);
    },
    
    showMouseLocation: function(event) {
	var latlng = event.latLng;
	$('#id_current_location')[0].innerHTML = CachesMap.toWGS84(1, latlng);

    },
    
    toWGS84: function(type_, latlng)
    {
	var lat = latlng.lat(), lng = latlng.lng();
	var latD = 'N', lngD = 'E';

	if(lat < 0) {
		lat = -lat;
		latD = 'S';
	}
	if(lng < 0) {
		lng = -lng;
		lngD = 'W';
	}

	var latstr, lngstr;

	if(type_ == 0) {
		latstr = lat.toFixed(5) + "°";
		lngstr = lng.toFixed(5) + "°";
	}
	else if(type_ == 1) {
		var degs1 = lat | 0;
		var degs2 = lng | 0;
		var minutes1 = ((lat - degs1)*60);
		var minutes2 = ((lng - degs2)*60);
		latstr = degs1 + "° " + minutes1.toFixed(3) + "'";
		lngstr = degs2 + "° " + minutes2.toFixed(3) + "'";
	}
	else if(type_ == 2) {
		var degs1 = lat | 0;
		var degs2 = lng | 0;
		var minutes1 = ((lat - degs1)*60);
		var minutes2 = ((lng - degs2)*60);
		var seconds1 = (minutes1 - (minutes1 | 0))*60;
		var seconds2 = (minutes2 - (minutes2 | 0))*60;
		latstr = degs1 + "° " + (minutes1 | 0) + "' " + (seconds1.toFixed(2)) + "\"";
		lngstr = degs2 + "° " + (minutes2 | 0) + "' " + (seconds2.toFixed(2)) + "\"";;
	}
	return latD + " " + latstr + " " + lngD + " " + lngstr;
    }

    

    

    
}

function getInsideWindowWidth() {
  if (window.innerWidth) {
    return window.innerWidth;
  } else if (isIE6CSS) {
    return document.body.parentElement.clientWidth;
  } else if (document.body && document.body.clientWidth) {
    return document.body.clientWidth;
  }
  return 0;
}

function setElementWidth(element_id, percent) {
    var e = document.getElementById(element_id);
    if (!e) return;
    var win_width =  getInsideWindowWidth();
    var perc_width = Math.round(win_width * percent / 100.0 );
    e.style.width = perc_width + 'px';
}