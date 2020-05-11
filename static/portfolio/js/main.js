jQuery(document).ready(function($) {


    /*======= Skillset *=======*/
    
    $('.level-bar-inner').css('width', '0');
    
    $(window).on('load', function() {

        $('.level-bar-inner').each(function() {
        
            var itemWidth = $(this).data('level');
            
            $(this).animate({
                width: itemWidth
            }, 800);
            
        });

    });
    
    /* Bootstrap Tooltip for Skillset */
    $('.level-label').tooltip();

    var initial = true;
    var listTicker = function(options) {

        var defaults = {
            list: [],
            startIndex:0,
            interval: 3000
        }

        var options = $.extend(defaults, options);

        var listTickerInner = function(index) {

            if (options.list.length == 0) return;

            if (!index || index < 0 || index > options.list.length) index = 0;

            var value= options.list[index];

            if (!initial) {
                options.trickerPanel.fadeOut(function() {
                    $(this).html(value).fadeIn();
                });
            }

            var nextIndex = (index + 1) % options.list.length;

            setTimeout(function() {
                initial = false;
                listTickerInner(nextIndex);
            }, options.interval);

        };

        listTickerInner(options.startIndex);
    }

});