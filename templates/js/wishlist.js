
// ----- Добавляем в вишлист / удаляем из него -----


function changeWishlistInputData(option_id, price, attrs) {
  var $input = $('.js-wishlist-input');

  if ($input.length) {
    option_id = (option_id || 0).toString();
    price = (price || 0).toString();
    attrs = JSON.stringify(attrs || {});

    if (option_id) {
      $input.attr('data-option-id', option_id);
      $input.attr('data-price', price);
      $input.attr('data-attrs', attrs);
    };
  }
}


function sendWishlistItemData($input, dontShowPopup) {
  dontShowPopup = dontShowPopup || false;

  var add_url = $input.attr('data-add-url'),
      remove_url = $input.attr('data-remove-url'),
      product_id = parseInt($input.attr('data-product-id')),
      option_id = parseInt($input.attr('data-option-id')),
      price = parseFloat($input.attr('data-price') || 0.0),
      attrs = JSON.parse($input.attr('data-attrs') || {}),
      fromProductPage = $input.hasClass('js-from-product-page'),
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
      }
      else {
        if (error) { alert('При отправке формы произошла ошибка: ', error); }
        else { alert('При отправке формы произошла ошибка: ', res.status + ' ' + res.statusText); }
      };
    },
    error: function(res){
      if (res.status == 400) {
        var response;
        if (res.responseJSON == undefined) { response = JSON.parse(res.responseText); }

        if (response != undefined) {
          var click_to = response['click_to'],
              error = response['error'],
              alert_message = response['alert_message'];

          if (error) { alert('При отправке формы произошла ошибка: ', error); };
          if (click_to) { $(click_to).click(); };
          if (alert_message) { alert(alert_message); };
        } else {
          alert('При отправке формы произошла ошибка: ', res.status + ' ' + res.statusText);
        };
      } else {
        if (res.status == 0) { alert('Произошла ошибка: 500 Internal Server Error') }
        else { alert('Произошла ошибка: ' + res.status + ' ' + res.statusText); }
      }
    }
  });
}


$('.js-wishlist-input').on('change', function(e) {
  var $input = $(this);
  sendWishlistItemData($input);
});


function checkWishlistAndClick(show_errors, just_change) {
  show_errors = show_errors || false;
  just_change = just_change || false;

  var $button = $('.js-wishlist-button'),
      $input = $button.siblings('.js-wishlist-input');

  if ($input.length) {
    if ($input.is(':checked') && !just_change) {
      $input.click();
      $button.text('Добавить в список желаемых покупок');
    }
    else {
      var option = data['option'];
      if (option['id']) {
        collected_data = collectAttrs(option);
        _attrs = collected_data['_attrs'];
        errors = collected_data['errors'];
        if (errors.length) {
          if (show_errors) { showErrorPopup('Пожалуйста, выберите одно из значений:', errors.join('<br/>')); };
          return;
        }
        else {
          if (just_change) {
            sendWishlistItemData($input, true);
          } else {
            $input.click();
            $button.text('Удалить из списка желаемых покупок');
          }
        }
      } else {
        if (show_errors) { showErrorPopup('Такого товара нет в наличии'); };
      }
    };
  } else {
    console.log('error: no input near');
  }
}


$('.js-wishlist-button').click(function(e) {
  e.preventDefault();
  checkWishlistAndClick(true, false);
});


$('body').on('click', '.js-wishlist-cart-button', function(e){
  e.preventDefault();

  var $button = $(this),
      $form = $button.parents('.js-product-form'),
      $input = $form.find('.js-wishlist-input'),
      option_id = parseInt($input.attr('data-option-id')),
      price = parseFloat($input.attr('data-price') || 0.0),
      _attrs = JSON.parse($input.attr('data-attrs') || {}),
      _extra_products = {},
      count = 1,
      prices = {'count': count, 'option': price}
      data = null;

  submitProductForm($form, $button, option_id, _attrs, _extra_products, data, count, prices);
});
