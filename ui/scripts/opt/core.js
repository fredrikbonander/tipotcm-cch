﻿/*global jQuery*/
"use strict";
(function() {
    var window = this,
        document = window.document,
		$ = jQuery,
		model,
		view;

    view = {
        init: function() {
            /*$('.footer_menu li:first').bind('click', function () {
                $('.share_this').data('timeout', false).animate({ width: '190px' });
            });
            
            $('.share_this').mouseout(function () {
                $(this).data('timeout', setTimeout(function () {
                    $('.share_this').animate({ width: '0px' });
                }, 100));                
            }).mouseover(function () {
                clearTimeout($(this).data('timeout'));
            });
            
            $('.share_this a').click(function () {});*/
            
            $('#spot_description').live('keyup', function (e) {
                if ($(this).val().length > 140) {
                    $(this).val($(this).val().substring(0, 140))
                }
                
                $('#chars_left').text(140 - $(this).val().length);
            });
            
            $('.show_on_map').live('click', function (e) {
                e.preventDefault();
                view.map.showSpotOnMap(this);
                return false;
            });
            
            $('#tmp_fieldset .closeby-spots').live('click', function () {
                $('#categories-list').hide();
                $('#flip_switch').removeClass('hide');
                
                if ($(this).hasClass('true')) {
                    $('#flip_switch select option[value=true]').attr('selected', 'selected');
                } else {
                    $('#flip_switch select option[value=false]').attr('selected', 'selected');
                }
                
                $('#flip_switch select').next().remove();
                $('#flip_switch select').slider();
            });
            
            $(document).bind("ajaxComplete", function(){
                view.ajax.handlePageChange(arguments[2]);
            });
        },
        ajax : {
            handlePageChange : function (page) {
                if (page.url.indexOf('/en-us/reportpage/') != -1) {
                    view.spots.init();
                }
            }
        },
        /**
        * Handles Image Gallery.
        * @base view
        * @class 
        */
        spots : {
            init : function () {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(view.spots.locateMe);
                }
            },
                
            locateMe : function (position) {
                // Need to get position from browser and check if it's already active since FF trigger's this twice
                if (position && position.coords && $('#new_spot_form').length) {
                    $('#new_spot_form').removeClass('hide');
                    $('#new_spot_form #lat').val(position.coords.latitude);
                    $('#new_spot_form #lng').val(position.coords.longitude);
                    
                    view.spots.getSpots(position.coords);
                }
            },
            
            getSpots : function (position) {
                model.addToQueue(false, ['GetCloseBySpots', { 'lat' : position.latitude, 'lng' : position.longitude }], function (data) {
                    view.map.showMap(data, position);
                });
            }
        },
        
        map : {
            spotMaker : null,
            showSpotOnMap : function (sender) {
                var rel = $(sender).attr('id').split('_');
                    lat = parseFloat(rel[0]),
                    lng = parseFloat(rel[1]);
                
                if (!this.spotMarker) {
                    this.spotMarker = new google.maps.Marker({
                        map: view.map.gmap,
                        title: "this is you!"
                    })
                }
                
                this.spotMarker.setPosition(new google.maps.LatLng(lat, lng));
            },
            
            showMap : function (data, position) {
                if ($('#tmp_fieldset').length) {
                    return;
                }
                
                var options = {
                    zoom: 12,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                },
                i = 0,
                j = 0,
                initialLocation = new google.maps.LatLng(position.latitude, position.longitude),
                d;
                
                this.gmap = new google.maps.Map(document.getElementById("map_canvas"), options);
                this.gmap.setCenter(initialLocation);
                this.markersList = [];
                this.currentPosition = new google.maps.Marker({
                    position: initialLocation, 
                    map: view.map.gmap,
                    title: "this is you!"
                })
                
                if (!data.length) {
                    return;
                }

                tmp = '<div data-role="fieldcontain"><fieldset id="tmp_fieldset" data-role="controlgroup"><label class="ui-input-text">Close by spots:</label>';
                for (i = 0; i < data.length; i += 1) {
                    d = data[i];
                    tmpStr = '';
                    
                    if (d.fixed == true) {
                        tmpStr += '<strong>FIXED !!</strong>';
                    }
                    
                    for (j = 0; j < d.dList.length; j += 1) {
                        tmpStr += '<strong>' + d.dList[j].username + ' says:</strong> ' + d.dList[j].description;  
                        
                        if (j != (d.dList.length - 1)) {
                            tmpStr += ',<br /> ';
                        }
                    };
                    
                    tmp += '<input type="radio" name="closeby-spots" id="checkbox-tmp-' + i + 'a" class="closeby-spots ' + d.fixed + '" value="' + d.key +'" />';
                    tmp += '<label for="checkbox-tmp-' + i + 'a">' + tmpStr + ' - distance: ' + d.distance + ' - <span class="show_on_map" id="' + d.lat  +'_' + d.lng  +'">[Show on map]</span></label>'
                }
                                
                tmp += '</fieldset></div>';
                
                $('#new_spot_form fieldset:first').parent().before(tmp);
                $('#tmp_fieldset').find('input').customCheckboxRadio();
            }
            
        },
        
        /**
        * Handles Image Gallery.
        * @base view
        * @class 
        */
        imageGallery : {
            /**
            * Automaticlly invoked by $.runInit($.view) on dom:ready event
            */
            init : function () {
                $('.image_gallery_controls a:last').click(function () {
                    var currentImage = $('.image_single:visible'),
                        nextImage = currentImage.next('.image_single').length ? currentImage.next('.image_single') : $('.image_single:first');
                    
                    currentImage.fadeOut(function() {
                        nextImage.fadeIn();
                    });
                    
                });
                
                $('.image_gallery_controls a:first').click(function () {
                    var currentImage = $('.image_single:visible'),
                        nextImage = currentImage.prev('.image_single').length ? currentImage.prev('.image_single') : $('.image_single:last');
                    
                    currentImage.hide();
                    nextImage.show();
                    
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
                url: '/ClientService',
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