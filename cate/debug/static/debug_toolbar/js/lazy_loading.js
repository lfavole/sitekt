import { ajax } from "./utils.js";

function init() {
  const sidebarUrl = document.getElementById("djDebug").dataset.sidebarUrl;
  const storeId = encodeURIComponent(document.getElementById("djDebug").dataset.storeId);

  ajax(`${sidebarUrl}?store_id=${storeId}`).then(function (data) {
    Object.keys(data).forEach(function (panelId) {
      var panelElement = document.createElement("div");
      document.getElementById("djDebug").insertBefore(panelElement, document.getElementById("djDebugWindow"));
      panelElement.outerHTML = data[panelId].content;

      var buttonElement = document.createElement("li");
      document.getElementById("djDebugPanelList").appendChild(buttonElement);
      buttonElement.outerHTML = data[panelId].button;
    });
  });
}

if (document.readyState !== "loading") {
    init();
} else {
    document.addEventListener("DOMContentLoaded", init);
}
