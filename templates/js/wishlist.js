
// ----- Добавляем в вишлист / удаляем из него -----


function changeWishlistInputData(price, attrs) {
  var $input = $('.js-wishlist-input');

  if ($input.length) {
    price = (price || 0).toString();
    attrs = JSON.stringify(attrs || {});

    $input.attr('data-price', price);
    $input.attr('data-attrs', attrs);
  }
}


$('.js-wishlist-input').on('change', function(e) {
  var $input = $(this),
      add_url = $input.attr('data-add-url'),
      remove_url = $input.attr('data-remove-url'),
      product_id = parseInt($input.attr('data-product-id')),
      price = parseFloat($input.attr('data-price') || 0.0),
      attrs = JSON.parse($input.attr('data-attrs') || {}),
      url,
      form_data;

  if ($input.is(':checked')) { url = add_url; }
  else { url = remove_url; }

  form_data = {
    'product_id': product_id,
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

});


$('.js-wishlist-button').click(function(e) {
  e.preventDefault();

  var $button = $(this),
      $input = $button.siblings('.js-wishlist-input');

  if ($input.length) {
    if ($input.is(':checked')) { $button.text('Добавить в список желаемых покупок'); }
    else { $button.text('Удалить из списка желаемых покупок'); };
    $input.click();
  } else {
    console.log('error: no input near');
  }
});
