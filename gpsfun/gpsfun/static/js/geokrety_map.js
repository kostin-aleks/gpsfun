GeoKretyMap = {
    infowindow: null,
    alertwin: null,
    map: null,
    mc: null,
    geocoder: null,
    markers: [],
    marker: null,
    krety: [],
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
    MAX_COUNT: 500,
    marker_style: null,
    vectorSource: null,
    vectorLayer: null,
    popup: null,
    markers: null,
    //pruneCluster: null,
    leafletView: null,
    tip_text: '',
    only_found: false,
    geokret_waypoint: null,

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

        var HERE_hybridDay = L.tileLayer(
            'http://{s}.{base}.maps.cit.api.here.com/maptile/2.1/{type}/{mapID}/hybrid.day/{z}/{x}/{y}/{size}/{format}?app_id={app_id}&app_code={app_code}&lg={language}', {
            attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
            subdomains: '1234',
            mapID: 'newest',
            app_id: '053oEDBlB1koyGZIa8pj',
            app_code: 'eTHqVLdXEek6IDFVJlUc2A',
            base: 'aerial',
            maxZoom: 20,
            minZoom: 14,
            type: 'maptile',
            language: 'eng',
            format: 'png8',
            size: '256'
        });

        var baseMaps = {
            "OSM StreetMap": osm,
            //"HERE hybrid": HERE_hybridDay,
            "OpenTopoMap": OpenTopoMap,
        };

        var overlayMaps = {};

        L.control.layers(baseMaps, overlayMaps).addTo(map);

        L.control.scale(imperial=false).addTo(map);
        L.control.zoom().addTo(map);


        //map.on('viewreset', GeoKretyMap.loadThings);
        map.on('dragend', GeoKretyMap.loadThings);
        map.on('zoomend', GeoKretyMap.loadThings);


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
        GeoKretyMap.loadThings();

    },

    show_spinner: function() {
        $('#map_spinner').show();
    },

    hide_spinner: function() {
        $('#map_spinner').hide();
    },

    createIcons: function() {
        GeoKretyMap.green_kret_marker = L.icon({
            iconUrl: "/static/img/kret_green.png",
            shadowUrl: "/static/img/shadow-kret.png",
            iconSize:     [33.0, 24.0],
            shadowSize:   [46.0, 24.0],
            iconAnchor:   [0, 0],
            shadowAnchor: [0, 0],
            popupAnchor:  [16, 12]
            }
        );

        GeoKretyMap.yellow_kret_marker = L.icon({
            iconUrl: "/static/img/kret_yellow.png",
            shadowUrl: "/static/img/shadow-kret.png",
            iconSize:     [33.0, 24.0],
            shadowSize:   [46.0, 24.0],
            iconAnchor:   [0, 0],
            shadowAnchor: [0, 0],
            popupAnchor:  [16, 12]
            }
        );

        GeoKretyMap.red_kret_marker = L.icon({
            iconUrl: "/static/img/kret_red.png",
            shadowUrl: "/static/img/shadow-kret.png",
            iconSize:     [33.0, 24.0],
            shadowSize:   [46.0, 24.0],
            iconAnchor:   [0, 0],
            shadowAnchor: [0, 0],
            popupAnchor:  [16, 12]
            }
        );

        GeoKretyMap.default_marker = L.icon({
            iconUrl: '/static/img/green_bulb.png',
            shadowUrl: '/static/img/shadow-bulb.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [39.0, 34.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

    },

    iconByType: function() {
        return GeoKretyMap.default_marker
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
    },

    showAlert: function(count) {
        var bounds = GeoKretyMap.map.getBounds();
        var lat = (3*bounds.getNorthEast().lat + 2*bounds.getSouthWest().lat)/5.0;
        var lon = (bounds.getSouthWest().lng + bounds.getNorthEast().lng)/2.0
        GeoKretyMap.alertwin.setContent(gettext('Only first ')+ count +
                gettext(' geocaches are shown on the map. <br/>Please magnify the view to display all geocaches.'));
        GeoKretyMap.alertwin.setLatLng([lat, lon])
        GeoKretyMap.alertwin.openOn(GeoKretyMap.map);
    },

    hideAlert: function(count) {
       GeoKretyMap.map.closePopup(GeoKretyMap.alertwin);
    },

    getMapBounds: function() {
        return GeoKretyMap.map.getBounds();
        },

    getCenter: function() {
        return GeoKretyMap.map.getCenter();
    },

    loadThings: function() {
        GeoKretyMap.hideAlert();
        GeoKretyMap.clear_search()
        bounds = GeoKretyMap.getMapBounds();
        map_center = GeoKretyMap.getCenter();

        if (!GeoKretyMap.only_found) {
            GeoKretyMap.show_spinner();
            $.ajax({
                url: GeoKretyMap.get_things_url,
                type: 'GET',
                dataType: 'JSON',
                data: {
                    'left': bounds.getWest(),
                    'top': bounds.getNorth(),
                    'right': bounds.getEast(),
                    'bottom': bounds.getSouth(),
                    'center_lat': map_center.lat,
                    'center_lng': map_center.lng,
                    'zoom': GeoKretyMap.map.getZoom(),
                },
                success: function(doc) {
                    GeoKretyMap.removeAllMarkers();
                    GeoKretyMap.hide_spinner();
                    GeoKretyMap.showFound(doc.count);

                    if (doc.count > GeoKretyMap.MAX_COUNT) {
                        GeoKretyMap.showAlert(doc.count);
                    } else {
                        GeoKretyMap.hideAlert();
                        GeoKretyMap.krety = doc.krety;
                        GeoKretyMap.addMarkers(GeoKretyMap.krety);
                    }
                    GeoKretyMap.addMarker();
                }
            });
        }
    },


    removeAllMarkers: function () {
        GeoKretyMap.leafletView.RemoveMarkers();
    },

    addMarkers: function(krety_list) {
        GeoKretyMap.removeAllMarkers();

        if (!krety_list.length) {GeoKretyMap.hide_spinner(); return;}
        for (var i = 0; i < krety_list.length; ++i) {
            var kret = krety_list[i];

            var marker = new PruneCluster.Marker(
                kret.latitude,
                kret.longitude,
                {
                    popup: kret.content,
                    icon: GeoKretyMap.iconByDistance(kret.distance)
                });

            GeoKretyMap.leafletView.RegisterMarker(marker);
        }

        GeoKretyMap.map.addLayer(GeoKretyMap.leafletView);

    },

    addMarker: function() {
        if (GeoKretyMap.geokret_waypoint) {
           if (GeoKretyMap.marker != undefined) {
                GeoKretyMap.map.removeLayer(GeoKretyMap.marker)
            }
            GeoKretyMap.marker = new L.marker([
                GeoKretyMap.geokret_waypoint.lat,
                GeoKretyMap.geokret_waypoint.lng]).addTo(GeoKretyMap.map);
        }
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

    showFound: function(cnt) {
        var txt = '';
        txt = gettext("found:") + ' ' + cnt;
        document.getElementById('id_count').innerHTML = txt;
    },

    go_in: function() {
        var item_id = 'waypoint';
        if (GeoKretyMap.text_changed) { return; }
        var  item = document.getElementById(item_id)
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
            this.show_spinner();
            $.ajax({
                url: GeoKretyMap.find_by_waypoint_url,
                type: 'GET',
                dataType: 'JSON',
                data: {'waypoint': txt},
                success: function(doc) {
                    if (doc.status != "OK") {
                        return;
                    }
                    GeoKretyMap.centerMap(doc.rect);
                    GeoKretyMap.addMarkers(doc.krety);
                    GeoKretyMap.geokret_waypoint = null;
                    if (doc.kret_waypoint) {
                        GeoKretyMap.geokret_waypoint = doc.kret_waypoint;
                    }
                    GeoKretyMap.addMarker();
                    GeoKretyMap.hide_spinner();
                },
                error:  function(xhr, str){
                    alert('error: ' + xhr.responseCode);
                },
                complete:  function(){
                }
            });
        } else {}
    },

    centerMap: function(rectangle) {
        if (rectangle == []) return;
        if ((rectangle.lat_min=='') || (rectangle.lat_max=='') || (rectangle.lng_min=='') || (rectangle.lng_max=='')) return;

        GeoKretyMap.map.fitBounds([
            [rectangle.lat_min, rectangle.lng_min],
            [rectangle.lat_max, rectangle.lng_max]
        ]);
    },

    set_found: function() {
        GeoKretyMap.only_found = true;
    },

    reset_found: function() {
        GeoKretyMap.only_found = false;
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
        // this.go_out();
    },

}



