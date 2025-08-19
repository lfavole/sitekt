var categories = window.categories || [];
var categoryNames = window.categoryNames || {};
var gettext = window.gettext || function(e) {return e};

$(function() {
    $("main .label-help").click(function(e) {
        e.preventDefault();
        var lines = [
            gettext("Please select the categories corresponding to your children."),
            gettext("You can also add the dates to your personal calendar or download the list."),
        ];
        var content = document.createElement("div");
        lines.forEach(line => {
            var p = document.createElement("p");
            p.textContent = line;
            content.appendChild(p);
        });
        swal({
            title: gettext("How to use the calendar?"),
            content: content,
            icon: "info",
        });
    });

    var selectedCategories = [...categories];
    var allSelected = true;
    var displayPast = false;
    try {
        var settings = JSON.parse(localStorage.getItem("calendarSettings"));
        if(Array.isArray(settings.c)) {
            allSelected = false;
            selectedCategories = settings.c;
        }
        displayPast = !!settings.p;
    } catch(e) {}

    var allCategories = $();
    if(categories) {
        allCategories = $("<a>").text("Tout").attr("href", "#").click((e) => {
            e.preventDefault();
            allSelected = true;
            updateDisplay();
        }).appendTo(".filters");
        $(document.createTextNode(" · ")).appendTo(".filters");
        var buttons = {};
        categories.forEach(category => {
            buttons[category] = $("<a>").text(categoryNames[category]).attr("href", "#").click((e) => {
                e.preventDefault();

                if(allSelected) {
                    allSelected = false;
                    selectedCategories = [];
                }

                if(selectedCategories.includes(+category))
                    selectedCategories = selectedCategories.filter(c => c !== +category);
                else
                    selectedCategories.push(+category);

                updateDisplay();
            }).appendTo(".filters");
        });
    }

    function updateDisplay() {
        if(!selectedCategories.length)
            allSelected = true;
        if(allSelected)
            selectedCategories = [...categories];
        allCategories.toggleClass("checked", allSelected);

        for(var [category, button] of Object.entries(buttons))
            button.toggleClass("checked", !allSelected && selectedCategories.includes(+category));

        var filteredPastCount = 0;
        $("tr[data-ids]").removeClass("colored").each((i, e) => {
            var ids = ($(e).data("ids") + "").split(",").map(id => +id);
            var filteringOk = selectedCategories.some(id => ids.includes(id));
            if(filteringOk && $(e).hasClass("past"))
                filteredPastCount++;
            $(e).toggle((displayPast || !$(e).hasClass("past")) && filteringOk);
        });

        $("tr[data-ids]:visible:odd").addClass("colored");

        var label = displayPast ? gettext("Hide past dates") : gettext("Show past dates");
        pastSeparator.toggle(filteredPastCount > 0);
        pastSeparator.find("a").text(label + " (" + filteredPastCount + ")");

        var categoriesParameter = allSelected ? "" : selectedCategories.map(category => categorySlugs[category]).join(",");

        var calendarURL = new URL($("add-to-calendar-button").attr("url"), location.href);
        calendarURL.searchParams.set("categories", categoriesParameter);
        $("add-to-calendar-button").attr("url", calendarURL + "");

        var pdfURL = new URL($(".pdf-link").attr("href"), location.href);
        pdfURL.searchParams.set("categories", categoriesParameter);
        $(".pdf-link").attr("href", pdfURL + "");

        localStorage.setItem(
            "calendarSettings",
            JSON.stringify({c: allSelected ? "all" : selectedCategories, p: displayPast}),
        );
    }

    var pastSeparator = $("<tr>").addClass("separation show").append(
        $("<td>").attr("colspan", 4).append($("<a>").attr("href", "#"))
    ).click(function(e) {
        e.preventDefault();
        displayPast = !displayPast;
        updateDisplay();
    });
    // Add it at the correct spot (after the last .past)
    $("main table tr.past:last").after(pastSeparator);

    $("main table").addClass("colored");

    updateDisplay();
});
