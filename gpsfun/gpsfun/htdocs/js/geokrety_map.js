GeoKretyMap = {
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
    geokret_info_url: null,
    change_country_url: null,
    find_by_waypoint_url: null,
    get_geokrety_url: null,
    text_changed: false,
    tip_text: '',


    setInformationWindow: function (obj) {
        $.ajax({
            url: GeoKretyMap.geokret_info_url,
            type: 'GET',
            dataType: 'JSON',
            data: {    'waypoint': obj.waypoint },
            success: function(doc) {
                if (doc.status != "OK") {
                    return;
                }
                GeoKretyMap.infowindow.setContent(doc.content);
                //document.getElementById('infoWindow').parentNode.style.overflow = '';
                //document.getElementById('infoWindow').parentNode.style.overflowX = 'hidden';

                //GeoKretyMap.infowindow.setContent(doc.content);
                GeoKretyMap.infowindow.open(GeoKretyMap.map, obj);
            }
        });

    //var df = Ajax.load_json(GeoKretyMap.geokret_info_url,
                            //{'waypoint': obj.waypoint
                             //});
    //df.addCallback(function(doc) {
                           //if (doc.status != "OK") {
                               //return;
                           //}
                           //GeoKretyMap.infowindow.setContent(doc.content);
               //GeoKretyMap.infowindow.open(GeoKretyMap.map, obj);
                       //});

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
    GeoKretyMap.map = new google.maps.Map($("#map_canvas")[0],
                                  myOptions);
    var mcOptions = {gridSize: 50, maxZoom: 10};

    var boxText = document.createElement("div");
        boxText.style.cssText = "border: 1px solid black; margin-top: 8px; background: white; padding: 5px;";
        boxText.innerHTML = "...";

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

    GeoKretyMap.infowindow = new InfoBubble({
        minWidth: 300,
        minHeight: 130,
        disableAnimation: true,
        backgroundColor: '#E8FFDD'
        });

    GeoKretyMap.mc = new MarkerClusterer(GeoKretyMap.map, [], mcOptions);
    GeoKretyMap.createIcons();
    GeoKretyMap.geocoder = new google.maps.Geocoder();

    google.maps.event.addListener(GeoKretyMap.map, 'click', function() {
        GeoKretyMap.infowindow.close();
        });
    google.maps.event.addListener(GeoKretyMap.map, 'mousemove', function (event) {
        GeoKretyMap.showMouseLocation(event);
    });
    google.maps.event.addListener(GeoKretyMap.map, 'zoom_changed', function() {
            GeoKretyMap.loadGeoKrety();
        });
    google.maps.event.addListener(GeoKretyMap.map, 'dragend', function() {
            GeoKretyMap.loadGeoKrety();
        });
    var all_option =  $('#id_types_all')[0];

    },

    show_spinner: function() {
        $('#map_spinner').show();
    },

    hide_spinner: function() {
        $('#map_spinner').hide();
    },

    createIcons: function() {
    GeoKretyMap.green_kret_marker = new google.maps.MarkerImage("/static/img/kret_green.png",
        new google.maps.Size(33.0, 24.0),
        new google.maps.Point(0, 0),
        new google.maps.Point(16.0, 12.0)
    );
    GeoKretyMap.yellow_kret_marker = new google.maps.MarkerImage("/static/img/kret_yellow.png",
        new google.maps.Size(33.0, 24.0),
        new google.maps.Point(0, 0),
        new google.maps.Point(16.0, 12.0)
    );
    GeoKretyMap.red_kret_marker = new google.maps.MarkerImage("/static/img/kret_red.png",
        new google.maps.Size(33.0, 24.0),
        new google.maps.Point(0, 0),
        new google.maps.Point(16.0, 12.0)
    );
    GeoKretyMap.shadow = new google.maps.MarkerImage("/static/img/shadow-kret.png",
        new google.maps.Size(46.0, 24.0),
        new google.maps.Point(0, 0),
        new google.maps.Point(16.0, 12.0)
    );

    },


    iconByDistance: function(d, c) {
        if (d==0) {
        return GeoKretyMap.green_kret_marker;
        }
        if (d > 0 && d < 500) {
        return  GeoKretyMap.yellow_kret_marker;
        }
        if (d > 499) {
        return  GeoKretyMap.red_kret_marker;
        }


    return GeoKretyMap.green_kret_marker
    },

    shadowByDistance: function(d,c) {
    return GeoKretyMap.shadow;
    },
    drawMap: function() {


    GeoKretyMap.mc.addMarkers(GeoKretyMap.markers);
    },


    loadGeoKrety: function(o) {
    //var country_iso = $('#id_country').val();
    //if (country_iso == 'SEARCH') return;

    this.show_spinner();
    //this.clear_search()
    bounds = GeoKretyMap.map.getBounds();
    $.ajax({
            url: GeoKretyMap.get_geokrety_url,
            type: 'GET',
            dataType: 'JSON',
            data: {    'left': bounds.getSouthWest().lng(),
                    'top': bounds.getNorthEast().lat(),
                    'right': bounds.getNorthEast().lng(),
                    'bottom': bounds.getSouthWest().lat()
            },
            success: function(doc) {
                {
                    GeoKretyMap.addMarkers(doc.krety);
                    GeoKretyMap.hide_spinner();
                }
            }
        })

    },
    loadThings: function() {
        CachesMap.show_spinner();
        bounds = CachesMap.map.getBounds();
        $.ajax({
            url: CachesMap.get_things_url,
            type: 'GET',
            dataType: 'JSON',
            data: {    'left': bounds.getSouthWest().lng(),
                    'top': bounds.getNorthEast().lat(),
                    'right': bounds.getNorthEast().lng(),
                    'bottom': bounds.getSouthWest().lat()
            },
            success: function(doc) {
                {
                    CachesMap.addMarkers(doc.caches);
                    CachesMap.addConfluence(doc.points);
                    CachesMap.hide_spinner();
                }
            }
        });
    },

    addMarkers: function(krety_list) {
        //$('#id_count')[0].innerHTML = '';
    GeoKretyMap.markers = [];
    GeoKretyMap.mc.clearMarkers();
    if (!krety_list.length) return;

    var marker;
    for (var i=0;i<krety_list.length;i++) {
        marker = new google.maps.Marker({
        position: new google.maps.LatLng(krety_list[i].latitude, krety_list[i].longitude),
        map: GeoKretyMap.map,
        title: krety_list[i].waypoint,
        waypoint: krety_list[i].waypoint,
        icon: GeoKretyMap.iconByDistance(krety_list[i].distance, krety_list[i].count),
        shadow:  GeoKretyMap.shadowByDistance(krety_list[i].distance, krety_list[i].distance)
        });
        google.maps.event.addListener(marker, 'click', function () {
        GeoKretyMap.setInformationWindow(this);
        });
        GeoKretyMap.markers[GeoKretyMap.markers.length] = marker;
    }
    GeoKretyMap.mc.addMarkers(GeoKretyMap.markers);
    //$('#id_count')[0].innerHTML = gettext('found') + ': ' + krety_list.length;

    },

    centerMap: function(rectangle) {
        if ((rectangle.lat_min=='') || (rectangle.lat_max=='') || (rectangle.lng_min=='') || (rectangle.lng_max=='')) return;

        GeoKretyMap.map.setCenter(new google.maps.LatLng(
            ((rectangle.lat_max + rectangle.lat_min) / 2.0),
            ((rectangle.lng_max + rectangle.lng_min) / 2.0)
        ));

        GeoKretyMap.map.fitBounds(new google.maps.LatLngBounds(
            //bottom left
            new google.maps.LatLng( rectangle.lat_min,  rectangle.lng_min),
            //top right
            new google.maps.LatLng( rectangle.lat_max,  rectangle.lng_max)
        ));
    },

    codeAddress: function(address) {
    GeoKretyMap.geocoder.geocode( { 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
        GeoKretyMap.map.setCenter(results[0].geometry.location);
        GeoKretyMap.map.setZoom(10);
        }
    });
    },


    showMouseLocation: function(event) {
    var latlng = event.latLng;
    $('#id_current_location')[0].innerHTML = GeoKretyMap.toWGS84(1, latlng);

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
    return latD + " " + latstr + " <br/>" + lngD + " " + lngstr;
    },

    go_in: function() {
        var item_id = 'waypoint';
        this.set_search();
        if (GeoKretyMap.text_changed) { return; }
        var  item = document.getElementById(item_id)
        //item.className = css_class;
        item.value = '';
    },

    go_out: function() {
        var item_id = 'waypoint';
        var item = document.getElementById(item_id)
        GeoKretyMap.find_waypoint(item);
        if (!item.value.length) {
            item.value = GeoKretyMap.tip_text;
            GeoKretyMap.text_changed = false;
        }
    },

    find_waypoint: function(elm) {
        if (elm.substring) {
            elm = document.getElementById(elm);
        }
        var txt = elm.value;
        if (txt!=GeoKretyMap.tip_text) {
            var waypoint = txt;
            this.set_search();
            this.show_spinner();
            $.ajax({
                url: GeoKretyMap.find_by_waypoint_url,
                type: 'GET',
                dataType: 'JSON',
                data: {    'waypoint': txt },
                success: function(doc) {
                    if (doc.status != "OK") {
                        return;
                    }
                    GeoKretyMap.centerMap(doc.rect);
                    GeoKretyMap.addMarkers(doc.krety);
                    GeoKretyMap.hide_spinner();
                },
                error:  function(xhr, str){
                    alert('error: ' + xhr.responseCode);
                },
                complete:  function(){
                }
            });
        }
    },

    key_pressed_here: function(e) {
        var keycode = e.keyCode?e.keyCode:e.keyChar;
        if (keycode==13 || keycode==9) {
            return GeoKretyMap.go_out();
        }
        return false;
    },

    clear_search: function() {
        $('#waypoint').val('');
        this.go_out();
    },

    set_search: function() {
        $('#id_country').val('SEARCH');
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

