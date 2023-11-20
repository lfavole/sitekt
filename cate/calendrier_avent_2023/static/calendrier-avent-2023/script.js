$(function() {
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
