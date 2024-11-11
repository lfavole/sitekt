function mot_pluriel(e, n) {
	if(n < 2 || e.match(/s(\s|$)/)) return e;
	return /\s/.test(e) ? e.replace(/([a-z]+)(\s+.*)/, "$1s$2") : e + "s";
}
function unite_pluriel(u, c) {
	return (/^(j|h|min|s|[A-Z]+|([mcdhkKMGgTt]|da)?[mLgo][²³]?)$/.test(u) ? u : mot_pluriel(u, c));
}

function countdown(options) {
	var opt = $.extend({
		couleur: null,
		raccourci: false,
		unChiffre: false,
		anim: true
	}, options || {}, {
		prec: null,
		timeout: null
	});
	opt.date = moment(opt.date).toDate().getTime();
	opt.element = $(opt.element);
	opt.element.addClass("cpt");
	opt.txts = opt.txts || {
		0: "CPT",
		[-Infinity]: "Le compte à rebours est fini !"
	};
	if(opt.txts["-inf"] || opt.txts.inf) {
		opt.txts[-Infinity] = opt.txts["-inf"] || opt.txts.inf;
		delete opt.txts["-inf"];
		delete opt.txts.inf;
	}
	if(opt.anim)
		opt.element.addClass("anim");
	var id = countdown.cpts.length;
	countdown.cpts[id] = opt;
	var f = function() {
		var debut = performance.now();
		var max = moment.duration(10, "y").add(-1, "ms")._data;
		var cpt = countdown.cpts[this];
		var txts = cpt.txts;
		var date = cpt.date;
		var el = cpt.element;
		var couleur = cpt.couleur;
		var raccourci = cpt.raccourci;
		var unChiffre = cpt.un_chiffre;
		var now = new Date().getTime();
		var distance = date - now;
		var diff = moment.duration(Math.abs(distance));
		var a = moment(date).isDST();
		var b = moment(now).isDST();
		if(a != b)
			diff.add(a && !b ? 1 : -1, "hours");
		var html = [];
		var units = [];
		units.push(["y", "an"]);
		units.push(["M", "mois"]);
		units.push(["d", "j"]);
		units.push("h");
		units.push("min");
		units.push("s");
		for(var p = false, e, u, i = 0, l = units.length; i < l; i++) {
			u = units[i][0];
			e = diff.get(u);
			p = p || e;
			if(html.length) html.push('<span class="hidden2">' + (raccourci && i > 2 ? ":" : " ") + "</span>");
			html.push([
				e,
				unite_pluriel(typeof units[i] == "string" ? units[i] : units[i][1] || u, e),
				u,
				i < 3 ? e : p
			]);
		}


		html = html.map(function(part, index) {
			if(typeof part == "string") return part;
			var c = part[0] + "";
			if(!unChiffre && part[2] != "d" && part[2] != "M" && part[2] != "y" && c < 10) c = "0" + c;
			var cssColors = [];
			var classes = [];
			if(!part[3])
				classes.push("hidden");
			else if(couleur)
				cssColors.push("color:" + (typeof couleur == "function" ? couleur(part[0], part[2], max[moment.normalizeUnits(part[2]) + "s"] + 1) : couleur));
			var t = "";
			if(c.length < 2) {
				for(var iter = c.length; iter < 2; iter++)
					t += '<span class="hidden"></span>';
			}
			return "<span" + (classes.length ? ' class="' + classes.join(" ") + '"' : "") + (cssColors.length ? ' style="' + cssColors.join("; ") + '"' : "") + ">" + t + "<span>" + [].slice.call(c, 0).join("</span><span>") + "</span>" + (raccourci && index > 2 ? "" : " <small>" + part[1] + "</small>") + "</span>";
		});
		var txt;
		for(var i in txts) {
			if(distance > i * 1000) {
				txt = typeof txts[i] == "function" ? txts[i]() : txts[i];
				if(cpt.prec != txt)
					el.html(txt.replace(/CPT/g, html.join("")));
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
					for(var t, t2, nb = 1, l = e.children().length; nb <= l; nb++) {
						t = elt.find(":nth-child(" + nb + ")");
						t2 = e.find(":nth-child(" + nb + ")");
						t.toggleClass("hidden", t2.hasClass("hidden"));
						if(t.attr("style") != t2.attr("style"))
							t.attr("style", t2.attr("style"));
						if(t.html() != t2.html()) {
							t.attr("data-prec", t.text().trim());
							t.attr("data-act", t2.text().trim());
							t.addClass("prec");
							setTimeout(function() {
								this.removeClass("prec");
							}.bind(t), 400);
							t.html(t2.html());
						}
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
countdown.cpts = [];
