const clock = document.getElementById("clock");
const date = document.getElementById("date");
const launch = document.querySelector('[data-target="accesos-menues"]');

function renderClock() {
  const now = new Date();
  clock.textContent = now.toLocaleTimeString("es-EC", {
    hour: "2-digit",
    minute: "2-digit",
  });
  date.textContent = now.toLocaleDateString("es-EC", {
    weekday: "long",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

renderClock();
setInterval(renderClock, 1000);

if (launch) {
  launch.addEventListener("click", () => {
    const target = new URL("../accesos-menues/frontend/index.html", window.location.href);
    window.location.assign(target.toString());
  });
}
