

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
      rebuildCarousel(attr_slug, color_id);
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

function rebuildCarousel(attr_slug, color_id) {
  // меняем порядок фоток в главом слайдере при выборе цвета

  var $carousel = $('.nom_img_med_wrap');

  if ($carousel.hasClass('js-with-photos')) {

    var $photos1 = $('.js-photo-thumb'),
        $photos2 = $('.js-photo-big'),
        $buttons = $('.js-navigation-button'),
        $container1 = $('.js-photo-thumb-container'),
        $container2 = $('.js-photo-big-container'),
        $container3 = $('.js-navigation-buttons');

    // сортируем список объектов-фоток
    $photos1 = sortPhotosByColor($photos1, attr_slug, color_id);
    $photos2 = sortPhotosByColor($photos2, attr_slug, color_id);

    // перемещаем фотки и сбасываем state у фоток и кнопок навигации
    movePhotos($container1, $photos1, true);
    movePhotos($container2, $photos2, false);
    movePhotos($container3, $buttons, false);

    // скроллим карусель к первому элементу
    $carousel.jcarousel('scroll', 0);
    $container1.css({'left': '0px', 'top': '0px'});
    $container2.css({'left': '0px', 'top': '0px'});

    // сбрасываем карусель
    $carousel.jcarousel('destroy');
    {% include 'catalog/include/init_product_photos.js' %}
  };
}


function sortPhotosByColor($arr, attr_slug, color_id) {
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


function movePhotos($container, $arr, set_active) {
  // перемещаем объекты-фотки в начало контейнера в нужном порядке:
  // клонируем их в нужном порядке без сохранения state, оригиналы удаляем
  $arr.each(function(i) {
    var $item = $(this);

    $item.clone().appendTo($container);
    $item.remove();

    // $item.appendTo($container);
    // if (i>0) { $item.removeClass('active'); }
    // else { $item.addClass('active'); }
  });
}
