jQuery(function($) {
    $('ul.can-be-collapsed').each(function() {
        var $ul = $(this), $label = $ul.siblings('label');

        if ($ul.hasClass('errors')) { $ul.addClass('attr_collapse'); }
        else { $ul.addClass('attr_collapse collapsed'); $ul.hide() }

        $label.append('<a class="attr_collapse-toggle" style="color: #0d64a2; margin-left: 5px;" href="#">(' + gettext('Show') + ')</a> ');
    })

    $('body').on('click', 'a.attr_collapse-toggle', function(e){
        e.preventDefault();

        $ul = $(this).parent('label').next('ul');
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
