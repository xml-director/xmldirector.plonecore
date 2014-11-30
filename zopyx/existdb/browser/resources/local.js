$(document).ready(function() {

    var num_editors = 0;
    var editors = [];

    /* View mode */
    $('.template-view .xml-field').each(function() {

        $(this).hide();
        var id = $(this).attr('id');
        
        $(this).after('<div class="xml-editor" id="' + id + '-editor" style="width: 80%; min-height: 100px; height: 100px; max-height: 400px"></div>')
        var editor = ace.edit(id + '-editor');
        editor.setTheme("ace/theme/chrome");
        editor.getSession().setMode("ace/mode/xml");
        editor.setShowPrintMargin(false);
        editor.setReadOnly(true);
        editor.getSession().setValue($(this).text());
    });

    /* Edit mode */
    $('#form .xml-field').each(function() {

        $(this).hide();
        num_editors++;

        var id = $(this).attr('id');
        $(this).after('<div class="xml-editor-chars" id="' + id + '-chars"></div>');
        $(this).after('<div class="xml-editor" id="' + id + '-editor" style="width: 80%; min-height: 200px; height: 400px; max-height: 400px"></div>')
        var editor = ace.edit(id + '-editor');
        editors.push(editor);
        editor.setTheme("ace/theme/chrome");
        editor.getSession().setMode("ace/mode/xml");
        editor.setShowPrintMargin(false);
        editor.setReadOnly(false);
        editor.getSession().setValue($(this).val());
        $('#' + id + '-chars').text($(this).val().length + ' chars');
        editor.getSession().on('change', function(){
              var xml = editor.getSession().getValue();
              $('#' + id + '-chars').text(xml.length + ' chars');
        });
    });

    /* Push XML content from editors back to textarea fields before submit */    
    if (num_editors) {
        $('#form').on('submit', function(e) {
            $(editors).each(function(i) {
                var editor = editors[i];
                var editor_id = editor['container'].getAttribute('id');
                var textarea_id = editor_id.replace('-editor', '');
                var xml = editor.getSession().getValue();
                $('#' + textarea_id).val(xml); 
            });
        });
    }
});
