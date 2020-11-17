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
    only_found: false,


    init: function(center, zoom) {
        osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
        var map = L.map("map", {
            attributionControl: false,
            zoomControl: false
        }).setView(center, zoom);

        osm = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            detectRetina: true,
            maxNativeZoom: 17,
            maxZoom: 18,
            attribution: osmAttrib
        }).addTo(map);


        OpenTopoMap = L.tileLayer('http://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 17,
            attribution: 'Map data: &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
        }).addTo(map);


        var baseMaps = {
            "OSM StreetMap": osm,
            "OpenTopoMap": OpenTopoMap,
        };

        var overlayMaps = {};

        L.control.layers(baseMaps, overlayMaps).addTo(map);

        L.control.scale(imperial=false).addTo(map);
        L.control.zoom().addTo(map);


        map.on('moveend', GeoKretyMap.loadGeoKrety);
        map.on('zoomend', GeoKretyMap.loadGeoKrety);

        new L.control.mousePosition({
            lngFormatter: function(lng) { return GeoKretyMap.to_string(lng, ['E', 'W']);},
            latFormatter: function(lat) { return GeoKretyMap.to_string(lat, ['N', 'S']);},
            separator: '&nbsp;'
        }).addTo(map);

        new L.Control.GeoSearch({
            provider: new L.GeoSearch.Provider.OpenStreetMap()
        }).addTo(map);

        GeoKretyMap.map = map;

        GeoKretyMap.alertwin = L.popup({
            closeOnClick: true,
            })
            .setLatLng(center)
            .setContent('')


        GeoKretyMap.createIcons();

        GeoKretyMap.leafletView = new PruneClusterForLeaflet();
        GeoKretyMap.reset_found();
        GeoKretyMap.loadGeoKrety();


    },

    show_spinner: function() {
        $('#map_spinner').show();
    },

    hide_spinner: function() {
        $('#map_spinner').hide();
    },

    createIcons: function() {
        GeoKretyMap.green_kret_marker = L.icon({
            iconUrl: '/static/img/kret_green.png',
            shadowUrl: '/static/img/shadow-kret.png',

            iconSize:     [33.0, 24.0], // size of the icon
            shadowSize:   [46.0, 24.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [16, 12] // point from which the popup should open relative to the iconAnchor
        });

        GeoKretyMap.yellow_kret_marker = L.icon({
            iconUrl: '/static/img/kret_yellow.png',
            shadowUrl: '/static/img/shadow-kret.png',

            iconSize:     [33.0, 24.0], // size of the icon
            shadowSize:   [46.0, 24.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [16, 12] // point from which the popup should open relative to the iconAnchor
        });

        GeoKretyMap.red_kret_marker = L.icon({
            iconUrl: '/static/img/kret_red.png',
            shadowUrl: '/static/img/shadow-kret.png',

            iconSize:     [33.0, 24.0], // size of the icon
            shadowSize:   [46.0, 24.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [16, 12] // point from which the popup should open relative to the iconAnchor
        });
    },

    iconByDistance: function(d) {
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

    shadowByDistance: function() {
        return GeoKretyMap.shadow;
    },

    drawMap: function() {
        GeoKretyMap.mc.addMarkers(GeoKretyMap.markers);
    },

    getMapBounds: function() {
        return GeoKretyMap.map.getBounds();
    },

    getCenter: function() {
        return GeoKretyMap.map.getCenter();
    },

    loadGeoKrety: function(o) {
        //var country_iso = $('#id_country').val();
        //if (country_iso == 'SEARCH') return;
        GeoKretyMap.show_spinner();
        //this.clear_search()
        bounds = GeoKretyMap.getMapBounds();
        map_center = GeoKretyMap.getCenter();
        $.ajax({
            url: GeoKretyMap.get_geokrety_url,
            type: 'GET',
            dataType: 'JSON',
            data: { 'left': bounds.getSouthWest().lng,
                    'top': bounds.getNorthEast().lat,
                    'right': bounds.getNorthEast().lng,
                    'bottom': bounds.getSouthWest().lat
            },
            success: function(doc) {
                {
                    GeoKretyMap.addMarkers(doc.krety);
                    GeoKretyMap.hide_spinner();
                }
            }
        })

    },

    removeAllMarkers: function () {
        GeoKretyMap.leafletView.RemoveMarkers();
    },

    addMarkers: function(krety_list) {
        //$('#id_count')[0].innerHTML = '';
        GeoKretyMap.markers = [];
        GeoKretyMap.removeAllMarkers();
        if (!krety_list.length) return;

        for (var i = 0; i < krety_list.length; ++i) {
            var item= krety_list[i];
            var marker = new PruneCluster.Marker(
                item.latitude,
                item.longitude,
                {
                    popup: item.content,
                    icon: GeoKretyMap.iconByDistance(item.distance)
                });

            GeoKretyMap.leafletView.RegisterMarker(marker);
        }

        GeoKretyMap.map.addLayer(GeoKretyMap.leafletView);
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

    toWGS84: function(type_, latlng) {
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
    },

    reset_found: function() {
        GeoKretyMap.only_found = false;
    },

    to_string: function(x, signs) {
        var D = signs[0];
        if(x < 0) {
            x = -x;
            D = signs[1];
        }

        var degs = x | 0;
        var minutes = ((x - degs)*60);
        var s = degs + "° " + minutes.toFixed(3) + "'";
        return D + " " + s;
    },

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

