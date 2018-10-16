$(document).ready(function() {
    var localStorageEnabled = true;
    try { localStorage }
    catch(DOMException) { localStorageEnabled = false; };

    if(localStorageEnabled && localStorage.getItem("cookSub") && localStorage.getItem("cookSub") == 1) {
        // если кнопка вкл
        $('#cookie-notice').css("display", "none");
    } else {
        // если кнопка НЕ вкл
        $('#cookie-notice').css("display", "block");
        $("#cn-accept-cookie").on("click",function(){ //
            if (localStorageEnabled) {
                localStorage.setItem("cookSub", "1");
                var cookSub = localStorage.getItem("cookSub");
            };
            $('#cookie-notice').css("display", "none");
        });
    }
});
