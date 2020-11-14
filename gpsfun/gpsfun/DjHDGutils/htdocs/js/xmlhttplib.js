var xhttp_debug_win;

function xml_http_call_url(url,query,on_success,on_fail,content) {
    var options= {'headers': {'Accept': 'application/javascript',
                              'Content-type': 'application/x-www-form-urlencoded'} };

    if (content) {
        options['method'] = 'POST';

        if (typeof content == 'object') {
            content = queryString(content);
        }
        options['sendContent'] = content;
    }

    if (typeof query == 'string') {
        if (url.substr(url.length-1,1) != '?' && query.substr(0,1) != '?') {
            url += '?';
        }
        url += query;
    } else {
        options['queryString'] = query;
    }

    var ajax = doXHR(url,options);

    ajax.addCallbacks(
        function(t){
            var obj = evalJSONRequest(t);

            if (obj.status == 500) {
                if (obj.debug) {
                    if (!xhttp_debug_win || xhttp_debug_win.closed) {
                        xhttp_debug_win = window.open("","debug","scrollbars,width=1024,height=800");
                    } else {
                        xhttp_debug_win.focus();
                    }
                    xhttp_debug_win.document.write(obj.debug_msg);
                    xhttp_debug_win.document.close();

                } else if(on_fail) {
                    on_fail(obj.status, t)
                } else {
                    alert("Oops! Error happend while execute XML request. Server return "+obj.status+" code");
                }
            } else {
                if (on_success)
                    on_success(obj.content, obj.status, t)
            }
        },
        function(t){
            alert("Timeout while XML Http request to server");
            if (on_fail) {
                on_fail(0)
            }
        }
    );
}

function xml_http_call(f_name,get_var,on_success,on_fail) {
    return xml_http_call_url('/xmlhttp/'+f_name+'/',get_var,on_success,on_fail);
}
