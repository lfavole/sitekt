document.addEventListener("DOMContentLoaded", function () {
    function updateGroup() {
        const inputs = Array.from(group.querySelectorAll('input[name$="-is_present"]'))
        .filter(i => !i.disabled && !/__prefix__/.test(i.name));
        if (!inputs.length) {
            badge.style.display = "none";
            return;
        }
        const total = inputs.length;
        const absent = inputs.filter(i => !i.checked).length;
        const percent = (absent / total) * 100;
        badge.textContent = `Taux d'absentéisme : ${fmt.format(percent)} % (${absent} absent${absent >= 2 ? "s" : ""} sur ${total})`;
        badge.style.display = "";
    }

    const fmt = new Intl.NumberFormat({}, {maximumFractionDigits: 1});

    const group = document.getElementById("attendance_set-group");

    const badge = document.createElement("div");
    badge.className = "attendance-absent-rate";
    badge.style.margin = "0.5em 0";
    badge.style.fontWeight = "bold";
    group.appendChild(badge);

    updateGroup();
    group.addEventListener("change", updateGroup);
    document.addEventListener("formset:added", updateGroup);
    document.addEventListener("formset:removed", updateGroup);
});
