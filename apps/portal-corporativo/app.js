const clock = document.getElementById("clock");
const date = document.getElementById("date");
const launch = document.querySelector('[data-target="accesos-menues"]');
const sessionBadge = document.getElementById("sessionBadge");
const sessionSummary = document.getElementById("sessionSummary");
const sessionStatus = document.getElementById("sessionStatus");
const modulesGrid = document.getElementById("portalModules");
const accessGrid = document.getElementById("portalAccessList");
const notificationsList = document.getElementById("portalNotifications");
const quickActions = document.getElementById("portalQuickActions");
const statusStack = document.getElementById("portalStatusStack");
const tree = document.getElementById("portalTree");
const portalWelcome = document.getElementById("portalWelcome");
const userRoles = document.getElementById("portalRoles");
const userGroups = document.getElementById("portalGroups");
const launchStatus = document.getElementById("portalLaunchStatus");

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

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function setText(node, value) {
  if (node) {
    node.textContent = value;
  }
}

function renderStaticFallback() {
  setText(portalWelcome, "Tu centro de acceso a tableros y gestiones");
  setText(sessionBadge, "Sin sesion activa");
  setText(sessionSummary, "Ingresa desde Usuarios y Accesos para ver tu contexto real.");
  setText(sessionStatus, "Pendiente de autenticar");
  setText(launchStatus, "Usuarios y Accesos sera el primer subportal autorizado.");
}

function renderDynamicContext(context) {
  const usuario = context?.usuario || {};
  const roles = Array.isArray(context?.roles) ? context.roles : [];
  const grupos = Array.isArray(context?.grupos) ? context.grupos : [];
  const resumen = context?.resumen || {};
  const permisos = context?.permisos || { headers: [], rows: [] };
  const notificaciones = Array.isArray(context?.notificaciones) ? context.notificaciones : [];
  const accionesRapidas = Array.isArray(context?.acciones_rapidas) ? context.acciones_rapidas : [];
  const menuArbol = Array.isArray(context?.menu_arbol) ? context.menu_arbol : [];
  const estado = context?.estado || {};

  setText(portalWelcome, `Bienvenido, ${usuario.nombre || "usuario"}`);
  setText(sessionBadge, `${usuario.cargo || "Usuario"} activo`);
  setText(sessionSummary, `${usuario.correo || ""} · ${usuario.estado || ""}`);
  setText(sessionStatus, `${roles.length} rol(es) · ${grupos.length} grupo(s)`);
  setText(launchStatus, `Portal principal: ${context?.portal_principal || "Portal Corporativo"}`);

  if (modulesGrid) {
    const moduleCards = [
      {
        title: "Usuarios y Accesos",
        description: "Subportal madre para administrar usuarios, roles, grupos y menues.",
        tone: "primary",
        target: "accesos-menues",
      },
      {
        title: "Produccion",
        description: "Programacion y control de planta.",
      },
      {
        title: "Inventario",
        description: "Existencias, lotes y movimientos.",
      },
      {
        title: "Finanzas",
        description: "Contabilidad, cierres y reportes.",
      },
      {
        title: "Compras",
        description: "Solicitudes, ordenes y proveedores.",
      },
      {
        title: "Reportes",
        description: "Dashboards ejecutivos y analitica.",
      },
    ];
    modulesGrid.innerHTML = moduleCards
      .map((module) => `
        <button class="preview-module ${module.tone || ""}" ${module.target ? `data-target="${escapeHtml(module.target)}"` : ""}>
          <strong>${escapeHtml(module.title)}</strong>
          <span>${escapeHtml(module.description)}</span>
        </button>
      `)
      .join("");
  }

  if (accessGrid) {
    const accessCards = [
      ["Dashboard Gerencial", "Acceso total", "Visible"],
      ["Usuarios y Accesos", "Gestion administrativa", "Subportal"],
      ["Programacion Produccion", "Gestion operativa", "Pendiente"],
      ["Reportes Ejecutivos", "Solo lectura", "Visible"],
    ];
    accessGrid.innerHTML = accessCards
      .map(([title, description, badge]) => `
        <div class="portal-access-item">
          <div>
            <strong>${escapeHtml(title)}</strong>
            <span>${escapeHtml(description)}</span>
          </div>
          <span class="portal-badge-success">${escapeHtml(badge)}</span>
        </div>
      `)
      .join("");
  }

  if (notificationsList) {
    notificationsList.innerHTML = notificaciones.length
      ? notificaciones
          .map(
            (note) => `
              <div class="portal-notification portal-notification-${escapeHtml(note.nivel || "info")}">
                <strong>${escapeHtml(note.titulo)}</strong>
                <span>${escapeHtml(note.detalle)}</span>
              </div>
            `
          )
          .join("")
      : `<div class="portal-notification"><strong>Sin novedades</strong><span>No hay notificaciones en este momento.</span></div>`;
  }

  if (quickActions) {
    quickActions.innerHTML = accionesRapidas.length
      ? accionesRapidas
          .map(
            (item) => `
              <button class="portal-action" type="button">
                <strong>${escapeHtml(item.titulo)}</strong>
                <span>${escapeHtml(item.descripcion)}</span>
              </button>
            `
          )
          .join("")
      : "";
  }

  if (statusStack) {
    const statusRows = [
      ["Portal Corporativo", estado?.portal ? "En linea" : "Pendiente"],
      ["accesos-menues", "Disponible"],
      ["Base de datos", "SQLite local"],
      ["Sincronizacion", "Local + Ubuntu + GitHub"],
    ];
    statusStack.innerHTML = statusRows
      .map(([left, right]) => `<div><strong>${escapeHtml(left)}</strong><span>${escapeHtml(right)}</span></div>`)
      .join("");
  }

  if (tree) {
    tree.innerHTML = [
      `<div class="tree-node root">plataformacorporativa</div>`,
      `<div class="tree-node">docs</div>`,
      `<div class="tree-node indent">SKILLS_INDEX.md</div>`,
      `<div class="tree-node indent">SKILLPortalCorporativo.md</div>`,
      `<div class="tree-node indent">SKILL_accesos-menues.md</div>`,
      `<div class="tree-node">apps</div>`,
      `<div class="tree-node indent">portal-corporativo</div>`,
      `<div class="tree-node indent">accesos-menues</div>`,
    ].join("");
  }

  if (userRoles) {
    userRoles.innerHTML = roles.length ? roles.map((role) => `<span class="portal-tag">${escapeHtml(role.nombre || role)}</span>`).join("") : `<span class="portal-tag">Sin roles</span>`;
  }

  if (userGroups) {
    userGroups.innerHTML = grupos.length ? grupos.map((group) => `<span class="portal-tag">${escapeHtml(group.nombre || group)}</span>`).join("") : `<span class="portal-tag">Sin grupos</span>`;
  }

  if (window.location.hash === "#contexto" && sessionSummary) {
    sessionSummary.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

async function fetchJson(url, headers = {}) {
  const response = await fetch(url, { headers });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

async function loadContext() {
  const token = localStorage.getItem("plataforma_session_token") || "";
  if (!token) {
    renderStaticFallback();
    return;
  }
  try {
    const context = await fetchJson("/api/portal/contexto", {
      "X-Session-Token": token,
    });
    renderDynamicContext(context);
  } catch (error) {
    console.error(error);
    renderStaticFallback();
  }
}

renderClock();
setInterval(renderClock, 1000);
renderStaticFallback();
loadContext();

if (launch) {
  launch.addEventListener("click", () => {
    const target = new URL("../accesos-menues/frontend/index.html", window.location.href);
    window.location.assign(target.toString());
  });
}
