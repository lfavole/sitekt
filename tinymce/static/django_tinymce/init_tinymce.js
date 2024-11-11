"use strict";

{
    function initTinyMCE(el) {
        if (el.closest(".empty-form") !== null)  // Don't do empty inlines
            return
        var mce_conf = JSON.parse(el.dataset.mceConf);

        // There is no way to pass a JavaScript function as an option
        // because all options are serialized as JSON.
        const fns = [
            "color_picker_callback",
            "file_browser_callback",
            "file_picker_callback",
            "images_dataimg_filter",
            "images_upload_handler",
            "paste_postprocess",
            "paste_preprocess",
            "setup",
            "urlconverter_callback",
        ];
        fns.forEach((fn_name) => {
            if (typeof mce_conf[fn_name] == "undefined")
                return;
            if (mce_conf[fn_name].includes("("))
                mce_conf[fn_name] = eval("(" + mce_conf[fn_name] + ")");
            else
                mce_conf[fn_name] = window[mce_conf[fn_name]];
        });

        if("protect" in mce_conf)
            mce_conf["protect"] = mce_conf["protect"].map(function(item) {
                var match = /^\/(.*)\/([gimuy]*)$/.exec(item);
                if(match === null)
                    return new RegExp(item);
                else
                    return new RegExp(match[1], match[2]);
            });

        if (!"selector" in mce_conf)
            mce_conf["target"] = el;
        if (!tinyMCE.get(el.id))
            tinyMCE.init(mce_conf);
    }

    function initializeTinyMCE(element, formsetName) {
        django.jQuery(".tinymce", element).each((_index, element) => initTinyMCE(element));
    }

    django.jQuery(function($) {
        if (!tinyMCE)
            throw "tinyMCE is not loaded. If you customized TINYMCE_JS_URL, double-check its content.";
        // initialize the TinyMCE editors on load
        initializeTinyMCE(document);

        // initialize the TinyMCE editor after adding an inline in the django admin context.
        $(document).on("formset:added", (event, $row, formsetName) => {
            if (event.detail && event.detail.formsetName)
                // Django >= 4.1
                initializeTinyMCE(event.target);
            else
                // Django < 4.1, use $row
                initializeTinyMCE($row.get(0));
        });
    });
}
