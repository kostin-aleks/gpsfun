var  win_opened;

function fake_href() {}


function w_open(url,height,width) {

    var left = parseInt((screen.availWidth/2) - (width/2));
    var top  = parseInt((screen.availHeight/2) - (height/2));

    if (win_opened && !win_opened.closed) {
        win_opened.close();
    }
    win_opened = window.open(url,'popWin','width='+width+','+
                                 'height='+height+','+
                                 'left='+left+','+
                                 'top='+top+', resizable=yes,scrollbars=yes,status=no');

    if (!win_opened.opener) {
        alert("opener not defined");
    }


    if (!win_opened.opener)
        win_opened.opener = self;

    win_opened.focus();
    return win_opened;
}

function document_reload() {
    var location_href;

    location_href = document.location.href;

    document.location.href = location_href;
}