//TODO -> move to its own waypoints.js file
// -------------------------- WAYPOINTS ------------------------------------
function WaypointManager(waypointVectorSource, meter2pixel) {
    var waypointCount = 0;
    var features = [];
    var pathFeature = null;
    var waypointColor = 'rgba(255,204,51,0.7)';
    var selectedColor = 'rgba(255, 51, 51, 0.7)';

    function createWaypoint(coordinates) {
        var index = waypointCount++;
        // Create feature
        var waypoint = new ol.Feature({
            geometry: new ol.geom.Point(coordinates),
            index: index,
            'text-index': index.toString(),
            radius: 1
        });

        features[index] = waypoint;

        // Add utility function
        waypoint.isSelected = function () {
            return $('#map-select-waypoint option[value=' + waypoint.get('index') + ']').is(':selected');
        };

        return waypoint;
    };

    function createStyle(waypoint) {
        return function (resolution, data) {
            var fillColor = waypoint.isSelected() ? selectedColor : waypointColor;

            var radius = waypoint.get('radius');
            if (typeof waypoint.get('waypointData') !== 'undefined') {
                radius = waypoint.get('waypointData').data['radius'];
            }
            radius *= meter2pixel;

            // Waypoint style
            var waypointStyle = new ol.style.Style({
                text: new ol.style.Text({ text: waypoint.get('text-index').toString() }),
                stroke: new ol.style.Stroke({
                    color: '#ffcc33',
                    width: 2 / resolution
                }),
                image: new ol.style.Circle({
                    radius: radius / resolution,
                    fill: new ol.style.Fill({
                        color: fillColor
                    })
                }),
                scale: resolution
            });
            return waypointStyle;
        };
    };


    this.addWaypoint = function (coordinates, waypointData) {
        console.debug('create waypoint');
        var waypoint = createWaypoint(coordinates);

        console.debug('create waypoint style')
        waypoint.setStyle(createStyle(waypoint));

        console.debug('add waypoint to layer');
        waypointVectorSource.addFeature(waypoint);

        console.debug('add waypoint control');
        waypointData = waypointControls.addWaypoint(waypoint.get('index'), coordinates, waypointData);
        waypoint.set('waypointData', waypointData, true);
    };

    this.clear = function () {
        console.debug('clear waypoints layer');
        for (var i = 0; i < features.length; i++) {
            if (typeof features[i] !== 'undefined') {
                waypointVectorSource.removeFeature(features[i]);
                delete features[i];
            }
        }
        if (pathFeature !== null) {
            waypointVectorSource.removeFeature(pathFeature);
            pathFeature = null;
        }
    }

    this.changed = function () {
        for (var i = 0; i < features.length; i++) {
            if (typeof features[i] !== 'undefined') {
                features[i].changed();
            }
        }
    };

    this.removeWaypoint = function (index) {
        var feature = features[index];
        waypointVectorSource.removeFeature(feature);
        delete features[index];
        this.changed();
    };

    this.redrawPath = function (indexes) {
        console.debug('redraw path');
        var lineStringGeometry = new ol.geom.LineString([]);
        for (i = 0; i < indexes.length; i++) {
            if (typeof features[indexes[i]] !== 'undefined') {
                features[indexes[i]].set('text-index', i);
                lineStringGeometry.appendCoordinate(features[indexes[i]].getGeometry().getCoordinates());
            }
        }

        if (typeof pathFeature !== 'undefined' && pathFeature !== null) {
            waypointVectorSource.removeFeature(pathFeature);
        }
        pathFeature = new ol.Feature({
            geometry: lineStringGeometry
        });

        pathFeature.setStyle(function (resolution, data) {
            var style = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#ffcc33',
                    width: 0.01 * meter2pixel
                }),
                scale: resolution
            });
            return style;
        });

        waypointVectorSource.addFeature(pathFeature);
    };
}

function DronePositionManager(droneVectorSource, meter2pixel) {
    var WebSocketClient = require('websocket.js').default;

    // Create feature
    var drone = new ol.Feature({
        geometry: new ol.geom.Point([256, 0]),
    });

    function style(resolution, data) {
        var radius = 0.50 * meter2pixel;
        var fillColor = "rgb(0,0,255)";

        // Waypoint style
        var style = new ol.style.Style({
            image: new ol.style.Circle({
                radius: radius / resolution,
                fill: new ol.style.Fill({
                    color: fillColor
                })
            }),
            scale: resolution
        });
        return style;
    };

    drone.setStyle(style);
    droneVectorSource.addFeature(drone);

    var ws = new WebSocketClient("ws://" + window.location.host + "/datasource?s=mavlink/localposition");
    ws.onopen = function () { ws.binaryType = 'arraybuffer'; };

    ws.onmessage = function (message) {
        var view = new DataView(message.data);
        var coordinates = drone.getGeometry().getCoordinates();
        var x = view.getFloat64(0);
        var y = view.getFloat64(8);
        coordinates[0] = x;
        coordinates[1] = y;
        drone.getGeometry().setCoordinates(coordinates);
    };

};

var waypointControls = new function () {
    var waypointManager = null;

    function Waypoint(index) {
        this.data = {
            hold: 1,
            radius: 1,
            trajectory: 0,
            yaw: 0,
            latitude: 0,
            longitude: 0,
            altitude: 5
        };
        this.getIndex = function () {
            return index;
        };
    };

    // Called when the user (un)select waypoints in the <select>
    function selectionChanged() {
        if (waypointManager !== null) {
            waypointManager.changed();
        }
        if ($('#map-select-waypoint option:selected').length > 0) {
            $('.waypoint-control').removeAttr('disabled');
        } else {
            $('.waypoint-control').attr('disabled', 'disabled');
        }
        refreshWaypointEditor();
    };

    // Called when the user select one or more waypoints and refresh the waypoint editor panel
    function refreshWaypointEditor() {
        $options = $('#map-select-waypoint option:selected');
        var data = {};
        if ($options.length === 0) {
            var blank = {
                hold: null,
                radius: null,
                trajectory: null,
                yaw: null,
                latitude: null,
                longitude: null,
                altitude: null
            };
            data = blank;
        } else {
            $options.each(function (index, option) {
                var waypoint = $(option).data('waypoint');
                for (key in waypoint.data) {
                    if (typeof data[key] === 'undefined' || data[key] == waypoint.data[key]) {
                        data[key] = waypoint.data[key];
                    } else if (data[key] != waypoint.data[key]) {
                        data[key] = '<unchanged>';
                    }
                }
            });
        }

        $.each(data, function (name, val) {
            var $wpc = $('#map-waypoint-editor [name="' + name + '"]');
            $wpc.val(val);
        });
    }

    // Called when the user click the "set" button in the waypoint editor panel
    function saveWaypointChange() {
        var data = {};
        $('#map-waypoint-editor [type="text"]').each(function (index, element) {
            if ($(element).val() !== '<unchanged>') {
                data[$(element).attr('name')] = $(element).val();
            }
        });
        $('#map-select-waypoint option:selected').each(function (index, option) {
            for (key in data) {
                $(option).data('waypoint').data[key] = (data[key]);
            }
        });
        if (waypointManager !== null) {
            waypointManager.changed();
            updateFile();
        }
    }

    // Called when the user click the delete waypoint button
    function deleteSelectedWaypoint() {
        // Get the selected waypoints
        $('#map-select-waypoint option:selected').each(function (i, e) {
            var $option = $(e);
            // remove the waypoint from manager
            waypointManager.removeWaypoint($option.val());
            // remove the option from list
            $option.remove();
        });
        $('#map-select-waypoint').change();
        waypointManager.redrawPath(getOrdering());
        updateFile();
    };

    // Move selected waypoints up or down 
    function orderWaypoint(e) {
        // Get direction "up" or "down"
        var direction = $(this).attr('data-direction');
        // Get the selected waypoints
        $selected = $('#map-select-waypoint option:selected');
        if (direction == "down") {
            $selected = $($selected.toArray().reverse());
        }
        $selected.each(function (i, e) {
            var $option = $(e);
            if (direction === 'up') {
                var $before = $option.prev();
                $before.before($option);
            } else if (direction === 'down') {
                var $after = $option.next();
                $after.after($option);
            } else {
                console.error('Direction must be "up" or "down". "' + direction + '" given.')
            }
        });
        updateFile();
        waypointManager.redrawPath(getOrdering());
    };

    // Return the waypoints index in order
    function getOrdering() {
        var ordering = $('#map-select-waypoint option').map(function () {
            return $(this).val();
        });

        $('#map-select-waypoint option').each(function (i, e) {
            $(e).text('Waypoint #' + i);
        });

        return ordering;
    }

    // Update the save file
    function updateFile() {
        var data = [];

        $('#map-select-waypoint option').each(function (i, e) {
            var $e = $(e);
            var option = {
                waypoint: $(e).data('waypoint'),
                coordinates: $(e).data('coordinates')
            };
            data.push(option);
        });



        $('a.map-save-waypoints').attr('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data)));
        $('a.map-save-waypoints').attr('download', 'waypoints.json');
        $('a.map-save-waypoints').click();
    }

    // Load a file from client computer
    function loadFile() {
        var file = document.getElementById("map-waypoints-file").files[0];
        if (file) {
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            reader.onload = function (evt) {
                var data = JSON.parse(evt.target.result);
                $('#map-select-waypoint').empty();
                waypointManager.clear();
                for (var i = 0; i < data.length; i++) {
                    console.debug('load waypoint #' + i)
                    waypointManager.addWaypoint(
                        data[i].coordinates,
                        data[i].waypoint
                        );
                }
            }
            reader.onerror = function (evt) {
                alert("Error reading file");
            }
        }
    }

    this.init = function () {
        $('a.map-open-waypoints').on('click', loadFile);
        $('#map-select-waypoint').on('change', selectionChanged);
        $('#map-delete-waypoint').on('click', deleteSelectedWaypoint);
        $('.map-order-waypoint').on('click', orderWaypoint);
        $('#map-waypoint-editor input[type="submit"]').on('click', saveWaypointChange);
    }

    this.bindWaypointManager = function (wm) {
        waypointManager = wm;
        $('#map-select-waypoint').empty();
        $('#map-select-waypoint').removeAttr('disabled');
    };

    this.unbindWaypointManager = function () {
        waypointManager = null;
        $('#map-select-waypoint').empty();
        $('#map-select-waypoint').attr('disabled', 'disabled');
    };

    this.addWaypoint = function (index, coordinates, waypointData) {
        if (typeof waypointData === 'undefined') {
            waypointData = new Waypoint(index);
        }
        $waypointOption = $('<option>')
            .text('Waypoint #' + index)
            .val(index)
            .data('coordinates', coordinates)
            .data('waypoint', waypointData);
        $('#map-select-waypoint').append($waypointOption);
        waypointManager.redrawPath(getOrdering());
        updateFile();
        return waypointData;
    };
};

$(function () {
    // Add menu item
    $.get('/content/plugins/map/templates/menu_item.mustache', function (template) {
        var view = {
            i: function () {
                return function (text, render) {
                    return render(text);
                };
            }
        };
        var menuItem = Mustache.render(template, view);
        $('ul.sidebar-menu > li:nth-child(1)').after(menuItem);
    });

    // Add page page-map
    $.get('/content/plugins/map/templates/page-map.mustache', function (template) {
        var page = Mustache.render(template);
        $('.content-wrapper').append(page);
        $('#map-toolbar-cursor').click();
        $('.map-slider').bootstrapSlider();
        waypointControls.init();

        $.getJSON('/map/maps', function (maps) {
            console.debug(maps);
            maps.forEach(function (v, i) {
                var $option = $('<option>').text(v);
                $option.val(v);
                if (i === 0) {
                    $option.attr('selected', 'selected');
                    createMap(v);
                }
                $('.map-select-tiles').append($option);
            });
            $('.map-select-tiles').on('change', function () {
                var mapName = $(this).val();
                createMap(mapName);
            });
        });
    });

    function createMap(name, mapInfo) {
        var mapMaxZoom = 1;
        var meter2pixel = 1;
        var waypointVectorSource
        $.getJSON('/map/' + name, function (mapInfo) {
            mapMaxZoom = mapInfo['zoom'] - 1;
            meter2pixel = mapInfo['meter2pixel'];
        }).always(function () {
            if (typeof map !== 'undefined') {
                $(document.getElementById(map.getTarget())).empty();
            }
            waypointControls.unbindWaypointManager();

            var mapMaxResolution = 1.0;
            var x = Math.pow(2, mapMaxZoom);
            var mapExtent = [0.0, -256.0 * x, 256.0 * x, 0.0];
            var mapMinZoom = 0;

            var tileExtent = [0.0, -256.0 * x, 256.0 * x, 0.0];

            var mapResolutions = [];
            for (var z = 0; z <= mapMaxZoom; z++) {
                mapResolutions.push(Math.pow(2, mapMaxZoom - z) * mapMaxResolution);
            }

            var projection = new ol.proj.Projection({
                code: 'map-projection',
                units: 'pixel',
                metersPerUnit: '1000',
                extent: tileExtent,
            });


            var mapTileGrid = new ol.tilegrid.TileGrid({
                extent: tileExtent,
                minZoom: mapMinZoom,
                resolutions: mapResolutions
            });

            var mapSource = new ol.source.XYZ({
                //projection: projection,
                tileGrid: mapTileGrid
            });
            mapSource.setUrl('/map/' + name + '/{z}/{x}/{y}.png')

            var mapView = new ol.View({
                //projection: projection,
                extent: mapExtent,
                maxResolution: mapTileGrid.getResolution(mapMinZoom)
            });

            //Mouse position control
            var mousePositionControl = new ol.control.MousePosition({
                coordinateFormat: ol.coordinate.createStringXY(4),
                //projection: projection,
                // comment the following two lines to have the mouse position
                // be placed within the map.
                //  className: 'custom-mouse-position',
                // target: document.getElementById('mouse-position'),
                undefinedHTML: '&nbsp;'
            });

            //Drone layer
            var droneVectorSource = new ol.source.Vector();
            var droneLayer = new ol.layer.Vector({
                source: droneVectorSource
            });

            // Waypoint layer
            waypointVectorSource = new ol.source.Vector();

            var vectorLayer = new ol.layer.Vector({
                source: waypointVectorSource,
            });

            map = new ol.Map({
                loadTilesWhileInteracting: true,
                loadTilesWhileAnimating: true,
                controls: ol.control.defaults({
                    attributionOptions: ({
                        collapsible: false
                    })
                }).extend([mousePositionControl]),
                target: 'dric-map',
                layers: [
                      new ol.layer.Tile({
                          source: mapSource
                      }),
                    vectorLayer,
                    droneLayer
                ],
                view: mapView
            });
            map.getView().fit(mapExtent, map.getSize());

            window.page_map_after_show = function () {
                map.updateSize();
            }


            waypointManager = new WaypointManager(waypointVectorSource, meter2pixel);

            waypointControls.bindWaypointManager(waypointManager);

            DronePositionManager(droneVectorSource, meter2pixel);

            // Events
            map.on('singleclick', function (e) {
                if ($('#map-toolbar-waypoint').is(':checked')) {
                    waypointManager.addWaypoint(e.coordinate);
                }
            });


        });
    }

});



