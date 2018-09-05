function setYMClientID() {
  var yametrics_enabled = typeof yaCounter{{ YM_COUNTER }} !== 'undefined';

  console.log('yametrics_enabled? ' + yametrics_enabled);

  if (yametrics_enabled) {
    var clientID = yaCounter{{ YM_COUNTER }}.getClientID();

    console.log('clientID: ' + clientID);

    if (clientID) { $.post("{% url 'set_ym_client_id' %}", {'client_id': clientID}); }
  }
}

$(document).ready(function(){
  console.log('setting!');

  setTimeout(function(){ setYMClientID(); }, 1000);
});
