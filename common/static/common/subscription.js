var gettext = window.gettext || function(e) {return e};
var interpolate = window.interpolate || function(e) {return e};
var emailURL = window.emailURL || "";
var csrftoken = window.csrftoken || "";

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

    var emails = [];

    function displayEmails(ul) {
        while (ul.firstChild)
            ul.removeChild(ul.firstChild);
        if (!emails.length)
            return;
        emails.forEach(email => {
            var li = document.createElement("li");
            li.textContent = email.email;
            ul.appendChild(li);
        });
    }

    async function fetchEmails(ul) {
        var response = await fetch(emailURL, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
        });
        if (!response.ok)
            throw new Error(gettext("There was an error while fetching the email addresses."));
        var data = await response.json();
        emails = data.data || [];

        if(ul)
            displayEmails(ul);
    }

    $(".help-subscription a").on("click", async function(e) {
        e.preventDefault();

        var content = document.createElement("div");
        function add_p(text) {
            var p = document.createElement("p");
            p.textContent = text;
            content.appendChild(p);
        }

        add_p(gettext("To be able to do the quick subscription of children, you must give us an email address that you gave us in previous years."));

        add_p(gettext("Currently you gave us those email addresses:"));

        var ul = document.createElement("ul");
        ul.style.textAlign = "left";
        displayEmails(ul);
        content.appendChild(ul);

        add_p(gettext("Try adding other addresses."));

        var input = document.createElement("input");
        input.className = "swal-content__input";
        input.type = "email";
        content.appendChild(input);

        fetchEmails(ul);

        var ok = await swal({
            title: gettext("Why can't you find your children?"),
            content: content,
            buttons: [
                gettext("Cancel"),
                {
                    text: gettext("Add an email address"),
                    closeModal: false,
                },
            ],
        });
        if (!ok) {
            swal.stopLoading();
            return;
        }
        var email = input.value.trim();
        try {
            var response = await fetch(emailURL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrftoken,
                },
                body: $.param({
                    email: email,
                    action_add: "",
                }),
            });
            if (!response.ok)
                throw new Error(gettext("There was an error while adding your email address."));
        } catch(e) {
            console.error("Error adding email:", e);
            swal(gettext("Error"), gettext("There was an error while adding your email address."), "error");
            return;
        }
        swal.stopLoading();
        swal({
            title: gettext("Email address added"),
            text: interpolate("The email address %s has been added.", [email]),
            icon: "success",
            buttons: false,
            timer: 1000,
        }).then(() => {
            location.reload();
        });
    });
});
