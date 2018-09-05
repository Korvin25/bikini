function setYMClientID() {
  var yametrics_enabled = typeof yaCounter{{ YM_COUNTER }} !== 'undefined';

  if (yametrics_enabled) {
    var clientID = yaCounter{{ YM_COUNTER }}.getClientID();

    if (clientID) { $.post("{% url 'set_ym_client_id' %}", {'client_id': clientID}); }
  }
}

$(document).ready(function(){
  setTimeout(function(){ setYMClientID(); }, 1000);
});
