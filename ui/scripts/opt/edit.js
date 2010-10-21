/*global jQuery*/
"use strict";
(function() {
    var window = this,
        document = window.document,
		$ = jQuery,
		model,
		view;

    view = {
        editor : {
            init : function () {
                view.editor.addButton();
                
                $('textarea').tinymce({
                    script_url: '/ui/scripts/lib/tiny_mce.js',
                    mode: 'textareas',
                    theme: 'advanced',
                    plugins: '-exlink',
                    setup: function(ed) {
                        ed.onPaste.add(function(ed, e, o) {
                            $.view.editor.storeBookmark();
                            $.view.editor.openPasteDialog();
                            return tinymce.dom.Event.cancel(e);
                        });
                    },
                    paste_use_dialog: true,
                    width: '354',
                    height: '212',
                    theme_advanced_buttons1: 'bold,italic,underline,strikethrough,bullist,numlist, exlink',
                    theme_advanced_buttons2: '',
                    theme_advanced_buttons3: '',
                    theme_advanced_toolbar_location: 'top',
                    theme_advanced_toolbar_align: 'left'
                });
                
                view.editor.addPasteDialog();
                
            },
            
            editor_bookmark : false,
        
            storeBookmark : function () {
                if (tinymce.isIE){
                    this.editor_bookmark = this.editor_bookmark = tinymce.EditorManager.activeEditor.selection.getBookmark();
                }
            },

            restoreBookmark : function () {
                if (tinymce.isIE){
                    tinymce.EditorManager.activeEditor.selection.moveToBookmark(this.editor_bookmark);
                }
                //tinymce.EditorManager.activeEditor.selection.moveToBookmark(this.editor_bookmark);
            },
            
            addPasteDialog: function() {
                $('body').append('<div id="post_dialog"><div class="box"><p>Paste you content here:</p><textarea id="post_dialog_textarea"></textarea><button id="post_dialog_btn" class="medium">Paste</button><button id="post_dialog_cancel_btn" class="cancelButton">Cancel</button></div></div>');
                $('#post_dialog').dialog({
                    title : 'Paste',
                    autoOpen: false,
                    closeText: '',
                    modal: true,
                    width: 465,
                    open: function() {
                        if ($.isIE) {
                            setTimeout( function () { $('#post_dialog_textarea').get(0).focus() }, 100);
                        }
                        
                        $('#post_dialog button').button();
                        $('#post_dialog_textarea').val('');
                        $('#post_dialog_btn').click(function() {
                            //tinymce.EditorManager.activeEditor.selection.setContent($('#post_dialog_textarea').val());
                            $.view.editor.restoreBookmark();          
                            tinymce.EditorManager.activeEditor.execCommand("mceInsertContent", false, $('#post_dialog_textarea').val());
                            $('#post_dialog').dialog('close');
                            $('#post_dialog_btn').unbind('click');
                            $('#post_dialog_cancel_btn').unbind('click');
                            $('.ui-widget-overlay').unbind('click');
                        });

                        $('#post_dialog_cancel_btn').click(function() {
                            $('#post_dialog').dialog('close');
                            $('#post_dialog_btn').unbind('click');
                            $('#post_dialog_cancel_btn').unbind('click');
                            $('.ui-widget-overlay').unbind('click');
                        });

                        $('.ui-widget-overlay').click(function() {
                            $('#post_dialog').dialog('close');
                            $('#post_dialog_btn').unbind('click');
                            $('#post_dialog_cancel_btn').unbind('click');
                            $('.ui-widget-overlay').unbind('click');
                        });
                    }
                });
            },

            openPasteDialog: function() {
                $('#post_dialog').dialog('open');
            },
            
            toggleExternalLink: function() {
                if ($('#external_link_tr').length) {
                    $('#external_link_tr').remove();
                } else {
                    $.view.editor.storeBookmark();
                    var ed = tinymce.EditorManager.activeEditor,
                        content = ed.selection.getContent(),
                        val = ed.selection.getContent({ format: 'text' }),
                        href = typeof content === 'undefined' ? ($(content).get(0).nodeName === 'A' ? $(content).attr('href') : ($(ed.selection.getNode()).get(0).nodeName === 'A' ? $(ed.selection.getNode()).attr('href') : '')) : '',
                        addToEditor = function () {
                            var href = (/^(ftp|http[s]?|mailto)(\:)(\/{2})?/i).test($('#external_link_href').val()) ? $('#external_link_href').val() : 'http://' + $('#external_link_href').val();
                            $.view.editor.restoreBookmark();
                            tinymce.EditorManager.activeEditor.execCommand("mceInsertContent", false, '<a class="external_link" href="' + href + '">' + $('#external_link').val() + '</a>');
                            //$.view.editor.storeBookmark();
                            $('#external_link_btn').unbind('click');
                            $('#external_link_tr').remove();
                        };
                        
                    $('#' + ed.editorContainer).find('tr:first').after('<tr id="external_link_tr"><td><label style="margin: 0 0 3px 5px;" for="external_link" class="first">Link text</label><input style="background-color: #fff; border: 1px solid #222; height: 20px; margin: 0 0 3px 5px; width: 341px;" class="small" autocomplete="off" id="external_link" type="text" value="' + val + '" /><label style="margin: 0 0 3px 5px;" for="external_link_href">Link url</label><input style="background-color: #fff; border: 1px solid #222; height: 20px; margin: 0 0 3px 5px; width: 341px;" class="small" autocomplete="off" id="external_link_href" value="' + href + '" type="text" /><button style="display:block; margin: 2px 0 5px 5px; width: 50px;"  id="external_link_btn" type="button" class="small">Add</button></td></tr>');
                    
                    
                    $('#external_link_btn').button().click(function(e) {
                        addToEditor();    
                    });
                }
            },
            
            addButton: function(){
                // Create a new plugin class
                tinymce.create('tinymce.plugins.exlink', {
                    init: function(ed, url){
                        // Register an example button
                        ed.addCommand('ExLinkCommand', $.view.editor.toggleExternalLink, $.view.editor);
                        
                        ed.addButton('exlink', {
                            title: 'Add link',
                            cmd: 'ExLinkCommand',
                            'class': 'mce_exlink' // Use the bold icon from the theme
                        });
                        
                    }
                });
                
                tinymce.PluginManager.add('exlink', tinymce.plugins.exlink);
            }
        },
        ui : {
            init: function() {
                $('#tabs').tabs();
                
                $('button').button();
                
                $('ul.actions a').hover(
                    function() { $(this).addClass('ui-state-hover'); }, 
                    function() { $(this).removeClass('ui-state-hover'); }
                );
            },
        },
        /**
        * Setup dialogs
        * @base view
        * @class
        */
        dialog : {
            /**
            * DOM:ready invoked
            */
            init : function () {
                $('.image_list a span').click(function (e) {
                    e.preventDefault();
                    
                    var t = $(this),
                        title = t.parent().text(),
                        imageSrc = t.parent().attr('rel') + '=s720';
                   
                    $('#image_dialog').find('img').bind('load', function () {
                        $('#image_dialog').dialog('option', 'title', title).dialog('option', 'width', 760).dialog('open');
                    }).attr('src', imageSrc);
                });

                $('<div id="image_dialog"><img /></div>').appendTo('body').dialog({
                    autoOpen : false,
                    modal : true,
                    minHeight : 400
                });
                
                $('.select_images_btn').click(function () {
                    var lang = $(this).attr('id');
                    $('#image_list_wrapper_'+lang ).dialog('option', 'title', $(this).text()).dialog('open');
                    $('#image_list_wrapper_'+ lang + ' ul').sortable({
                        connectWith: '.image_list_connector_' + lang
                    }).disableSelection();
                    
                    $('#image_list_wrapper_'+ lang + ' ul:first li').each(function (index, elem) {
                        var id = $(elem).attr('id').split('_')[1];
                        if ($(this).parent().parent().siblings('.list_area').find('li[id$=' + id + ']').length){
                            $(this).hide();
                        }
                    });
                    
                });
                
                $('.page_images .image_list_wrapper').dialog({
                    autoOpen : false,
                    modal : true,
                    minHeight : 400,
                    minWidth: 430
                });
                
                $('.save_image_list').click(function () {
                    var t = $(this),
                        inputId = t.attr('id').split('_')[3],
                        lang = inputId.split('|')[3],
                        selectedValues = [],
                        selectedList = t.closest('.image_list_wrapper').find('#image_list_' + lang + '_selected li');
                        
                    selectedList.each(function (index, elem) {
                       selectedValues.push($(elem).attr('id').split('_')[1]); 
                    });
                    
                    document.getElementById(inputId).value = selectedValues.join(',');
                    
                    $('#image_list_'+lang).html('').append(selectedList.clone());
                    
                    $('#image_list_wrapper_'+lang ).dialog('close');
                });
            }
        },

        /**
        * Handles data transfer from .net to js via input elements.
        * @base view
        * @class 
        */
        bridge: {
            /**
            * All properties in properties object is stored with the same name as the id attribute of the input element.
            * Data is reached from $.view.bridge.properties.properties_name. ie.
            * @example $.view.bridge.properties.language_code
            * @property
            */
            properties: {},
            /**
            * Get data from .net via input elements inside #net_js_bridge element. All data is stored in the properties object.
            * Automaticlly invoked by $.runInit($.view) on dom:ready event
            */
            init: function() {
                var element;

                $('#net_js_bridge input').each(function(index, elem) {
                    element = $(elem);
                    view.bridge.properties[element.attr('id')] = element.val();
                });
            }
        }
    };

    /**
    * Handle Ajax request against ClientScriptService
    * @class
    */
    model = {
        /**
        * Handles the response from jQuery ajax object
        * @param {Array} data	JSON data loaded from server.
        * @param {String} queued	ID of current queue, cloud also be bool False it no queue is used.
        */
        handleResponse: function(data, queueId) {
            if (data.d.ResponseStatus !== 200) {
                this.handleError(data.d.ResponseMessage);
                return false;
            }

            if (!queueId && this.queue.tmpCallback) {
                this.queue.tmpCallback(data.d.ResponseData[0].Value);
            } else if (queueId) {
                var i = 0,
                    l = data.d.ResponseData.length,
					x;

                for (x in this.queue[queueId]) {
                    if (this.queue[queueId][x]) {
                        for (i = 0; i < l; i += 1) {
                            if (data.d.ResponseData[i].CommandName.toLowerCase() === x.toLowerCase() && this.queue[queueId][x].callback) {
                                this.queue[queueId][x].callback(data.d.ResponseData[i].Value);
                            }
                        }
                    }
                }

                model.resetQueue(queueId);
            }
        },
        /**
        * Holds queue objects. Each queue should have a unique name and contains properties with correspondant names of the name of webservice to be called.
        * Value of "WebServiceMethod" should always be false
        * @example queue1 : { WebServiceMethod : false }
        * @property
        */
        queue: {
            CartPageQueue: {
                UpdateCart: false,
                GetCartDeliveryType: false,
                GetCartTotalAmount: false
            }
        },
        /**
        * Add new Queue Item to que based on queueId. If que is full. Trigger the JSON request. ie. 
        * @example model.addToQueue('que1', ['AddStuff', { name: 'stuff' }], view.removeStuff)
        * 
        * @param {String} queueId	ID of current queue, cloud also be bool False it no queue is used.
        * @param {Array} payload	Array containg Webservie name and arguments ie. ['DoStuff',  { name : 'lorem ipsum' }]
        * @param {Function} callback	Callback method, can be false if no callback is requierd 
        */
        addToQueue: function(queueId, payload, callback) {
            var queuePayload,
				i,
				queueObj = { Name: payload[0], Params: [] };

            for (i in payload[1]) {
                if (i in payload[1]) {
                    queueObj.Params.push({ Name: i, Value: payload[1][i] });
                }
            }

            if (!queueId) {
                this.queue.tmpCallback = callback;

                this.addToAjaxQueue({ request: { Commands: [queueObj]} }, false);
                return;
            } else if (this.queue[queueId][payload[0]]) {
                return false;
            }

            if (typeof this.queue[queueId] === 'undefined' || typeof this.queue[queueId][payload[0]] === 'undefined') {
                this.handleError('No queueId with the name ' + queueId + ' or the queItem ' + payload[0] + ' is not in the queue ' + queueId);
            }

            this.queue[queueId][payload[0]] = {};
            this.queue[queueId][payload[0]].payload = queueObj;
            this.queue[queueId][payload[0]].callback = callback;

            if (this.isQueueReady(queueId)) {
                queuePayload = this.getQueuePayload(queueId);
                this.addToAjaxQueue(queuePayload, queueId);
            }
        },
        /**
        * Check if queue is ready to be triggered.
        * @param {String} queueId	ID of current queue.
        * @return {Boolean}	Returns true if queue is ready.
        */
        isQueueReady: function(queueId) {
            var isReady = true,
				i;

            for (i in this.queue[queueId]) {
                if (!this.queue[queueId][i]) {
                    isReady = false;
                    break;
                }
            }

            return isReady;
        },
        /**
        * Get current queues payload as and Array.
        * @param {String} queueId	ID of current queue.
        * @return {Array}	Payload array with main webservice methods as first argument.
        */
        getQueuePayload: function(queueId) {
            var payloadArray = [],
				i;

            for (i in this.queue[queueId]) {
                if (this.queue[queueId][i]) {
                    payloadArray.push(this.queue[queueId][i].payload);
                }
            }

            return { request: { Commands: payloadArray} };
        },
        /**
        * Resets the queue of current queueId.
        * @param {String} queueId	ID of current queue.
        */
        resetQueue: function(queueId) {
            var i;
            for (i in this.queue[queueId]) {
                if (this.queue[queueId][i]) {
                    this.queue[queueId][i] = false;
                }
            }
        },
        /**
        * Setup ajax properties for new ajax request.
        * @param {Array} payload	Array to be posted to webservice.
        * @param {String} queueId	ID of current queue.
        */
        addToAjaxQueue: function(payload, queueId) {
            var ajaxOptions = {
                url: '/ScriptServices/ClientDataTransferService.asmx/GetData',
                type: 'post',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(payload),
                callback: queueId,
                success: function(data) {
                    var arg = [data, this.callback];
                    model.handleResponse.apply(model, arg);
                },
                error: model.handleError
            };

            this.doJsonPost(ajaxOptions);
        },
        /**
        * Array to hold currently running ajax requests
        * @property
        */
        ajaxQueue: [],

        /**
        * Triggers jQuery's ajax method and triggers handleResponse method passing loaded data and queId.
        * Uses this.ajaxQueue queue to keep ajax request to be invoked in proper order.
        * @param {Object} ajaxOptions Object containing properties of ajax request.
        */
        doJsonPost: function(ajaxOptions) {
            var ajaxQueueItem,
                ajaxCall = (function(ajaxOptions, obj) { //Return anonymouse function to keep context of ajaxOpotions and obj.
                    return function() {
                        var onSuccess = ajaxOptions.success,
                            ajaxQueue = obj.ajaxQueue;
                        // Override succuess function in ajaxOptions to add logic for handling ajaxQueue
                        ajaxOptions.success = function() {
                            if (onSuccess) {
                                onSuccess.apply(ajaxOptions, arguments);
                            }

                            ajaxQueue.shift();

                            if (ajaxQueue.length > 0) {
                                ajaxQueueItem = obj.ajaxQueue[0];
                                ajaxQueueItem();
                            }
                        };
                        $.ajax(ajaxOptions);
                    };
                } (ajaxOptions, this));
            //Add new Ajax call to queue
            this.ajaxQueue.push(ajaxCall);
            //If ajax queue is empty or contain only a singel call, invoke it.
            if (this.ajaxQueue.length <= 1) {
                ajaxQueueItem = this.ajaxQueue[0];
                ajaxQueueItem();
            }
        },
        /**
        * Throws error from jQuery ajax method.
        */
        handleError: function(err) {
            throw new Error(err);
        }
    };

    $.extend({ view: view });

    $(document).ready(function() {
        $.runInit($.view);
    });

} ());