$(function() {
    $("a[data-needs-parent-type]").on("click", function(e) {
        e.preventDefault();
        var url = new URL(e.target.href, location.href);
        swal({
            title: "Qui complète l'autorisation ?",
            buttons: {
                mother: "La mère",
                father: "Le père",
            },
        }).then(function(parent_type) {
            if(!parent_type) return;
            url.searchParams.set("parent_type", parent_type);
            window.open(url, "_blank");
        });
    });
});
