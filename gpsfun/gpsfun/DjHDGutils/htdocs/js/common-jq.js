/*
 * Support for CSRF validation
 * From Django https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
 */
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

/*
 * wrapper on response to work in pair with @accept_ajax decorator
 * 
 */
/*
$(document).ajaxComplete(function(event, xhr, settings) {
    function _write_debug(msg) {
        var _window = window.open("","debug","scrollbars,width=1024,height=800");
        _window.focus();
        _window.document.write(msg);
        _window.document.close();
    }

    try {
        result = jQuery.parseJSON(xhr.responseText);
    } catch(e) {
        return;
    };
    if (result.status && result.status == 500) {
        if (result.debug) {
            _write_debug(result.debug_msg);
        } else {
            alert("Unexpected error while communication with server");    
        }
    }
});
*/

jQuery.extend({'hdg': {}});

(function($, ns) {
     function _write_debug(msg) {
         var _window = window.open("","debug","scrollbars,width=1024,height=800");
         _window.focus();
         _window.document.write(msg);
         _window.document.close();
     }

     function _json_callback(orginal_cb) {
         function _wrapper(data, status, jqXHR) {
             if (data.status && data.status == 500) {
                 if (data.debug) {
                     _write_debug(data.debug_msg);
                 } else {
                     alert("Unexpected error while communication with server");    
                 }
                 return;
             }
             orginal_cb(data, status, jqXHR);
         }
         return _wrapper;
     }

     function getJson(url, data, callback, callback_error) {
         return jQuery.ajax({type: 'GET',
			                 url: url,
			                 data: data,
                             cache: false,
                             headers: {'If-Modified-Since': 'Sat, 1 Jan 2000 00:00:00 GMT'},
			                 success: _json_callback(callback),
                             error: callback_error,
			                 dataType: 'json'
		                    }); 
     }
     ns.getJson = getJson;

     function postJson(url, data, callback, callback_error) {
         return jQuery.ajax({type: 'POST',
			                 url: url,
			                 data: data,
                             cache: false,
                             headers: {'If-Modified-Since': 'Sat, 1 Jan 2000 00:00:00 GMT'},
			                 success: _json_callback(callback),
                             error: callback_error,
			                 dataType: 'json'
		                    }); 
     }
     ns.postJson = postJson;

     

})(jQuery, jQuery.hdg);



(function($, ns) {
     var current_layer;

     function get(element) {
         var _elem = $(element);
         return _elem;

         if (typeof(_elem) == 'object' && _elem.length && _elem.length > 0) {
             _elem = _elem[0];
         }
         return _elem;
     };

     function position(element, options) {
         /* 
          * options:
          *   relative - relative object for position to
          *   v        - vertical alignment: 
          *   h        - horizontal alignment:
          *   shift    - for target element
          */
          
         var _elem = get(element);
         var _rel = get(options.relative || window);
         var _options = options || {};
         
         var _vertical = options.v || 'center';
         var _horizontal = options.v || 'center';
         
         var _pos = {top: 0, left: 0};
         try {
             var _rel_pos = _rel.position();
         } catch (e) {
             var _rel_pos = {top: 0, left: 0};
         };
         

        switch (_options.v) {
        case 'under':
            _pos.top = _rel_pos.top + _rel.height() + (_options.shift || 1);
            break;
        case 'above':
            _pos.top = _rel_pos.top - _elem.height() + (_options.shift || 1);
            break;

        default:
            // center
            _pos.top = _rel_pos.top + _rel.height()/2 - _elem.height()/2;
            break;
        }

        switch (_options.h) {
        case 'rifht':
            _pos.left = _rel_pos.left + _rel.width() - _elem.width();
            break;
        case 'left':
            _pos.left = _rel_pos.left;
            break;

        default:
            // center
            _pos.top = _rel_pos.left + _rel.width()/2 - _elem.width()/2;
            break;
        }

         if (_pos.left + _elem.width() + 5 > get(window).width()) {
             _pos.left = get(window).width() - _elem.width() - 5;
         }
         
         if (_pos.left < 5) {
             _pos.left = 5;
         }

         _elem.css('top', _pos.top);
         _elem.css('left', _pos.left);
         return _elem;
     };
     ns.show = position;

     function show(element, options) {
         var _elem = get(element);
         var _options = options || {};
         
         if (current_layer == _elem) {
             return _elem;
         }

         if (_options.exclusive && current_layer) {
             hide(current_layer);
         }
         
         if (_options.relative) {
             position(_elem, options);
         }
         
         current_layer = _elem;
         
         return _elem.show();
     };
     
     ns.show = show;

/*
     _Layer = function(element_path) {
         this.layer = $(element_path).first();
     };

     _Layer.prototype.show = function() {
     };

     _Layer.prototype.hide = function() {
     };
*/

})(jQuery, jQuery.hdg);
