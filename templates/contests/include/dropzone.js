{% load i18n %}

Dropzone.options.loadingFiles = { // The camelized version of the ID of the form element

    maxFiles:5,
    url:'{% url "photo_upload" %}',
    acceptedFiles:'image/*',
    dictDefaultMessage: '{% trans "Перетащите сюда файлы или выберите на компьютере" %}',
    dictFallbackMessage: '{% trans "Ваш браузер не поддерживает загрузку файлов перетаскиванием" %}',
    dictFallbackText: '{% trans "Пожалуйста, используйте стандартный загрузчик файлов" %}',
    dictInvalidFileType: '{% trans "Вы не можете загружать файлы этого типа" %}',
    dictFileTooBig: '{% trans "Загружаемый вами файл слишком большой" %}',
    dictResponseError: '{% trans "При загрузке этого файла возникла ошибка, попробуйте позднее" %}',

    // The setting up of the dropzone
    init: function() {
        var myDropzone = this;

        this.on("successmultiple", function(files, response) {
            // Gets triggered when the files have successfully been sent.
            // Redirect user or notify of success.
            var v;

            if ($('[name="photos"]').val()) { v = $('[name="photos"]').val() + ';' }
            else { v = '' };

            $('[name="photos"]').val( v + response);
        });
    }
}
