{% load i18n %}

// ----- Отправка форм на бекенд: вспомогательные функции -----


function removeErrors($form) {
    // $form.find('.error').removeClass('error');
    // $form.find('.err-message').remove();
    $form.find('.errr').removeClass('errr');
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
      var $input = $form.find('[name="'+item.name+'"]');
      $input.addClass('errr');
      if (error && !without_errors) {
        // if (without_names) { $error_messages.append('<div class="err-message">' + error + '<br/></div>'); }
        // else { $error_messages.append('<div class="err-message">' + name + ': ' + error + '<br/></div>'); }
        $input.siblings('.err_r').text(error);
      }
    }
  });
}

// ----- Отправка форм на бекенд -----

function sendCertificateForm(url, form_data, $to_disable, $form) {
  if (!areCookiesEnabled) { alertCookiesDisabled(); return false; }
  if ($to_disable) { $to_disable.addClass('_disabled'); };
  $(document.activeElement).blur();

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    // processData: false,
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      var error = res['error'],
          errors = res['errors'],
          result = res['result'],
          cart_count = res['count'],
          cart_summary = res['summary'];

      if ($to_disable) { $to_disable.removeClass('_disabled'); };

      if (result == 'ok') {
        if (cart_count) { $('.js-cart-count').text(cart_count); }
        if (cart_summary) { $('.js-cart-summary').text(cart_summary); }
        $('.js-call-close').filter(':visible').click();
        setTimeout( function() {
          showPopup('#success-popup');
        }, 500);
      }
      else {
        if (error) { showErrorPopup('При отправке формы произошла ошибка:', error); }
        else if (errors) { 
          if ($form) { addErrors($form, errors); }
          else { showErrorPopup('При отправке формы произошла ошибка:', errors); }
        }
        else { showErrorPopup('При отправке формы произошла ошибка:', res.status + ' ' + res.statusText); }
      };
    },
    error: function(res){
      if ($to_disable) { $to_disable.removeClass('_disabled'); };

      if (res.status == 400) {
        var response;
        if (res.responseJSON == undefined) { response = JSON.parse(res.responseText); }

        if (response != undefined) {
          var click_to = response['click_to'],
              error = response['error'],
              errors = response['errors'],
              alert_message = response['alert_message'];

          if (error) { showErrorPopup('При отправке формы произошла ошибка:', error); }
          else if (errors) { 
            if ($form) { addErrors($form, errors); }
            else { showErrorPopup('При отправке формы произошла ошибка:', errors); }
          };
          if (click_to) { $(click_to).click(); };
          if (alert_message) { alert(alert_message); };
        } else {
          showErrorPopup('При отправке формы произошла ошибка:', res.status + ' ' + res.statusText);
        };
      } else {
        if (res.status == 0) { alert('Произошла ошибка: 500 Internal Server Error') }
        else { alert('Произошла ошибка: ' + res.status + ' ' + res.statusText); }
      }
    }
  });
}


$('.js-certificate-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($form);
  sendCertificateForm(url, form_data, $form, $form);
});


// ----- Меняем тип даты -----

$('input[name="date"]').on('change', function(e){
  var $input = $(this),
      value = $input.val(),
      $date_div = $('.js-send-date-div'),
      $date_input = $('input[name="send_date"');

  if (value == 'today') {
    $date_div.hide();
    $date_input.attr('required', false);
  } else {
    $date_div.show();
    $date_input.attr('required', true);
  }
});
