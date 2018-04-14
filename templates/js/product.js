{% load i18n %}

// ----- Офомление заказа -----

// function showSuccessPopup() {
//   var success_popup_id = 'success-popup',
//       $a = $('a[href="#'+success_popup_id+'"]'),
//       $popup = $('#'+success_popup_id+'');

//   $('a[rel*=leanModal1]').leanModal({ top : 200, closeButton: ".js-call-close" });
//   $a.click();
// };


// function showErrorPopup(title, text) {
//   var error_popup_id = 'error-popup',
//       title = title || '',
//       text = text || '',
//       $a = $('a[href="#'+error_popup_id+'"]'),
//       $popup = $('#'+error_popup_id+''),
//       $popup_title = $popup.find('.popup_title'),
//       $popup_text = $popup.find('.popup_text');

//   $('a[rel*=leanModal1]').leanModal({ top : 200, closeButton: ".js-call-close" });

//   $popup_title.text(title);
//   $popup_text.html(text);
//   $a.click();
// };


function parsePrice(price) {
  // console.log(price, typeof(price));
  if (parseInt(price) == parseFloat(price)) { return price; }
  else { return price.toFixed(2); }
}


function submitProductForm($form, $button, option_id, _attrs, _extra_products, data, count, prices, $wishlistInput) {
  var data = data || {'prices': {}},
      url = $form.attr('action'),
      product_id = parseInt($form.find('input[name="product_id"]').val()),
      count = count || data.prices.count,
      prices = prices || data.prices,
      form_data;

  form_data = {
    'product_id': product_id,
    'option_id': option_id,
    'attrs': _attrs,
    'extra_products': _extra_products,
    'count': count,
    'prices': prices,
  };

  $button.addClass('_disabled');

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    // processData: false,
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      $button.removeClass('_disabled');

      var error = res['error'],
          errors = res['errors'],
          result = res['result'],
          cart_count = res['count'],
          cart_summary = res['summary'],
          product_link = res['product_link'];

      if (result == 'ok') {
        if (cart_count) { $('.js-cart-count').text(cart_count); }
        if (cart_summary) { $('.js-cart-summary').text(cart_summary); }
        if (product_link) { $('.js-product-continue-link').attr('href', product_link); }
        if ($wishlistInput && $wishlistInput.length && $wishlistInput.is(':checked')) {
          $wishlistInput.click();
        }
        $('.js-call-close').filter(':visible').click();
        setTimeout( function() {
          showPopup('#success-popup');
        }, 500);
      }
      else {
        if (error) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', error); }
        if (errors) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', errors); }
        else { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', res.status + ' ' + res.statusText); }
      };
    },
    error: function(res){
      $button.removeClass('_disabled');

      if (res.status == 400) {
        var response;
        if (res.responseJSON == undefined) { response = JSON.parse(res.responseText); }

        if (response != undefined) {
          var click_to = response['click_to'],
              error = response['error'],
              errors = response['errors'],
              alert_message = response['alert_message'];

          if (error) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', error); };
          if (errors) { add_errors($form, errors, true); };
          if (click_to) { $(click_to).click(); };
          if (alert_message) { alert(alert_message); };
        } else {
          showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', res.status + ' ' + res.statusText);
        };
      } else {
        if (res.status == 0) { alert('{% trans "Произошла ошибка" %}: 500 Internal Server Error') }
        else { alert('{% trans "Произошла ошибка" %}: ' + res.status + ' ' + res.statusText); }
      }
    }
  });
};


function collectExtraProductsAttrs(errors, _id) {
  var _extra_products = {},
      errors = errors || [],
      _id = _id || false,
      _data;

  $.each(data.extra_products, function(id, product){
    var $product_trigger = $('.js-extra-product-trigger[data-extra-product-id="'+id+'"]'),
        product_obj = {};

    if (_id && (id == _id) || !_id && $product_trigger.is(':checked')) {
      $.each(product.attrs, function(slug){
        var $checkboxes = $('.js-attr-checkbox[data-attr-slug="'+slug+'"]').filter(':visible'),
            checked_id = $checkboxes.filter(':checked').attr('data-option-id');

        if ($checkboxes.length == 1) { checked_id = $($checkboxes[0]).attr('data-option-id'); };

        if (checked_id) { product_obj[slug] = parseInt(checked_id); }
        else { errors.push(product['title'] + ': ' + data.attrs[slug]['title']); }
      });

      _extra_products[id] = product_obj;
    }
  });

  _data = {
    'errors': errors,
    '_extra_products': _extra_products,
  };
  return _data;
}


function collectAttrs(option) {
  // собираем чекнутые атрибуты в виде словариков (для передачи на бекенд)
  option = option || data['option'];

  var _attrs = {},
      _extra_products = {},
      errors = [],
      _extra_data,
      _data;

  if (option.attrs) {
    $.each(option.attrs, function(slug){
      var $checkboxes = $('.js-attr-checkbox[data-attr-slug="'+slug+'"]').filter(':visible'),
          checked_id = $checkboxes.filter(':checked').attr('data-option-id');

      if ($checkboxes.length == 1) { checked_id = $($checkboxes[0]).attr('data-option-id'); };

      if (checked_id) { _attrs[slug] = parseInt(checked_id); }
      else { errors.push(data.attrs[slug]['title']) }
    });

    _extra_data = collectExtraProductsAttrs(errors);
    _extra_products = _extra_data['_extra_products'];
    errors = _extra_data['errors'];
  }

  _data = {
    '_attrs': _attrs,
    '_extra_products': _extra_products,
    'errors': errors,
  };
  return _data;
}


$('.js-cart-button').click(function(e){
  e.preventDefault();

  var $button = $(this),
      $form = $button.parents('.js-product-form'),
      option = data.option || {},
      _attrs = {},
      _extra_products = {},
      errors = [];

  if (!$form.length) { $form = $('.js-product-form'); }

  if (!Object.keys(option).length) {
    showErrorPopup('{% trans "Произошла ошибка" %}:', '{% trans "Такого товара нет в наличии" %}.');
    return;
  }

  collected_data = collectAttrs(option);

  _attrs = collected_data['_attrs'];
  _extra_products = collected_data['_extra_products'];
  errors = collected_data['errors'];

  if (errors.length) { showErrorPopup('{% trans "Пожалуйста, выберите одно из значений" %}:', errors.join('<br/>')); }
  else { submitProductForm($form, $button, option['id'], _attrs, _extra_products, data); }
})


// ----- Функции по смене цены -----

function updateShownCheckboxes(options, attr_types) {
  // скрываем/показываем цвета при выборе фасонов (на основании получившихся вариантов)

  var attr_types = attr_types || ['color', 'size'];

  $.each(data['attrs'], function(slug, attr){
    if ((attr['category'] == 'primary') && (attr_types.indexOf(attr['type'])>-1)) {
      var $checkboxes = $('.js-attr-checkbox[data-attr-slug="'+slug+'"]'),
          $labels = $('label[data-attr-slug="'+slug+'"]'),
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

      // if (attr['type'] == 'color') {
      //   $.each($labels, function(i, checkbox){
      //     var $label = $(this);

      //     if ($label.is(':hidden')) { $label.removeClass('js-can-be-shown'); }
      //     else { $label.addClass('js-can-be-shown'); }
      //   });

      //   var $shown_checkboxes = $checkboxes.filter(':visible');

      //   if ($shown_checkboxes.length > 4) {
      //     var checked_id = $shown_checkboxes.filter(':checked').attr('data-option-id'),
      //         can_hide = false;

      //     console.log(checked_id);

      //     if (!checked_id) { can_hide = true; }
      //     else {
      //       $.each($shown_checkboxes, function(i, item) {
      //         if (i > 4) {
      //           var $checkbox = $(item);
      //           if ($checkbox.attr('data-option-id') == checked_id) {
      //             can_hide = true;
      //           }
      //         }
      //       });
      //     }

      //     if (can_hide) { console.log('HIDE'); }
      //     else { console.log('NOT HIDE'); }
      //   }
      // }
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


function isNotEmpty(obj) {
  return Object.getOwnPropertyNames(obj).length;
}


function chooseOption(update_total_price, dont_update_wishlist_input) {
  // получаем выбранный вариант и прописываем его везде
  // update_total_price (true|false) - обновляем ли общую стоимость

  var options = filterOptions(),
      option = {},
      update_total_price = update_total_price || false;
      dont_update_wishlist_input = dont_update_wishlist_input || false;
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

  if (!dont_update_wishlist_input) {
    collected_data = collectAttrs(option);

    _attrs = collected_data['_attrs'];
    _extra_products = collected_data['_extra_products'];
    errors = collected_data['errors'];

    if (isNotEmpty(_attrs) && isNotEmpty(option) && !errors.length) {
      // console.log('wishlist change', _attrs, errors, option);
      changeWishlistInputData(data['option']['id'], data['prices']['option'] + data['prices']['extra'], _attrs, _extra_products);
      // var $input = $('.js-wishlist-input'));
      // if ($input.length && $input.is(':checked')) { checkWishlistAndClick(false, true); }
    }

    var $input = $('.js-wishlist-input'),
        $button = $('.js-wishlist-button');
    if ($input.length) { $input.attr('checked', false); };
    if ($button.length) { $button.text('{% trans "Добавить в список желаемых покупок" %}'); };
  };
}


function updateCartButton() {
  // обновляем надпись и тип кнопки "добавить"

  var $button = $('.js-cart-button'),
      $blocks_to_hide = $('.js-hide-if-not-option')
      p = data['prices'];

  if (!Object.keys(data['option']).length) {
    $blocks_to_hide.hide();
    $button.addClass('_disabled');

    $button.text('{% trans "Такого товара нет в наличии" %}');
    $button.attr('data-type', 'none');
  } else {
    $blocks_to_hide.show();
    $button.removeClass('_disabled');

    if (p['count'] > p['maximum_in_stock']) {
      $button.text('{% trans "Под заказ" %}');
      $button.attr('data-type', 'order');
    } else {
      $button.text('{% trans "В корзину" %}');
      $button.attr('data-type', 'add');
    }
  }
}


function updateTotalPrice(update_cart_button) {
  // обновляем общую стоимость
  // update_cart_button (true/false) - обновлять ли еще при этом надпись на кнопке

  var $price_label = $('.js-cart-price'),
      $base_price_label = $('.js-base-price'),
      update_button = update_button || true,
      p = data['prices'],
      total_price;

  if (update_cart_button) {
    chooseOption(false);  // на случай, что кол-во увеличилось - выбираем вариант с нужным кол-вом
  }

  // console.log(data);

  base_price = (p['option']+p['extra'])*p['count'] + p['wrapping'];
  data['prices']['base'] = total_price;

  discount_price = (p['option']*p['count'])*p['discount'] / 100
  total_price = (p['option']+p['extra'])*p['count'] + p['wrapping'] - discount_price
  data['prices']['total'] = total_price;
  data['prices']['discount_price'] = discount_price;

  $base_price_label.text(parsePrice(base_price));
  $price_label.text(parsePrice(total_price));
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

  var price = parseFloat(price);

  if (is_checked) {
    data['prices']['wrapping'] = price;
    data['prices']['with_wrapping'] = true;
  }
  else {
    data['prices']['wrapping'] = 0;
    data['prices']['wrapping'] = false;
  };

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
  }

  if (attr_type == 'style') {
    $('.js-expand-colors').click();
    options = filterOptions(['style']);
    updateShownCheckboxes(options, ['color', 'size']);
  } else if (attr_type == 'color') {
    options = filterOptions(['style', 'color']);
    updateShownCheckboxes(options, ['size']);
  };

  if ($checkbox.hasClass('js-extra-product-attr')) {
    var $extraParent = $checkbox.parents('.js-extra-product-parent');
        extra_product_id = parseInt($extraParent.attr('data-extra-product-id')),
        $extraProductTrigger = $extraParent.find('.js-extra-product-trigger')
        extra_is_checked = $extraProductTrigger.is(':checked'),

        _extra_data = collectExtraProductsAttrs([], extra_product_id),
        _extra_product = _extra_data['_extra_products'][extra_product_id],
        _extra_length = Object.keys(_extra_product).length,
        _errors_length = _extra_data['errors'].length;

    console.log('extra_length', _extra_length, 'errors_length', _errors_length);

    if (is_checked && !extra_is_checked && !_errors_length) { console.log('check!'); $extraProductTrigger.click(); }
    else if (!is_checked && extra_is_checked && !_extra_length) { console.log('uncheck!'); $extraProductTrigger.click(); }
  }

  chooseOption(true);
});


// ----- Кнопки "показать еще" у цветов и видео -----

$('.js-expand-colors').click(function(e) {
  e.preventDefault();

  var $button = $(this),
      attr_id = $button.attr('data-attr-id');

  $('label.color_option.js-can-be-shown[data-attr-id="'+attr_id+'"]').show();
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
    {% include 'js/init_product_photos.js' %}
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
