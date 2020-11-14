/* TabPage widget
 * Usally use next HTML structure:
 * 
 * <div id="tabs_frame_id" class="tabs">
 *   <ul>
 *     <li><a href="#tab_id1">tab_title 1</a></li>
 *     <li><a href="#tab_id2">tab_title 2</a></li>
 *   </ul>
 *   <div id="tab_id1">body<div>
 *   <div id="tab_id2">body<div>
 * </div>
 *
 * <script language="JavaScript">
 *  var tab = new Tabs('tabs_frame_id');
 *  tab.selectTabByIndex(0);
 *  // or select tab by id
 *  tab.selectTabByIndex('tab_id1');
 * </script>
 */


Tabs = function(element, options) {
    this.tab_frame = getElement(element);
    this.use_hash = true;
  
    forEach(findChildElements(this.tab_frame, ['ul > li > a']),
            function(item) {
                connect(item, 'onclick', this, this.onTabClick);
            }, this);
};


Tabs.prototype.onTabClick = function(event) {
    event.stop();
    var tab_id = event.src().hash;
    this.selectTab(tab_id.substr(1));

};

Tabs.prototype._findTabById = function(tab_id) {
    var tab_item = null;
    forEach(findChildElements(this.tab_frame, ['ul > li > a']),
            function(item) {
                if (item.hash == '#'+tab_id) {
                    tab_item = item;
                    throw StopIteration;
                };
            }, this);
    if (tab_item) {
        return getFirstParentByTagAndClassName(tab_item, tagName='li');
    }
    return null;
};

Tabs.prototype.selectTab = function(tab_id) {
    var tab_body = getElement(tab_id);
    var tab_header = this._findTabById(tab_id);

    forEach(findChildElements(this.tab_frame, ['ul > li']),
            function(item) {
                removeElementClass(item, 'active');
            });

    var current_body = null;
    forEach(findChildElements(this.tab_frame, ['> div']),
            function(item) {
                if (getStyle(item, 'display') != 'none') {
                    current_body = item;
                    throw StopIteration;
                }
                
            }, this);

    addElementClass(tab_header, 'active');
    
    if (current_body) {
        Sequence([fade(current_body, {'sync': true}),
                  appear(tab_body, {'sync': true})],
                {'duration': 0.4,
                 'transition': "sinoidal"});
    } else {
        showElement(tab_body);
    }

    if (this.use_hash) {
        location.hash = tab_id;
    }

};

Tabs.prototype.selectTabByIndex = function(tab_index) { 
    var tabs_headers = findChildElements(this.tab_frame, ['ul > li > a']);
    
    this.selectTab(tabs_headers[tab_index].hash.substr(1));
};

Tabs.prototype.selectTabByHash = function() {
    if (!location.hash) {
        return false;
    }
    
    if (!this._findTabById(location.hash.substr(1))) {
        return false;
    }
    this.selectTab(location.hash.substr(1));
    return true;
};