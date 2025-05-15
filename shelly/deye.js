function getDeyeData() {
  Shelly.call("HTTP.REQUEST", {
    method: "GET",
    url: "http://192.168.1.200:8080/api/data/deye/events",
  }, function (res, err) {
    if (res && res.code === 200) {
      let data = JSON.parse(res.body);
      let eventData = data["deye/events"];
      print("✅ Données Deye reçues :", eventData);
      if (eventData && eventData.battery_percent) {
        print("Batterie :", eventData.battery_percent);
        Virtual.getHandle("number:200").setValue(eventData.battery_percent);
      }
      if (eventData && eventData.battery_power) {
        print("Batterie Power:", eventData.battery_power);
        Virtual.getHandle("number:202").setValue(eventData.battery_power);
      }
      if (eventData && eventData.generator_power) {
        print("generator_power Power:", eventData.generator_power);
        Virtual.getHandle("number:200").setValue(eventData.generator_power);
      }
     if (eventData && eventData.inverter_temp) {
        print("inverter_temp :", eventData.inverter_temp);
        Virtual.getHandle("number:203").setValue(eventData.inverter_temp);
      }
           if (eventData && eventData.grid_power) {
        print("grid_power :", eventData.grid_power);
        Virtual.getHandle("number:204").setValue(eventData.grid_power);
      }
    } else {
      print("❌ Erreur requête Deye:", err || res.code);
      Virtual.getHandle("text:200").setValue("Erreur API");
    }
  });
}

Timer.set(10000, true, getDeyeData);
