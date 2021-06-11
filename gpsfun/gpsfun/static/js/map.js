CachesMap = {
    infowindow: null,
    alertwin: null,
    map: null,
    mc: null,
    geocoder: null,
    markers: [],
    caches: [],
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
    MAX_COUNT: 1000,
    marker_style: null,
    vectorSource: null,
    vectorLayer: null,
    popup: null,
    markers: null,
    //pruneCluster: null,
    leafletView: null,
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
            "HERE hybrid": HERE_hybridDay,
            "OpenTopoMap": OpenTopoMap,
        };

        var overlayMaps = {};

        L.control.layers(baseMaps, overlayMaps).addTo(map);

        L.control.scale(imperial=false).addTo(map);
        L.control.zoom().addTo(map);


        map.on('viewreset', CachesMap.loadThings);
        map.on('zoomend', CachesMap.loadThings);
        map.on('dragend', CachesMap.loadThings);

        new L.control.mousePosition({
            lngFormatter: function(lng) { return CachesMap.to_string(lng, ['E', 'W']);},
            latFormatter: function(lat) { return CachesMap.to_string(lat, ['N', 'S']);},
            separator: '&nbsp;'
        }).addTo(map);

        new L.Control.GeoSearch({
            provider: new L.GeoSearch.Provider.OpenStreetMap()
        }).addTo(map);

        CachesMap.map = map;

        CachesMap.alertwin = L.popup({
            closeOnClick: true,
            })
            .setLatLng(center)
            .setContent('')


        CachesMap.createIcons();

        CachesMap.leafletView = new PruneClusterForLeaflet();
        CachesMap.reset_found();
        CachesMap.loadThings();

    },

    show_spinner: function() {
        $('#map_spinner').show();
    },

    hide_spinner: function() {
        $('#map_spinner').hide();
    },

    createIcons: function() {
        CachesMap.default_marker = L.icon({
            iconUrl: '/static/img/green_bulb.png',
            shadowUrl: '/static/img/shadow-bulb.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [39.0, 34.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageTR = L.icon({
            iconUrl: '/static/img/su_tr_bulb.png',
            shadowUrl: '/static/img/shadow-su_tr.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [39.0, 34.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageTR = L.icon({
            iconUrl: '/static/img/su_tr_bulb.png',
            shadowUrl: '/static/img/shadow-su_tr.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [39.0, 34.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageVI = L.icon({
            iconUrl: '/static/img/su_vi_bulb.png',
            shadowUrl: '/static/img/shadow-su_vi.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [31.0, 20.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageMS = L.icon({
            iconUrl: '/static/img/su_ms_bulb.png',
            shadowUrl: '/static/img/shadow-su_ms1.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [31.0, 20.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageMV = L.icon({
            iconUrl: '/static/img/su_mv_bulb.png',
            shadowUrl: '/static/img/shadow-su_mv.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [31.0, 20.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageMV = L.icon({
            iconUrl: '/static/img/su_mv_bulb.png',
            shadowUrl: '/static/img/shadow-su_mv.png',

            iconSize:     [21.0, 34.0], // size of the icon
            shadowSize:   [31.0, 20.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageH = L.icon({
            iconUrl: '/static/img/tajnik24.png',
            shadowUrl: '/static/img/shadow-tajnik24.png',

            iconSize:     [26.0, 26.0], // size of the icon
            shadowSize:   [40.0, 26.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageP = L.icon({
            iconUrl: '/static/img/dost32.png',
            shadowUrl: '/static/img/shadow-dost32.png',

            iconSize:     [26.0, 26.0], // size of the icon
            shadowSize:   [40.0, 26.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageQ = L.icon({
            iconUrl: '/static/img/quest24.png',
            shadowUrl: '/static/img/shadow-quest24.png',

            iconSize:     [26.0, 26.0], // size of the icon
            shadowSize:   [40.0, 26.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageC = L.icon({
            iconUrl: '/static/img/casket24.png',
            shadowUrl: '/static/img/shadow-casket24.png',

            iconSize:     [24.0, 24.0], // size of the icon
            shadowSize:   [37.0, 24.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageCon = L.icon({
            iconUrl: '/static/img/confluence24.png',
            shadowUrl: '/static/img/shadow-confluence24.png',

            iconSize:     [24.0, 24.0], // size of the icon
            shadowSize:   [37.0, 24.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageG = L.icon({
            iconUrl: '/static/img/benchmark24.png',
            shadowUrl: '/static/img/shadow-benchmark24.png',
            iconSize:     [24.0, 24.0], // size of the icon
            shadowSize:   [37.0, 24.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOPTR = L.icon({
            iconUrl: '/static/img/traditional-s.png',
            shadowUrl: '/static/img/shadow-op-tr.png',
            iconSize:     [32.0, 32.0], // size of the icon
            shadowSize:   [49.0, 32.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOPMS = L.icon({
            iconUrl: '/static/img/multi-s.png',
            shadowUrl: '/static/img/shadow-op-ms.png',
            iconSize:     [32.0, 32.0], // size of the icon
            shadowSize:   [49.0, 32.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageQZ = L.icon({
            iconUrl: '/static/img/quiz-s.png',
            shadowUrl: '/static/img/shadow-op-qz.png',
            iconSize:     [32.0, 32.0], // size of the icon
            shadowSize:   [49.0, 32.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOT = L.icon({
            iconUrl: '/static/img/unknown-s.png',
            shadowUrl: '/static/img/shadow-op-other.png',
            iconSize:     [32.0, 32.0], // size of the icon
            shadowSize:   [49.0, 32.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageMOV = L.icon({
            iconUrl: '/static/img/moving-s.png',
            shadowUrl: '/static/img/shadow-op-mv.png',
            iconSize:     [32.0, 32.0], // size of the icon
            shadowSize:   [49.0, 32.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOPVI = L.icon({
            iconUrl: '/static/img/virtual-s.png',
            shadowUrl: '/static/img/shadow-op-vi.png',
            iconSize:     [32.0, 32.0], // size of the icon
            shadowSize:   [49.0, 32.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOCTR = L.icon({
            iconUrl: '/static/img/occom_tr.png',
            shadowUrl: '/static/img/shadow-occom.png',
            iconSize:     [24.0, 30.0], // size of the icon
            shadowSize:   [40.0, 30.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOCMS = L.icon({
            iconUrl: '/static/img/occom_ms.png',
            shadowUrl: '/static/img/shadow-occom.png',
            iconSize:     [24.0, 30.0], // size of the icon
            shadowSize:   [40.0, 30.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOCQZ = L.icon({
            iconUrl: '/static/img/occom_qz.png',
            shadowUrl: '/static/img/shadow-occom.png',
            iconSize:     [24.0, 30.0], // size of the icon
            shadowSize:   [40.0, 30.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

        CachesMap.imageOCVI = L.icon({
            iconUrl: '/static/img/occom_vi.png',
            shadowUrl: '/static/img/shadow-occom.png',
            iconSize:     [24.0, 30.0], // size of the icon
            shadowSize:   [40.0, 30.0], // size of the shadow
            iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [10, 0] // point from which the popup should open relative to the iconAnchor
        });

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

    showAlert: function(count) {
        var bounds = CachesMap.map.getBounds();
        var lat = (3*bounds.getNorthEast().lat + 2*bounds.getSouthWest().lat)/5.0;
        var lon = (bounds.getSouthWest().lng + bounds.getNorthEast().lng)/2.0
        CachesMap.alertwin.setContent(gettext('There are ')+ count +
                gettext('  geocaches on the map. <br/>Please magnify the view to display the geocaches.'));
        CachesMap.alertwin.setLatLng([lat, lon])
        CachesMap.alertwin.openOn(CachesMap.map);
    },

    hideAlert: function(count) {
       CachesMap.map.closePopup(CachesMap.alertwin);
    },

    getMapBounds: function() {
        return CachesMap.map.getBounds();
        },

    getCenter: function() {
        return CachesMap.map.getCenter();
    },

    loadThings: function() {
        CachesMap.hideAlert();
        bounds = CachesMap.getMapBounds();
        map_center = CachesMap.getCenter();

        if (!CachesMap.only_found) {
            CachesMap.show_spinner();
            $.ajax({
                url: CachesMap.get_things_url,
                type: 'GET',
                dataType: 'JSON',
                data: {
                    'left': bounds.getWest(),
                    'top': bounds.getNorth(),
                    'right': bounds.getEast(),
                    'bottom': bounds.getSouth(),
                    'center_lat': map_center.lat,
                    'center_lon': map_center.lon,
                    'zoom': CachesMap.map.getZoom(),
                },
                success: function(doc) {
                    CachesMap.removeAllMarkers();
                    CachesMap.hide_spinner();
                    CachesMap.showFound(doc.count);
                    if (doc.count > CachesMap.MAX_COUNT) {
                        CachesMap.showAlert(doc.count);
                    } else {
                        CachesMap.hideAlert();
                        CachesMap.caches = doc.caches;
                        CachesMap.addMarkers(CachesMap.caches);
                    }
                }
            });
        }
    },

    showCacheTypes: function(o) {
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
            data: {'type': type_selected},

            success: function(doc) {
                if (doc.status != "OK") { return;}
                CachesMap.reset_found();
                CachesMap.loadThings();
            }
        })
    },


    removeAllMarkers: function () {
        CachesMap.leafletView.RemoveMarkers();
    },

    addMarkers: function(caches_list) {
        if (!caches_list.length) return;

        CachesMap.removeAllMarkers();

        for (var i = 0; i < caches_list.length; ++i) {
            var cache = caches_list[i];
            var marker = new PruneCluster.Marker(
                cache.latitude_degree,
                cache.longitude_degree,
                {
                    popup: cache.content,
                    icon: CachesMap.iconByType(cache.site_code, cache.type_code)
                });

            CachesMap.leafletView.RegisterMarker(marker);
        }

        CachesMap.map.addLayer(CachesMap.leafletView);

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
        this.set_search();
        if (CachesMap.text_changed) { return; }
        var  item = document.getElementById(item_id)
        item.value = '';
    },

    go_out: function() {
        var item_id = 'waypoint';
        var item = document.getElementById(item_id)
        CachesMap.find_waypoint(item);
        if (!item.value.length) {
            item.value = CachesMap.tip_text;
            CachesMap.text_changed = false;
        }
    },

    find_waypoint: function(elm) {
        if (elm.substring) {
            elm = document.getElementById(elm);
        }
        var txt = elm.value;
        if (txt.length && txt != CachesMap.tip_text ) {
            var waypoint = txt;
            this.set_found();
            this.show_spinner();
            $.ajax({
                url: CachesMap.find_by_waypoint_url,
                type: 'GET',
                dataType: 'JSON',
                data: {'waypoint': txt},

                success: function(doc) {
                    if (doc.status != "OK") {
                        return;
                    }

                    CachesMap.removeAllMarkers();
                    CachesMap.centerMap(doc.rect);
                    CachesMap.caches = doc.caches;
                    CachesMap.addMarkers(doc.caches);
                    CachesMap.hide_spinner();
                    CachesMap.showFound(doc.caches.length);
                },

                error:  function(xhr, str){
                    alert('error: ' + xhr.responseCode);
                },
                complete:  function(){
                }
            });
        } else {
            CachesMap.reset_found();
            CachesMap.loadThings();
        }
    },

    centerMap: function(rectangle) {
        if (rectangle == []) return;
        if ((rectangle.lat_min=='') || (rectangle.lat_max=='') || (rectangle.lng_min=='') || (rectangle.lng_max=='')) return;

        CachesMap.map.fitBounds([
            [rectangle.lat_min, rectangle.lng_min],
            [rectangle.lat_max, rectangle.lng_max]
        ]);
    },

    set_found: function() {
        CachesMap.only_found = true;
    },

    reset_found: function() {
        CachesMap.only_found = false;
    }
}



