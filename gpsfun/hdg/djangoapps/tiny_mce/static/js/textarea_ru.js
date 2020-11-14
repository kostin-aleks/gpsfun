// function insertFileChooser() {
// //   var rows = [
// // 	       ["dataA1", "dataA2", "dataA3"],
// // 		 ["dataB1", "dataB2", "dataB3"]
// //   ];
// //   row_display = function (row) {return TR(null, map(partial(TD, null), row));};
// //   var newTable = TABLE({'class': 'prettytable'},
// // 		   THEAD(null,
// // 		   row_display(["head1", "head2", "head3"])),
// // 		   TFOOT(null,
// // 		   row_display(["foot1", "foot2", "foot3"])),
// // 		   TBODY(null,
// //         map(row_display, rows)));
// //   swapDOM(getElement('srcbrowser'), newTable);
// }


// function CustomFileBrowser(field_name, url, type, win) {
//   hrefs = getElementsByTagAndClassName('a', null);
//   log(hrefs);
//   //for (href=chain(hrefs);;) {
//   //  log(href);
//   //}
//   //file_divs = getElementsByTagAndClassName('div', 'form-row');
//   //alert(file_divs);
//   //
//   // withWindow(win, insertFileChooser)
// }


// function myCustomSetupContent(editor_id, body, doc) {
//     if (body.innerHTML == "") {
//         body.innerHTML = "<p>xxx</p>";
//     }
// }


// //log(getElement("id_flatpageimage_set-0-image").text);


// // for (i=0; i<10; i++) {
// //   log('id_flatpageimage_set-' + i + '-image');
// //   label = getElement('id_flatpageimage_set-' + i + '-image');
// //   log(label);
// //   if (i>10) {
// //     break;
// //   }
// // }

tinyMCE.init({
	       mode : "textareas",
    language: 'ru',
	       theme : "advanced",
	       //content_css : "/appmedia/blog/style.css",
	       theme_advanced_toolbar_location : "top",
	       theme_advanced_toolbar_align : "left",
	       theme_advanced_buttons1 : "fullscreen,separator,preview,separator,bold,italic,underline,strikethrough,separator,bullist,numlist,outdent,indent,separator,undo,redo,separator,link,unlink,anchor,separator,image,cleanup,help,separator,code",
	       theme_advanced_buttons2 : "",
	       theme_advanced_buttons3 : "",
	       // auto_cleanup_word : true,
	       convert_urls : false,
	       relative_urls : false,
	       plugins : "table,save,advhr,advimage,advlink,emotions,iespell,insertdatetime,preview,zoom,flash,searchreplace,print,contextmenu,fullscreen",
	       plugin_insertdate_dateFormat : "%m/%d/%Y",

	       plugin_insertdate_timeFormat : "%H:%M:%S",
	       extended_valid_elements : "a[name|href|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
	       fullscreen_settings : {
		 theme_advanced_path_location : "top",
		 theme_advanced_buttons1 : "fullscreen,separator,preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
		 theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
		 theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
	       }
//	       file_browser_callback : 'CustomFileBrowser'
});

