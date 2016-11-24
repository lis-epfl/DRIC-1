define(function () {

    isUpData = {isUp: true};
    var dricofflineLogoindic = {
        template: '<a href="/" class="logo" v-on:down="alert();isUp=false" v-on:up="alert();isUp=true">'
                    + '<img src="/content/core/index/img/dric.png" style="height:50%;margin:auto;top:25%;position:relative;" class="logo-mini" v-show="isUp">'
                    + '<i class="fa fa-exclamation-circle connecting-orange blink " title="You are disconnected" v-cloak v-show="!isUp"></i>'
                    + '</a>',
        data: function () {
            return isUpData;
        }
    };

    vapp = new Vue({
        el: '.main-header',
        components: {
            'dricoffline-logoindic': dricofflineLogoindic
        }
    });

    function setUp(up) {
        isUpData.isUp = up;
    }

    setInterval(function () {
        var xhr = new XMLHttpRequest();
        xhr.open('HEAD', '/');
        xhr.timeout = 1000; 
        xhr.onload = function () {
            setUp(true);
        };
        xhr.ontimeout = function () {
            setUp(false);
        };
        xhr.send();
    }, 1000);
    
});