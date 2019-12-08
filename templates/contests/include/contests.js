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

  $('.window_popup').hide();
  $('a[rel*=leanModal1]').leanModal({ top : 200, closeButton: ".js-call-close" });

  if (title) { $popup_title.text(title); };
  $popup_text.html(text);
  $a.click();
};


function showPopup(popup_id, old_popup_id) {
  var $a = $('a[href="'+popup_id+'"]'),
      $popup = $(popup_id),
      $closeButtons = $('.js-call-close').filter(':visible');

  $('.window_popup').hide();
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


// ----- Участие в конкурсе -----

$('.js-apply-button').click(function(e) {
  e.preventDefault();

  var $button = $(this),
      popup_id = $button.attr('data-popup-id');

  showPopup(popup_id);
});


$('.js-apply-form').on('submit', function(e) {
  e.preventDefault();

  var $form = $(this),
      url = $form.attr('action'),
      form_data;

  form_data = getFormData($form);
  removeErrors($form);

  $form.addClass('_disabled');
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
          error = res['error'],
          result = res['result'],
          redirect_url = res['redirect_url'],
          popup = res['popup'];

      $form.removeClass('_disabled');

      if (result == 'ok') {
        if (redirect_url) { 
          $form.addClass('_disabled');
          window.location = redirect_url; 
        }
        else if (popup) { showPopup(popup); };
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
      $form.removeClass('_disabled');

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

});


// ----- Лайк/дизлайк -----

$('.js-rate-participant').click(function(e){
  e.preventDefault();
  $('.js-like-participant').click();
})

$('.js-like-participant').on('change', function(){ 
  var $button = $(this), 
      $parent = $button.parents('.js-like-parent'),
      $likes_count_span = $parent.find('.js-likes-count-span'),
      $button_text = $('.js-rate-participant'),

      is_checked = $button.is(':checked'),

      participant_id = $button.attr('data-participant-id'),
      like_url = $button.attr('data-like-url'), 
      dislike_url = $button.attr('data-dislike-url'),

      url,
      form_data;

  form_data = {
    'id': participant_id,
  };

  if (is_checked) { url = like_url; }
  else { url = dislike_url; };

  $button_text.addClass('_disabled');

  $.ajax({
    url: url,
    type: 'POST',
    data: JSON.stringify(form_data),
    // processData: false,
    dataType: 'json',
    contentType: 'application/json',

    success: function(res){
      $button_text.removeClass('_disabled');

      var err = res['errors'],
          result = res['result'],
          likes_count = res['count'],
          button_text = res['button_text'];

      if (result == 'ok') {
        $likes_count_span.text(likes_count);
        if (button_text) { $button_text.text(button_text); };
      }
      else {
        // if (error) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', error); }
                // if (errors) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', errors); }
        // else { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', res.status + ' ' + res.statusText); }
        if (error) { alert('{% trans "При отправке формы произошла ошибка" %}: ' + error); }
        if (errors) { alert('{% trans "При отправке формы произошла ошибка" %}: '+  errors); }
        else { alert('{% trans "При отправке формы произошла ошибка" %}: ' + res.status + ' ' + res.statusText); }
      };
    },
    error: function(res){
      $button.removeClass('_disabled');
      $button_text.removeClass('_disabled');

      if (res.status == 400) {
        var response;
        if (res.responseJSON == undefined) { response = JSON.parse(res.responseText); }

        if (response != undefined) {
          var click_to = response['click_to'],
              error = response['error'],
              errors = response['errors'],
              alert_message = response['alert_message'];

          // if (error) { showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', error); };
          if (error) { alert('{% trans "При отправке формы произошла ошибка" %}: ' + error); };
          if (errors) { add_errors($form, errors, true); };
          if (click_to) { $(click_to).click(); };
          if (alert_message) { alert(alert_message); };
        } else {
          // showErrorPopup('{% trans "При отправке формы произошла ошибка" %}:', res.status + ' ' + res.statusText);
          alert('{% trans "При отправке формы произошла ошибка" %}: ' + res.status + ' ' + res.statusText);
        };
      } else {
        if (res.status == 0) { alert('{% trans "Произошла ошибка" %}: 500 Internal Server Error') }
        else { alert('{% trans "Произошла ошибка" %}: ' + res.status + ' ' + res.statusText); }
      }
    }
  });

});
