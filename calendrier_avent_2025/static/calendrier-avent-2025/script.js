$(function() {
    var picture_popup_hidden = true;
    var picture_popup_img = null;
    var picture_popup_close = $("<div>")
    .addClass("fermer")
    .click(function() {
        picture_popup_hidden = true;
        var container = $(this).parent().css("opacity", 0).css("pointer-events", "none");
        container.find("img").remove();
        $("body").css("overflow", "");
        setTimeout(function() {
            container.hide().css("pointer-events", "");
        }, 400);
    });
	var picture_popup = $("<div>")
    .addClass("picture-popup")
    .append(picture_popup_close)
    .hide()
    .appendTo("body");
	$("body").on("click", "img", function() {
        var img = $(this);
        // is it the picture in the popup or is the popup shown?
        if(img.closest(picture_popup).length || !picture_popup_hidden) return;
        picture_popup_hidden = false;
        picture_popup_img = this;
		picture_popup.show();
		$("body").css("overflow", "hidden");
        setTimeout(function() {
            picture_popup.css("opacity", 1).append(
                $("<img>")
                .attr("src", img.attr("src"))
                .attr("style", "width: auto; height: auto; max-width: 100%; max-height: 100%; margin: auto;")
            );
        }, 0);
	});
    $(window).on("keydown", function(evt) {
        if(picture_popup_hidden) return;
        if(evt.keyCode == 27)
            picture_popup_close.click();
        if(evt.keyCode == 37 || evt.keyCode == 39) {
            if(!picture_popup_img) return;
            var imgs = $("body").find("img:not(:is(.picture-popup img))");
            var img_index = 0;
            imgs.each(function(index, element) {
                if(element == picture_popup_img) {
                    img_index = index;
                    return false;
                }
            });
            var new_img_index;
            if(evt.keyCode == 37) {  // left
                if(img_index == 0)
                    new_img_index = imgs.length - 1;
                else
                    new_img_index = img_index - 1;
            } else if(evt.keyCode == 39) {  // right
                if(img_index == imgs.length - 1)
                    new_img_index = 0;
                else
                    new_img_index = img_index + 1;
            }
            picture_popup.find("img").remove();
            picture_popup_hidden = true;
            $(imgs[new_img_index]).click();
        }
    });

    var $countdown = $("h1 + p .cpt[data-date]");
    if(!$countdown.length) return;
    countdown({
        "element": $countdown,
        "date": $countdown.attr("data-date"),
        "txts": {
            0: "Revenez dans CPT.",
            "-inf": function() {
                setTimeout(function() {location.reload()}, 15000);
                return "Vous pouvez actualiser la page.";
            },
        },
    });
});
