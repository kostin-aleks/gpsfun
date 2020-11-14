function optionally_disable_input() {
    if (this.value=='new-batch') {
	addElementClass($('id_exclude_unsubscribed').parentNode.parentNode, 'invisible');
    }
    if (this.value=='mail' | this.value=='new-batch') {
	removeElementClass($('id_text').parentNode.parentNode, 'invisible');
	removeElementClass($('id_subject').parentNode.parentNode, 'invisible');
	removeElementClass($('id_from_address').parentNode.parentNode, 'invisible');
	removeElementClass($('id_from_name').parentNode.parentNode, 'invisible');
	removeElementClass($('id_content_type').parentNode.parentNode, 'invisible');
	if (this.value=='mail') {
	    removeElementClass($('id_exclude_unsubscribed').parentNode.parentNode, 'invisible');
	    addElementClass($('id_send_after').parentNode.parentNode, 'invisible');
	} else {
	    removeElementClass($('id_send_after').parentNode.parentNode, 'invisible');
	}
	if ($('id_text').value=='---') {
	    $('id_text').value='';
	}
	if ($('id_subject').value=='---') {
	    $('id_subject').value='';
	}
    } else {
	addElementClass($('id_text').parentNode.parentNode, 'invisible');
	addElementClass($('id_subject').parentNode.parentNode, 'invisible');
	addElementClass($('id_from_address').parentNode.parentNode, 'invisible');
	addElementClass($('id_from_name').parentNode.parentNode, 'invisible');
	addElementClass($('id_content_type').parentNode.parentNode, 'invisible');
	addElementClass($('id_exclude_unsubscribed').parentNode.parentNode, 'invisible');
	addElementClass($('id_send_after').parentNode.parentNode, 'invisible');
	if ($('id_text').value=='') {
	    $('id_text').value='---';
	}
	if ($('id_subject').value=='') {
	    $('id_subject').value='---';
	}

    } 
}

window.onload = function () {
    connect('id_batch_option', 'onchange', optionally_disable_input);
    if ($('id_batch_option').value!='new-batch') {
	addElementClass($('id_send_after').parentNode.parentNode, 'invisible');
    }
}