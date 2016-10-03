$(function () {
    // Add menu item
    $.get("/content/plugins/map/templates/menu_item.mustache", function (template) {
        var view = {
            i: function () {
                return function (text, render) {
                    return render(text);
                }
            }
        };
        var menuItem = Mustache.render(template, view);
        $('ul.sidebar-menu > li:nth-child(1)').after(menuItem);
    });

    // Add page page-map
    $.get("/content/plugins/map/templates/page-map.mustache", function (template) {
        var page = Mustache.render(template);
        $('.content-wrapper').append(page);


        $.getJSON('/map/maps', function (maps) {
            console.log(maps);
            maps.forEach(function (v, i) {
                var $option = $('<option>').text(v);
                $option.val(v);
                if (i === 0) {
                    $option.attr('selected', 'selected');
                    load_map(v);
                }
                $('.map-select-tiles').append($option);
            });
            $('.map-select-tiles').on('change', function () {
                load_map($(this).val());
            });
        });
    });

    function load_map(name) {
        var mapExtent = [0.00000000, -2000.00000000, 2000.00000000, 0.00000000];
        var mapMinZoom = 0;
        var mapMaxZoom = 3;
        var mapMaxResolution = 1.00000000;
        var tileExtent = [0.00000000, -2000.00000000, 2000.00000000, 0.00000000];

        var mapResolutions = [];
        for (var z = 0; z <= mapMaxZoom; z++) {
            mapResolutions.push(Math.pow(2, mapMaxZoom - z) * mapMaxResolution);
        }

        var mapTileGrid = new ol.tilegrid.TileGrid({
            extent: tileExtent,
            minZoom: mapMinZoom,
            resolutions: mapResolutions
        });

        var map = new ol.Map({
            target: 'dric-map',
            layers: [
              new ol.layer.Tile({
                  source: new ol.source.XYZ({
                      projection: 'PIXELS',
                      tileGrid: mapTileGrid,
                      url: "/map/"+name+"/{z}/{x}/{y}.png"
                  })
              })
            ],
            view: new ol.View({
                projection: ol.proj.get('PIXELS'),
                extent: mapExtent,
                maxResolution: mapTileGrid.getResolution(mapMinZoom)
            })
        });
        map.getView().fit(mapExtent, map.getSize());

        window.page_map_after_show = function () {
            map.updateSize();
        }
    }

});
