$(document).ready(function() {

    var num_editors = 0;
    var editors = [];

    /* View mode */
    $('.template-view .xmltext-field').each(function() {

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
    $('textarea.xmltext-field').each(function() {

        $(this).hide();

        var id = $(this).attr('id');
        $(this).after('<div class="xml-editor-chars" id="' + id + '-chars"></div>');
        $(this).after('<span  class="xml-editor-validation-msg" id="' + id + '-validate" data-index="' + num_editors + '"></span>');
        $(this).after('<a class="xml-editor-validate" id="' + id + '-validate" data-index="' + num_editors + '"><button>Validate XML</button></a>');
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
        num_editors++;

    });

    /* Push XML content from editors back to textarea fields before submit */    
    if (num_editors) {
        $('#form').on('submit', function(e) {
            var editors_ok = true;
            $(editors).each(function(i) {
                var editor = editors[i];
                var editor_id = editor['container'].getAttribute('id');
                var textarea_id = editor_id.replace('-editor', '');
                var xml = editor.getSession().getValue();
                try {
                    $.parseXML(xml);
                    var msg = 'XML is OK';
                    $('#' + textarea_id).siblings('.xml-editor-validation-msg').text(msg).addClass('status-ok');
                } catch(e) {
                    editors_ok = false;
                    var msg = 'Error in XML';
                    $('#' + textarea_id).siblings('.xml-editor-validation-msg').text(msg).addClass('status-error');
                }
                $('#' + textarea_id).val(xml); 
            });
            if (! editors_ok) {
                e.preventDefault();
            }
        });
    }

    $('.xml-editor-validate').on('click', function(e) {
            e.preventDefault();
            var index = $(this).data('index');
            var editor = editors[index];
            var xml = editor.getSession().getValue();
            try {
                $.parseXML(xml);
                var msg = 'XML is OK';
                $(this).siblings('.xml-editor-validation-msg').text(msg).addClass('status-ok');
            } catch(e) {
                var msg = 'Error in XML';
                $(this).siblings('.xml-editor-validation-msg').text(msg).addClass('status-error');
            }

    });
});
