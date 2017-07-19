/**
 * Created by dfitzgerald on 1/23/17.
 */
function extend(obj, src) {
    for (var key in src) {
        if (src.hasOwnProperty(key)) obj[key] = src[key];
    }
    return obj;
}

// Stolen from StackOverflow
// https://goo.gl/fHfxpH
String.prototype.format = function () {
  var i = 0, args = arguments;
  return this.replace(/{}/g, function () {
    return typeof args[i] != 'undefined' ? args[i++] : '';
  });
};

function makeToast(options) {
    console.log('making toast');
    $.toast(extend({
        bgColor: '#138a36',
        textColor: '#e1e6e1',
        loaderBg: '#333333',
        position: 'bottom-right'
    }, options));
}