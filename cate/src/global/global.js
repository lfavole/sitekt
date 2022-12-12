function input_erreur() {
	var listemois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
	if(!$('<input type="month">').val("2021-01").get(0).valueAsDate) {
		$("input[type=month]").each(function() {
			if($(this).parent().is("span.input-month")) return;
			var e = $(this).hide().wrap($('<span class="input-month">'));
			var c = e.parent();
			var d = new Date();
			var x = this.value.split("-");
			var mois = +x[1] || (d.getMonth() + 1);
			var annee = +x[0] || d.getFullYear();
			function afficher() {
				e.val(annee + "-" + (mois < 10 ? "0" : "") + mois);
			}
			var m = $("<select>").on("input", function() {
				mois = +this.value;
				afficher();
			});
			$.each(listemois, function(i, l) {
				m.append($("<option>").attr("value", i + 1).text(l));
			});
			m.val(mois);
			var a = $('<input type="number" placeholder="Année">').val(annee).on("input", function() {
				annee = +this.value;
				afficher();
			});
			c.append(m).append(a);
		});
	}
	if(!$('<input type="date">').val("2021-01-01").get(0).valueAsDate) {
		$("input[type=date]").each(function() {
			if($(this).parent().is("span.input-date")) return;
			var e = $(this).hide().wrap($('<span class="input-date">'));
			var c = e.parent();
			var d = new Date();
			var x = this.value.split("-");
			var jour = +x[2] || d.getDate();
			var mois = +x[1] || (d.getMonth() + 1);
			var annee = +x[0] || d.getFullYear();
			var max_jour = new Date(new Date(annee, mois, 1, 0, 0, 0) - 1).getDate();
			function afficher() {
				max_jour = new Date(new Date(annee, mois, 1, 0, 0, 0) - 1).getDate();
				j.attr("max", max_jour);
				e.val(annee + "-" + (mois < 10 ? "0" : "") + mois + "-" + (jour < 10 ? "0" : "") + jour);
			}
			var j = $('<input type="number" placeholder="Jour" min="1">').attr("max", max_jour).val(jour).on("input", function() {
				jour = +this.value;
				afficher();
			});
			var m = $("<select>").on("input", function() {
				mois = +this.value;
				afficher();
			});
			$.each(listemois, function(i, l) {
				m.append($("<option>").attr("value", i + 1).text(l));
			});
			m.val(mois);
			var a = $('<input type="number" placeholder="Année">').val(annee).on("input", function() {
				annee = +this.value;
				afficher();
			});
			c.append(j).append(m).append(a);
		});
	}
};
$(input_erreur);

function nb_format(n) {
	var f = new Intl.NumberFormat({lang: "fr-FR"});
	return f.format(n);
}
function pl(n) {
	return n >= 2 ? "s" : "";
}
function mot_pluriel(e, n) {
	if(n < 2 || e.match(/s(\s|$)/)) return e;
	return /\s/.test(e) ? e.replace(/([a-z]+)(\s+.*)/, "$1s$2") : e + "s";
}
function unite_pluriel(u, c) {
	return (/^(j|h|min|s|[A-Z]+|([mcdhkKMGgTt]|da)?[mLgo][²³]?)$/.test(u) ? u : mot_pluriel(u, c));
}
function chiffre(c, u) {
	return nb_format(c) + " " + unite_pluriel(u, c) + (u == "L" && c >= 900 ? " = " + nb_format(c / 1000) + " m³" : "");
}

function cpt_rb(el, ct_date, txtS, txt, opt) {
	if(!el.jquery) el = $(el);
	el.addClass("cpt");
	var txts = {};
	if($.type(txts) == "array")
		txts = {0: txtS[0], inf: txtS[1]};
	else if(!txtS || $.type(txtS) == "string")
		txts = {0: txtS || "CPT", inf: txt || "Le compte à rebours est fini !"};
	else
		txts = txtS;
	if(!txtS)
		opt = txt,
		txt = txtS;
	if($.type(opt) == "function")
		opt = {couleur: opt};
	opt = opt || {};
	opt = $.extend({couleur: null, raccourci: false, un_chiffre: false, anim: true}, opt);
	opt = $.extend(opt, {txts: txts, ct_date: moment(ct_date).toDate().getTime(), el: el, prec: null, timeout: null});
	if(txts["-inf"] || txts.inf) {
		txts[-Infinity] = txts["-inf"] || txts.inf;
		delete txts["-inf"];
		delete txts.inf;
	}
	if(opt.anim)
		el.addClass("anim");
	var id = cpt_rb.cpts.length;
	cpt_rb.cpts[id] = opt;
	var f = function() {
		var debut = performance.now();
		var max = moment.duration(10, "y").add(-1, "ms")._data;
		var cpt = cpt_rb.cpts[this];
		var txts = cpt.txts;
		var ct_date = cpt.ct_date;
		var el = cpt.el;
		var couleur = cpt.couleur;
		var raccourci = cpt.raccourci;
		var un_chiffre = cpt.un_chiffre;
		var now = new Date().getTime();
		var distance = ct_date - now;
		var diff = moment.duration(Math.abs(distance));
		var a = moment(ct_date).isDST();
		var b = moment(now).isDST();
		if(a != b)
			diff.add(a && !b ? 1 : -1, "hours");
		var html = [];
		var t = [];
		t.push(["y", "an"]);
		t.push(["M", "mois"]);
		t.push(["d", "j"]);
		t.push("h");
		t.push("min");
		t.push("s");
		for(var p = false, e, u, i=0, l=t.length; i<l; i++) {
			u = t[i][0];
			e = diff.get(u);
			p = p || e;
			if(html.length) html.push('<span class="hidden2">' + (raccourci && i > 2 ? ":" : " ") + "</span>");
			html.push([e, unite_pluriel(typeof t[i] == "string" ? t[i] : t[i][1] || u, e), u, i < 3 ? e : p]);
		}


		html = html.map(function(e, i) {
			if(typeof e == "string") return e;
			var c = e[0] + "";
			if(!un_chiffre && e[2] != "d" && e[2] != "M" && e[2] != "y" && c < 10) c = "0" + c;
			var s = [], cl = [];
			if(!e[3])
				cl.push("hidden");
			else if(couleur)
				s.push("color:" + ($.type(couleur) == "function" ? couleur(e[0], e[2], max[moment.normalizeUnits(e[2]) + "s"] + 1) : couleur));
			var t = "";
			if(c.length < 2) {
				for(var i=c.length; i<2; i++)
					t += '<span class="hidden"></span>';
			}
			return "<span" + (cl.length ? ' class="' + cl.join(" ") + '"' : "") + (s.length ? ' style="' + s.join("; ") + '"' : "") + ">" + t + "<span>" + [].slice.call(c, 0).join("</span><span>") + "</span>" + (raccourci && i > 2 ? "" : " <small>" + e[1] + "</small>") + "</span>";
		});
		var join = function(a, r) {
			return a.map(function(e, i) {
				return e + (i < a.length - 1 ? '<span class="hidden2">' + (r || i < 3 ? " " : ':') + "</span>" : "");
			}).join("");
		};
		var txt;
		for(var i in txts) {
			if(distance > i * 1000) {
				txt = $.type(txts[i]) == "function" ? txts[i]() : txts[i];
				if(cpt.prec != txt)
					// el.html(txt.replace(/CPT/g, html.join(" ")));
					el.html(txt.replace(/CPT/g, html.join("")));
					// el.html(txt.replace(/CPT/g, join(html, raccourci)));
				cpt.prec = txt;
				$.each(html, function(x, e) {
					e = $(e);
					if(e.text() == e.html()) {
						var elt = el.eq(x);
						e.toggleClass("hidden", elt.hasClass("hidden"));
						if(e.attr("style") != elt.attr("style"))
							e.attr("style", elt.attr("style"));
						if(e.html() != elt.html())
							e.html(elt.html());
						return;
					}
					if(e.find("> span").length == 1)
						e.prepend($("<span>").hide());
					var elt = el.find("> span").eq(x);
					elt.toggleClass("hidden", e.hasClass("hidden"));
					if(elt.attr("style") != e.attr("style"));
						elt.attr("style", e.attr("style"));
					for(var t, t2, nb=1, l=e.children().length; nb<=l; nb++) {
						t = elt.find(":nth-child(" + nb + ")");
						t2 = e.find(":nth-child(" + nb + ")");
						t.toggleClass("hidden", t2.hasClass("hidden"));
						if(t.attr("style") != t2.attr("style"))
							t.attr("style", t2.attr("style"));
						if(t.html() != t2.html())
							t.attr("data-prec", t.text().trim()),
							t.attr("data-act", t2.text().trim()),
							t.addClass("prec"),
							setTimeout(function() {
								this.removeClass("prec");
							}.bind(t), 400),
							t.html(t2.html());
					}
				});
				if(!txt.match(/CPT/g))
					return;
				break;
			}
		}
		var fin = performance.now();
		cpt.timeout = setTimeout(cpt.f, 1000 - (fin - debut));
	}.bind(id);
	opt.f = f;
	f();
}
cpt_rb.cpts = [];

function calc_soleil(lat, lon, fh, mois, j, m) {
	if(lat == null) lat = position.latitude;
	if(lon == null) lon = position.longitude;
	var r = {};
	var a = !m || m == 1 ? moment().format("Y") : m;
	var CONVERT = 180 / Math.PI;
	r.lat = lat / CONVERT; r.lon = -lon / CONVERT; r.mois = mois; r.jour = j; r.fh = fh;
	var txtd = a + "-" + (mois < 10 ? "0" : "") + mois + "-" + (j < 10 ? "0" : "") + j;
	var jr = r.j = Math.floor((new Date(txtd) - new Date(a + "-01-01")) / 864e5) + 1;

	var a = 2 * Math.PI * (jr - 1) / 365;
	r.dec = 0.006918 - 0.399912 * Math.cos(a) + 0.070257 * Math.sin(a) - 0.006758 * Math.cos(2 * a) + 0.000907 * Math.sin(2 * a) - 0.002697 * Math.cos(3 * a) + 0.00148 * Math.sin(3 * a);

	var M = (357.5291 + 0.98560028 * jr) / CONVERT;
	var C = 1.9148 * Math.sin(M) + 0.02 * Math.sin(2 * M) + 0.0003 * Math.sin(3 * M);
	var L = (280.4665 + C + 0.98564736 * jr) / CONVERT;
	var R = -2.468 * Math.sin(2 * L) + 0.053 * Math.sin(4 * L) - 0.0014 * Math.sin(6 * L);
	r.eqt = (C + R) / 15;

	r.am = 90 - (r.lat - r.dec) * CONVERT;
	r.hm = (12 + r.lon * CONVERT / 15 + r.eqt + fh) % 24;
	var cosgha = (-0.01396218 - Math.sin(r.dec) * Math.sin(r.lat)) / Math.cos(r.dec) / Math.cos(r.lat);
	var cosazi = (Math.sin(r.dec) + 0.010471784 * Math.sin(r.lat)) / 0.999902524 / Math.cos(r.lat);
	if (cosgha >= -1 && cosgha <= 1 && cosazi >= -1 && cosazi <= 1) {
		var gha = Math.acos(cosgha);
		r.hl = (24 + r.hm - gha * 12 / Math.PI) % 24;
		r.hc = (24 + r.hm + gha * 12 / Math.PI) % 24;
		r.al = Math.acos(cosazi) * CONVERT;
		r.ac = 360 - r.al;
	} else {
		r.hl = "-";
		r.hc = "-";
		r.al = "-";
		r.ac = "-";
		if(r.am <= -2) {
			r.am = "-";
			r.hm = "-";
		}
	}
	if(m)
		for(var i in r)
			if(i[0] == "h")
				r[i] = moment(r[i] == "-" ? NaN : txtd).add(r[i], "h");
	return r;
}
moment.fn.soleil = function(lat = null, lon = null) {
	return calc_soleil(lat, lon, this.utcOffset() / 60, this.month() + 1, this.date(), true);
};
$.each(["Before", "BeforeOr", "After", "AfterOr", ""], function(i, e) {
	$.each(["Sunrise", "Meridian", "Sunset"], function(ii, ee) {
		var f = "is" + e + ee;
		var f2 = "is" + (e.substr(-2) == "Or" ? "SameOr" + e.substr(0, e.length - 2) : e || "Same");
		moment.fn[f] = function() {
			return this[f2](this.soleil()["h" + "lmc"[ii]]);
		};
	});
});
var position = {
	latitude: 44.5662047,
	longitude: 6.48334128
};
var mode_nuit = {
	date: null,
	interval: null,
	auto: function(jr) {
		if(mode_nuit.interval == null)
			mode_nuit.interval = setInterval(function() {
				if(new Date() >= mode_nuit.date)
					mode_nuit.date += 864e5,
					mode_nuit.auto("i");
			}, 1000);
		var interval = false;
		if(jr == "i")
			interval = true,
			jr = undefined;

		$(".cpt-soleil").remove();
		jr = jr ? moment(jr) : moment();
		var j = moment();
		var d = calc_soleil(null, null, jr.isDST() ? 2 : 1, jr.format("M"), jr.format("D"), true);
		d = [d.hl, d.hc];
		if(!d[0].isValid() || !d[1].isValid()) {
			console.warn("Erreur dans le calcul du lever / coucher du soleil");
			return;
		}
		var nuit, dt;
		if(j.isBefore(d[0]))
			nuit = true, dt = d[0];
		else if(j.isBefore(d[1]))
			nuit = false, dt = d[1];
		else
			return mode_nuit.auto(j.add(1, "day"));

		// var div = $("<div>").addClass("cpt-soleil").appendTo("body");
		// $("head").append($("<style>").html(".cpt-soleil {position:fixed; bottom:0px; right:0px; padding:4px 8px; background-color:#f88; border-top-left-radius:8px;} @media(max-width: 500px) {.espace-cpt-soleil {height:30px;} .cpt-soleil {right:unset; left:50%; transform:translateX(-50%); border-radius:8px 8px 0px 0px;}}"));
		// $("main").append($("<div>").addClass("espace-cpt-soleil"));
		// cpt_rb(div, dt);
		$("body").toggleClass("mode-nuit", nuit);
		console.log((nuit ? "Lever" : "Coucher") + " du soleil à :", dt);
		mode_nuit.date = dt;
		if(interval) {
			var el = $("<div>").addClass("popup").html(nuit ? "Bonne nuit !" : "Bonjour !").appendTo($("body"));
			setTimeout(function() {el.remove();}, 4000);
		}
	}
};

/*
function mode_nuit_auto(jr) {
	$(".cpt-soleil").remove();
	jr = jr ? moment(jr) : moment();
	var j = moment();
	var d = calc_soleil(44.5662047, 6.48334128, jr.isDST() ? 2 : 1, jr.format("M"), jr.format("D"), true);
	d = [d.hl, d.hc];
	if(!d[0].isValid() || !d[1].isValid()) {
		console.warn("Erreur dans le calcul du lever / coucher du soleil");
		return;
	}
	var cpt = function(date) {
		// var div = $("<div>").addClass("cpt-soleil").attr("style", "position:fixed; bottom:0%; left:50%; transform:translateX(-50%); padding:4px 8px; background-color:#f88; border-radius:8px 8px 0px 0px;").appendTo("body");
		// cpt_rb(div, date);
		// return div;
	};
	var div_cpt;
	if(j.isBefore(d[0]))
		div_cpt = cpt(d[0]),
		$("body").addClass("mode-nuit"),
		console.log("d[0] :", d[0]),
		setTimeout(function() {
			$(".cpt-soleil").remove();
			$("body").removeClass("mode-nuit");
			var el = $("<div>").addClass("popup").html("Bonjour !").appendTo($("body"));
			setTimeout(function() {el.remove();}, 4000);
			mode_nuit_auto();
		}, d[0].diff(j));
	else if(j.isBefore(d[1]))
		div_cpt = cpt(d[1]),
		$("body").removeClass("mode-nuit"),
		console.log("d[1] :", d[1]),
		setTimeout(function() {
			$(".cpt-soleil").remove();
			$("body").addClass("mode-nuit");
			var el = $("<div>").addClass("popup").html("Bonne nuit !").appendTo($("body"));
			setTimeout(function() {el.remove();}, 4000);
			mode_nuit_auto();
		}, d[1].diff(j));
	else
		mode_nuit_auto(j.add(1, "day"));
}
*/
var mode_nuit_auto = mode_nuit.auto;