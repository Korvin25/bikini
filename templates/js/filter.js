{% load i18n %}

var objListState;

function sendFilterForm($form, $container, url, data, src){

    var title = $(document).attr('title'),
        $oldPagination = $container.find('.js-pagination-container'),
        $toScroll;

    if (src == 'load_more') {
        $toScroll = $oldPagination;
        $container = $('#products_div');
    }
    else { $toScroll = $container; }

    if (src != 'restore' && objListState != 'refresh'){
        uri = url + '?' + data;
        history.pushState({}, title, uri);
        //history.pathname = uri;
    }

    if (objListState != 'refresh'){ $('html, body').animate({scrollTop: $toScroll.offset().top}, 750); }
    else { objListState = ''; }

    $container.addClass('_disabled');

    $.ajax({
        url: url,
        data: data,
        cache: false,
        success: function(res){
            if (src == 'load_more') {
                $oldPagination.before(res);
                $oldPagination.remove();
            } else {
                $container.html(res);
            }
            $container.removeClass('_disabled');
        },
        error: function(){
            $container.removeClass('_disabled');
            alert('{% trans "Произошла ошибка" %}');
        }
    });
};


function submitFilterForm($form, src){
    var $container = $('#'+$form.attr('data-container-id')),
        url = $form.attr('action');

    $(document.activeElement).blur();

    var filter = $form.serializeArray();
    filter = jQuery.grep(filter, function(element) {
        // return ((element.value != '') && !(element.name == 'page' && element.value == '1'))
        return (element.value != '')
    });
    var data = jQuery.param(filter);
    sendFilterForm($form, $container, url, data, src);
};


function setFilterPageNum($form, pageNum){
    $form.find('input[name="page"]').remove();
    if (pageNum > 1) { 
        $form.prepend('<input type="hidden" name="page" value="'+pageNum+'"/>');
    };
}


$('.js-filter-form').on('submit', function(e){
    e.preventDefault();

    var $form = $(this),
        src='js_filter_form';

    setFilterPageNum($form, 1);
    submitFilterForm($form, src);
});


$('body').on('click', '.js-page', function(e){
    e.preventDefault();

    var $form = $('.js-filter-form'),
        pageNum = parseInt($(this).data('page')),
        src = 'page';

    setFilterPageNum($form, pageNum);
    submitFilterForm($form, src);
});


$('body').on('click', '.js-load-more', function(e){
    e.preventDefault();

    var $form = $('.js-filter-form'),
        pageNum = parseInt($(this).data('page')),
        src = 'load_more';

    setFilterPageNum($form, pageNum);
    submitFilterForm($form, src);
});


$('.js-form-reset').click(function(e){
    var $form = $(this).closest('form');

    $form.find(':input','option:selected')
     .not(':button, :submit, :reset, :hidden')
     .removeAttr('checked')
     .removeAttr('selected');

    $form.find('input[type="text"]').val('');

    $form.submit();
})


$("#category").click(function () {
    if ($("#category_list").is(":hidden")) {
        $("#category_list").show("slow");
    } else {
        $("#category_list").hide("slow");
    }
    return false;
});

$("#filter").click(function () {
    if ($("#filter_list").is(":hidden")) {
        $("#filter_list").show("slow");
    } else {
        $("#filter_list").hide("slow");
    }
    return false;
});
