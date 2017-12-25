
// ----- Функции по смене цены -----

function updateShownCheckboxes(options, attr_types) {
  // скрываем/показываем цвета при выборе фасонов (на основании получившихся вариантов)

  var attr_types = attr_types || ['color', 'size'];

  $.each(data['attrs'], function(slug, attr){
    if ((attr['category'] == 'primary') && (attr_types.indexOf(attr['type'])>-1)) {
      var $checkboxes = $('.js-attr-checkbox[data-attr-slug="'+slug+'"]'),
          ids = [];

      $.each(options, function(i, option){
        ids = ids.concat(option['attrs'][slug]);
      });

      $.each($checkboxes, function(i, checkbox){
        var $checkbox = $(this),
            $parent = $checkbox.parents('label');
            option_id = parseInt($checkbox.attr('data-option-id'));


        if (ids.indexOf(option_id) > -1) { $parent.show(); }
        else { $parent.hide(); }
      });

    };
  })
}


function filterOptions(attr_types) {
  // получаем список выбранных на данный момент вариантов (можно отфильтровать по типам атрибутов)

  var attr_types = attr_types || ['style', 'color', 'size']
      options = {};

  $.each(data['options'], function(i, item){
    options[i] = item;
  });

  $.each(data['attrs'], function(slug, attr){
    if ((attr['category'] == 'primary') && (attr_types.indexOf(attr['type'])>-1)) {
      var $checkboxes = $('.js-attr-checkbox[data-attr-slug="'+slug+'"]:visible'),
          $checked = $checkboxes.filter(':checked'),
          chosen_id;

      if ($checkboxes.length == 1) { chosen_id = $($checkboxes[0]).attr('data-option-id'); }
      else if ($checked.length) { chosen_id = $($checked[0]).attr('data-option-id'); }

      chosen_id = parseInt(chosen_id);

      if (chosen_id) {
        $.each(options, function(i, option){
          if (option['attrs'][slug].indexOf(chosen_id) == -1) { delete options[i] };
        });
      }
    };
  })

  return options;
}


function chooseOption(update_total_price) {
  // получаем выбранный вариант и прописываем его везде
  // update_total_price (true|false) - обновляем ли общую стоимость

  var options = filterOptions(),
      option = {},
      update_total_price = update_total_price || false;
      count = data['prices']['count'],
      maximum_in_stock = 0;

  $.each(options, function(i, item){
    if (!Object.keys(option).length || ((count>maximum_in_stock) && (count<=item['in_stock']))) {
      maximum_in_stock = item['in_stock'];
      option = item;
      data['prices']['option'] = item['price'];
    }
  });

  if (data['prices']['extra']) {
    data['prices']['maximum_in_stock'] = Math.min(maximum_in_stock, data['prices']['extra_maximum_in_stock']);
  } else {
    data['prices']['maximum_in_stock'] = maximum_in_stock;
  }
  data['option'] = option;

  if (update_total_price) { updateTotalPrice(true) };
}


function updateCartButton() {
  // обновляем надпись и тип кнопки "добавить"

  var $button = $('.js-cart-button'),
      $blocks_to_hide = $('.js-hide-if-not-option')
      p = data['prices'];

  if (!Object.keys(data['option']).length) {
    $blocks_to_hide.hide();
    $button.addClass('_disabled');

    $button.text('Такого товара нет в наличии');
    $button.attr('data-type', 'none');
  } else {
    $blocks_to_hide.show();
    $button.removeClass('_disabled');

    if (p['count'] > p['maximum_in_stock']) {
      $button.text('Под заказ');
      $button.attr('data-type', 'order');
    } else {
      $button.text('В корзину');
      $button.attr('data-type', 'add');
    }
  }
}


function updateTotalPrice(update_cart_button) {
  // обновляем общую стоимость
  // update_cart_button (true/false) - обновлять ли еще при этом надпись на кнопке

  var $price_label = $('.js-cart-price'),
      update_button = update_button || true,
      p = data['prices'],
      total_price;

  if (update_cart_button) {
    chooseOption(false);  // на случай, что кол-во увеличилось - выбираем вариант с нужным кол-вом
  }

  total_price = (p['option']+p['extra'])*p['count'] + p['wrapping'];
  data['prices']['total'] = total_price;

  $price_label.text(total_price);
  if (update_cart_button) {
    updateCartButton(); 
  }
}


function updateCount(count) {
  // обновляем количество товара
  data['prices']['count'] = count;
  updateTotalPrice(true);
}


function changeExtraProduct(extra_product_id, is_checked) {
  // добавляем или удаляем дополнительный товар (is_checked == true/false)

  var extra_p = data['extra_products'][extra_product_id],
      selected = data['extra_p_selected'],
      price_extra = 0,
      extra_maximum_in_stock = 9999;
      maximum_in_stock = data['option']['in_stock'] || 0;

  if (extra_p) {
    if (is_checked) { selected[extra_product_id] = extra_p }
    else { delete selected[extra_product_id] };

    $.each(selected, function(i, item) {
      price_extra += item['price'];
      if (item['in_stock'] < maximum_in_stock) { maximum_in_stock = item['in_stock'] };      
      if (item['in_stock'] < extra_maximum_in_stock) { extra_maximum_in_stock = item['in_stock'] };      
    });

    data['prices']['extra'] = price_extra;
    data['prices']['extra_maximum_in_stock'] = extra_maximum_in_stock;
    data['prices']['maximum_in_stock'] = maximum_in_stock;
    updateTotalPrice(true);
  }
}


function changeGiftWrapping(price, is_checked) {
  // добавляем или удаляем подарочную упаковку (is_checked == true/false)

  var price = parseInt(price);

  if (is_checked) { data['prices']['wrapping'] = price; }
  else { data['prices']['wrapping'] = 0; };

  updateTotalPrice(false);
}


// ----- Триггеры, связанные со сменой цены -----

$('.js-extra-product-trigger').click(function(e) {
  var $obj = $(this),
      extra_product_id = $obj.attr('data-extra-product-id'),
      is_checked = $obj.is(':checked');

  changeExtraProduct(extra_product_id, is_checked);
});

$('.js-gift-wrapping-trigger').click(function(e) {
  var $obj = $(this),
      gift_wrapping_price = $obj.attr('data-wrapping-price'),
      is_checked = $obj.is(':checked');

  changeGiftWrapping(gift_wrapping_price, is_checked);
});


// ----- Клик по чекбоксу (превращаем их в радиобаттоны + вызываем пересчет цен) -----

$('.js-not-checkbox').click(function(e) {
  var $checkbox = $(this),
      attr_slug = $checkbox.attr('data-attr-slug'),
      attr_type = $checkbox.attr('data-attr-type'),
      is_checked = $checkbox.is(':checked'),
      color_id = parseInt($checkbox.attr('data-color-id'));

  if (is_checked) {
    $('.js-not-checkbox[data-attr-slug="'+attr_slug+'"]').not(this).attr('checked', false); 
    if (color_id) { 
      // смена порядка фото при выборе цвета
      rebuildCarousel(attr_slug, color_id);
    }
  }  // else { e.preventDefault(); }

  if (attr_type) {
    if (attr_type == 'style') {
      $('.js-expand-colors').click();
      options = filterOptions(['style']);
      updateShownCheckboxes(options, ['color', 'size']);
    } else if (attr_type == 'color') {
      options = filterOptions(['style', 'color']);
      updateShownCheckboxes(options, ['size']);
    };
    chooseOption(true);
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
