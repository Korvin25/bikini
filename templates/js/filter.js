var objListState;

function submitFilterForm($form, $container, url, data, src){

    var title = $(document).attr('title');

    // console.log('submitForm data="' + data + '" data_type="' + data_type + '"' + ' src=' +src );

    if( src != 'restore' && objListState != 'refresh' ){
        uri = url + '?' + data;
        history.pushState({}, title, uri);
        //history.pathname = uri;
    }

    if (objListState != 'refresh'){ $('html, body').animate({scrollTop: $("#main_content").offset().top}, 1000); }
    else { objListState = ''; }

    $container.addClass('_disabled');
    
    $.ajax({
        url: url,
        data: data,
        cache: false,
        success: function(res){
            $container.html(res);
            $container.removeClass('_disabled');
        },
        error: function(){
            $container.removeClass('_disabled');
            alert('Произошла ошибка');
        }
    });
};



$('.js-filter-form').on('submit', function(e){
    e.preventDefault();

    var $form = $(this),
        $container = $('#'+$form.attr('data-container-id')),
        url = $form.attr('action');

    $(document.activeElement).blur();

    var filter = $form.serializeArray();
    filter = jQuery.grep(filter, function(element) {
        return (element.value != '')
    });
    var data = jQuery.param(filter);
    submitFilterForm($form, $container, url, data, 'js_filter_form');
});


$('.js-form-reset').click(function(e){
    var $form = $(this).closest('form');

    $form.find(':input','option:selected')
     .not(':button, :submit, :reset, :hidden')
     .val('')
     .removeAttr('checked')
     .removeAttr('selected');    

    $form.submit();
})
