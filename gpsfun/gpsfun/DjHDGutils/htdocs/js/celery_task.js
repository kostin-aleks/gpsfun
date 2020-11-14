// cross-browser emulation of bind
function bind_emulation(func, context) {
    return function() {
        return func.apply(context, arguments);
    }
}

function ieVersion() {
    var ua = navigator.userAgent.toLowerCase();
        var res = /msie (\d+)/.exec(ua);
        if (res) {
            return parseInt(res[1])
        }
    return null;
}

// class CeleryTask
function CeleryTask(element_id, start_task_url, task_hash) {
    this.running = false;
    this.linkTitle = '';
    this.task_hash = task_hash;
    this.element_id = element_id;
    this.start_task_url = start_task_url;
    this.task_text = gettext('Downloading...');
    this.get_parameters = null;
    this.callback_function = null;
    this.css_class_waiting = 'waiting';
}

CeleryTask.prototype.start_callback = function(doc) {
    callLater(5, bind_emulation(CeleryTask.prototype.checkStatus, this));
}

CeleryTask.prototype.check_status_callback = function(result) {
    if (result.status == 'not running') {
        this.running = false;
        return;
    }
    if (result.status == 'SUCCESS') {
        callLater(1, bind_emulation(CeleryTask.prototype.setProcessedStatus, this));
        if (this.callback_function) {
            this.callback_function(result);
        } else {
            // document.location = result.result;
            ver = ieVersion();
            if (ver && ver <= 9) {
                document.location = result.result;
            } else {
                window.open(result.result, 'resizable,scrollbars');
            }
        }
        this.set_normal_style();
    } else {
        if (this.task_hash) {
            this.set_next_round_style();
            callLater(5, bind_emulation(CeleryTask.prototype.checkStatus, this));
        }
    }
}

CeleryTask.prototype.is_task_running_callback = function(result) {
    if (result.found) {
        this.start();
    }
}

CeleryTask.prototype.set_processed_status_callback = function(doc) {
    this.running = false;
}

CeleryTask.prototype.set_waiting_style = function() {
    var elm = getElement(this.element_id);
    if (elm) {
        addElementClass(this.element_id, this.css_class_waiting);
        this.linkTitle = getElement(this.element_id).value;
        getElement(this.element_id).value = this.task_text;
        pulsate(this.element_id, {'pulses': 5, 'duration': '5'});
    }
}

CeleryTask.prototype.set_normal_style = function() {
    var elm = getElement(this.element_id);
    if (elm) {
        removeElementClass(this.element_id, this.css_class_waiting);
        getElement(this.element_id).value = this.linkTitle;
        setStyle(this.element_id,  {'display': 'inline'});
    }
}


CeleryTask.prototype.remove_download_link = function() {
    var download_link_id = this.element_id+'-download';
    var download_link_elm = getElement(download_link_id);
    if (download_link_elm) {
        removeElement(download_link_elm);
    }
}

CeleryTask.prototype.add_download_link = function(href) {
    var elm = getElement(this.element_id);
    var download_link_id = this.element_id+'-download';
    var download_link_elm = getElement(download_link_id);
    if (download_link_elm) {
        insertSiblingNodesAfter(elm, A({'id': download_link_id,
                                        'href': href}, 'download'));
    }
}

CeleryTask.prototype.set_next_round_style = function() {
    var elm = getElement(this.element_id);
    if (elm) {pulsate(this.element_id, {'pulses': 5, 'duration': '5'});}
}

CeleryTask.prototype.start = function() {
    this.set_waiting_style();
    this.remove_download_link();

    var get_params = {'stamp': new Date().getTime()}
    if (this.get_parameters) {
        for (var key in this.get_parameters) {
            get_params[key] = this.get_parameters[key];
        }
    }
    df = Ajax.load_json(this.start_task_url, get_params);

    callLater(5, bind_emulation(CeleryTask.prototype.checkStatus, this));
    this.running = true;
    return false;
}

CeleryTask.prototype.setProcessedStatus = function() {
    df = Ajax.load_json('/core/async-task/set/processed/',
                        {'task_hash': this.task_hash,
                         'stamp': new Date().getTime()});
    df.addCallback(bind_emulation(CeleryTask.prototype.set_processed_status_callback, this));
}

CeleryTask.prototype.checkStatus = function() {
    df = Ajax.load_json('/core/async-task/status/',
                        {'task_hash': this.task_hash,
                         'stamp': new Date().getTime()});
    df.addCallback(bind_emulation(CeleryTask.prototype.check_status_callback, this));
}

CeleryTask.prototype.is_task_running = function() {
    df = Ajax.load_json('/core/async-task/is_task_running/',
                        {'task_hash': this.task_hash});
    df.celerytask = this;
    df.addCallback(bind_emulation(CeleryTask.prototype.is_task_running_callback, this));
    df.addErrback(function(err) {
        if (window.console) {
            window.console.log(['celery task error:', err]);
        }
    });
}


CeleryTask.prototype.stop_work = function() {
    this.running = false;
}
