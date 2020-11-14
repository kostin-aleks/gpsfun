CachesMap = {
    infowindow: null,
    alertwin: null,
    map: null,
    mc: null,
    geocoder: null,
    markers: [],
    //confluence_markers: [],
    imageTR: null,
    imageVI: null,
    imageMS: null,
    imageMV: null,
    shadow: null,
    cache_info_url: null,
    change_country_url: null,
    region_caches_url: null,
    get_confluence_url: null,
    get_things_url: null,
    show_cache_types_url: null,
    MAX_COUNT: 2000,
    marker_style: null,
    vectorSource: null,
    vectorLayer: null,
    popup: null,

    setInformationWindow: function (obj) {
		$.ajax({
			url: CachesMap.cache_info_url,
			type: 'GET',
			dataType: 'JSON',
			data: { 'cache_pid': obj.pid,
					'cache_site': obj.site_code
			},
			success: function(doc) {
				if (doc.status != "OK") { return;}
				//CachesMap.infowindow.setContent(doc.content);
				//CachesMap.infowindow.open(CachesMap.map, obj);
			}
		})
    },


    init: function(center, zoom) {
        var mousePositionControl = new ol.control.MousePosition({
            coordinateFormat: function(coordinate) {
                  return CachesMap.toWGS84(1, coordinate)
            },
            projection: 'EPSG:4326',
            // comment the following two lines to have the mouse position
            // be placed within the map.
            className: 'custom-mouse-position',
            target: document.getElementById('id_current_location'),
            undefinedHTML: '&nbsp;'
        });

        //var iconFeature = new ol.Feature({
        //  geometry: new ol.geom.Point(ol.proj.fromLonLat(center)),
        //  name: 'Null Island',
        //  population: 4000,
        //  rainfall: 500
        //});

        CachesMap.marker_style = new ol.style.Style({
          image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
            anchor: [0.5, 46],
            anchorXUnits: 'fraction',
            anchorYUnits: 'pixels',
            opacity: 0.75,
            src: '/static/img/su_tr_bulb.png'
          }))
        });

        //iconFeature.setStyle(CachesMap.marker_style);

        CachesMap.vectorSource = new ol.source.Vector({
          features: []
        });

        CachesMap.vectorLayer = new ol.layer.Vector({
          source: CachesMap.vectorSource
        });

        var map = new ol.Map({
            layers: [
              new ol.layer.Tile({
                source: new ol.source.OSM()
              }), CachesMap.vectorLayer
            ],
            target: 'map',
            controls: ol.control.defaults({
              attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                collapsible: false
              })
            }).extend([mousePositionControl]),
            view: new ol.View({
              center: ol.proj.fromLonLat(center),
              zoom: zoom
            })
        });



        //CachesMap.infowindow = new ol.Overlay.Popup;
        //map.addOverlay(CachesMap.infowindow);

        //CachesMap.alertwin = new ol.Overlay.Popup;
        //map.addOverlay(CachesMap.alertwin);

        var exampleLoc = ol.proj.transform(
            [36, 50], 'EPSG:4326', 'EPSG:3857');

        //CachesMap.map.addOverlay(new ol.Overlay({
        //  position: exampleLoc,
        //  element: $('<img src="/static/img/su_tr_bulb.png">')
        //  .css({marginTop: '-200%', marginLeft: '-50%', cursor: 'pointer'})
        //  .tooltip({title: 'Hello, world!', trigger: 'click'})
        //}));


        var element = document.getElementById('popup');
        CachesMap.popup = new ol.Overlay({
            element: element,
            positioning: 'bottom-center',
            stopEvent: false
        });
        map.addOverlay(CachesMap.popup);

        map.on('click', function(evt) {

          var element = CachesMap.popup.getElement();
          var coordinate = evt.coordinate;
          var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(
              coordinate, 'EPSG:3857', 'EPSG:4326'));
                        alert(hdms);
          $(element).popover('destroy');

          CachesMap.popup.setPosition(coordinate);
          // the keys are quoted to prevent renaming in ADVANCED_OPTIMIZATIONS mode.

          $(element).popover({
            'placement': 'top',
            'animation': false,
            'html': true,
            'content': '<p>The location you clicked was:</p><code>' + hdms + '</code>'
          });

          $(element).popover('show');

        });


        map.on('moveend', CachesMap.loadThings);
        map.on('zoomend', CachesMap.loadThings);
        //map.on('click', function() { CachesMap.infowindow.close(); });
        //map.on('mousemove', function (event) {
        //                    CachesMap.showMouseLocation(event);
        //});

        CachesMap.map = map;
    },

    show_spinner: function() {
        $('#map_spinner').show();
    },

    hide_spinner: function() {
        $('#map_spinner').hide();
    },

    createIcons: function() {
	CachesMap.default_marker = new google.maps.MarkerImage("/static/img/green_bulb.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
        CachesMap.imageTR = new google.maps.MarkerImage("/static/img/su_tr_bulb.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
	CachesMap.imageVI = new google.maps.MarkerImage("/static/img/su_vi_bulb.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
        CachesMap.imageMS = new google.maps.MarkerImage("/static/img/su_ms_bulb.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
	CachesMap.imageMV = new google.maps.MarkerImage("/static/img/su_mv_bulb.png",
	    new google.maps.Size(21.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);	
	CachesMap.shadow = new google.maps.MarkerImage("/static/img/shadow-bulb.png",
	    new google.maps.Size(39.0, 34.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 17.0)
	);
	CachesMap.shadow_su_tr = new google.maps.MarkerImage("/static/img/shadow-su_tr.png",
	    new google.maps.Size(31.0, 20.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 10.0)
	);
	CachesMap.shadow_su_vi = new google.maps.MarkerImage("/static/img/shadow-su_vi.png",
	    new google.maps.Size(31.0, 20.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 10.0)
	);
	CachesMap.shadow_su_ms = new google.maps.MarkerImage("/static/img/shadow-su_ms1.png",
	    new google.maps.Size(31.0, 20.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 10.0)
	);
	CachesMap.shadow_su_mv = new google.maps.MarkerImage("/static/img/shadow-su_mv.png",
	    new google.maps.Size(31.0, 20.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(10.0, 10.0)
	);
	CachesMap.shadow_h = new google.maps.MarkerImage("/static/img/shadow-tajnik24.png",
	    new google.maps.Size(40.0, 26.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(13.0, 13.0)
	);
	CachesMap.shadow_p = new google.maps.MarkerImage("/static/img/shadow-dost32.png",
	    new google.maps.Size(40.0, 26.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(13.0, 13.0)
	);
	CachesMap.shadow_p = new google.maps.MarkerImage("/static/img/shadow-quest24.png",
	    new google.maps.Size(40.0, 26.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(13.0, 13.0)
	);
	CachesMap.shadow_c = new google.maps.MarkerImage("/static/img/shadow-casket24.png",
	    new google.maps.Size(37.0, 24.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 12.0)
	);
	CachesMap.shadow_con = new google.maps.MarkerImage("/static/img/shadow-confluence24.png",
	    new google.maps.Size(37.0, 24.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 12.0)
	);
	CachesMap.shadow_g = new google.maps.MarkerImage("/static/img/shadow-benchmark24.png",
	    new google.maps.Size(37.0, 24.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 12.0)
	);
	
	CachesMap.imageH = new google.maps.MarkerImage("/static/img/tajnik24.png",
	    new google.maps.Size(26.0, 26.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(13.0, 13.0)
	);
	CachesMap.imageP = new google.maps.MarkerImage("/static/img/dost32.png",
	    new google.maps.Size(26.0, 26.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(13.0, 13.0)
	);
	CachesMap.imageQ = new google.maps.MarkerImage("/static/img/quest24.png",
	    new google.maps.Size(26.0, 26.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(13.0, 13.0)
	);
	CachesMap.imageC = new google.maps.MarkerImage("/static/img/casket24.png",
	    new google.maps.Size(24.0, 24.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 12.0)
	);
	CachesMap.imageCon = new google.maps.MarkerImage("/static/img/confluence24.png",
	    new google.maps.Size(24.0, 24.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 12.0)
	);
	CachesMap.imageG = new google.maps.MarkerImage("/static/img/benchmark24.png",
	    new google.maps.Size(24.0, 24.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 12.0)
	);
	
	CachesMap.imageOPTR = new google.maps.MarkerImage("/static/img/traditional-s.png",
	    new google.maps.Size(32.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.imageOPMS = new google.maps.MarkerImage("/static/img/multi-s.png",
	    new google.maps.Size(32.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.imageQZ = new google.maps.MarkerImage("/static/img/quiz-s.png",
	    new google.maps.Size(32.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.imageOT = new google.maps.MarkerImage("/static/img/unknown-s.png",
	    new google.maps.Size(32.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.imageMOV = new google.maps.MarkerImage("/static/img/moving-s.png",
	    new google.maps.Size(32.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.imageOPVI = new google.maps.MarkerImage("/static/img/virtual-s.png",
	    new google.maps.Size(32.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.shadow_optr = new google.maps.MarkerImage("/static/img/shadow-op-tr.png",
	    new google.maps.Size(49.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.shadow_opms = new google.maps.MarkerImage("/static/img/shadow-op-ms.png",
	    new google.maps.Size(49.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.shadow_qz = new google.maps.MarkerImage("/static/img/shadow-op-qz.png",
	    new google.maps.Size(49.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.shadow_ot = new google.maps.MarkerImage("/static/img/shadow-op-other.png",
	    new google.maps.Size(49.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.shadow_mov = new google.maps.MarkerImage("/static/img/shadow-op-mv.png",
	    new google.maps.Size(49.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	CachesMap.shadow_opvi = new google.maps.MarkerImage("/static/img/shadow-op-vi.png",
	    new google.maps.Size(49.0, 32.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(16.0, 16.0)
	);
	
	CachesMap.imageOCTR = new google.maps.MarkerImage("/static/img/occom_tr.png",
	    new google.maps.Size(24.0, 30.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 15.0)
	);
	CachesMap.imageOCMS = new google.maps.MarkerImage("/static/img/occom_ms.png",
	    new google.maps.Size(24.0, 30.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 15.0)
	);
	CachesMap.imageOCQZ = new google.maps.MarkerImage("/static/img/occom_qz.png",
	    new google.maps.Size(24.0, 30.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 15.0)
	);
	CachesMap.imageOCVI = new google.maps.MarkerImage("/static/img/occom_vi.png",
	    new google.maps.Size(24.0, 30.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 15.0)
	);
	CachesMap.shadow_occom = new google.maps.MarkerImage("/static/img/shadow-occom.png",
	    new google.maps.Size(40.0, 30.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(12.0, 15.0)
	);
	CachesMap.iconPoint = new google.maps.MarkerImage("/static/img/c_b.gif",
	    new google.maps.Size(6.0, 6.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(6.0, 6.0)
	);
	CachesMap.iconConfluence = new google.maps.MarkerImage("/static/img/icon50l.png",
	    new google.maps.Size(16.0, 16.0),
	    new google.maps.Point(0, 0),
	    new google.maps.Point(8.0, 8.0)
	);
	CachesMap.shadowConfluence = CachesMap.shadow;
    },

    iconByType: function(site_code, type_code) {
	if (site_code == 'GC_SU') {
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
	}
	if (site_code == 'SHUKACH') {
	    if (type_code=='H') {
		return CachesMap.imageH;
	    }
	    if (type_code=='Q') {
		return CachesMap.imageQ;
	    }
	    if (type_code=='P') {
		return CachesMap.imageP;
	    }
	    if (type_code=='C') {
		return CachesMap.imageC;
	    }
	    if (type_code=='G') {
		return CachesMap.imageG;
	    }
	    if (type_code=='Con') {
		return CachesMap.imageCon;
	    }
	}
	if ((site_code == 'OCPL') || (site_code == 'OCUK') ||
	    (site_code == 'OCNL') || (site_code == 'OCUS') ||
		(site_code == 'OCDE') || (site_code == 'OCCZ')){
	    if ((type_code=='TR') || (type_code=='DR')){
		return CachesMap.imageOPTR;
	    }
	    if (type_code=='MS') {
		return CachesMap.imageOPMS;
	    }
	    if ((type_code=='QZ') || (type_code=='MT')) {
		return CachesMap.imageQZ;
	    }
	    if (type_code=='OT') {
		return CachesMap.imageOT;
	    }
	    if (type_code=='MO') {
		return CachesMap.imageMOV;
	    }
	    if (type_code=='VI') {
		return CachesMap.imageOPVI;
	    }
	    if (type_code=='WC') {
		return CachesMap.imageOPVI;
	    }
	}
	if (site_code == 'OC_COM') {
	    if (type_code=='TR') {
		return CachesMap.imageOCTR;
	    }
	    if (type_code=='VI') {
		return CachesMap.imageOCVI;
	    }
	    if (type_code=='OT') {
		return CachesMap.imageOCQZ;
	    }
	    if (type_code=='MS') {
		return CachesMap.imageOCMS;
	    }
	}
	return CachesMap.default_marker
    },

    shadowByType: function(site_code, type_code) {
	if (site_code == 'GC_SU') {
	    return CachesMap.shadow;

	    if (type_code=='TR') {
		return CachesMap.shadow_su_tr;
	    }
	    if (type_code=='VI') {
		return CachesMap.shadow_su_vi;
	    }
	    if (type_code=='MV') {
		return CachesMap.shadow_su_mv;
	    }
	    if (type_code=='MS') {
		return CachesMap.shadow_su_ms;
	    }
	}
	if (site_code == 'SHUKACH') {
	    if (type_code=='H') {
		return CachesMap.shadow_h;
	    }
	    if (type_code=='Q') {
		return CachesMap.shadow_q;
	    }
	    if (type_code=='P') {
		return CachesMap.shadow_p;
	    }
	    if (type_code=='C') {
		return CachesMap.shadow_c;
	    }
	    if (type_code=='G') {
		return CachesMap.shadow_g;
	    }
	    if (type_code=='Con') {
		return CachesMap.shadow_con;
	    }
	}
	if ((site_code == 'OCPL') || (site_code == 'OCUK') ||
	    (site_code == 'OCNL') || (site_code == 'OCUS') ||
		(site_code == 'OCDE') || (site_code == 'OCCZ')){
	    if (type_code=='TR') {
		return CachesMap.shadow_optr;
	    }
	    if (type_code=='MS') {
		return CachesMap.shadow_opms;
	    }
	    if (type_code=='QZ') {
		return CachesMap.shadow_qz;
	    }
	    if (type_code=='OT') {
		return CachesMap.shadow_ot;
	    }
	    if (type_code=='MO') {
		return CachesMap.shadow_mov;
	    }
	    if (type_code=='VI') {
		return CachesMap.shadow_opvi;
	    }
	}
	if (site_code == 'OC_COM') {
	    return CachesMap.shadow_occom;
	}
	return CachesMap.shadow;
    },

    drawMap: function() {
		CachesMap.mc.addMarkers(CachesMap.markers);
    },

	showAlert: function(count) {
		var bounds = CachesMap.map.getBounds();
		var lat = (3*bounds.getNorthEast().lat() + 2*bounds.getSouthWest().lat())/5.0;
		var lon = (bounds.getSouthWest().lng() + bounds.getNorthEast().lng())/2.0
		var p = new google.maps.Marker({
			position: new google.maps.LatLng(lat, lon),
			map: CachesMap.map,
			title: '',
			icon: CachesMap.iconPoint,
		});
		//CachesMap.alertwin.setContent(gettext('There are ')+ count +gettext('  geocaches on the map. <br/>Please magnify the view to display the geocaches.'));
		//CachesMap.alertwin.open(CachesMap.map, p);
	},

	hideAlert: function(count) {
		//CachesMap.alertwin.close();
	},

    changeRegions: function(obj) {
		$.ajax({
			url: CachesMap.change_country_url,
			type: 'GET',
			dataType: 'JSON',
			data: {	'country': obj.value },
			success: function(doc) {
				if (doc.status != "OK") { return; }
				var target = $('#id_region')[0];
				target.options.length = 0;
				var first_option = new Option('-- all regions --', 'all', true, false);
				first_option.id = 'all_regions_option';
				target.options[0] = first_option;
				$('#all_regions_option').bind('click', CachesMap.chooseAllRegions);
				
				for (var i=0;i<doc.regions.length;i++) {
				 var item = doc.regions[i];
				 item.name = gettext(item.name);
				 doc.regions[i] = item;
				}

				doc.regions.sort(function(a,b){if(a.name==b.name) {return 0;} else {return a.name < b.name ?-1:1}})
				for (var i=0;i<doc.regions.length;i++) {
				 target.options[target.options.length] = new Option(doc.regions[i].name, doc.regions[i].code, false, false)
				}

				target.size = doc.regions.length+1;
				CachesMap.markers = [];
				CachesMap.mc.clearMarkers();
				CachesMap.codeAddress(doc.address);
				//$('#id_count')[0].innerHTML = '';
			}
		})
    },

    getMapBounds: function() {
        var extent = CachesMap.map.getView().calculateExtent(CachesMap.map.getSize());
        extent = ol.proj.transformExtent(extent, 'EPSG:3857', 'EPSG:4326');
        return extent;
        },

    getCenter: function() {
        return CachesMap.map.getView().getCenter();
    },

    loadThings: function() {
        CachesMap.show_spinner();
        CachesMap.hideAlert();
        bounds = CachesMap.getMapBounds();
        map_center = CachesMap.getCenter();
        map_center = ol.proj.toLonLat(map_center)

        if (bounds) {
            $.ajax({
                url: CachesMap.get_things_url,
                type: 'GET',
                dataType: 'JSON',
                data: {
                    'left': bounds[0],
                    'top': bounds[3],
                    'right': bounds[2],
                    'bottom': bounds[1],
                    'center_lat': map_center[1],
                    'center_lon': map_center[0],
                    'zoom': CachesMap.map.getView().getZoom(),
                },
                success: function(doc) {
                    //alert(doc.count);
                    CachesMap.addMarkers(doc.caches, doc.points);
                    CachesMap.hide_spinner();
                    //if (doc.count>CachesMap.MAX_COUNT) {
                    //    CachesMap.showAlert(doc.count);
                    //} else { CachesMap.hideAlert(); }
                }
            });
        }
    },

	showCacheTypes: function(o) {
	    this.show_spinner();
		type_selected = new Array();
		$("[type=checkbox]").each(function(){
			var _input = $(this);
			if (_input.is(':checked')) {
			    type_selected.push(_input.val());
			}
		});

		$.ajax({
			url: CachesMap.show_cache_types_url,
			type: 'GET',
			dataType: 'JSON',
			data: {	'type': type_selected,
				   },
			success: function(doc) {
					if (doc.status != "OK") { return;}
					CachesMap.loadThings();
				    //CachesMap.hide_spinner();
					}
		})
	},

    loadCaches: function(o) {
		this.show_spinner();
			// region
		var obj = $('#id_region')[0];
		var selected = new Array();
		for (var i=0;i<obj.options.length;i++) {
		  if (obj.options[i].selected) selected.push(obj.options[i].value);
		}
		var region_selected = selected;
		// site
		var obj = $('#id_site')[0];
		var selected = new Array();
		for (var i=0;i<obj.options.length;i++) {
		  if (obj.options[i].selected) selected.push(obj.options[i].value);
		}
		var site_selected = selected;
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

		$.ajax({
			url: CachesMap.region_caches_url,
			type: 'GET',
			dataType: 'JSON',
			data: {'region': region_selected,
					'type': type_selected,
					'related': related_selected,
					'country': $('#id_country').val(),
					'site': site_selected
				   },
			success: function(doc) {
					if (doc.status != "OK") { return;}
					CachesMap.centerMap(doc.rect);
					if (doc.caches.length) {
						CachesMap.addMarkers(doc.caches);
					} else {
						var	address = doc.address ? doc.address : ''
						CachesMap.notFoundMarkers(address);
					}
				    CachesMap.hide_spinner();
					}
		})
    },

    addMarkers: function(caches_list, points_list) {
        CachesMap.vectorSource.clear();
        if (caches_list.length) {
            $('#import_data').show();
        } else {
            $('#import_data').hide();
        }
        if (!caches_list.length) return;

        for (var i=0;i<caches_list.length;i++) {
            var iconFeature = new ol.Feature({
              geometry: new ol.geom.Point(ol.proj.fromLonLat([caches_list[i].longitude_degree, caches_list[i].latitude_degree])),
            });

            iconFeature.setStyle(CachesMap.marker_style);

            CachesMap.vectorSource.addFeature(iconFeature);
        }
        CachesMap.vectorSource.refresh();
        //var markers = new OpenLayers.Layer.Vector('Markers');

        //CachesMap.map.addLayer(markers);
        return;



		CachesMap.markers = [];
		CachesMap.mc.clearMarkers();
		if (caches_list.length) {
			$('#import_data').show();
		} else {
			$('#import_data').hide();
		}
		if (!caches_list.length) return;
		
		var marker;
		for (var i=0;i<caches_list.length;i++) {
			marker = new google.maps.Marker({
				position: new google.maps.LatLng(caches_list[i].latitude_degree,
				caches_list[i].longitude_degree),
				map: CachesMap.map,
				title: caches_list[i].name,
				pid: caches_list[i].pid,
				site: caches_list[i].site,
				site_code: caches_list[i].site_code,
				icon: CachesMap.iconByType(caches_list[i].site_code,
				caches_list[i].type_code),
				shadow:  CachesMap.shadowByType(caches_list[i].site_code,
				caches_list[i].type_code)
			});
			google.maps.event.addListener(marker, 'click', function () {
				CachesMap.setInformationWindow(this);
			});
			CachesMap.markers[CachesMap.markers.length] = marker;
		}

		for (var i=0;i<points_list.length;i++) {
			marker = new google.maps.Marker({
			position: new google.maps.LatLng(points_list[i].latitude_degree,
			                                 points_list[i].longitude_degree),
			map: CachesMap.map,
			title: 'confluence',
			icon: CachesMap.iconConfluence,
			});
			marker.kind = 'confluence';

			CachesMap.markers[CachesMap.markers.length] = marker;
			CachesMap.mc.addMarker(marker);
		}
		CachesMap.mc.addMarkers(CachesMap.markers);
    },

    notFoundMarkers: function(address) {
		CachesMap.markers = [];
		CachesMap.mc.clearMarkers();
		$('#import_data').hide();
		if (address) {
		CachesMap.codeAddress(address);
		}
	},
	
    centerMap: function(rectangle) {
		if (!rectangle) return;
		
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
			CachesMap.map.setZoom(12);
			CachesMap.loadThings();
			}
		});
    },

    chooseAllRegions: function() {
		var target = $('#id_region')[0];
		CachesMap.loadCaches(target);
    },

    chooseAllTypes: function() {
		var target = $('#id_type')[0];
		CachesMap.loadCaches(target);
    },

    //showMouseLocation: function(event) {
    //    var latlng = event.latLng;
    //    $('#id_current_location')[0].innerHTML = CachesMap.toWGS84(1, latlng);
    //},

    toWGS84: function(type_, latlng)
    {
		var lat = latlng[1], lng = latlng[0];
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
		return latD + " " + latstr + " &nbsp;" + lngD + " " + lngstr;
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

/*
        CachesMap.infowindow = new InfoBubble({
            minWidth: 300,
            minHeight: 200,
            disableAnimation: true,
            backgroundColor: '#F8FFFD'
        });

        CachesMap.alertwin = new InfoBubble({
            minWidth: 200,
            minHeight: 100,
            disableAnimation: true,
            backgroundColor: 'lightgreen'
        });


		var myOptions = {
				 content: boxText
				,disableAutoPan: false
		        ,alignBottom: false
				,maxWidth: 280
				,pixelOffset: new google.maps.Size(-140, 0)
				,zIndex: null
				,boxStyle: {
				  background: "url('/img/tipbox.gif') no-repeat"
				  //,opacity: 0.9
				  ,width: "280px"
				 }
				,closeBoxMargin: "10px 2px 2px 2px"
				,closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif"
				,infoBoxClearance: new google.maps.Size(1, 1)
				,isHidden: false
				,pane: "floatPane"
				,enableEventPropagation: false
		};
		
		
var mcOptions = {gridSize: 50, maxZoom: 10};
		
		var boxText = document.createElement("div");
		boxText.style.cssText = "border: 1px solid black; margin-top: 8px; background: white; padding: 5px;";
		boxText.innerHTML = "...";
		
CachesMap.mc = new MarkerClusterer(CachesMap.map, [], mcOptions);
		CachesMap.createIcons();
		CachesMap.geocoder = new google.maps.Geocoder();
		
		google.maps.event.addListener(CachesMap.map, 'click', function() {
			CachesMap.infowindow.close();
			});
		google.maps.event.addListener(CachesMap.map, 'mousemove', function (event) {
			CachesMap.showMouseLocation(event);
		});
		google.maps.event.addListener(CachesMap.map, 'zoom_changed', function() {
			CachesMap.loadThings();
		});
		google.maps.event.addListener(CachesMap.map, 'dragend', function() {
			CachesMap.loadThings();
		});
		var all_option =  $('#id_types_all')[0];

*/

