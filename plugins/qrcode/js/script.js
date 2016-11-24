function qrCode() {
    return;
    var templateUrl = "/qrcode/templates/qrcode.mustache";
    //Initialize the box with the box helper
    qrbox = new dric.Box();
    qrbox.setTitle('QRCode');
    qrbox.setCloseable(true);
    qrbox.setCollapsable(true);

    $.get(templateUrl, function (template) {
        qrbox.setContent($('<div>', {
            id: "qrcode-connx",
            style: "text-align:center"
        })[0].outerHTML);
        dric.box.net.append(qrbox, function () {

            //We have to wait for the network plugin to load (if it exists)
            dric.ready('network', function () {
                dric.ready('network.ip', function () {
                    $('#qrcode-connx').qrcode('http://'+dric.network.ip);
                });
            });
        });
    });
}
qrCode();