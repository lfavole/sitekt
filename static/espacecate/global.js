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