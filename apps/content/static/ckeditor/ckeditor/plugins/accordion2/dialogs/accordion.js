CKEDITOR.dialog.add( 'accordionDialog', function ( editor ) {
    return {
        title: 'Настройка аккордеона',
        minWidth: 400,
        minHeight: 200,
        contents: [
            {
                id: 'tab-basic',
                label: 'Basic Settings',
                elements: [
                    {
                        type: 'text',
                        id: 'number',
                        label: 'Количество секций аккордеона',
                        validate: CKEDITOR.dialog.validate.notEmpty( "Не может быть пустым" )
                    }
                ]
            }
        ],
        onOk: function() {
            var dialog = this;
            var sections = parseInt(dialog.getValueOf('tab-basic','number'));  // Количество секций, которые будут созданы

            section = '<div class="parent"><h2 class="accordion-title">Заголовок секции</h2><div class="uk-accordion-content"><p>Текст секции</p></div></div>'
            intern = ""
            for (i=0;i<sections;i++){
                intern = intern + section
            }

            editor.insertHtml('<div class="wrap-accordion">'+ intern +'</div>');

        }
    };
});
