// ----- AJAX setup: check cookies, set CSRF  -------

// var csrftoken = $.cookie('csrftoken');
var csrftoken = Cookies.get('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            if (!areCookiesEnabled) {
                alertCookiesDisabled();
                return false;
            } else {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            };
        }
    }
});
