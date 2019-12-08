{% load i18n %}

// ----- Добавляем в вишлист / удаляем из него -----


function changeWishlistInputData(option_id, price, attrs, extra_products) {
  var $input = $('.js-wishlist-input');

  if ($input.length) {
    option_id = (option_id || 0).toString();
    price = (price || 0).toString();
    attrs = JSON.stringify(attrs || {}),
    extra_products = JSON.stringify(extra_products || {});

    if (option_id) {
      $input.attr('data-option-id', option_id);
      $input.attr('data-price', price);
      $input.attr('data-attrs', attrs);
      $input.attr('data-extra-products', extra_products);
    };
  }
}


function sendWishlistItemData($input, dontShowPopup) {
  if (!areCookiesEnabled) { alertCookiesDisabled(); return false; }
  dontShowPopup = dontShowPopup || false;

  var add_url = $input.attr('data-add-url'),
      remove_url = $input.attr('data-remove-url'),
      product_id = parseInt($input.attr('data-product-id')),
      option_id = parseInt($input.attr('data-option-id')),
      price = parseFloat($input.attr('data-price') || 0.0),
      attrs = JSON.parse($input.attr('data-attrs') || {}),
      extra_products = JSON.parse($input.attr('data-extra-products') || {}),
      fromProductPage = $input.hasClass('js-from-product-page'),
      fromCartPage = $input.hasClass('js-from-cart-page'),
      adding = false,
      url,
      form_data;

  if ($input.is(':checked')) { url = add_url; adding = true; }
  else { url = remove_url; }

  form_data = {
    'product_id': product_id,
    'option_id': option_id,
    'price': price,
    'attrs': attrs,
    'extra_products': extra_products,
  };

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      var err = res['error'],
          result = res['result'],
          wishlist_count = res['wishlist_count'];

      if (result == 'ok') {
        if (wishlist_count != undefined) { $('.js-wishlist-count').text(wishlist_count); }
        if (fromProductPage && adding && !dontShowPopup) { showWishlistPopup(); }
        if (fromCartPage) {
          var $item_div = $input.parents('.js-item-div'),
              $item_count_input = $item_div.find('input[name="item-count"]'),
              count = $input.attr('data-count') || 1;
          if (adding) { $item_count_input.val(0); }
          else { $item_count_input.val(count); }
          $item_count_input.change();
        }
      }
      else {
        if (error) { alert('{% trans "При отправке формы произошла ошибка" %}: ', error); }
        else { alert('{% trans "При отправке формы произошла ошибка" %}: ', res.status + ' ' + res.statusText); }
      };
    },
    error: function(res){
      if (res.status == 400) {
        var response;
        if (res.responseJSON == undefined) { response = JSON.parse(res.responseText); }
        else { response = res.responseJSON; }

        if (response != undefined) {
          var click_to = response['click_to'],
              error = response['error'],
              alert_message = response['alert_message'];

          if (error) { alert('{% trans "При отправке формы произошла ошибка" %}: ', error); };
          if (click_to) { $(click_to).click(); };
          if (alert_message) { alert(alert_message); };
        } else {
          alert('{% trans "При отправке формы произошла ошибка" %}: ', res.status + ' ' + res.statusText);
        };
      } else {
        if (res.status == 0) { alert('{% trans "Произошла ошибка" %}: 500 Internal Server Error') }
        else { alert('{% trans "Произошла ошибка" %}: ' + res.status + ' ' + res.statusText); }
      }
    }
  });
}


$('body').on('change', '.js-wishlist-input', function(e){
  var $input = $(this);
  sendWishlistItemData($input);
  // console.log('onchange js-wishlist-input');
});


function checkWishlistAndClick(show_errors, just_change) {
  show_errors = show_errors || false;
  just_change = just_change || false;

  // console.log('checkWishlistAndClick');

  var $button = $('.js-wishlist-button'),
      $input = $button.siblings('.js-wishlist-input');

  if ($input.length) {
    if ($input.is(':checked') && !just_change) {
      $input.click();
      $button.text('{% trans "Добавить в список желаемых покупок" %}');
    }
    else {
      var option = data['option'];
      if (option['id']) {
        collected_data = collectAttrs(option);
        _attrs = collected_data['_attrs'];
        _extra_products = collected_data['_extra_products'];
        errors = collected_data['errors'];
        if (errors.length) {
          if (show_errors) { showErrorPopup('{% trans "Пожалуйста, выберите одно из значений" %}:', errors.join('<br/>')); };
          return;
        }
        else {
          if (just_change) {
            sendWishlistItemData($input, true);
          } else {
            $input.click();
            $button.text('{% trans "Удалить из списка желаемых покупок" %}');
          }
        }
      } else {
        if (show_errors) { showErrorPopup('{% trans "Такого товара нет в наличии" %}'); };
      }
    };
  } else {
    // console.log('error: no input near');
  }
}


$('body').on('click', '.js-wishlist-button', function(e){
  e.preventDefault();
  checkWishlistAndClick(true, false);
  // console.log('onclick js-wishlist-button');
});


$('body').on('click', '.js-wishlist-cart-button', function(e){
  e.preventDefault();

  var $button = $(this),
      $form = $button.parents('.js-product-form'),
      $input = $form.find('.js-wishlist-input'),
      option_id = parseInt($input.attr('data-option-id')),
      price = parseFloat($input.attr('data-price') || 0.0),
      _attrs = JSON.parse($input.attr('data-attrs') || {}),
      _extra_products = JSON.parse($input.attr('data-extra-products') || {}),
      count = 1,
      // prices = {'count': count, 'option': price},
      prices = {'count': count},
      $wishlistInput = $form.find('.js-wishlist-input'),
      data = null;

  submitProductForm($form, $button, option_id, _attrs, _extra_products, data, count, prices, $wishlistInput);
  // console.log('onclick js-wishlist-cart-button');
});
