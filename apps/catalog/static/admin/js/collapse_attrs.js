jQuery(function($) {
    // FROM: https://djangosnippets.org/snippets/1492/

    $('ul.hide_me').each(function() {
        var $ul = $(this);

        $ul.parent().hide();
    })

    $('ul.can_be_collapsed').each(function() {
        var $ul = $(this),
            $label = $ul.siblings('label'),
            margin_left;

        if ($label.hasClass('required')) { margin_left = 20; }
        else { margin_left = 5; }

        if ($label.hasClass('required') || $ul.hasClass('errors')) { 
            $ul.addClass('attr_collapse');
            $label.after('<a class="attr_collapse-toggle" style="color: #0d64a2; margin-left: ' + margin_left + 'px;" href="#">(' + gettext('Hide') + ')</a> ');
        }
        else { 
            $ul.addClass('attr_collapse collapsed'); 
            $ul.hide();
            $label.after('<a class="attr_collapse-toggle" style="color: #0d64a2; margin-left: ' + margin_left + 'px;" href="#">(' + gettext('Show') + ')</a> ');
        }

    })

    $('body').on('click', 'a.attr_collapse-toggle', function(e){
        e.preventDefault();

        $ul = $(this).next('ul');
        if (!$ul.hasClass('collapsed'))
        {
            $ul.addClass('collapsed');
            $ul.hide();
            $(this).html('(' + gettext('Show') + ')');
        }
        else
        {
            $ul.removeClass('collapsed');
            $ul.show();
            $(this).html('(' + gettext('Hide') + ')');
        }
    }).removeAttr('href').css('cursor', 'pointer');
});
