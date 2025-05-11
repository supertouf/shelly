function getSIAEvent() {
  Shelly.call("HTTP.REQUEST", {
    method: "GET",
    url: "http://192.168.1.200:8080/api/data/sia/events",
  }, function (res, err) {
    if (res && res.code === 200) {
      let data = JSON.parse(res.body);
      print("✅ Dernier event SIA:");
      let eventData = data["sia/events"];

      if (eventData.event_type) {
         print("Status event_type", eventData.event_type);
        Virtual.getHandle("text:200").setValue(eventData.event_type);
      } else {
       Virtual.getHandle("text:200").setValue("Aucun yiki event");
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
