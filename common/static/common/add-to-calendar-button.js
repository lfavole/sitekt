function urlToWebcal(url) {
    if (!url) return '';
    return url.replace(/^https?:\/\//, 'webcal://');
}

class CalendarProvider {
    constructor() {}

    getURL(url) {
        return urlToWebcal(url);
    }

    addToCalendar(url, name) {
        window.open(this.getURL(url, name), "_blank");
    }
}

class GoogleCalendarProvider extends CalendarProvider {
    cssClass = "google";
    name = gettext("Google");

    getURL(url) {
        return (
            "https://calendar.google.com/calendar/u/0/r?cid="
            + encodeURIComponent(urlToWebcal(url))
        );
    }
}

class AppleProvider extends CalendarProvider {
    cssClass = "apple";
    name = gettext("Apple");
}

class OutlookProvider extends CalendarProvider {
    cssClass = "outlook";
    name = gettext("Outlook.com");

    getURL(url, name) {
        return (
            "https://outlook.live.com/calendar/0/addfromweb/?url="
            + encodeURIComponent(urlToWebcal(url))
            + "&name=" + encodeURIComponent(name)
        );
    }
}

class Microsoft365Provider extends CalendarProvider {
    cssClass = "microsoft365";
    name = gettext("Microsoft 365");

    getURL(url, name) {
        return (
            "https://outlook.office.com/calendar/0/addfromweb/?url="
            + encodeURIComponent(urlToWebcal(url))
            + "&name=" + encodeURIComponent(name)
        );
    }
}

class YahooProvider extends CalendarProvider {
    cssClass = "yahoo";
    name = gettext("Yahoo!");

    getURL() {
        return "https://www.yahoo.com/calendar";
    }

    addToCalendar(url) {
        var steps = [
            gettext("Open now the Yahoo Calendar."),
            gettext("Click the 'Actions' tab."),
            gettext("Hit 'Follow Other Calendars'."),
            gettext("Set a name and paste the clipboard content into the URL field."),
        ];
        var ol = document.createElement("ol");
        steps.forEach(step => {
            var li = document.createElement("li");
            li.textContent = step;
            ol.appendChild(li);
        });
        swal({
            title: gettext("Add to Yahoo!"),
            content: ol,
            buttons: {
                open: gettext("Open Yahoo calendar"),
                cancel: gettext("Cancel"),
            },
        }).then((value) => {
            if (value === "open") {
                navigator.clipboard.writeText(url).then(() => {
                    super.addToCalendar();
                });
            }
        });
    }
}

class ICalProvider extends CalendarProvider {
    cssClass = "ical";
    name = gettext("iCal file");

    getURL(url) {
        return url;
    }

    addToCalendar(url, name) {
        // warning message with swal
        swal({
            title: gettext("Warning!"),
            text: [
                gettext("This will download an iCal file that you can import into your calendar application."),
                gettext("This is essentially the same as printing the events list."),
                gettext("The events will NOT be automatically updated, and you will have to stay up to date using other ways."),
                gettext("If you can, use the other methods, as they automatically update the events."),
                gettext("Do you want to continue?"),
            ].join("\n\n"),
            icon: "warning",
            buttons: {
                download: gettext("Download"),
                cancel: gettext("Cancel"),
            },
        }).then((value) => {
            if (value == "download")
                super.addToCalendar(url, name);
        });
    }
}

CalendarProvider.providers = [
    new GoogleCalendarProvider(),
    new AppleProvider(),
    new OutlookProvider(),
    new Microsoft365Provider(),
    new YahooProvider(),
    new ICalProvider(),
];

class AddToCalendarButton extends HTMLElement {
    static get observedAttributes() {
        return ["url", "name"];
    }

    constructor() {
        super();
        this.attachShadow({mode: "open"});
        this.shadowRoot.innerHTML = `
            <style>
                details {
                    display: inline-block;
                    cursor: pointer;
                    position: relative;
                }
                summary {
                    display: inline-block;
                    padding: 0.25em 0.5em;
                    background-color: #ffff8d;
                    border: 2px solid black;
                    border-radius: 4px;
                    transition: background-color 0.2s;
                }
                /*
                Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com
                License - https://fontawesome.com/license/free
                Copyright 2025 Fonticons, Inc.

                Compressed with https://svgomg.net/
                */
                summary::after {
                    content: "";
                    display: inline-block;
                    width: 1em;
                    height: 1em;
                    background-size: contain;
                    vertical-align: middle;
                    margin-left: 0.3em;
                    background-position: center;
                    background-repeat: no-repeat;
                    /* calendar-plus */
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M224 64c17.7 0 32 14.3 32 32v32h128V96c0-17.7 14.3-32 32-32s32 14.3 32 32v32h32c35.3 0 64 28.7 64 64v288c0 35.3-28.7 64-64 64H160c-35.3 0-64-28.7-64-64V192c0-35.3 28.7-64 64-64h32V96c0-17.7 14.3-32 32-32zm96 192c-13.3 0-24 10.7-24 24v48h-48c-13.3 0-24 10.7-24 24s10.7 24 24 24h48v48c0 13.3 10.7 24 24 24s24-10.7 24-24v-48h48c13.3 0 24-10.7 24-24s-10.7-24-24-24h-48v-48c0-13.3-10.7-24-24-24z"/></svg>');
                }
                .dropdown-content {
                    display: none;
                    opacity: 0;
                    pointer-events: none;
                    transition: opacity 0.4s;
                    position: absolute;
                    left: 50%;
                    transform: translateX(-50%);
                    width: max-content;
                    max-width: 90%;
                    text-align: left;
                    background-color: white;
                    border: 1px solid #ccc;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    z-index: 1;
                }
                details[open] .dropdown-content {
                    display: block;
                }
                details[open]:not(.hiding) .dropdown-content {
                    opacity: 1;
                    pointer-events: auto;
                }
                .dropdown-content a {
                    display: block;
                    padding: 0.5em;
                    text-decoration: none;
                    color: black;
                }
                .dropdown-content a:hover {
                    background-color: #eeeeee;
                }
                .dropdown-content a::before {
                    content: "";
                    display: inline-block;
                    width: 1em;
                    height: 1em;
                    background-position: center;
                    background-repeat: no-repeat;
                    margin-right: 0.3em;
                }
                .apple::before {
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 245.657"><path d="M167.084 130.514c-.308-31.099 25.364-46.022 26.511-46.761-14.429-21.107-36.91-24.008-44.921-24.335-19.13-1.931-37.323 11.27-47.042 11.27-9.692 0-24.67-10.98-40.532-10.689-20.849.308-40.07 12.126-50.818 30.799-21.661 37.581-5.54 93.281 15.572 123.754 10.313 14.923 22.612 31.688 38.764 31.089 15.549-.612 21.433-10.073 40.242-10.073s24.086 10.073 40.546 9.751c16.737-.308 27.34-15.214 37.585-30.187 11.855-17.318 16.714-34.064 17.009-34.925-.372-.168-32.635-12.525-32.962-49.68l.045-.013zm-30.917-91.287C144.735 28.832 150.524 14.402 148.942 0c-12.344.503-27.313 8.228-36.176 18.609-7.956 9.216-14.906 23.904-13.047 38.011 13.786 1.075 27.862-7.004 36.434-17.376z"/></svg>');
                }
                .google::before {
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><path d="M152.637 47.363H47.363v105.273h105.273z" fill="%23fff"/><path d="M152.637 200L200 152.637h-47.363z" fill="%23f72a25"/><path d="M200 47.363h-47.363v105.273H200z" fill="%23fbbc04"/><path d="M152.637 152.637H47.363V200h105.273z" fill="%2334a853"/><path d="M0 152.637v31.576A15.788 15.788 0 0 0 15.788 200h31.576v-47.363z" fill="%23188038"/><path d="M200 47.363V15.788A15.79 15.79 0 0 0 184.212 0h-31.575v47.363z" fill="%231967d2"/><path d="M15.788 0A15.79 15.79 0 0 0 0 15.788v136.849h47.363V47.363h105.274V0z" fill="%234285f4"/><path d="M68.962 129.02c-3.939-2.653-6.657-6.543-8.138-11.67l9.131-3.76c.83 3.158 2.279 5.599 4.346 7.341 2.051 1.742 4.557 2.588 7.471 2.588 2.995 0 5.55-.911 7.699-2.718 2.148-1.823 3.223-4.134 3.223-6.934 0-2.865-1.139-5.208-3.402-7.031s-5.111-2.718-8.496-2.718h-5.273v-9.033h4.736c2.913 0 5.387-.781 7.389-2.376 2.002-1.579 2.995-3.743 2.995-6.494 0-2.441-.895-4.395-2.686-5.859s-4.053-2.197-6.803-2.197c-2.686 0-4.818.716-6.396 2.148s-2.767 3.255-3.451 5.273l-9.033-3.76c1.204-3.402 3.402-6.396 6.624-8.984s7.34-3.89 12.337-3.89c3.695 0 7.031.716 9.977 2.148s5.257 3.418 6.934 5.941c1.676 2.539 2.507 5.387 2.507 8.545 0 3.223-.781 5.941-2.327 8.187-1.546 2.23-3.467 3.955-5.729 5.143v.537a17.39 17.39 0 0 1 7.34 5.729c1.904 2.572 2.865 5.632 2.865 9.212s-.911 6.771-2.718 9.57c-1.823 2.799-4.329 5.013-7.52 6.624s-6.787 2.425-10.775 2.425c-4.622 0-8.887-1.318-12.826-3.988zm56.087-45.312l-10.026 7.243-5.013-7.601 17.985-12.972h6.901v61.198h-9.847z" fill="%231a73e8"/></svg>');
                }
                .ical::before {
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200.016"><path d="M132.829 7.699c0-4.248 4.199-7.699 9.391-7.699s9.391 3.451 9.391 7.699v33.724c0 4.248-4.199 7.699-9.391 7.699s-9.391-3.451-9.391-7.699zm-25.228 161.263c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm-81.803-59.766c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.902 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.902 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.918 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zM25.798 139.079c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.902 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.902 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.918 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zM25.798 168.962c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zm40.902 0c-.553 0-.993-2.327-.993-5.208s.439-5.208.993-5.208h25.7c.553 0 .993 2.327.993 5.208s-.439 5.208-.993 5.208zM48.193 7.699C48.193 3.451 52.393 0 57.585 0s9.391 3.451 9.391 7.699v33.724c0 4.248-4.199 7.699-9.391 7.699s-9.391-3.451-9.391-7.699zM10.417 73.763h179.15V34.945c0-1.302-.537-2.49-1.4-3.369-.863-.863-2.051-1.4-3.369-1.4h-17.155c-2.881 0-5.208-2.327-5.208-5.208s2.327-5.208 5.208-5.208h17.171c4.183 0 7.975 1.709 10.726 4.46S200 30.762 200 34.945v44.043 105.843c0 4.183-1.709 7.975-4.46 10.726s-6.543 4.46-10.726 4.46H15.186c-4.183 0-7.975-1.709-10.726-4.46C1.709 192.79 0 188.997 0 184.814V78.971 34.945c0-4.183 1.709-7.975 4.46-10.726s6.543-4.46 10.726-4.46h18.343c2.881 0 5.208 2.327 5.208 5.208s-2.327 5.208-5.208 5.208H15.186c-1.302 0-2.49.537-3.369 1.4-.863.863-1.4 2.051-1.4 3.369zm179.167 10.433H10.417v100.618c0 1.302.537 2.49 1.4 3.369.863.863 2.051 1.4 3.369 1.4h169.629c1.302 0 2.49-.537 3.369-1.4.863-.863 1.4-2.051 1.4-3.369zM82.08 30.176c-2.881 0-5.208-2.327-5.208-5.208s2.327-5.208 5.208-5.208h34.977c2.881 0 5.208 2.327 5.208 5.208s-2.327 5.208-5.208 5.208z"/></svg>');
                }
                .microsoft365::before {
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 239.766"><path d="M200 219.785l-.021-.012V20.591L128.615 0 .322 48.172 0 48.234.016 192.257l43.78-17.134V57.943l84.819-20.279-.012 172.285L.088 192.257l128.515 47.456v.053l71.376-19.753v-.227z"/></svg>');
                }
                .outlook::before {
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 175"><path d="M178.725 0H71.275A8.775 8.775 0 0 0 62.5 8.775v9.975l60.563 18.75L187.5 18.75V8.775A8.775 8.775 0 0 0 178.725 0z" fill="%230364b8"/><path d="M197.813 96.281c.915-2.878 2.187-5.855 2.187-8.781-.002-1.485-.795-2.857-1.491-3.26l-68.434-38.99a9.37 9.37 0 0 0-9.244-.519c-.312.154-.614.325-.906.512l-67.737 38.6-.025.013-.075.044a4.16 4.16 0 0 0-2.088 3.6c.541 2.971 1.272 5.904 2.188 8.781l71.825 52.532z" fill="%230a2767"/><path d="M150 18.75h-43.75L93.619 37.5l12.631 18.75L150 93.75h37.5v-37.5z" fill="%2328a8ea"/><path d="M150 18.75h37.5v37.5H150z" fill="%2350d9ff"/><path d="M150 93.75l-43.75-37.5H62.5v37.5l43.75 37.5 67.7 11.05z" fill="%230364b8"/><path d="M106.25 56.25v37.5H150v-37.5zM150 93.75v37.5h37.5v-37.5zm-87.5-75h43.75v37.5H62.5z" fill="%230078d4"/><path d="M62.5 93.75h43.75v37.5H62.5z" fill="%23064a8c"/><path d="M126.188 145.113l-73.706-53.75 3.094-5.438 68.181 38.825a3.3 3.3 0 0 0 2.625-.075l68.331-38.937 3.1 5.431z" fill="%230a2767" opacity=".5"/><path d="M197.919 91.106l-.088.05-.019.013-67.738 38.588c-2.736 1.764-6.192 1.979-9.125.569l23.588 31.631 51.588 11.257v-.001c2.434-1.761 3.876-4.583 3.875-7.587V87.5c.001 1.488-.793 2.862-2.081 3.606z" fill="%231490df"/><path d="M200 165.625v-4.613l-62.394-35.55-7.531 4.294a9.356 9.356 0 0 1-9.125.569l23.588 31.631 51.588 11.231v.025a9.362 9.362 0 0 0 3.875-7.588z" opacity=".05"/><path d="M199.688 168.019l-68.394-38.956-1.219.688c-2.734 1.766-6.19 1.984-9.125.575l23.588 31.631 51.587 11.256v.001a9.38 9.38 0 0 0 3.562-5.187z" opacity=".1"/><path d="M51.455 90.721c-.733-.467-1.468-1.795-1.455-3.221v78.125c-.007 5.181 4.194 9.382 9.375 9.375h131.25c1.395-.015 2.614-.366 3.813-.813.638-.258 1.252-.652 1.687-.974z" fill="%2328a8ea"/><path d="M112.5 141.669V39.581a8.356 8.356 0 0 0-8.331-8.331H62.687v46.6l-10.5 5.987-.031.012-.075.044A4.162 4.162 0 0 0 50 87.5v.031-.031V150h54.169a8.356 8.356 0 0 0 8.331-8.331z" opacity=".1"/><path d="M106.25 147.919V45.831a8.356 8.356 0 0 0-8.331-8.331H62.687v40.35l-10.5 5.987-.031.012-.075.044A4.162 4.162 0 0 0 50 87.5v.031-.031 68.75h47.919a8.356 8.356 0 0 0 8.331-8.331z" opacity=".2"/><path d="M106.25 135.419V45.831a8.356 8.356 0 0 0-8.331-8.331H62.687v40.35l-10.5 5.987-.031.012-.075.044A4.162 4.162 0 0 0 50 87.5v.031-.031 56.25h47.919a8.356 8.356 0 0 0 8.331-8.331z" opacity=".2"/><path d="M100 135.419V45.831a8.356 8.356 0 0 0-8.331-8.331H62.687v40.35l-10.5 5.987-.031.012-.075.044A4.162 4.162 0 0 0 50 87.5v.031-.031 56.25h41.669a8.356 8.356 0 0 0 8.331-8.331z" opacity=".2"/><path d="M8.331 37.5h83.337A8.331 8.331 0 0 1 100 45.831v83.338a8.331 8.331 0 0 1-8.331 8.331H8.331A8.331 8.331 0 0 1 0 129.169V45.831A8.331 8.331 0 0 1 8.331 37.5z" fill="%230078d4"/><path d="M24.169 71.675a26.131 26.131 0 0 1 10.263-11.337 31.031 31.031 0 0 1 16.313-4.087 28.856 28.856 0 0 1 15.081 3.875 25.875 25.875 0 0 1 9.988 10.831 34.981 34.981 0 0 1 3.5 15.938 36.881 36.881 0 0 1-3.606 16.662 26.494 26.494 0 0 1-10.281 11.213 30 30 0 0 1-15.656 3.981 29.556 29.556 0 0 1-15.425-3.919 26.275 26.275 0 0 1-10.112-10.85 34.119 34.119 0 0 1-3.544-15.744 37.844 37.844 0 0 1 3.481-16.563zm10.938 26.613a16.975 16.975 0 0 0 5.769 7.463 15.069 15.069 0 0 0 9.019 2.719 15.831 15.831 0 0 0 9.631-2.806 16.269 16.269 0 0 0 5.606-7.481 28.913 28.913 0 0 0 1.787-10.406 31.644 31.644 0 0 0-1.687-10.538 16.681 16.681 0 0 0-5.413-7.75 14.919 14.919 0 0 0-9.544-2.956 15.581 15.581 0 0 0-9.231 2.744 17.131 17.131 0 0 0-5.9 7.519 29.85 29.85 0 0 0-.044 21.5z" fill="%23fff"/></svg>');
                }
                .yahoo::before {
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 177.803"><path d="M0 43.284h38.144l22.211 56.822 22.5-56.822h37.135L64.071 177.803H26.694l15.308-35.645L.001 43.284zm163.235 45.403H121.64L158.558 0 200 .002zm-30.699 8.488c12.762 0 23.108 10.346 23.108 23.106s-10.345 23.106-23.108 23.106a23.11 23.11 0 0 1-23.104-23.106 23.11 23.11 0 0 1 23.104-23.106z"/></svg>');
                }
                .warning::before {
                    background-image: url('data:image/svg+xml,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><path d="m100 0c27.613 0 52.613 11.195 70.711 29.293 18.094 18.094 29.289 43.098 29.289 70.707 0 27.613-11.195 52.613-29.289 70.711-18.098 18.094-43.098 29.289-70.711 29.289-27.609 0-52.613-11.195-70.707-29.289-18.098-18.098-29.293-43.098-29.293-70.711 0-27.609 11.195-52.613 29.293-70.707 18.094-18.098 43.098-29.293 70.707-29.293zm57.66 42.34c-14.758-14.754-35.145-23.883-57.66-23.883-22.516 0-42.902 9.1289-57.66 23.883-14.754 14.758-23.883 35.145-23.883 57.66 0 22.516 9.1289 42.902 23.883 57.66 14.758 14.754 35.145 23.883 57.66 23.883 22.516 0 42.902-9.1289 57.66-23.883 14.754-14.758 23.883-35.145 23.883-57.66 0-22.516-9.1289-42.902-23.883-57.66z" fill="%23f44336" fill-rule="nonzero" stroke-width=".39062"/><g transform="matrix(3.8384 0 0 3.8384 2277.8 -576.85)" style="shape-inside:url(%23rect7396);white-space:pre" aria-label="!"><path d="m-563.8 161.59-0.65341 20.185h-5.8381l-0.65341-20.185zm-3.5796 29.503q-1.5199 0-2.6136-1.0795-1.0796-1.0796-1.0796-2.6136 0-1.5057 1.0796-2.571 1.0938-1.0796 2.6136-1.0796 1.4631 0 2.571 1.0796 1.1222 1.0653 1.1222 2.571 0 1.0227-0.52557 1.8608-0.51137 0.83807-1.3494 1.3352-0.82387 0.49715-1.8182 0.49715z"/></g></svg>');
                }
            </style>
        `;
        var details = document.createElement("details");

        var summary = document.createElement("summary");
        summary.textContent = gettext("Add to calendar");
        summary.addEventListener("click", (e) => {
            if (details.open) {
                e.preventDefault();
                details.classList.add("hiding");
                setTimeout(() => {
                    details.removeAttribute("open");
                    details.classList.remove("hiding");
                }, 400);
            } else {
                e.preventDefault();
                details.setAttribute("open", "");
                details.classList.add("hiding");
                setTimeout(() => {
                    details.classList.remove("hiding");
                }, 10);
            }
        });
        // close when clicking outside
        details.addEventListener("click", (e) => {
            e.stopPropagation(); // Prevent click from bubbling up to document
        });
        document.addEventListener("click", (e) => {
            details.classList.add("hiding");
            setTimeout(() => {
                details.removeAttribute("open");
                details.classList.remove("hiding");
            }, 400);
        });
        details.appendChild(summary);

        var dropdownContent = document.createElement("div");
        dropdownContent.classList.add("dropdown-content");
        CalendarProvider.providers.forEach(provider => {
            var link = document.createElement("a");
            link.href = "#";
            link.classList.add(provider.cssClass);
            link.textContent = provider.name;
            link.addEventListener("click", () => provider.addToCalendar(this.url, this.name));
            dropdownContent.appendChild(link);
        });
        details.appendChild(dropdownContent);

        this.shadowRoot.append(details);
    }

    get url() {
        return this.getAttribute("url") || "";
    }

    set url(value) {
        this.setAttribute("url", value);
    }

    get name() {
        return this.getAttribute("name") || "";
    }

    set name(value) {
        this.setAttribute("name", value);
    }
}
customElements.define("add-to-calendar-button", AddToCalendarButton);
