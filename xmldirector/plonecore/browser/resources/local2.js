
var container_template = '\
    <div class="editor-container">\
        %s\
        <div class="editor-messages">\
            <span class="editor-number-chars">%d</span> <span>chars</span>\
            <span class="editor-verification"></span>\
        </div>\
        <div class="editor-actions">\
            <button class="editor-save" type="context">Save</button>\
            <button class="editor-clear" type="context">Clear</button>\
            <button class="editor-validate-xml" type="context">Validate XML</button>\
        </div>\
    </div>';

var EDITORS = Array();

function init_ace_editors() {

    $('.ace-editable').each(function() {
        var html = $(this).clone().wrap('<div>').parent().html();
        var xml_length = $(this).data('length');
        html = $.sprintf(container_template, html, xml_length);
        $(this).replaceWith(html);
    });

    $('.editor-container').each(function(i) {
        var id_ =  i + 1;
        $(this).find('.editor').attr('id', 'editor-' + id_);
        $(this).find('.editor').attr('editor-id', id_);
        $(this).find('.editor-number-chars').attr('editor-id',  id_);
        $(this).find('.editor-verification').attr('editor-id', id_);
        $(this).find('.editor-save').attr('editor-id', id_);
        $(this).find('.editor-clear').attr('editor-id', id_);
        $(this).find('.editor-validate-xml').attr('editor-id', id_);
        
        var editor = ace.edit('editor-' + id_);
        EDITORS[id_] = editor;
        editor.editor_id = id_;
        editor.setTheme("ace/theme/chrome");
        editor.getSession().setMode("ace/mode/" + ACE_MODE);
        editor.setShowPrintMargin(false);
        editor.setReadOnly(ACE_READONLY);
        
        editor.getSession().on('change', function(){
            var xml = editor.getSession().getValue();
            var editor_id = editor.editor_id;
            $('.editor-number-chars[editor-id="' + editor_id + '"]').text(xml.length);
        });
    });

    $('.editor-validate-xml').on('click', function() {
        var editor_id = parseInt($(this).attr('editor-id'));
        var editor = EDITORS[editor_id];
        var xml = editor.getSession().getValue();
        var selector = '.editor-verification[editor-id="' + editor_id + '"]';
        var validation_field = $(selector);
        try {
            $.parseXML(xml);
            var msg = 'XML is OK';
            var css_class = 'status-ok';
        } catch(e) {
            var msg = 'XML has errors';
            var css_class = 'status-error';
        }
        validation_field.removeClass('status-ok');
        validation_field.removeClass('status-error');
        validation_field.addClass(css_class)
        validation_field.text(msg).stop(true, true).show().fadeOut(5000);
    });

    $('.editor-clear').on('click', function(e) {
        e.preventDefault();
        var editor_id = parseInt($(this).attr('editor-id'));
        var editor = EDITORS[editor_id];
        if (confirm('Do you really to remove the XML content?')) {
            editor.setValue('');
        }
    });

    $('.editor-save').on('click', function() {

        var editor_id = parseInt($(this).attr('editor-id'));
        var selector = '.editor[editor-id="' + editor_id + '"]';
        var editor_field = $(selector);
        var editor = EDITORS[editor_id];
        var xml = editor.getSession().getValue();
        var url = editor_field.data('url');
        var selector = '.editor-verification[editor-id="' + editor_id + '"]';
        var validation_field = $(selector);
        
        $.post(url, {
            data: xml})
        .done(function() {
            validation_field.removeClass('status-ok');
            validation_field.removeClass('status-error');
            validation_field.addClass('status-ok')
            validation_field.text('Saving OK').stop(true, true).show(). fadeOut(2500);
            $('#ajax-result').html('<span class="status-ok">Content saved<span>').show().delay(2500).fadeOut(500);
        })
        .fail(function() {
            validation_field.removeClass('status-ok');
            validation_field.removeClass('status-error');
            validation_field.addClass('status-error')
            validation_field.text('Saving failed').stop(true, true).show(). fadeOut(2500);
        })
    });
}
