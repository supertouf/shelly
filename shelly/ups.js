function interpretUPSStatus(status) {
  if (!status) return "Statut inconnu";

  var parts = status.split(" ");
  var messages = "";

  for (var i = 0; i < parts.length; i++) {
    var part = parts[i];
    if (part === "OL") messages += "✅ Secteur OK / ";
    else if (part === "OB") messages += "⚠️ Sur batterie / ";
    else if (part === "CHRG") messages += "🔌 En charge / ";
    else if (part === "DISCHRG") messages += "🔋 Décharge / ";
    else if (part === "LB") messages += "❗ Batterie faible / ";
    else if (part === "RB") messages += "❗ Batterie à remplacer / ";
  }

  return messages !== "" ? messages.slice(0, -3) : "⚠️ Statut inconnu";
}

function getUPSEvent() {
  Shelly.call("HTTP.REQUEST", {
    method: "GET",
    url: "http://192.168.1.200:8080/api/data/ups/events",
  }, function (res, err) {
    if (res && res.code === 200) {
      let data = JSON.parse(res.body);
      print("✅ Dernier event UPS:");

      let eventData = data["ups/events"];

      if (eventData && eventData["battery.charge"]) {
        print("🔋 Batterie =", eventData["battery.charge"]);
        Virtual.getHandle("number:200").setValue(parseFloat(eventData["battery.charge"]));
      } else {
        print("⚠️ Charge batterie non trouvée");
        Virtual.getHandle("text:200").setValue("Aucune donnée");
      }

      let status = eventData["ups.status"];
      let readableStatus = interpretUPSStatus(status);
      Virtual.getHandle("text:200").setValue(readableStatus);

    } else {
      print("❌ Erreur API :", err || res.code);
      Virtual.getHandle("text:200").setValue("Erreur API");
    }
  });
}

Timer.set(5000, true, getUPSEvent);
