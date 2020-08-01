function translate(sourceElem, destElem, sourceLang, destLang) {
  $.post('/translate', {
    text: $(sourceElem).text(),
    source_language: sourceLang,
    dest_language: destLang
  }).done(function(response) {
    $(destElem).text(response['text'])
  }).fail(function() {
    $(destElem).text(translate_error_txt);
  });
}
