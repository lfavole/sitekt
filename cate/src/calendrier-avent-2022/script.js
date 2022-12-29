/* global YT */

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
			$("body").removeClass(this.classe(this.prec));
			if(this.href != location.href) history.pushState({}, "", this.href);
		} else {
			this.page_chargee();
		}
		this.prec = location.href;
		$("body").addClass(this.classe(location.href));
	},
	page_chargee: function() {
		input_erreur();
		var cpts, d;
		if((cpts = $(".texte .cpt")).length && (d = $("body").attr("class").match(/\bj(\d+)\b/))) {
			var date = moment([2022, 11, d[1]]);
			cpts.each(function(i, e) {
				var d = date.clone();
				if($(e).is(".debut")) d.date(1);
				cpt_rb(e, d);
			});
		}
	},
	classe: function(e) {
		var m;
		e = e.split("?");
		if(e[1] && (m = e[1].match(/^j=(\d+)/)))
			return "j" + m[1];
		else
			return "calendrier-avent";
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
		var prec = location.href;
		this.init();
		var m = href.match(/^\?j=(\d+)/);
		if(m) {
			var j = +m[1];
			var title = "" + j + (j == 1 ? "er" : "") + " décembre";
			var c = " – Calendrier de l'Avent";
			document.title = title + c;
			$("main")
				.html("")
				.append(
					$("<h1>")
						.html(title.replace(/(\d+)(er)\b/, "$1<sup>$2</sup>"))
				)
				.append($("<div>").addClass("texte").html('<div class="prog"><p>Chargement en cours...</p><div class="progress"></div></div>'));
			$.get("?j=" + j + "&xhr=1").always(function(html, status, xhr) {
				if(status == "error") {
					xhr = html;
					html = xhr.response || xhr.responseText || "";
				}
				// html = $.parseHTML(html);
				// html = [(html.match(/<h1>(.*?)<\/h1>/) || [""])[1], (html.match(/<div class="texte">(.*?)<\/div>/) || [""])[1]];
				html = $("<div>").html(html).children();
				$("h1").html(html[0].innerHTML);
				$(".texte").attr("class", html[1].className).html(html[1].innerHTML);
				document.title = (html[0].textContent || html[0].innerText) + c;
				pages.page_chargee();
			});
			return;
		}
		m = href.match(/calendrier-avent(\/(index\.php)?)?\??$/);
		if(m) {
			var title = "Calendrier de l'Avent";
			document.title = title;
			var jours1 = $("<div>").addClass("jours");
			var jours2 = $("<div>").addClass("jours");
			var date = new Date();
			for(var day = 1; day <= 25; day++)
				(day == 25 ? jours2 : jours1).append($("<a>").toggleClass("ajd", date.getMonth() == 12 && date.getDate() == day).attr("href", "?j=" + day).html(day));

			$("main")
				.html("")
				.append(
					$("<h1>").html(title)
				)
				.append(jours1)
				.append(jours2)
				.append($("<div>").addClass("note-photos").html("NB : n'hésitez pas à cliquer sur les photos pour les agrandir."));
			pages.page_chargee();
			return;
		}
		if(get && post) {
			href += (href.indexOf("?") < 0 ? "?" : "&") + post;
			this.href = href;
			post = null;
		}
		$("main").addClass("chargement").html('<div class="prog"><p>Chargement en cours...</p><div class="progress"></div></div>');
		$.ajax({
			url: href,
			method: get ? "GET" : "POST",
			data: post || null
		}).always(pages.ajaxLoad);
	}
};

$(function() {
	if("serviceWorker" in navigator)
		navigator.serviceWorker.register("/calendrier-avent/sw.js");

	String.prototype.decodeHTML = function() {
		return $("<div>", {html: "" + this}).text();
	};

	pages.init();
	moment.locale("fr");
	moment.locale(navigator.language);
	moment.locale(navigator.languages || []);

	$("header .mode").click(function() {
		$("body").toggleClass("mode-nuit");
	});

	$(window).on("popstate", function(e) {
		if(e.originalEvent.state !== null) {
			pages.href = pages.href2 = location.href;
			pages.loadPage(location.href);
			$(".popup-photo .fermer").click();
		}
	}).on("popstate hashchange", function() {
		if(location.hash.replace(/^#/, "") == "")
			history.replaceState(history.state, "", location.href.match(/^(.*?)(?:#.*)?$/)[1]);
	});

	$(document).on("click", "a, area", function(e) {
		if(!$(this).attr("href") || $(this).attr("target") == "_blank" || ($(this).is("nav a") && !$(this).attr("href").replace(/^#/, ""))) return;
		var href = $(this).attr("href") || "";
		var href2 = this.href || "";
		if(href.match(/(calendrier|_pdf)\.php(?:\?.*)?$/)) return;
		if((href.indexOf(document.domain) > -1 || href.indexOf(":") === -1) && href.substr(0, 1) != "#") {
			pages.txt_lien = this.textContent || this.innerText;
			pages.href = href;
			pages.href2 = href2;
			e.preventDefault();
			pages.loadPage(href);
			return false;
		}
	}).on("submit", "form", function(evt) {
		if(evt.isDefaultPrevented()) return;
		var form = $(evt.target);
		if(typeof evt.target.pushstate == "undefined" && form.get(0).method.toUpperCase() != "GET") return;
		pages.loadPage(pages.href = form.attr("action") || location.pathname, form.serialize(), form.attr("method").toUpperCase() == "GET");
		evt.preventDefault();
	});

	/*
	var media = window.matchMedia("(prefers-color-scheme: dark)");
	$("body").toggleClass("mode-nuit", media.matches);
	media.addEventListener("change", function(e) {
		$("body").toggleClass("mode-nuit", e.matches);
	});
	*/

	mode_nuit_auto();

	var popupPhoto = $("<div>")
		.addClass("popup-photo")
		.attr("style", "position:fixed; left:0; right:0; top:0; bottom:0; background-color:rgba(0, 0, 255, 0.4); background-position:center; background-size:contain; background-repeat:no-repeat;")
		.append(
			$("<div>")
				.addClass("fermer")
				.click(function() {
					$(this).parent().hide("fade").css("background-image", "");
					$("body").css("overflow", "");
				})
		)
		.hide()
		.appendTo("body");
	$("body").on("click", "img", function() {
		popupPhoto.show("fade").css("background-image", "url(" + $(this).attr("src") + ")");
		$("body").css("overflow", "hidden");
	});

	// https://maxl.us/hide-related

	// Activate only if not already activated
	if(window.hideYTActivated)
		return;
	// Load API
	if(typeof YT === "undefined")
		$("<script>").attr("src", "https://www.youtube.com/iframe_api").insertBefore($("script").first());

	// Activate on all players
	var ytAPIReadyCallbacks = [];
	$(".hytPlayerWrap").each(function(_i, playerWrap) {
		var playerFrame = playerWrap.find("iframe").get(0);

		function onPlayerStateChange(event) {
			if(event.data == YT.PlayerState.ENDED) {
				playerWrap.classList.add("ended");
			} else if(event.data == YT.PlayerState.PAUSED) {
				playerWrap.classList.add("paused");
			} else if(event.data == YT.PlayerState.PLAYING) {
				playerWrap.classList.remove("ended");
				playerWrap.classList.remove("paused");
			}
		}

		var player;
		ytAPIReadyCallbacks.push(function() {
			player = new YT.Player(playerFrame, {events: {onStateChange: onPlayerStateChange}});
		});

		playerWrap.on("click", function() {
			var playerState = player.getPlayerState();
			if(playerState == YT.PlayerState.ENDED)
				player.seekTo(0);
			else if(playerState == YT.PlayerState.PAUSED)
				player.playVideo();
		});
	});

	window.onYouTubeIframeAPIReady = function() {
		for(var callback of ytAPIReadyCallbacks)
			callback();
	};

	window.hideYTActivated = true;
});