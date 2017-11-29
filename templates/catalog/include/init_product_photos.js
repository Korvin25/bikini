var connector = function(itemNavigation, carouselStage) {
  return carouselStage.jcarousel('items').eq(itemNavigation.index()); 
}; 
$(function() {
  var carouselStage = $('.nom_img_med_wrap').jcarousel({wrap: 'circular'}); 
  var carouselNavigation = $('.carousel-navigation').jcarousel();
  carouselNavigation.jcarousel('items').each(function() { 
    var item = $(this); 
    var target = connector(item, carouselStage); 
    item .on(
      'jcarouselcontrol:active', function() {
        carouselNavigation.jcarousel('scrollIntoView', this); 
        item.addClass('active'); 
      }).on('jcarouselcontrol:inactive', function() { 
        item.removeClass('active'); 
      }).jcarouselControl({ target: target, carousel: carouselStage }); 
  });
  
  $('#l_arr_nom_img').on('jcarouselcontrol:inactive', function() {
      $(this).addClass('inactive'); 
    }
  ).on('jcarouselcontrol:active', function() {
      $(this).removeClass('inactive'); 
    }
  ).jcarouselControl({ target: '-=1' }); 
  
  $('#r_arr_nom_img').on('jcarouselcontrol:inactive', function() {
      $(this).addClass('inactive');
    }
  ).on('jcarouselcontrol:active', function() {
      $(this).removeClass('inactive');
    }
  ).jcarouselControl({ target: '+=1' }); 
});
