

// ----- Превращаем чекбоксы в радиобаттоны -----

$('.js-not-checkbox').click(function(e) {
  var $checkbox = $(this),
      attr_slug = $checkbox.attr('data-attr-slug'),
      is_checked = $checkbox.is(':checked'),
      color_id = parseInt($checkbox.attr('data-color-id'));

  if (!is_checked) { e.preventDefault(); }
  else {
    $('.js-not-checkbox[data-attr-slug="'+attr_slug+'"]').not(this).attr('checked', false); 
    if (color_id) { 
      // смена порядка фото при выборе цвета
      rebuild_carousel(attr_slug, color_id);
    }
  }
});


// ----- Кнопки "показать еще" у цветов и видео -----

$('.js-expand-colors').click(function(e) {
  e.preventDefault();

  var $button = $(this),
      attr_id = $button.attr('data-attr-id');

  $('label.color_option[data-attr-id="'+attr_id+'"]').show();
  $button.hide();
});


$('.js-expand-videos').click(function(e) {
  e.preventDefault();

  $('.js-video-item:hidden').css('display', 'block').css('margin-top', '40px');
  $(this).hide();
})


// ----- Смена порядка фото при выборе цвета -----

function _sort_by_color($arr, attr_slug, color_id) {
  // сортируем список объектов-фоток
  // первый приоритет - наличие нужного цвета (data-attrs[attr_slug][color_id]),
  // второй - первоначальный порядок (data-order)

  $arr.sort(function(a, b){
    var $a = $(a),
        $b = $(b),
        a_order = parseInt($a.attr('data-order')),
        b_order = parseInt($b.attr('data-order'))
        a_attrs = JSON.parse($a.attr('data-attrs')),
        b_attrs = JSON.parse($b.attr('data-attrs')),
        a_has_color = (a_attrs[attr_slug].indexOf(color_id)>-1),
        b_has_color = (b_attrs[attr_slug].indexOf(color_id)>-1);

    if (a_has_color && b_has_color || !a_has_color && !b_has_color) { return a_order - b_order; }
    else if (a_has_color) { return -5 }
    else { return 5 }
  });

  return $arr;
}


function _move_photos($container, $arr, set_active) {
  // перемещаем объекты-фотки в начало контейнера в нужном порядке
  $arr.each(function(i) {
    var $item = $(this);

    $item.appendTo($container);
    if (i>0) { $item.removeClass('active'); }
    else { $item.addClass('active'); }
  });
}


function rebuild_carousel(attr_slug, color_id) {

  var $container = $('.nom_img_med_wrap');

  if ($container.hasClass('js-with-photos')) {
    var $photos1 = $('.js-photo-thumb'),
        $photos2 = $('.js-photo-big'),
        $container1 = $('.js-photo-thumb-container'),
        $container2 = $('.js-photo-big-container');

    // сортируем список объектов-фоток
    $photos1 = _sort_by_color($photos1, attr_slug, color_id);
    $photos2 = _sort_by_color($photos2, attr_slug, color_id);

    // меняем и в контейнерах
    _move_photos($container1, $photos1, true);
    _move_photos($container2, $photos2, false);

    // сбрасываем карусель
    // TODO: fix
    // https://yandex.ru/search/?text=jcarousel%20reset%20prevojbect&&lr=23
    // https://stackoverflow.com/questions/1375171/jcarousel-can-you-remove-all-items-and-rebind-to-a-new-collection
    // https://stackoverflow.com/questions/906432/removing-all-li-elements-inside-a-ul-except-first-and-last-elements-in-jquery/906446#906446
    // https://sorgalla.com/jcarousel/docs/reference/usage.html
    // https://sorgalla.com/jcarousel/docs/reference/api.html#items
    // https://stackoverflow.com/questions/4589893/scroll-to-first-item-of-jcarousel
    //
    // +https://stackoverflow.com/questions/2645980/removing-an-item-from-jcarousel-plug-in
    // https://stackoverflow.com/questions/4299661/jcarousel-unload-disable-remove
    // https://stackoverflow.com/questions/1375171/jcarousel-can-you-remove-all-items-and-rebind-to-a-new-collection
    $('.nom_img_med_wrap').jcarousel('scroll', 0);
    $('.nom_img_med_wrap').jcarousel('reset');
    $('.nom_img_med_wrap').jcarousel('reload');

    $container1.css({'left': '0px', 'top': '0px'});
    $container2.css({'left': '0px', 'top': '0px'});

    $('#l_arr_nom_img').addClass('inactive');
    $('#r_arr_nom_img').removeClass('inactive');
  };
}
