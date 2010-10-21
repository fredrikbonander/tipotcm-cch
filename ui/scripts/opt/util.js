/*global jQuery console alert*/
"use strict";
(function () {
	var window = this,
		$ = jQuery,
        ua = navigator.userAgent;
	
    $.isIE7 = (/MSIE\s[7]/).test(ua);
    $.isIE8 = (/MSIE\s[8]/).test(ua);
    $.isIE78 = (/MSIE\s[78]/).test(ua);

    $.fn.foolProof = function () {
        this.slideUp = function (elem) {
            return function () {
                if ($.isIE7) {
                    $.fn.hide.apply(elem, arguments);
                } else {
                    $.fn.slideUp.apply(elem, arguments);
                }
            }
        }(this);

        this.slideDown = function (elem) {
            return function () {
                if ($.isIE7) {
                    $.fn.show.apply(elem, [0, arguments[0]]);
                } else {
                    $.fn.slideDown.apply(elem, arguments);
                }
            }
        }(this);

        return this;
    }
	
	$.log = function (message) {
        if (window.console && window.console.debug) {
            console.debug(arguments);
        } else if (window.console && window.console.log) {
            console.log(arguments);
        } else {
            alert(message);
        }
    };

	$.fn.bindEvent = function () {
        var ev = arguments[0].event,
			callback = arguments[0].callback,
			l = callback.length,
			callbackMethod,
			i,
			bindMethod = function (e) {
                var arg = [],
					x; 
					
				try {
					for (x = 1; x < arguments.length; x += 1) {
						arg.push(arguments[x]);	
					}
					
					e.data.n[e.data.f].apply(e.data.n, arg);
                } catch (err) {
					$.log(err.message);
                }
            };
		
			
        for (i = 0; i < l; i += 1) {
            callbackMethod = callback[i];
            $(this).bind(ev, callbackMethod, bindMethod);
        }
    };
	
	$.objectWalk = function (obj, func, args) {
        var i,
			ar = args ? args : [];
 
        if (typeof func !== "function") {
            throw new Error("file: custom.js, Error: " + func + " is not a function");
        }
        func.apply(obj, ar);
 
        for (i in obj) {
            if (obj[i] && typeof obj[i] === "object" && (!obj[i].length && obj[i].length !== 0)) {
                $.objectWalk(obj[i], func, ar);
            }
        }
    };
   
    $.runAll = function () {
        var that = this,
			prop,
			obj;
       
        $.objectWalk(that, function () {
            if (this[arguments[0]]) {
                if (typeof this[arguments[0]] === "function") {
                    this[arguments[0]]();
                } else if (typeof this[arguments[0]] === "object" && (!this[arguments[0]].length && this[arguments[0]].length !== 0)) {
                    // this generates an Error in JSLInt:
                    // "Problem at line 41 character 26: Bad for in variable 'k'."
                   
                    // I have no idea what it should be called to be a 'good one'.
                    // The 'k' variable is apparently ok in '$.objectWalk'...
                    obj = this[arguments[0]];
                    for (prop in obj) {
                        if (typeof obj[prop] === "function") {
                            obj[prop]();
                        }
                    }
                }
            }
        }, [arguments[0]]);
    };
   
    $.runInit = function (obj) {
        $.runAll.apply(obj, ["init"]);
    };
	
}());