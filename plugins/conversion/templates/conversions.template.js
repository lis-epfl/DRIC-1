(function(){
    var edges = {{{ edges }}};
var quantities = {{{ quantities }}};

if(typeof window.Conversion === 'undefined'){
    var Conversion = {};
    window.Conversion = Conversion;
}

Conversion = window.Conversion;

Conversion.edges = edges;
Conversion.quantities = quantities;

})();