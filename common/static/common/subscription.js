var gettext = window.gettext || function(e) {return e};
var ngettext = window.ngettext || function(s, p, c) {return c == 1 ? s : p};
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

    function displayEmails(p, ul) {
        while (ul.firstChild)
            ul.removeChild(ul.firstChild);
        if (!emails.length) {
            p.textContent = gettext("Currently you didn't give us any email addresses.");
            return;
        }

        p.textContent = ngettext("Currently you gave us this email address:", "Currently you gave us these email addresses:", emails.length);

        emails.forEach(email => {
            var li = document.createElement("li");
            li.textContent = email.email;
            ul.appendChild(li);
        });
    }

    async function fetchEmails(p, ul) {
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

        if(p && ul)
            displayEmails(p, ul);
    }

    $(".help-subscription a").on("click", async function(e) {
        e.preventDefault();

        var content = document.createElement("div");
        function add_p(text) {
            var p = document.createElement("p");
            p.textContent = text;
            content.appendChild(p);
        }

        add_p(gettext("To be able to do the quick subscription of children, you must give us the email address (from the mother or the father) that you gave us the last year."));

        var p = document.createElement("p");
        content.appendChild(p);

        var ul = document.createElement("ul");
        ul.style.textAlign = "left";
        content.appendChild(ul);

        displayEmails(p, ul);

        add_p(gettext("Try with another address:"));

        var input = document.createElement("input");
        input.className = "swal-content__input";
        input.type = "email";
        input.placeholder = gettext("Email address");
        content.appendChild(input);

        add_p(gettext("If this does not work, please click on 'Register a new child' and perform the full registration of your child."));

        fetchEmails(p, ul);

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
