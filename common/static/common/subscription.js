var gettext = window.gettext || function(e) {return e};
var emails = window.emails || [];
var emailURL = window.emailURL || [];

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

    $("a.help-subscription").on("click", function(e) {
        e.preventDefault();

        var content = document.createElement("div");
        function add_p(text) {
            var p = document.createElement("p");
            p.textContent = text;
            content.appendChild(p);
        }

        add_p(gettext("To be able to do the quick subscription of children, you must verify an email address that you gave us previously."));

        if(emails.length) {
            add_p(gettext("Currently you gave us those email addresses:"));

            var ul = document.createElement("ul");
            ul.style.textAlign = "left";

            emails.forEach(email => {
                var li = document.createElement("li");
                li.textContent = email.email + " ";

                var label = document.createElement("span");
                label.classList.add("label-" + (email.isVerified ? "ok": "error"));
                label.textContent = email.isVerified ? gettext("Verified") : gettext("Unverified");
                li.appendChild(label);

                ul.appendChild(li);
            });
            content.appendChild(ul);
        }

        add_p(gettext("If an address isn't verified, check your inbox and click on the link that you received."));
        add_p(gettext("Otherwise try adding and verifying other addresses."));

        swal({
            title: gettext("Why can't you find your children?"),
            content: content,
            buttons: {
                add_email: gettext("Add an email address"),
                cancel: gettext("Cancel"),
            },
        }).then((value) => {
            if (value === "add_email")
                window.open(emailURL);
        });
    });
});
