{% load i18n %}

// ----- Отправка форм на бекенд: вспомогательные функции -----


function checkCartMethods() {
  var $deliveryMethods = $('[name="delivery_method_id"]'),
      $paymentMethods = $('[name="payment_method_id"]');


  // --- скрываем способы оплаты ---

  var $deliveryMethod = $deliveryMethods.filter(':checked:visible');

  if ($deliveryMethod.length) {
    var ids = JSON.parse($deliveryMethod.attr('data-payment-ids')),
        $labels = $('.js-payment-method-label');

    if (ids && ids.length) {
      $labels.hide();
      $.each(ids, function(i, method_id){
        // $labels.find('[data-payment-method-id="'+method_id+'"]').show();
        $('[data-payment-method-id="'+method_id+'"]').show();
      });
    }
  }

  // // --- скрываем способы доставки ---

  // var $paymentMethod = $paymentMethods.filter(':checked:visible');

  // if ($paymentMethod.length) {
  //   var ids = JSON.parse($paymentMethod.attr('data-delivery-ids')),
  //       $labels = $('.js-delivery-method-label');

  //   if (ids && ids.length) {
  //     $labels.hide();
  //     $.each(ids, function(i, method_id){
  //       // $labels.find('[data-delivery-method-id="'+method_id+'"]').show();
  //       $('[data-delivery-method-id="'+method_id+'"]').show();
  //     });
  //   }
  // }
}


function showOrHide(cart_count) {
  if (cart_count) {
    $('.js-disabled-if-not-cart').removeClass('_disabled');
    $('.js-show-if-not-cart').hide();
    $('.js-hide-if-not-cart').show();
  } else {
    $('.js-disabled-if-not-cart').addClass('_disabled');
    $('.js-show-if-not-cart').show();
    $('.js-hide-if-not-cart').hide();
  }
};


function showErrorPopup(title, text) {
  var error_popup_id = 'error-popup',
      title = title || '',
      text = text || '',
      $a = $('a[href="#'+error_popup_id+'"]'),
      $popup = $('#'+error_popup_id+''),
      $popup_title = $popup.find('.popup_title'),
      $popup_text = $popup.find('.popup_text');

  $('.window_popap').hide();
  $('a[rel*=leanModal1]').leanModal({ top : 200, closeButton: ".js-call-close" });

  if (title) { $popup_title.text(title); };
  $popup_text.html(text);
  $a.click();
};


function showPopup(popup_id, old_popup_id) {
  var $a = $('a[href="'+popup_id+'"]'),
      $popup = $(popup_id),
      $closeButtons = $('.js-call-close').filter(':visible');

  $('.window_popap').hide();
  $('a[rel*=leanModal1]').leanModal({ top : 200, closeButton: ".js-call-close" });
  $a.click();
  $('html, body').animate({scrollTop: $popup.offset().top-75}, 400);
};


function getFormData($form){
  // FROM: https://stackoverflow.com/a/11339012
  var unindexed_array = $form.serializeArray();
  var indexed_array = {};

  $.map(unindexed_array, function(n, i){ indexed_array[n['name']] = n['value']; });
  return indexed_array;
};


function removeErrors($form) {
    $form.find('.error').removeClass('error');
    $form.find('.err-message').remove();
}


function addErrors($form, errors, without_errors, without_names) {
  var $error_messages = $form.find('.error-messages'),
      without_errors = without_errors || false,
      without_names = without_names || false;

  errors.forEach(function(item, i, list) {
    var error = item.error_message,
        name = item.label || item.name;

    if (name == '__all__') {
      if (error && !without_errors) { $error_messages.append('<div class="err-message">' + error + '<br/></div>'); };
    } else {
      $form.find('[name="'+item.name+'"]').addClass('error');
      if (error && !without_errors) {
        if (without_names) { $error_messages.append('<div class="err-message">' + error + '<br/></div>'); }
        else { $error_messages.append('<div class="err-message">' + name + ': ' + error + '<br/></div>'); }
      }
    }
  });
}


function rotateSpecialOffers() {
  var $offers = $('.js-special-offer');

  if ($offers.length && ($offers.length > 1)) {
    var $visibleOffer = $('.js-special-offer:visible'),
        $offerToShow;

    if ($visibleOffer.length) {
      $offerToShow = $visibleOffer.next();
      if (!$offerToShow.hasClass('js-special-offer') || $offerToShow.is(':visible')) {
        $offerToShow = $($offers[0]);
      }
      $offers.hide();
      $offerToShow.show();
      setTimeout(rotateSpecialOffers, 6000);
    }
  }
  
}



// ----- Отправка форм на бекенд -----

function sendSomeForm(url, form_data, send_type, $to_disable, $form, $item_div, $row_clear_div) {
  if ($to_disable) { $to_disable.addClass('_disabled'); };
  $(document.activeElement).blur();

  var yametrics_enabled = typeof yaCounter26447493 !== 'undefined';

  function yaGoalCallback() {
      console.log('yandex metrics goal completed (' + send_type + ')');
  };

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    // processData: false,
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      var errors = res['errors'],
          result = res['result'],
          cart_count = res['count'],
          cart_summary = res['summary'],
          order_number = res['order_number'],
          item_count = res['item_count'],
          item_price = res['item_price'],
          item_base_price = res['item_price_without_discount'],
          popup = res['popup'],
          shipping_data = res['profile_shipping_data'];

      if ($to_disable) { $to_disable.removeClass('_disabled'); };
      if (send_type == 'remove') {
        if ($item_div) { $item_div.slideUp(function() { $item_div.remove(); }); };
        if ($row_clear_div) { $row_clear_div.slideUp(function() { $row_clear_div.remove(); }); };
      }

      if (result == 'ok') {
        if (cart_count != undefined) {
          showOrHide(cart_count);
          $('.js-cart-count').text(cart_count); 
        }
        if (cart_summary != undefined) { $('.js-cart-summary').text(cart_summary); }
        if (order_number != undefined) { $('.js-order-number').text(order_number); }
        if ($item_div && send_type == 'set') {
          if (item_count != undefined) {
            $item_div.find('input[name="item-count"]').val(item_count);
            if (item_count > 0) { $item_div.find('.js-with-data-count').attr('data-count', item_count); }
          }
          if (item_price != undefined) { $item_div.find('.item-summary-span').html(item_price); }
          if (item_base_price != undefined) { $item_div.find('.item-base-summary-span').html(item_base_price); }
        };
        if (send_type == 'step0') {
          if (yametrics_enabled) {
            yaCounter26447493.reachGoal('button_zakaz', {}, yaGoalCallback);
          };
        }
        if (send_type == 'step1') {
          $('.js-auth-switch').toggle();
          if (shipping_data) {
            $.each(shipping_data, function(slug, value){
              var $input = $('#step3').find('[name="'+slug+'"]');
              $input.val(value);
              if (slug == 'email') { $('.js-email-cart-input').remove(); };
            });
          }
          {% include 'js/csrf.js' %}
          if (yametrics_enabled) {
            if ($form.hasClass('js-step1-login-form')) {
              yaCounter26447493.reachGoal('zakaz_login', {}, yaGoalCallback);
            }
            else if ($form.hasClass('js-step1-registration-form')) {
              yaCounter26447493.reachGoal('zakaz_registration', {}, yaGoalCallback);
            }
          };
        }
        if (send_type == 'step3') {
          showOrHide(0);
          $('.js-cart-count').text(0);
          $('.js-cart-summary').text(0);
          $('#step4 .js-cart-summary').text(cart_summary);
          $('#step5 .js-cart-summary').text(cart_summary);
          if (yametrics_enabled) {
            var yaGoalParams = {
              order_price: parseFloat(res['ya_summary'] || 0.0),
              currency: res['ya_currency'] || 'RUB',
              city: form_data['city'],
            };
            yaCounter26447493.reachGoal('zakaz_form', yaGoalParams, yaGoalCallback);
          };
        }
        if (popup) {
          showPopup(popup);
          $('html, body').animate({scrollTop: $(popup).offset().top-75}, 400);
          if (popup == '#step5') { setTimeout(rotateSpecialOffers, 6000); }
        };
      }
      else {
        if (error) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', error); }
        else if (errors) { 
          if ($form) { addErrors($form, errors); }
          else { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', errors); }
        }
        else { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', res.status + ' ' + res.statusText); }
      };
    },
    error: function(res){
      if ($to_disable) { $to_disable.removeClass('_disabled'); };

      if (res.status == 400) {
        var response;
        if (res.responseJSON == undefined) { response = JSON.parse(res.responseText); }

        if (response != undefined) {
          var click_to = response['click_to'],
              popup = response['popup'],
              error = response['error'],
              errors = response['errors'],
              alert_message = response['alert_message'];

          if (error) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', error); }
          else if (errors) { 
            if ($form) { addErrors($form, errors); }
            else { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', errors); }
          };
          if (click_to) { $(click_to).click(); };
          if (popup) { showPopup(popup); };
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
}


function setItem($item_div, count, with_wrapping) {
  var url = $item_div.attr('data-set-url'),
      item_id = parseInt($item_div.attr('data-item-id')),
      form_data;

  form_data = {
    'item_id': item_id,
    'count': count,
    'prices': {
      'with_wrapping': with_wrapping,
    },
  };
  sendSomeForm(url, form_data, 'set', null, null, $item_div, null);
};


function removeItem($item_div) {
  var url = $item_div.attr('data-remove-url'),
      item_id = parseInt($item_div.attr('data-item-id')),
      $row_clear_div = $($item_div.attr('data-row-clear-selector')),
      form_data;

  form_data = {'item_id': item_id};
  sendSomeForm(url, form_data, 'remove', $item_div, null, $item_div, $row_clear_div);
};


$('.js-choose-cart-method').change(function() {
  var $input = $(this),
      input_name = $input.attr('name'),
      input_val = $input.val(),

      $parent = $input.parents('js-method-inputs-parent'),
      $cart_parent = $('.js-cart-parent'),
      url = $cart_parent.attr('data-update-url'),
      form_data = {};

  checkCartMethods();
  form_data[input_name] = input_val;
  sendSomeForm(url, form_data, 'choose_method', $parent);
});


$('.js-step0-button').click(function() {
  var $button = $(this),
      $cart_parent = $('.js-cart-parent'),
      url = $cart_parent.attr('data-step0-url'),
      additional_info = $('[name="additional_info"]').val() || '',
      delivery_method_id = $('[name="delivery_method_id"]:checked:visible').val() || 0,
      payment_method_id = $('[name="payment_method_id"]:checked:visible').val() || 0,
      // delivery_method_id = $('[name="delivery_method_id"]:checked:enabled').val() || 0,
      // payment_method_id = $('[name="payment_method_id"]:checked:enabled').val() || 0,
      form_data;

  form_data = {
    'additional_info': additional_info,
    'delivery_method_id': delivery_method_id,
    'payment_method_id': payment_method_id,
  };
  sendSomeForm(url, form_data, 'step0', $button);
});


$('.js-step1-login-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      $forms = $('.js-step1-form'),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($forms);
  sendSomeForm(url, form_data, 'step1', $forms, $form);
});


$('.js-step1-registration-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      $forms = $('.js-step1-form'),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($forms);

  if (form_data['password'] != form_data['password_repeat']) {
    var errors = [{name: 'password', error_message: '{% trans "Введенные пароли не совпадают" %}!'}, {name: 'password_repeat'}];
    addErrors($form, errors);
  }
  else { 
    sendSomeForm(url, form_data, 'step1', $forms, $form);
  }
});


$('.js-step3-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($form);
  sendSomeForm(url, form_data, 'step3', $form, $form);
});


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
      with_wrapping = false,
      $summary_span = $item_div.find('.item-summary-span');

  if (count >= 0) {
    // if ($gift_wrapping.is(':checked')) { gift_wrapping_price = parseFloat($gift_wrapping.attr('data-wrapping-price')); };
    if ($gift_wrapping.is(':checked')) { with_wrapping = true };
    // summary = count * base_price + gift_wrapping_price;
    // $summary_span.html(summary);
    setItem($item_div, count, with_wrapping);
  }
});


// ----- Удаление товара -----

$('.js-remove-item').click(function(e) {
  e.preventDefault();
  var $item_div = $(this).parents('.js-item-div');
  removeItem($item_div);
});
