{% load i18n %}

// ----- Отправка форм на бекенд: вспомогательные функции -----


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

function sendSomeForm(url, form_data, send_type, $to_disable, $form, $item_div, $row_clear_div) {
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
          has_password = res['has_password'];

      if ($to_disable) { $to_disable.removeClass('_disabled'); };

      if (result == 'ok') {
        if (send_type == 'profile-edit') {
          $('html, body').animate({scrollTop: $form.offset().top}, 400);
          if (has_password) { $('input[name="old_password"').show(); };
        }
        if (popup) {
          showPopup(popup);
          $('html, body').animate({scrollTop: $(popup).offset().top-75}, 400);
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


$('.js-profile-edit-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($form);
  sendSomeForm(url, form_data, 'profile-edit', $form, $form);
});


// ---- Кнопка "изменить пароль" ----

$('.js-password-button').click(function() {
  $('.js-password-button-container').hide();
  $('.js-password-container').show();
});
