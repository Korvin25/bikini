CKEDITOR.plugins.add( 'accordion2', {
    icons: 'accordion',
    init: function( editor ) {
        // добавление команды
        editor.addCommand( 'accordionDialog', new CKEDITOR.dialogCommand( 'accordionDialog' ) );

        // установка кнопки
        editor.ui.addButton('Accordion', {
            label: 'Вставить аккордеон',
            command: 'accordionDialog',
            toolbar: 'insert'
        });

        // добавление окна диалога
        CKEDITOR.dialog.add( 'accordionDialog', this.path + 'dialogs/accordion.js' );
    }
    // onLoad: function () {
    //     CKEDITOR.addCss(
    //         '.accordion-list::before {font-size:10px;color:#000;content: "Bootstrap Accordion"} ' +
    //         '.accordion-list {padding: 8px;background: #eee;border-radius: 8px;border: 1px solid #ddd;box-shadow: 0 1px 1px #fff inset, 0 -1px 0px #ccc inset;}' +
    //         '.accordion-list-items {padding: 0 8px;box-shadow: 0 1px 1px #ddd inset;border: 1px solid #cccccc;border-radius: 5px;background: #fff;}' +
    //         '.accordion-list-items::before {font-size:14px;color:#ccc;content: "Insert collapsible items here"; position:relative;} '
    //     );
    // }
});
