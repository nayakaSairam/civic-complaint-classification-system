// geo.js

let currentCoords = null;

document.addEventListener("DOMContentLoaded", () => {
  const locationInput = document.getElementById("complaint-location");
  const form = document.getElementById("complaintForm");

  // Add "Use My Location" button dynamically
  if (locationInput) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "📍 Use My Location";
    btn.id = "getLocationBtn";
    btn.style.marginLeft = "10px";
    locationInput.insertAdjacentElement("afterend", btn);

    btn.addEventListener("click", () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            currentCoords = { lat, lng };

            locationInput.value = `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
            alert("Location captured successfully!");
          },
          (error) => {
            console.error("Geolocation error:", error);
            alert("Unable to fetch location. Please enter manually.");
          }
        );
      } else {
        alert("Geolocation is not supported by this browser.");
      }
    });
  }

  // Hook into form submission without touching app.js
  if (form) {
    form.addEventListener("submit", () => {
      if (currentCoords) {
        // You would typically attach this to the form data to be sent.
        // For this refactored version, app.js will handle passing this.
        // We'll leave this part as is, as app.js already handles the submission logic.
      }
    });
  }
});