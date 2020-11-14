
Celery = {};


Celery.Task = function(task_id) {
    this.df = new Deferred();
    this.celery_task_id = task_id;
    callLater(2, bind(this.poll, this));
};



Celery.Task.prototype.poll = function() {
    df = Ajax.load_json('/celery/' + this.celery_task_id + '/status/');
    df.addCallback(bind(this._pollResponse, this));
};


Celery.Task.prototype._pollResponse = function(doc) {
    log(doc.task.status);
    if (doc.task.status == 'SUCCESS') {
        this.df.callback(doc.task);
    } else {
        callLater(2, bind(this.poll, this));
    }
};