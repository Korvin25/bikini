
// ----- Отправка форм на бекенд: вспомогательные функции -----

function showErrorPopup(title, text) {
  var error_popup_id = 'error-popup',
      title = title || '',
      text = text || '',
      $a = $('a[href="#'+error_popup_id+'"]'),
      $popup = $('#'+error_popup_id+''),
      $popup_title = $popup.find('.popup_title'),
      $popup_text = $popup.find('.popup_text');

  $('.js-call-close').filter(':visible').click();
  $('a[rel*=leanModal1]').leanModal({ top : 200, closeButton: ".js-call-close" });

  if (title) { $popup_title.text(title); };
  $popup_text.html(text);
  $a.click();
};


function showPopup(popup_id) {
  var $a = $('a[href="'+popup_id+'"]'),
      $popup = $(popup_id);

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


// ----- Отправка форм на бекенд -----

function sendHeaderAuthForm(url, form_data, $to_disable, $form) {
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
      var errors = res['errors'],
          result = res['result'],
          next = res['next'];

      if ($to_disable) { $to_disable.removeClass('_disabled'); };

      if (result == 'ok') {
        if (next) { window.location = next; }
        else { window.location.reload(); }
      }
      else {
        if (error) { showErrorPopup('При отправке формы произошла ошибка:', error); }
        else if (errors) { 
          addErrors($form, errors);
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
              popup = response['popup'],
              error = response['error'],
              errors = response['errors'],
              alert_message = response['alert_message'];

          if (error) { showErrorPopup('При отправке формы произошла ошибка:', error); }
          else if (errors) { 
            if ($form) { addErrors($form, errors); }
            else { showErrorPopup('При отправке формы произошла ошибка:', errors); }
          };
          if (click_to) { $(click_to).click(); };
          if (popup) { showPopup(popup); };
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


$('.js-auth-login-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      $forms = $('.js-auth-form'),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($forms);
  sendHeaderAuthForm(url, form_data, $forms, $form);
});


$('.js-auth-registration-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      $forms = $('.js-auth-form'),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($forms);

  if (form_data['password'] != form_data['password_repeat']) {
    var errors = [{name: 'password', error_message: 'Введенные пароли не совпадают!'}, {name: 'password_repeat'}];
    addErrors($form, errors,);
  }
  else { 
    sendHeaderAuthForm(url, form_data, $forms, $form);
  }
});
