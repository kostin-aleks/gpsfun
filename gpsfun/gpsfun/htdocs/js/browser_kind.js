/* DHTML API Position elements */
var isCSS, isW3C, isIE4, isNN4, isIE6CSS;

function initDHTMLAPI() {
    isCSS = (document.body && document.body.style) ? true : false;
    isW3C = (isCSS && document.getElementById) ? true : false;
    isIE4 = (isCSS && document.all) ? true : false;
    isNN4 = (document.layers) ? true : false;
    isIE6CSS = (document.compatMode && document.compatMode.indexOf("CSS1")>=0) ? true : false;
}

initDHTMLAPI();
