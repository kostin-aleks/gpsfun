// simple placeholder
//
// set for element: Placeholder.assign('id_question', 'enter question')
Placeholder = {
    placeholded: {}, // elements with active placeholder {'elem_id': true, ...}

    _onfocus: function(event){
        elem = event.target()

        if (Placeholder.placeholded[elem.id])
        {
            elem.value = ''
            elem.style.color = '#334444';
            Placeholder.placeholded[elem.id] = false
        }
    },

    assign: function(elem_id, text)
    {
        elem = getElement(elem_id)

        elem.value = text
        elem.style.color = "#aaaaaa";
        Placeholder.placeholded[elem_id] = true

        connect(elem, 'onfocus',  Placeholder._onfocus)
    },

    // return non-placeholded element value
    real_value: function(elem_id)
    {
        if (Placeholder.placeholded[elem_id])
            return ''
        else
            return getElement(elem_id).value
    }
}
