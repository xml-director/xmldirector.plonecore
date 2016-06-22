
/* encodeHTML() */


if (!String.prototype.encodeHTML) {
  String.prototype.encodeHTML = function () {
    return this.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;')
               .replace(/"/g, '&quot;')
               .replace(/'/g, '&apos;');
  };
}


/* A custom sprintf() impelementation */


function sprintf(){
    var args = Array.prototype.slice.call(arguments);
    return args.shift().replace(/%s/g, function(){
        return args.shift();
    });
}


/* ACE editor integration */

/* template for wrapping the ACE editor into*/


var container_template = '\
    <div class="editor-container">\
        %s\
        <div class="editor-messages">\
            <span class="editor-number-chars">%s</span> <span>chars</span>\
            <span class="editor-verification"></span>\
        </div>\
        <div class="editor-actions">\
            <button class="editor-clear" type="context">Clear</button>\
            <button class="editor-validate-xml" type="context">Validate XML</button>\
            <button class="editor-validate-xml-server" type="context">Validate XML on server</button>\
        </div>\
    </div>';


/* Global variable for all ACE editor instances within page */


var EDITORS = Array();


/* Initialize all ACE editors for a given ``selector``.
 * ``add_editor_field`` is usually always true
 * ``readonly`` = true|false for setting the ACE editor into readonly mode
 */

function init_ace_editors(selector='.ace-editable', add_editor_field=false, readonly=false) {

    $(selector).each(function() {

        if(add_editor_field) 
            $(this).hide();
        var html = $(this).clone().wrap('<div>').parent().html();
        var xml_length = $(this).data('length');
        if (add_editor_field) {
            var inner_xml = $(this).text();
            html = sprintf(container_template, '<div class="editor">' + inner_xml.encodeHTML() + '</div>' + html, 0);
        } else {
            html = sprintf(container_template, html, xml_length);
        }
        $(this).replaceWith(html);
    });

    $('.editor-container').each(function(i) {

        /* ensure that ACE_MODE is defined */
        try {
            ACE_MODE;
        } catch(e) {
            ACE_MODE = 'xml';
        };

        var id_ =  i + 1;
        $(this).find('.editor').attr('id', 'editor-' + id_);
        $(this).find('.editor').attr('editor-id', id_);
        $(this).find('.editor-number-chars').attr('editor-id',  id_);
        $(this).find('.editor-verification').attr('editor-id', id_);
/*        $(this).find('.editor-save').attr('editor-id', id_);*/
        $(this).find('.editor-clear').attr('editor-id', id_);
        $(this).find('.editor-validate-xml').attr('editor-id', id_);
        $(this).find('.editor-validate-xml-server').attr('editor-id', id_);
        
        var editor = ace.edit('editor-' + id_);
        EDITORS[id_] = editor;
        editor.editor_id = id_;
        editor.setTheme("ace/theme/chrome");
        editor.getSession().setMode("ace/mode/" + ACE_MODE);
        editor.setShowPrintMargin(false);
        editor.setReadOnly(readonly);

        if (ACE_MODE != 'xml' && ACE_MODE != 'html') {
            $('.editor-validate-xml').remove();
            $('.editor-validate-xml-server').remove();
        }

        editor.getSession().on('change', function(){
            var xml = editor.getSession().getValue();
            var editor_id = editor.editor_id;
            $('.editor-number-chars[editor-id="' + editor_id + '"]').text(xml.length);
        });

        if (readonly) {
            $('.editor-actions').remove();
            $('.editor-messages').remove();
        }

    });

    $('.editor-validate-xml-server').on('click', function(e) {
        e.preventDefault();
        var editor_id = parseInt($(this).attr('editor-id'));
        var editor = EDITORS[editor_id];
        var xml = editor.getSession().getValue();
        var selector = '.editor-verification[editor-id="' + editor_id + '"]';
        var validation_field = $(selector);

        $.post('@@api-validate-xml', {xml: xml}, function(data, textStatus, jqXHR) {
            var result = $.parseJSON(data);
            if (result.length == 0) {
                var msg = 'XML is OK';
                validation_field.removeClass('status-ok');
                validation_field.removeClass('status-error');
                validation_field.addClass('status-ok')
                validation_field.text(msg).stop(true, true).show().fadeOut(5000);
            } else {
                var msg = 'Error in XML (' + data + ')';
                validation_field.removeClass('status-ok');
                validation_field.removeClass('status-error');
                validation_field.addClass('status-ok')
                validation_field.text(msg).stop(true, true).show().fadeOut(5000);
            }
        }); 
    });

    $('.editor-validate-xml').on('click', function(e) {
        e.preventDefault();
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
        if (confirm('Do you really to remove the content?')) {
            editor.setValue('');
        }
    });
}


/* onload handlers */

$(document).ready(function() {

    var plone5 = $('[data-bundle="plone-legacy"]').length > 0;
    if (plone5) {
        var portal_url = $('body').data('portal-url');
    }


    /* Deletion confirmation */
    $('body').on('click', '.confirm-action', function(e) {
        var text = $(this).data('text');
        if (! confirm(text)) {
            return false;
        }
    });

    
    /* Dexterity edit form subbmission handler */
    $('#form').on('submit', function(e) {
        $('.ace_text-input').each(function() {
            var editor_id = $(this).closest('.editor').attr('editor-id');
            var hidden_xml = $(this).closest('.xmltext-widget').find('.hidden-xml');
            var editor = EDITORS[editor_id]
            var xml = editor.getSession().getValue();
            hidden_xml.val(xml);
        });
    });

    // Test connection button for XML Director controlpanel
    var button = $('.template-xmldirector-core-settings #form-buttons-save');
    if (button.length > 0) {

        $.ajax('xmldirector-settings-json', {
            success: function(settings) {

                var settings = $.parseJSON(settings); 

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

                if (settings['connector_mode'] == 'existdb') {
                    var button3 = button.clone();
                    button3.attr('value', 'Install Exist-DB scripts');
                    button3.attr('name', 'form-button-install-scripts');
                    button3.attr('id', 'form-button-install-scripts');
                    button3.attr('type', 'button');
                    button3.attr('style', 'margin-left: 1em');
                    button3.insertAfter(button2);
                    button3.on('click', function() {
                        window.location.href = '@@xmldirector-install-scripts'; 
                    });
                }
            }
        })
    }            

});

