$(document).ready(function() {

    $('.template-edit .xml-field').each(function() {

        $(this).hide();

        var id = $(this).attr('id');
        $(this).after('<div id="' + id + '-chars"></div>');
        $(this).after('<div id="' + id + '-editor" style="width: 80%; min-height: 200px; height: 400px; max-height: 400px">hello</div>')
        var editor = ace.edit(id + '-editor');
        editor.setTheme("ace/theme/chrome");
        editor.getSession().setMode("ace/mode/xml");
        editor.setShowPrintMargin(false);
        editor.getSession().setValue($(this).val());
        editor.getSession().on('change', function(){
              var xml = editor.getSession().getValue();
              $('#' + id).val(xml)
              $('#' + id + '-chars').text(xml.length + ' chars');
        });
    });
});
