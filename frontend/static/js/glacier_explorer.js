document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/glaciers")
    .then(res => res.json())
    .then(data => initMap(data))
    .catch(err => console.error("API error:", err));
});

function initMap(glaciers) {

  const map = L.map("map").setView([30.5, 79.5], 6);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap"
  }).addTo(map);

  function riskColor(risk) {
    if (risk === "High") return "#d73027";
    if (risk === "Medium") return "#fc8d59";
    return "#1a9850";
  }

  glaciers.forEach(g => {
    if (g.lat === null || g.lon === null) return;

    const marker = L.circleMarker([g.lat, g.lon], {
      radius: 4,
      color: riskColor(g.risk_level),
      fillColor: riskColor(g.risk_level),
      fillOpacity: 0.8
    }).addTo(map);

    marker.on("click", () => {

      const area = g.area_km2 !== null ? g.area_km2.toFixed(2) : "NA";
      const melt = g.predicted_melt !== null ? g.predicted_melt.toFixed(2) : "NA";

      document.getElementById("glacier-info").innerHTML = `
        <h3>${g.glacier_id}</h3>

        <p><b>Latitude:</b> ${g.lat.toFixed(4)}</p>
        <p><b>Longitude:</b> ${g.lon.toFixed(4)}</p>

        <p><b>Area:</b> ${area} km²</p>
        <p><b>Predicted Melt:</b> ${melt}</p>

        <p><b>Risk Level:</b>
          <span style="color:${riskColor(g.risk_level)}; font-weight:600">
            ${g.risk_level}
          </span>
        </p>
      `;
    });
  });

  console.log(`🗺️ Rendered ${glaciers.length} glaciers`);
}
