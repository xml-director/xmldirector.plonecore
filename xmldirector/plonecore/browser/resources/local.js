
if(require === undefined){
  require = function(reqs, torun){
    'use strict';
    return torun(window.ace);
  };
}


require([
  'ace/ace'
  ], function(ace){

$(document).ready(function() {

    var plone5 = $('[data-bundle="plone-legacy"]').length > 0;
    if (plone5) {
        ace.config.set("basePath", $('body').attr('data-portal-url') + '/++resource++xmldirector.plonecore/ace-builds/src-min');
    }

    var editors = [];
    var num_editors = 0;

    /* View mode */
    $('.template-view .xmltext-field').each(function() {

        $(this).hide();
        var id = $(this).attr('id');
        
        $(this).after('<div class="xml-editor" id="' + id + '-editor" style="width: 80%; min-height: 100px; height: 250px; max-height: 400px"></div>')
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
        $(this).after('<a class="xml-editor-validate-server" id="' + id + '-validate-server" data-index="' + num_editors + '"><button class="xml-editor">Validate XML (Server)</button></a>');
        $(this).after('<a class="xml-editor-validate" id="' + id + '-validate" data-index="' + num_editors + '"><button class="xml-editor">Validate XML (Client)</button></a>');
        $(this).after('<a class="xml-editor-clear" id="' + id + '-clear" data-index="' + num_editors + '"><button class="xml-editor">Clear content </button></a>');
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
            $(this).siblings('.xml-editor-validation-msg').text(msg).removeClass('status-error').addClass('status-ok');
        } catch(e) {
            var msg = 'Error in XML';
            $(this).siblings('.xml-editor-validation-msg').text(msg).removeClass('status-ok').addClass('status-error');
        }
    });

    $('.xml-editor-validate-server').on('click', function(e) {
        e.preventDefault();
        var this_clicked = $(this);
        var index = $(this).data('index');
        var editor = editors[index];
        var xml = editor.getSession().getValue();
        $.post('@@api-validate-xml', {xml: xml}, function(data, textStatus, jqXHR) {
            var result = $.parseJSON(data);
            if (result.length == 0) {
                var msg = 'XML is OK';
                this_clicked.siblings('.xml-editor-validation-msg').text(msg).removeClass('status-error').addClass('status-ok');
            } else {
                var msg = 'Error in XML (' + data + ')';
                this_clicked.siblings('.xml-editor-validation-msg').text(msg).removeClass('status-ok').addClass('status-error');
            }
        }); 
    });

    $('.xml-editor-clear').on('click', function(e) {
        e.preventDefault();
        var index = $(this).data('index');
        var editor = editors[index];
        var xml = editor.getSession().getValue();
        if (confirm('Do you really to remove the XML content')) {
            editor.setValue('');
        }
    });

    // Test connection button for XML Director controlpanel
    var button = $('.template-xmldirector-core-settings #form-buttons-save');
    if (button.length > 0) {
        var button2 = button.clone();
        var cancel_button = $('#form-buttons-cancel');
        button2.attr('value', 'Test connection');
        button2.attr('name', 'form-button-test-connection');
        button2.attr('id', 'form-button-test-connection');
        button2.attr('type', 'button');
        button2.attr('style', 'margin-left: 1em');
        button2.insertAfter(cancel_button);
        button2.on('click', function() {
            window.location.href = '@@xmldirector-connection-test'; 
        });
    }            
});

});
