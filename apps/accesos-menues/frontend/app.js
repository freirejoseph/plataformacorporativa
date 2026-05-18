const state = {
  baseKpis: [
    { cls: 'KPIUsuariosTotales', tone: 'azul', icon: 'U', title: 'Usuarios Totales', key: 'usuarios_totales', detail: 'Activos: 142 | Inactivos: 14', trend: 'Base SQLite' },
    { cls: 'KPIRolesCreados', tone: 'verde', icon: 'R', title: 'Roles Creados', key: 'roles_creados', detail: 'Activos: 16 | Inactivos: 2', trend: 'RBAC activo' },
    { cls: 'KPIModulosDisponibles', tone: 'morado', icon: 'M', title: 'Modulos Disponibles', key: 'modulos', detail: 'SYSPRO: 18 | Odoo: 6', trend: 'Portales' },
    { cls: 'KPISesionesActivas', tone: 'naranja', icon: 'S', title: 'Sesiones Activas', key: 'sesiones_activas', detail: 'Ultima actualizacion: Ahora', trend: 'Tiempo real' },
    { cls: 'KPIPortalesConectados', tone: 'cyan', icon: 'P', title: 'Portales Conectados', key: 'portales', detail: 'Disponibles: 5 | Mantenimiento: 0', trend: '100% Operativos' },
    { cls: 'KPIFechaHoraSistema', tone: 'azul', icon: 'H', title: 'Fecha y Hora', key: 'clock', detail: '20/05/2024', trend: 'Lunes' }
  ],
  users: [],
  roles: [],
  groups: [],
  menus: [],
  permissions: [],
  activity: [],
  clock: { time: '', date: '', day: '' },
  sessionToken: localStorage.getItem('plataforma_session_token') || '',
  quickActions: [
    ['Crear usuario', 'Persona +', 'Alta de usuario'],
    ['Crear rol', 'Shield +', 'Definir perfil'],
    ['Asignar permisos', 'Matrix', 'Configurar accesos'],
    ['Asignar accesos a portal', 'Portal', 'Vincular modulo'],
    ['Importar usuarios', 'Upload', 'Carga masiva'],
    ['Grupos', 'Team', 'Gestion de grupos'],
    ['Politicas de acceso', 'Lock', 'Reglas de seguridad'],
    ['Auditoria', 'Log', 'Trazabilidad'],
    ['Respaldos', 'Backup', 'Copias de seguridad'],
    ['Configuracion', 'Gear', 'Parametros del sistema']
  ]
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[char]);
}

function initialsFromName(name) {
  const parts = String(name ?? '').trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) {
    return 'U';
  }
  return parts.map((part) => part[0] || '').join('').slice(0, 2).toUpperCase();
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value ?? '').trim());
}

function isValidCode(value) {
  return /^[A-Z0-9_]{2,64}$/.test(String(value ?? '').trim());
}

function showMessage(message, tone = 'info') {
  let box = document.getElementById('formMessage');
  if (!box) {
    box = document.createElement('div');
    box.id = 'formMessage';
    box.className = 'FormMessage';
    box.setAttribute('role', 'status');
    box.setAttribute('aria-live', 'polite');
    box.setAttribute('aria-atomic', 'true');
    document.body.appendChild(box);
  }
  box.className = `FormMessage ${tone}`;
  box.textContent = message;
  box.hidden = false;
  window.clearTimeout(showMessage._timer);
  showMessage._timer = window.setTimeout(() => {
    box.hidden = true;
  }, 3200);
}

function clearValidationState(form) {
  form.querySelectorAll('.is-invalid').forEach((field) => {
    field.classList.remove('is-invalid');
    field.removeAttribute('aria-invalid');
    field.setCustomValidity?.('');
  });
}

function markInvalid(field, message) {
  if (!field) {
    return;
  }
  field.classList.add('is-invalid');
  field.setAttribute('aria-invalid', 'true');
  if (message) {
    field.setCustomValidity?.(message);
    field.reportValidity?.();
  }
}

function firstField(form, selector) {
  return form.querySelector(selector);
}

function watchValidationFields(form) {
  form.querySelectorAll('input, select, textarea').forEach((field) => {
    field.addEventListener('input', () => {
      field.classList.remove('is-invalid');
      field.removeAttribute('aria-invalid');
      field.setCustomValidity?.('');
    });
    field.addEventListener('change', () => {
      field.classList.remove('is-invalid');
      field.removeAttribute('aria-invalid');
      field.setCustomValidity?.('');
    });
  });
}

function openDialog(id) {
  const dialog = document.getElementById(id);
  if (dialog && typeof dialog.showModal === 'function') {
    dialog.showModal();
  }
}

function closeDialogs() {
  document.querySelectorAll('dialog.PortalDialog[open]').forEach((dialog) => dialog.close());
}

async function fetchJson(url, options = {}) {
  const requestOptions = { ...options };
  const headers = new Headers(requestOptions.headers || {});
  if (state.sessionToken) {
    headers.set('X-Session-Token', state.sessionToken);
  }
  requestOptions.headers = headers;
  const response = await fetch(url, requestOptions);
  if (!response.ok) {
    let detail = `Request failed: ${response.status}`;
    try {
      const payload = await response.json();
      if (payload?.detail) {
        detail = String(payload.detail);
      }
    } catch (error) {
      void error;
    }
    throw new Error(detail);
  }
  return response.json();
}

async function ensureSession() {
  if (state.sessionToken) {
    return state.sessionToken;
  }
  openDialog('loginDialog');
  throw new Error('Inicia sesion para continuar.');
}

function renderClock() {
  const now = new Date();
  const time = now.toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit', hour12: true }).toUpperCase();
  const date = now.toLocaleDateString('es-EC', { day: '2-digit', month: '2-digit', year: 'numeric' });
  const day = now.toLocaleDateString('es-EC', { weekday: 'long' });
  state.clock = {
    time,
    date,
    day: day.charAt(0).toUpperCase() + day.slice(1)
  };
  const timeNode = document.getElementById('clockValue');
  const dateNode = document.getElementById('clockDate');
  const dayNode = document.getElementById('clockDay');
  if (timeNode) timeNode.textContent = state.clock.time;
  if (dateNode) dateNode.textContent = state.clock.date;
  if (dayNode) dayNode.textContent = state.clock.day;
}

function renderKpis(data) {
  const target = document.getElementById('kpiGrid');
  const values = {
    usuarios_totales: data.usuarios_totales,
    roles_creados: data.roles_creados,
    modulos: data.modulos,
    sesiones_activas: data.sesiones_activas,
    portales: data.portales,
    clock: state.clock
  };

  target.innerHTML = state.baseKpis.map((kpi) => `
    <article class="${kpi.cls}">
      ${
        kpi.key === 'clock'
          ? `
            <div class="KPIClock">
              <div class="ClockTitle">${escapeHtml(kpi.title)}</div>
              <div class="ClockTime" id="clockValue">${escapeHtml(values.clock.time || '09:45 AM')}</div>
              <div class="ClockDate" id="clockDate">${escapeHtml(values.clock.date || kpi.detail)}</div>
              <div class="ClockDay" id="clockDay">${escapeHtml(values.clock.day || kpi.trend)}</div>
            </div>
          `
          : `
            <div class="KPIHeader">
              <div class="KPIIcono ${kpi.tone}">${kpi.icon}</div>
            </div>
            <div class="KPITitulo">${escapeHtml(kpi.title)}</div>
            <div class="KPIValor">${escapeHtml(values[kpi.key] ?? '0')}</div>
            <div class="KPIDetalle">${escapeHtml(kpi.detail)}</div>
            <div class="KPITrend">${escapeHtml(kpi.trend)}</div>
            <div class="Sparkline"></div>
          `
      }
    </article>
  `).join('');
}

function renderUsers(list) {
  const target = document.getElementById('usersTable');
  target.innerHTML = list.map((user) => `
    <tr>
      <td>
        <div class="UserIdentityCell">
          <div class="UserAvatarMini">${initialsFromName(user.nombre)}</div>
          <div>
            <div class="UserName">${escapeHtml(user.nombre)}</div>
            <div class="UserSlug">${escapeHtml(String(user.nombre || '').trim().toLowerCase().replace(/\s+/g, '.'))}</div>
          </div>
        </div>
      </td>
      <td>${escapeHtml(user.correo)}</td>
      <td><span class="TagRol">${escapeHtml(user.rol)}</span></td>
      <td><span class="TagPortal">${escapeHtml(user.portal)}</span></td>
      <td>${user.estado === 'ACTIVO' ? '<span class="TagEstadoActivo">Activo</span>' : '<span class="TagEstadoInactivo">Inactivo</span>'}</td>
      <td>${escapeHtml(user.ultimo_acceso || '-')}</td>
      <td>...</td>
    </tr>
  `).join('');
}

function renderRoles(list) {
  const target = document.getElementById('rolesList');
  if (!target) return;
  target.innerHTML = list.map((role) => `
    <div class="ItemRolSistema">
      <div class="IconoRolSistema">${initialsFromName(role.nombre)}</div>
      <div>
        <div class="NombreRolSistema">${escapeHtml(role.nombre)}</div>
        <div class="DescripcionRolSistema">${escapeHtml(role.descripcion || '')}</div>
      </div>
      <div class="ContadorUsuariosRol">${escapeHtml(role.usuarios)}</div>
    </div>
  `).join('');
}

function renderGroups(list) {
  const target = document.getElementById('groupsList');
  if (!target) return;
  target.innerHTML = list.map((group) => `
    <div class="ItemRolSistema">
      <div class="IconoRolSistema">${initialsFromName(group.nombre)}</div>
      <div>
        <div class="NombreRolSistema">${escapeHtml(group.nombre)}</div>
        <div class="DescripcionRolSistema">${escapeHtml(group.descripcion || '')}</div>
      </div>
      <div class="ContadorUsuariosRol">${escapeHtml(group.usuarios)}</div>
    </div>
  `).join('');
}

function renderMenus(list) {
  const target = document.getElementById('menusTable');
  if (!target) return;
  target.innerHTML = list.map((menu) => `
    <tr>
      <td>${escapeHtml(menu.codigo)}</td>
      <td>${escapeHtml(menu.nombre)}</td>
      <td>${escapeHtml(menu.portal || '-')}</td>
      <td>${escapeHtml(menu.modulo || '-')}</td>
      <td>${escapeHtml(menu.orden)}</td>
      <td>${menu.estado === 'ACTIVO' ? '<span class="TagEstadoActivo">Activo</span>' : '<span class="TagEstadoInactivo">Inactivo</span>'}</td>
    </tr>
  `).join('');
}

function renderPermissions() {
  const headers = document.getElementById('permissionHeaders');
  const body = document.getElementById('permissionMatrix');
  if (!headers || !body) return;

  const portalHeaders = ['Módulo / Portal', 'SYSPRO ERP', 'Odoo RRHH', 'Portal Reportes', 'Portal Compras', 'Portal Calidad'];
  headers.innerHTML = portalHeaders.map((col) => `<th>${escapeHtml(col)}</th>`).join('');

  const rows = [
    { module: 'Producción', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO'] },
    { module: 'Inventario', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'SOLO_LECTURA', 'DENEGADO'] },
    { module: 'Finanzas', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'SOLO_LECTURA', 'DENEGADO'] },
    { module: 'CxC (Cuentas por Cobrar)', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'DENEGADO'] },
    { module: 'CxP (Cuentas por Pagar)', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'DENEGADO'] },
    { module: 'Compras', cells: ['PERMITIDO', 'PERMITIDO', 'SOLO_LECTURA', 'PERMITIDO', 'DENEGADO'] },
    { module: 'Costos', cells: ['PERMITIDO', 'PERMITIDO', 'DENEGADO', 'SOLO_LECTURA', 'DENEGADO'] },
    { module: 'Planeación', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO'] },
    { module: 'Empleados', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'SOLO_LECTURA', 'DENEGADO'] },
    { module: 'Nómina', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'DENEGADO'] },
    { module: 'Asistencia', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO'] },
    { module: 'Solicitudes', cells: ['PERMITIDO', 'PERMITIDO', 'SOLO_LECTURA', 'PERMITIDO', 'PERMITIDO'] },
    { module: 'Documentos', cells: ['PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'PERMITIDO', 'DENEGADO'] }
  ];

  body.innerHTML = rows.map((item) => `
    <tr>
      <td>${escapeHtml(item.module)}</td>
      ${item.cells.map((permiso) => `
        <td class="PermissionCell">
          <span class="PermissionBadge ${
            permiso === 'PERMITIDO'
              ? 'permitido'
              : permiso === 'SOLO_LECTURA'
                ? 'lectura'
                : 'denegado'
          }">
            ${permiso === 'PERMITIDO' ? '◉' : permiso === 'SOLO_LECTURA' ? '◐' : '⊘'}
          </span>
        </td>
      `).join('')}
    </tr>
  `).join('');
}

function renderActivity(list) {
  const target = document.getElementById('activityTable');
  target.innerHTML = list.map((item) => `
    <tr>
      <td>${escapeHtml(item.fecha_hora)}</td>
      <td>${escapeHtml(item.usuario || 'Sistema')}</td>
      <td>${escapeHtml(item.accion)}</td>
      <td>${escapeHtml(item.detalle || '-')}</td>
      <td>${escapeHtml(item.ip || '-')}</td>
    </tr>
  `).join('');
}

function renderActions() {
  const target = document.getElementById('quickActions');
  target.innerHTML = state.quickActions.map(([title, icon, subtitle]) => `
    <button class="ActionTile" type="button" aria-label="${escapeHtml(title)}">
      <div class="ActionTileIcon">${escapeHtml(icon)}</div>
      <div class="ActionTileTitle">${escapeHtml(title)}</div>
      <div class="ActionTileSubtitle">${escapeHtml(subtitle)}</div>
    </button>
  `).join('');
  target.querySelectorAll('.ActionTile').forEach((tile) => {
    tile.addEventListener('click', () => {
      const title = tile.querySelector('.ActionTileTitle')?.textContent || '';
      if (title === 'Crear usuario') openDialog('userDialog');
      else if (title === 'Crear rol') openDialog('roleDialog');
      else if (title === 'Grupos') openDialog('groupDialog');
      else if (title === 'Asignar permisos' || title === 'Asignar accesos a portal') openDialog('assignmentDialog');
      else showMessage(`${title}: accion pendiente de UI detallada`, 'success');
    });
  });
}

function applySearch() {
  const globalInput = document.getElementById('globalSearch');
  const panelInput = document.getElementById('userPanelSearch');
  const stateFilter = document.getElementById('userStateFilter');
  const apply = () => {
    const query = `${globalInput.value} ${panelInput.value}`.trim().toLowerCase();
    const stateValue = stateFilter.value;
    const filtered = state.users.filter((u) =>
      (stateValue === 'TODOS' || u.estado === stateValue) &&
      [u.nombre, u.correo, u.rol, u.portal, u.estado].some((value) => String(value || '').toLowerCase().includes(query))
    );
    renderUsers(filtered);
  };
  globalInput.oninput = apply;
  panelInput.oninput = apply;
  stateFilter.onchange = apply;
}

function fillSelect(select, items, valueKey, labelKey, placeholder) {
  const options = [];
  if (placeholder) {
    options.push(`<option value="">${escapeHtml(placeholder)}</option>`);
  }
  options.push(...items.map((item) => `<option value="${escapeHtml(item[valueKey])}">${escapeHtml(item[labelKey])}</option>`));
  select.innerHTML = options.join('');
}

function populateAssignmentControls() {
  const userSelect = document.getElementById('assignmentUserSelect');
  const roleSelect = document.getElementById('assignmentRoleSelect');
  const groupSelect = document.getElementById('assignmentGroupSelect');
  if (!userSelect || !roleSelect || !groupSelect) return;
  fillSelect(userSelect, state.users, 'id', 'nombre', 'Selecciona un usuario');
  fillSelect(roleSelect, state.roles, 'id', 'nombre', 'Selecciona un rol');
  fillSelect(groupSelect, state.groups, 'id', 'nombre', 'Selecciona un grupo');
}

async function submitJson(url, payload, method = 'POST') {
  await ensureSession();
  await fetchJson(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  showMessage('Operacion completada', 'success');
  await main();
}

function bindForms() {
  document.querySelectorAll('[data-close-dialog]').forEach((button) => {
    button.addEventListener('click', closeDialogs);
  });

  [
    document.getElementById('loginForm'),
    document.getElementById('userForm'),
    document.getElementById('roleForm'),
    document.getElementById('groupForm'),
    document.getElementById('assignmentForm')
  ].filter(Boolean).forEach(watchValidationFields);

  document.getElementById('securityBtn').onclick = () => openDialog('loginDialog');
  document.getElementById('openLoginBtn').onclick = async () => {
    try {
      if (state.sessionToken) {
        await fetchJson('/api/auth/logout', { method: 'POST' });
        state.sessionToken = '';
        localStorage.removeItem('plataforma_session_token');
        showMessage('Sesion cerrada', 'success');
      } else {
        openDialog('loginDialog');
      }
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };
  document.getElementById('createUserBtn').onclick = () => openDialog('userDialog');
  document.getElementById('createRoleBtn').onclick = () => openDialog('roleDialog');
  document.querySelectorAll('.MenuGruposSeguridad, .MenuPortalesModulos, .MenuAuditoria').forEach((item) => {
    item.addEventListener('click', () => openDialog('assignmentDialog'));
  });

  document.getElementById('loginForm').onsubmit = async (event) => {
    event.preventDefault();
    try {
      const form = event.currentTarget;
      clearValidationState(form);
      const formData = new FormData(form);
      const correo = String(formData.get('correo') || '').trim().toLowerCase();
      const password = String(formData.get('password') || '').trim();
      if (!isValidEmail(correo)) {
        markInvalid(firstField(form, '[name="correo"]'), 'Ingresa un correo valido.');
        showMessage('Ingresa un correo valido.', 'error');
        return;
      }
      if (password.length < 6) {
        markInvalid(firstField(form, '[name="password"]'), 'Ingresa una password valida.');
        showMessage('Ingresa una password valida.', 'error');
        return;
      }
      const login = await fetchJson('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, password })
      });
      state.sessionToken = login.token;
      localStorage.setItem('plataforma_session_token', login.token);
      showMessage(`Sesion iniciada como ${login.nombre}`, 'success');
      closeDialogs();
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('userForm').onsubmit = async (event) => {
    event.preventDefault();
    try {
      const form = event.currentTarget;
      clearValidationState(form);
      const formData = new FormData(form);
      const nombre = String(formData.get('nombre') || '').trim();
      const correo = String(formData.get('correo') || '').trim().toLowerCase();
      const cargo = String(formData.get('cargo') || '').trim();
      const estado = String(formData.get('estado') || 'ACTIVO').trim();
      if (nombre.length < 2) {
        markInvalid(firstField(form, '[name="nombre"]'), 'Ingresa un nombre valido de al menos 2 caracteres.');
        showMessage('Ingresa un nombre valido de al menos 2 caracteres.', 'error');
        return;
      }
      if (!isValidEmail(correo)) {
        markInvalid(firstField(form, '[name="correo"]'), 'Ingresa un correo valido.');
        showMessage('Ingresa un correo valido.', 'error');
        return;
      }
      await submitJson('/api/usuarios', { nombre, correo, cargo, estado });
      event.currentTarget.reset();
      closeDialogs();
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('roleForm').onsubmit = async (event) => {
    event.preventDefault();
    try {
      const form = event.currentTarget;
      clearValidationState(form);
      const formData = new FormData(form);
      const codigo = String(formData.get('codigo') || '').trim().toUpperCase();
      const nombre = String(formData.get('nombre') || '').trim();
      const descripcion = String(formData.get('descripcion') || '').trim();
      const estado = String(formData.get('estado') || 'ACTIVO').trim();
      if (!isValidCode(codigo)) {
        markInvalid(firstField(form, '[name="codigo"]'), 'El codigo debe usar mayusculas, numeros o guion bajo.');
        showMessage('El codigo debe usar mayusculas, numeros o guion bajo.', 'error');
        return;
      }
      if (nombre.length < 2) {
        markInvalid(firstField(form, '[name="nombre"]'), 'Ingresa un nombre de rol valido.');
        showMessage('Ingresa un nombre de rol valido.', 'error');
        return;
      }
      await submitJson('/api/roles', { codigo, nombre, descripcion, estado });
      event.currentTarget.reset();
      closeDialogs();
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('groupForm').onsubmit = async (event) => {
    event.preventDefault();
    try {
      const form = event.currentTarget;
      clearValidationState(form);
      const formData = new FormData(form);
      const codigo = String(formData.get('codigo') || '').trim().toUpperCase();
      const nombre = String(formData.get('nombre') || '').trim();
      const descripcion = String(formData.get('descripcion') || '').trim();
      const estado = String(formData.get('estado') || 'ACTIVO').trim();
      if (!isValidCode(codigo)) {
        markInvalid(firstField(form, '[name="codigo"]'), 'El codigo debe usar mayusculas, numeros o guion bajo.');
        showMessage('El codigo debe usar mayusculas, numeros o guion bajo.', 'error');
        return;
      }
      if (nombre.length < 2) {
        markInvalid(firstField(form, '[name="nombre"]'), 'Ingresa un nombre de grupo valido.');
        showMessage('Ingresa un nombre de grupo valido.', 'error');
        return;
      }
      await submitJson('/api/grupos', { codigo, nombre, descripcion, estado });
      event.currentTarget.reset();
      closeDialogs();
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('assignRoleBtn').onclick = async () => {
    try {
      const usuarioId = Number(document.getElementById('assignmentUserSelect').value);
      const rolId = Number(document.getElementById('assignmentRoleSelect').value);
      if (!usuarioId || !rolId) {
        alert('Selecciona un usuario y un rol.');
        return;
      }
      await submitJson(`/api/usuarios/${usuarioId}/roles`, { rol_id: rolId });
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('removeRoleBtn').onclick = async () => {
    try {
      const usuarioId = Number(document.getElementById('assignmentUserSelect').value);
      const rolId = Number(document.getElementById('assignmentRoleSelect').value);
      if (!usuarioId || !rolId) {
        alert('Selecciona un usuario y un rol.');
        return;
      }
      await ensureSession();
      await fetchJson(`/api/usuarios/${usuarioId}/roles/${rolId}`, { method: 'DELETE' });
      showMessage('Rol desasignado', 'success');
      await main();
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('assignGroupBtn').onclick = async () => {
    try {
      const usuarioId = Number(document.getElementById('assignmentUserSelect').value);
      const grupoId = Number(document.getElementById('assignmentGroupSelect').value);
      if (!usuarioId || !grupoId) {
        alert('Selecciona un usuario y un grupo.');
        return;
      }
      await submitJson(`/api/usuarios/${usuarioId}/grupos`, { grupo_id: grupoId });
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('removeGroupBtn').onclick = async () => {
    try {
      const usuarioId = Number(document.getElementById('assignmentUserSelect').value);
      const grupoId = Number(document.getElementById('assignmentGroupSelect').value);
      if (!usuarioId || !grupoId) {
        alert('Selecciona un usuario y un grupo.');
        return;
      }
      await ensureSession();
      await fetchJson(`/api/usuarios/${usuarioId}/grupos/${grupoId}`, { method: 'DELETE' });
      showMessage('Grupo desasignado', 'success');
      await main();
    } catch (error) {
      console.error(error);
      showMessage(error.message, 'error');
    }
  };

  document.getElementById('notificationsBtn').onclick = () => showMessage('No hay notificaciones nuevas', 'success');
}

async function main() {
  const [resumen, users, roles, groups, menus, permisos, activity] = await Promise.all([
    fetchJson('/api/dashboard/resumen'),
    fetchJson('/api/usuarios'),
    fetchJson('/api/roles'),
    fetchJson('/api/grupos'),
    fetchJson('/api/menus'),
    fetchJson('/api/permisos/matriz'),
    fetchJson('/api/logs/actividad')
  ]);

  state.users = users;
  state.roles = roles;
  state.groups = groups;
  state.menus = menus;
  state.permissions = permisos;
  state.activity = activity;

  renderClock();
  renderKpis(resumen);
  renderUsers(state.users);
  renderRoles(state.roles);
  renderGroups(state.groups);
  renderMenus(state.menus);
  renderPermissions(state.permissions);
  renderActivity(state.activity);
  renderActions();
  populateAssignmentControls();
  applySearch();

  window.clearInterval(state.clockInterval);
  state.clockInterval = window.setInterval(() => {
    renderClock();
  }, 1000);
}

bindForms();
main().catch((error) => {
  console.error(error);
  const output = document.createElement('pre');
  output.style.color = '#ffb5b5';
  output.style.padding = '16px';
  output.textContent = error.message;
  document.body.appendChild(output);
});
