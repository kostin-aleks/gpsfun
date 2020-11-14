Layer = {
    current_opened_layer: false,
    click_handler: false,
    defered: null,


    is_ie6: function() {
        return (navigator.userAgent.toLowerCase().indexOf('msie 6') != -1) || (navigator.userAgent.toLowerCase().indexOf('msie 7.0') != -1);
    },
    
    show_row_layer: function(layer_id) {
        if (!Layer.is_ie6()) {
            setDisplayForElement('table-row', layer_id);
            appear(layer_id, {'duration': 1.5});
        } else {
            setDisplayForElement('block', layer_id);
            showElement(layer_id);
        }            
        
    },    

    /*
     * Do position one later related to another layer
     * 
     * align - object with two property:
     *          align.h - horizontal -> 'above', 'under'
     *          align.v - vertial -> 'left', 'center', right'
     *         
     *          default behavior = left + under
     */
    set_position: function(layer_id, positional_obj, align) {
        var layer = getElement(layer_id);
        var pos_relative = getElementPosition(positional_obj);
        var pos = Coordinates(0,0);
        var dim = getElementDimensions(positional_obj);
        var layer_dim = getElementDimensions(layer);
        var viewport_dim = getViewportDimensions();
        var viewport_pos = getViewportPosition();

        if (!align) {
            align = {v: 'under',
                     h: 'right'};
        }
        pos.x = parseInt(getStyle(layer, 'top'));
        pos.y = parseInt(getStyle(layer, 'left'));

        switch (align.v) {
        case 'under':
            pos.y = pos_relative.y + dim.h + 1;
            break;
        case 'above':
            pos.y = pos_relative.y - layer_dim.h + 1;
            break;
        case 'center':
            pos.y = viewport_pos.y + viewport_dim.h/2 - layer_dim.h/2 ;
            break;
        }
        
        switch (align.h) {
        case 'right':
            pos.x = pos_relative.x + dim.w - layer_dim.w;
            break;
        case 'left':
            pos.x =  pos_relative.x + viewport_pos.x;
            break;
        case 'center':
            pos.x = viewport_dim.w/2 - layer_dim.w/2;
            break;
            
            
        }
        
        if (layer_dim.w + pos.x + 5 - viewport_pos.x > viewport_dim.w) {
            pos.x = viewport_dim.w - 50 - layer_dim.w + viewport_pos.x;
        }

        if (pos.x < 5) {
            pos.x = 5;
        }

        setElementPosition(layer, pos);
    },
    
    show: function(layer_id, positional_obj, align, skip_onclick) {
        var layer = getElement(layer_id);

        if (Layer.current_opened_layer && Layer.current_opened_layer != layer) {
            Layer.hide(Layer.current_opened_layer);
        }
        
        if (Layer.current_opened_layer == layer) {
            return Layer.defered;     
        }
        
        Layer.defered = new Deferred();

        if (positional_obj) {
            Layer.set_position(layer_id, positional_obj, align);
        }
        showElement(layer);
        Layer.current_opened_layer = layer;
        if (!skip_onclick)
            callLater(0, Layer.setup_onclick);
        signal(Layer, 'show_layer', layer);

        return Layer.defered;
    },
    
    hide: function(obj) {
        hideElement(obj);
        Layer.current_opened_layer = false;
        Layer.remove_onclick();
        if (Layer.defered) {
            Layer.defered.callback();
            Layer.defered = null;
        }
        signal(Layer, 'hide_layer', getElement(obj));
    },
    
    toggle_display : function(layer_id, positional_obj, align) {
        var layer = getElement(layer_id);
        var current = Layer.current_opened_layer;
        
        if (Layer.current_opened_layer) {
            Layer.hide(Layer.current_opened_layer);
            if (layer != current) {
                // force open layer when request toggle while another layer was opened
                return Layer.show(layer_id, positional_obj, align);    
            }  
            return null;
        } else {
            return Layer.show(layer_id, positional_obj, align);
        }
    },


    setup_onclick: function() {
        Layer.click_handler = connect(window, 'onclick', Layer.onclick);
    },

    remove_onclick: function() {
        if (Layer.click_handler) {
            disconnect(Layer.click_handler); 
        }
    },

    onclick: function(event) {
        if (event.target() != Layer.current_opened_layer && !isChildNode(event.target(), Layer.current_opened_layer) ) {
            Layer.hide(Layer.current_opened_layer);
            event.stop();
        }

    },

    create_layer: function(layer_id, layer_class) {
        var doc = currentDocument();
        
        if (!layer_class) {
            layer_class = "layer_widget";
        }
        
        
        var layer_div = DIV({'class': layer_class,
                             'id': layer_id}); 
        
        appendChildNodes(doc.body, layer_div);
        
        return layer_div;

    },

    get_or_create_layer: function(layer_id, layer_class) {
        var layer = getElement(layer_id);
        
        if (!layer) {
            return Layer.create_layer(layer_id, layer_class);
        }
        
        return layer;
        
    }
    
};


Ajax = {
    /*
     Ajax utility for django
     
     Functions:
     load_json        - load json document with additional GET argument action=load_json  
     load_html        - expect for DjHDGutils.accept_ajax decorator on view;
     support debugging through popup window when 500 error occured
     
     load_select_list - perform load list with options for <select> html object;
     Primary it designet to load <select> items list when it depend on
     choice in other select list;
     
     Example of using load_select_list together with django forms
     class TextForm(forms.Form):
     category    = forms.ChoiceField(widget=forms.Select(attrs={'onchange': mark_safe("Ajax.load_select_list(this, 'id_subcategory', 'load_subcategory', '');")}))
     subcategory = forms.ChoiceField()
     */   
    debug_window: null,

    /* https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#using-csrf
     * 
     */
    getCookie: function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = strip(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    sameOrigin: function(_url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        var url = _url.toString();
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    },

    safeMethod: function(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    },
    /* END
     * 
     */

    get_headers: function(url, other_headers) {
        var _headers = {'If-Modified-Since': 'Sat, 1 Jan 2000 00:00:00 GMT'};
        
        if (Ajax.sameOrigin(url)) {
            _headers['X-CSRFToken'] = Ajax.getCookie('csrftoken');
        };
        return update(_headers, other_headers);
    },

    _write_debug: function(msg) {
        if (!Ajax.debug_window) {
            Ajax.debug_window = window.open("","debug","scrollbars,width=1024,height=800");
        }
        Ajax.debug_window.focus();
        Ajax.debug_window.document.write(msg);
        Ajax.debug_window.document.close();
    },

    load_json: function(url, args) {
        var _args = args || {};

        if (typeof(_args) == 'object' && !_args.action) {
            _args['action'] = 'load_json';
        } else if(typeof(_args) == 'string') {
            // this give ability so send request with predefined string as query
            _args = parseQueryString(_args);
        }

        var base_df = new Deferred();     
        
        var df = doXHR(url, {'method': 'GET',
                             'headers': Ajax.get_headers(url),
                             'queryString': _args 
                            });
        df.addCallback(function(resp) {
                           doc = evalJSONRequest(resp);
                           if (!doc.status || doc.status != 500) {
                               return base_df.callback(doc);
                           } else if (doc.status == 500) {
                               if (doc.debug) {
                                   logError(doc.debug_msg);
                                   Ajax._write_debug(doc.debug_msg);
                               } else {
                                   alert("Unexpected error while communication with server");    
                               }
                           }
                           return base_df.errback(doc.status);
                       });
        df.addErrback(function(error) {
                          return base_df.errback(error);
                      });
        
        return base_df;
    },

    load_xhr: function(url, content, headers, args) {
        var _args = args || {};
        

        if (typeof(_args) == 'string') {
            // this give ability so send request with predefined string as query
            _args = parseQueryString(_args, true);
        }
        var _headers = update(Ajax.get_headers(url, headers),
                              {'Content-Type': 'application/x-www-form-urlencoded'});

        var base_df = new Deferred();
        var df = doXHR(url, 
                       {'method': 'POST',
                        'headers': _headers,
                        'sendContent': content,
                        'queryString': _args 
                       });
        
        df.addCallback(function(resp) {
                           doc = evalJSONRequest(resp);
                           if (!doc.status || doc.status != 500) {
                               return base_df.callback(doc);
                           } else if (doc.status == 500) {
                               if (doc.debug) {
                                   logError(doc.debug_msg);
                                   Ajax._write_debug(doc.debug_msg);
                               } else {
                                   alert("Unexpected error while communication with server");    
                               }
                           }
                           return base_df.errback(doc.status);
                       });
        df.addErrback(function(error) {
                          return base_df.errback(error);
                      });
        
        return base_df;
    },

    load_html: function(url, args) {
        var base_df = new Deferred();     
        
        var df = doXHR(url, {'method': 'GET',
                             'headers': Ajax.get_headers(url),
                             'queryString': args 
                            });
        df.addCallback(function(resp) {
                           doc = evalJSONRequest(resp);
                           if (doc.status == 200) {
                               return base_df.callback(doc.content);
                           } else if (doc.status == 500) {
                               if (doc.debug) {
                                   logError(doc.debug_msg);
                                   Ajax._write_debug(doc.debug_msg);
                               } else {
                                   alert("Unexpected error while communication with server");    
                               }
                           }
                           return base_df.errback(doc.status);
                       });
        df.addErrback(function(error) {
                          return base_df.errback(error);
                      });
        
        return base_df;
        
    },

    load_select_list: function(obj, target_id, action, url, select_default) {
        var target = getElement(target_id);

        if (!obj.value) {
            replaceChildNodes(target);
            appendChildNodes(target,OPTION({'value':''}, '---------'));
        } else {
            df = Ajax.load_json(url, {'function': action,
                                      value: obj.value});
            df.addCallback(
                function(doc) {
                    replaceChildNodes(target);
                    appendChildNodes(target,OPTION({'value':''}, '---------'));

                    forEach(doc, function(item) {
                                option_node = OPTION({'value': item.value}, item.label);
                                if (doc.length==1 && select_default) {
                                    setNodeAttribute(option_node, 'selected', 'selected');
                                    target.value = item.value;
                                }
                                appendChildNodes(target, option_node);
                            });
                    
                }
            );
            

        }
    },
    
    set_form_handler: function(form, callback) {
        /*
         * Set common handlers for all submit input and buttons inside form
         *  
         */
        forEach(getElementsByTagAndClassName('input', null, form),
                function(item) {
                    if (item.type == 'submit') {
                        connect(item, 'onclick', callback);
                    }
                });
        forEach(getElementsByTagAndClassName('button', null, form),
                function(item) {
                    if (item.type == 'submit') {
                        connect(item, 'onclick', callback);
                    }
                });
    },
    
    send_form: function(form, event, url, headers, args) {
        /*
         * Send form thought load_xhr.
         * Event must be event of element who initiate submit (<input type='submit'> or <button>);
         * value of this element will be set as 'action' POST variable
         */
        var _data = formContents(form);
        if (event) {
            _data[0].push('action');
            _data[1].push(event.src().name);
        }
        
        var _url = url || location;
        return Ajax.load_xhr(_url, 
                             queryString(_data),
                             headers,
                             args);
    }

};



