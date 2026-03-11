CoordinateConverter = {
    input_id: null,
    out_GMS_id: null,
    out_G_id: null,
    out_GM_id: null,
    converter_url: null,  

	
    init: function(input_id, out1_id, out2_id, out3_id, converter_url) {
		CoordinateConverter.input_id = input_id;
		CoordinateConverter.out_GM_id = out1_id;
		CoordinateConverter.out_G_id = out2_id;
		CoordinateConverter.out_GMS_id = out3_id;
		CoordinateConverter.converter_url = converter_url;
		document.getElementById(CoordinateConverter.input_id).focus();
		//CoordinateConverter.clear();
    },
    
    convert: function() {
		document.getElementById(CoordinateConverter.out_GM_id).innerHTML = '';
		document.getElementById(CoordinateConverter.out_G_id).innerHTML = '';
		document.getElementById(CoordinateConverter.out_GMS_id).innerHTML = '';
		var i = document.getElementById(CoordinateConverter.input_id);
		if (i && i.value) {
			$.ajax({
				url: CoordinateConverter.converter_url,
				type: 'POST',
				dataType: 'JSON',
				data: {	'input': i.value },
				success: function(doc) {
					if (doc.status != "OK") {
						return;
					}
					CoordinateConverter.showResults(doc);
				}
			})
		}
    },
    
    showResults: function(doc) {
		if (!doc) return;
		document.getElementById(CoordinateConverter.out_G_id).innerHTML = doc.d;
		document.getElementById(CoordinateConverter.out_GM_id).innerHTML = doc.dm;
		document.getElementById(CoordinateConverter.out_GMS_id).innerHTML = doc.dms;
		$('#converted').show();
    },
	
	clear: function() {
		
		document.getElementById(CoordinateConverter.out_G_id).innerHTML = '';
		document.getElementById(CoordinateConverter.out_GM_id).innerHTML = '';
		document.getElementById(CoordinateConverter.out_GMS_id).innerHTML = '';
		//$('#converted').hide();
	}
}

