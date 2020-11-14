

InlineEdit = function(base_url, template_id) {
    this.base_url = base_url;
    this.template = getElement(template_id);
    this.current_item = null;
    this.orininal_elements = null;
    this.original_value = null;
    this.input = null;
    this.class_action_mapping = {save: 'save',
                                 delete: 'delete',
                                 cancel: 'cancel'};
    this.active_request = null;
    this.confirmDialog = null;

};

InlineEdit.prototype.startEdit = function(elem) {
    if (this.current_item) {
        this.cancelEdit();
    }

    this.current_item = getFirstParentByTagAndClassName(elem);
    this.original_value = getElement(elem).innerHTML;
    
    edit_block = this.template.cloneNode(true);
    
    this.input = getFirstElementByTagAndClassName(null, 'edit', edit_block);
    this.input.value = this.original_value;

    this.orininal_elements = removeElement(elem);
    replaceChildNodes(this.current_item, edit_block);
    showElement(edit_block);

    forEach(keys(this.class_action_mapping),
            function(item) {
                var target = getFirstElementByTagAndClassName(null, this.class_action_mapping[item], this.edit_block);
                if (target) {
                    connect(target, 'onclick', this, method(this, item+'Edit'));
                }

            }, this);

};



InlineEdit.prototype.cancelEdit = function(event) {
    if (!this.current_item || this.active_request) {
        return;
    }
    
    replaceChildNodes(this.current_item, this.orininal_elements);
    this.current_item = null;
};


InlineEdit.prototype.saveEdit = function(event) {
    if (this.active_request) {
        return;
    }
    event.stop();
    this.input.disabled = true;
    
    this.active_request = Ajax.load_xhr(this.base_url,
                                        queryString({'value': this.input.value,
                                                     'action': 'save',
                                                     'id': this.current_item.id}));

    this.active_request.addCallback(this.onRequestComplete, this);
    

};



InlineEdit.prototype.deleteEdit = function(event) {
    if (this.active_request) {
        return;
    }
    event.stop();

    if (this.confirmDialog && !this.confirmDialog()) {
        return;
    }

    this.input.disabled = true;
    this.active_request = Ajax.load_xhr(this.base_url,
                                        queryString({'action': 'delete',
                                                     'id': this.current_item.id}));

    this.active_request.addCallback(this.onRequestComplete, this);
};


InlineEdit.prototype.onRequestComplete = function(self, doc) {
    self.active_request = null;
    switch (doc.action) {
        case 'replace': 
        self.current_item.innerHTML = doc.context;
        break;
        
        case 'delete':
        removeElement(self.current_item);
        break;
        
    };
    self.current_item = null;
};