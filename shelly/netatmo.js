function interpretRainStatus(rain) {
  if (!rain) return "❓ Donnée manquante";
  if (rain.Rain > 0) return "🌧️ Il pleut maintenant";
  if (rain.sum_rain_1 > 0) return "🌦️ Pluie récente (1h)";
  if (rain.sum_rain_24 > 0) return "☁️ Pluie aujourd'hui";
  return "☀️ Temps sec";
}

function getNetatmoRain() {
  Shelly.call("HTTP.REQUEST", {
    method: "GET",
    url: "http://192.168.1.200:8080/api/data/netatmo/events"
  }, function (res, err) {
    if (res && res.code === 200) {
      let payload = JSON.parse(res.body);
      let netatmo = payload["netatmo/events"];
      print(netatmo);
      let devices = [];
      if (netatmo && netatmo.body && netatmo.body.devices) {
       devices = netatmo.body.devices;
       }
      let rainModule = null;
      for (let d of devices) {
        for (let m of d.modules) {
          if (m.module_name === "Pluviomètre") {
            rainModule = m;
            break;
          }
        }
      }

      if (rainModule && rainModule.dashboard_data) {
        let rain = rainModule.dashboard_data;

        let status = interpretRainStatus(rain);
        print("🌧️ Statut pluie :", status);
        Virtual.getHandle("text:200").setValue(status);

        // Affecter les 3 valeurs numériques
        Virtual.getHandle("number:200").setValue(parseFloat(rain.Rain || 0));
        Virtual.getHandle("number:201").setValue(parseFloat(rain.sum_rain_1 || 0));
        Virtual.getHandle("number:202").setValue(parseFloat(rain.sum_rain_24 || 0));
        let now = new Date();

        let hh = now.getHours();
        let mm = now.getMinutes();
        let day = now.getDate();
        let month = now.getMonth() + 1;

        let timeStr =
          (hh < 10 ? "0" + hh : hh) + ":" +
          (mm < 10 ? "0" + mm : mm) + " " +
          (day < 10 ? "0" + day : day) + "/" +
          (month < 10 ? "0" + month : month);

        Virtual.getHandle("text:201").setValue("🕒 " + timeStr);

      } else {
        print("❌ Module Pluviomètre introuvable");
        Virtual.getHandle("text:200").setValue("Pluviomètre manquant");
        Virtual.getHandle("number:200").setValue(0);
        Virtual.getHandle("number:201").setValue(0);
        Virtual.getHandle("number:202").setValue(0);
      }
    } else {
      print("❌ Erreur API :", err || res.code);
      Virtual.getHandle("text:200").setValue("Erreur API pluie");
    }
  });
}

Timer.set(5000, true, getNetatmoRain);
