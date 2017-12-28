
// ----- Отправка форм на бекенд -----


function showOrHide(cart_count) {
  console.log(cart_count);

  if (cart_count) {
    console.log('show');
    $('.js-disabled-if-not-cart').removeClass('_disabled');
    $('.js-show-if-not-cart').hide();
    $('.js-hide-if-not-cart').show();
  } else {
    console.log('hide');
    $('.js-disabled-if-not-cart').addClass('_disabled');
    $('.js-show-if-not-cart').show();
    $('.js-hide-if-not-cart').hide();
  }
};


function setItem($item_div, count, gift_wrapping_price) {
  var url = $item_div.attr('data-set-url'),
      item_id = parseInt($item_div.attr('data-item-id')),
      form_data;

  form_data = {
    'item_id': item_id,
    'count': count,
    'prices': {
      'wrapping': gift_wrapping_price,
    },
  };

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    // processData: false,
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      var err = res['errors'],
          result = res['result'],
          cart_count = res['count'],
          cart_summary = res['summary'],
          item_count = res['item_count'],
          item_price = res['item_price'];

      if (result == 'ok') {
        if (cart_count != undefined) {
          showOrHide(cart_count);
          $('.js-cart-count').text(cart_count); 
        }
        if (cart_summary != undefined) { $('.js-cart-summary').text(cart_summary); }
        if (item_count != undefined) { $item_div.find('input[name="item-count"]').val(item_count); }
        if (item_price != undefined) { $item_div.find('.item-summary-span').html(item_price); }
      }
      else {
        if (err) { console.log(err) }
        else { console.log('error!!!') }
      };
    },
  });
};

function removeItem($item_div) {
  var url = $item_div.attr('data-remove-url'),
      item_id = parseInt($item_div.attr('data-item-id')),
      $row_clear_div = $($item_div.attr('data-row-clear-selector')),
      form_data;

  $item_div.addClass('_disabled');
  form_data = {'item_id': item_id,};

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    // processData: false,
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      var err = res['errors'],
          result = res['result'],
          cart_count = res['count'],
          cart_summary = res['summary'];

      $item_div.slideUp(function() { $item_div.remove(); });
      $row_clear_div.slideUp(function() { $row_clear_div.remove(); });

      if (result == 'ok') {
        if (cart_count != undefined) {
          showOrHide(cart_count);
          $('.js-cart-count').text(cart_count); 
        }
        if (cart_summary != undefined) { $('.js-cart-summary').text(cart_summary); }
      }
      else {
        if (err) { console.log(err) }
        else { console.log('error!!!') }
      };
    },
  });
};


// ----- Смена кол-ва товара в браузере -----

$('.minus').click(function () {
  var $input = $(this).parent().find('input');
  var count = parseInt($input.val()) - 1;
  count = count < 0 ? 0 : count;
  $input.val(count);
  $input.change();
  return false;
});

$('.plus').click(function () {
  var $input = $(this).parent().find('input');
  var count = parseInt($input.val()) + 1;
  $input.val(count);
  $input.change();
  return false;
});

$('input[name="gift_wrapping"]').click(function() {
  var $input = $(this).parents('.js-item-div').find('[name="item-count"]');
  $input.change();
});

$('input[name="item-count"]').change('keyup input', function() {
  var $input = $(this),
      $item_div = $input.parents('.js-item-div'),
      base_price = $item_div.attr('data-base-price'),
      count = this.value,
      summary = 0,
      $gift_wrapping = $item_div.find('input[name="gift_wrapping"]'),
      gift_wrapping_price = 0,
      $summary_span = $item_div.find('.item-summary-span');

  if (count >= 0) {
    if ($gift_wrapping.is(':checked')) { gift_wrapping_price = parseInt($gift_wrapping.attr('data-wrapping-price')); };
    summary = count * base_price + gift_wrapping_price;
    $summary_span.html(summary);
    setItem($item_div, count, gift_wrapping_price);
  }
});


// ----- Удаление товара -----

$('.js-remove-item').click(function(e) {
  e.preventDefault();
  var $item_div = $(this).parents('.js-item-div');
  removeItem($item_div);
});
