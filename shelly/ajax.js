function interpretSIAEventCode(code) {
  if (!code) return "Code inconnu";

  var label = "";

  if (code === "RP" || code === "OP") label = "📴 Désactivé";
  else if (code === "CL") label = "🔐 Activé total";
  else if (code === "NL") label = "🌙 Mode nuit";
  else if (code === "TA") label = "📡 Test automatique";
  else if (code === "TR") label = "✅ Test rétabli";
  else if (code === "YG") label = "🚨 Sabotage détecté";
  else if (code === "MA") label = "⚡❌ Alimentation coupée";
  else if (code === "WA") label = "🔋❗ Batterie faible";
  else if (code === "BA") label = "🚨🔔 Alarme déclenchée";
  else label = "❓ Code inconnu : " + code;

  return label;
}


function getSIAEvent() {
  Shelly.call("HTTP.REQUEST", {
    method: "GET",
    url: "http://192.168.1.200:8080/api/data/sia/events",
  }, function (res, err) {
    if (res && res.code === 200) {
      let data = JSON.parse(res.body);
      print("✅ Dernier event SIA:");
      let eventData = data["sia/events"];

      if (eventData && eventData.code) {
        var interpreted = interpretSIAEventCode(eventData.code);
        print("🔔 Interprétation code :", interpreted);
        Virtual.getHandle("text:200").setValue(interpreted);
      } else {
        Virtual.getHandle("text:200").setValue("Aucun événement");
      }
      if (eventData.alarm_triggered == true) {
        print("Status alarm_triggered", eventData.alarm_triggered);
        Virtual.getHandle("boolean:200").setValue(true);
      } else {
       print("Status alarm_triggered", eventData.alarm_triggered);
       Virtual.getHandle("boolean:200").setValue(false);
       }
    } else {
      print("❌ Erreur lors de la requête SIA:", err || res.code);
      Virtual.getHandle("text:200").setValue("Erreur API");
    }
  });
}

// === Run every 15 seconds
Timer.set(5000, true, getSIAEvent);
