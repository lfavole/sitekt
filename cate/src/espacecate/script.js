var pages = {
href: "",
href2: "",
chargement: false,
int_chargement: "",
txt_lien: "",
prec: {},

init: function() {
	if(this.href != "") {
		history.replaceState({}, "", location.href);
		var page = this.prec.href.match(/([a-z_]+)\.php$/);
		page = page ? (page[1] || "index") : "index";
		$("body").removeClass(page);
		if(this.href != location.href) history.pushState({}, "", this.href);
	} else this.page_chargee();
	$.extend(this.prec, location);
	var p = location.pathname.match(/^.*\/(.*)(?:\?.*)?$/);
	p = p ? (p[1] || "index.php") : "index.php";
	/*
	var m = location.search.match(/^\?page=([a-z_]+)/);
	m = m ? (m[1] || "index") : "index";
	*/
	var m = p.match(/^(.*)\.php$/);
	m = m ? (m[1] || "index") : "index";
	$("body").addClass(m);
	$("nav a").each(function(i, l) {
		var u = $(l).attr("href");
		var mm = /(.*)\.php/.exec(u);
		if(u[0] == "#" || u[0] == "/") mm = ["", ""];
		else if(!mm) mm = ["", "index"];
		$(l).toggleClass("act", m == mm[1]);
		if($(l).is("nav ul ul a"))
			for(var i=l; i; i = i.parentElement)
				if($(i).is("nav ul > li:has(> a + ul)")) {
					if(!$("> a", i).is(".act")) $("> a", i).toggleClass("act", m == mm[1]);
					break;
				}
	});
},
page_chargee: function() {
	input_erreur();
	if(location.pathname.match(/quiz\.php$/))
		$("head").append($('<link rel="stylesheet">').attr("href", "res/quiz.css"));
},

ajaxLoad: function(html, status, xhr) {
	var m = $("main");
	m.removeClass("chargement");
	pages.chargement = false;
	if(status == "error") {
		xhr = html;
		html = xhr.response || xhr.responseText || "";
	}
	if(xhr.getResponseHeader("Location")) {
		location.href = xhr.getResponseHeader("Location");
		return;
	}
	m.html("");
	document.title = (html.match(/<title>(.*?)<\/title>/) || ["", ""])[1].trim().decodeHTML();
	var html2 = html.match(/<main(?: class="(.*?)")?.*?>([^]*)<\/main>/m) || html.match(/<body()>([^]*)<\/body>/m) || ["", "", html];
	m[0].className = (html2 === null ? "" : html2[1] || "");
	m.html(m.html() + (html2 === null ? "" : html2[2]));
	pages.page_chargee();
},

loadPage: function(href, post = null, get = true) {
	if(get && post) {
		this.href = href += (href.indexOf("?") < 0 ? "?" : "&") + post;
		post = null;
	}
	var prec = location.href;
	this.init();
	$("main").addClass("chargement").html('<div class="prog"><p>Chargement en cours...</p><div class="progress"></div></div>');
	$.ajax({
		url: href,
		method: get ? "GET" : "POST",
		data: post || null,
		success: pages.ajaxLoad,
		error: pages.ajaxLoad
	});
}
};

$(function() {
	if("serviceWorker" in navigator)
		navigator.serviceWorker.register("/espacecate/sw.js");

	String.prototype.decodeHTML = function() {
		return $("<div>", {html: "" + this}).html();
	};

	pages.init();
	moment.locale("fr");
	moment.locale(navigator.language);
	moment.locale(navigator.languages || []);

	$(window).on("popstate", function(e) {
		if(e.originalEvent.state !== null) {
			pages.href = pages.href2 = location.href;
			pages.loadPage(location.href);
		}
	}).on("popstate hashchange", function() {
		if(location.hash.replace(/^#/, "") == "")
			history.replaceState(history.state, "", location.href.match(/^(.*?)(?:#.*)?$/)[1]);
	});

	$(document).on("click", "a, area", function(e) {
		if(!$(this).attr("href") || $(this).attr("target") == "_blank" || !$(this).attr("href").replace(/^#/, "") || $(this).attr("href").match(/^\//)) return;
		var href = $(this).attr("href") || "";
		var href2 = this.href || "";
		if(href.match(/(calendrier|_pdf)\.php(?:\?.*)?$/)) return;
		if((href.indexOf(document.domain) > -1 || href.indexOf(':') === -1) && href.substr(0, 1) != "#") {
			pages.txt_lien = this.textContent || this.innerText;
			pages.href = href;
			pages.href2 = href2;
			e.preventDefault();
			pages.loadPage(href);
			menu_fermer();
			this.blur();
			return false;
		}
	}).on("submit", "form", function(e) {
		if(e.isDefaultPrevented()) return;
		var f = $(e.target);
		if(typeof e.target.pushstate == "undefined" && f.get(0).method.toUpperCase() != "GET") return;
		pages.loadPage(pages.href = f.attr("action") || location.pathname, f.serialize(), f.attr("method").toUpperCase() == "GET");
		e.preventDefault();
	});
	$(window).on("resize", function() {
		if(innerWidth > 500) menu_fermer();
	});

	/*
	var media = window.matchMedia("(prefers-color-scheme: dark)");
	$("body").toggleClass("mode-nuit", media.matches);
	media.addEventListener("change", function(e) {
		$("body").toggleClass("mode-nuit", e.matches);
	});
	*/

	mode_nuit_auto();
});
function menu_ouvrir() {
	if($(".menu").is(".ouvert")) return;
	$(".menu").addClass("ouvert").css("opacity", 1);
	$("body").css("overflow", "hidden");
}
function menu_fermer() {
	if(!$(".menu").is(".ouvert")) return;
	$(".menu").removeClass("ouvert");
	$("body").css("overflow", "");
	setTimeout(function() {
		$(".menu").css("opacity", "");
	}, innerWidth > 500 ? 0 : 1000);
}