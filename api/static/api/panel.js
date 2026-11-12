const API = "/api/";
const $ = (s) => document.querySelector(s);
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`);
const csrf = () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || "";

let tab = "clientes", inactivos = false, datos = [], editando = null;

// Tabla Clientes y Vehículos
const TABLAS = {
  clientes: {
    url: "clientes/", id: "id_cliente", nombre: "cliente",
    cols: ["Cliente", "Teléfono", "Correo", "Vehículos"],
    fila: (c) => [`${c.apellido}, ${c.nombre}`, c.telefono, c.email, (c.vehiculos || []).map((v) => v.patente).join(", ")],
    campos: [["nombre", "Nombre", "text"], ["apellido", "Apellido", "text"], ["telefono", "Teléfono", "tel"], ["email", "Correo electrónico", "email"]],
  },
  vehiculos: {
    url: "vehiculos/", id: "id_vehiculo", nombre: "vehículo",
    cols: ["Patente", "Marca", "Modelo", "Dueño"],
    fila: (v) => [v.patente, v.marca, v.modelo, v.cliente_nombre],
    campos: [["cliente", "Cliente (dueño)", "select"], ["patente", "Patente", "text"], ["marca", "Marca", "text"], ["modelo", "Modelo", "text"]],
  },
};

//función para hablar con la API get, post, patch, delete
async function api(ruta, metodo = "GET", body) {
  const res = await fetch(API + ruta, {
    method: metodo,
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
    body: body && JSON.stringify(body),
  });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

const errorTexto = (e) =>
  Object.entries(e).map(([campo, msg]) => `${campo}: ${msg}`).join("\n") || "No se pudo conectar con el servidor.";

// busqueda de lista
async function cargar() {
  const p = new URLSearchParams({ search: $("#buscar").value });
  if (inactivos) p.set("activo", "false");
  try {
    const d = await api(`${TABLAS[tab].url}?${p}`);
    datos = d.results || d;
    render();
  } catch (e) { alert(errorTexto(e)); }
}

function render() {
  const t = TABLAS[tab];
  $("#thead").innerHTML = "<tr>" + [...t.cols, ""].map((c) => `<th>${c}</th>`).join("") + "</tr>";
  $("#tbody").innerHTML = datos.map((r) => {
    const id = r[t.id];
    const botones = inactivos
      ? `<button class="btn chico" data-accion="reactivar" data-id="${id}">Reactivar</button>`
      : `<button class="btn chico" data-accion="editar" data-id="${id}">Editar</button>
         <button class="btn chico peligro" data-accion="baja" data-id="${id}">Dar de baja</button>`;
    return "<tr>" + t.fila(r).map((x) => `<td>${esc(x)}</td>`).join("") + `<td class="acciones">${botones}</td></tr>`;
  }).join("");
  $("#vacio").hidden = datos.length > 0;
}

// FORMULARIO sirve para crear y para editar
async function abrir(registro = null) {
  const t = TABLAS[tab];
  editando = registro;
  $("#modal-titulo").textContent = (registro ? "Editar " : "Nuevo ") + t.nombre;
  $("#errores").hidden = true;

  let opciones = "";
  if (tab === "vehiculos") {
    const cl = await api("clientes/");
    opciones = (cl.results || cl).map((c) =>
      `<option value="${c.id_cliente}" ${c.id_cliente === registro?.cliente ? "selected" : ""}>${esc(c.apellido)}, ${esc(c.nombre)}</option>`
    ).join("");
  }

  $("#campos").innerHTML = t.campos.map(([n, etiqueta, tipo]) =>
    `<div class="campo"><label>${etiqueta}</label>` +
    (tipo === "select"
      ? `<select name="${n}" required><option value="">Elegí un cliente</option>${opciones}</select>`
      : `<input type="${tipo}" name="${n}" value="${esc(registro?.[n])}">`) +
    "</div>"
  ).join("");
  $("#modal").showModal();
}

// CREAR / EDITAR
$("#form").onsubmit = async (e) => {
  e.preventDefault();
  const t = TABLAS[tab];
  const body = Object.fromEntries(new FormData(e.target));
  try {
    await api(editando ? `${t.url}${editando[t.id]}/` : t.url, editando ? "PATCH" : "POST", body);
    $("#modal").close();
    cargar();
  } catch (err) {
    $("#errores").textContent = errorTexto(err);
    $("#errores").hidden = false;
  }
};

// EDITAR / DAR DE BAJA / REACTIVAR
$("#tbody").onclick = async (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  const t = TABLAS[tab], id = b.dataset.id;
  try {
    if (b.dataset.accion === "editar") return abrir(datos.find((r) => r[t.id] == id));
    if (b.dataset.accion === "baja") {
      if (!confirm("¿Dar de baja? Podrás reactivarlo después.")) return;
      await api(`${t.url}${id}/`, "DELETE");
    }
    if (b.dataset.accion === "reactivar") await api(`${t.url}${id}/?activo=false`, "PATCH", { activo: true });
    cargar();
  } catch (err) { alert(errorTexto(err)); }
};

// Pestañas, buscador y demás controles
document.querySelectorAll(".tab").forEach((b) => (b.onclick = () => {
  $(".tab.activa").classList.remove("activa");
  b.classList.add("activa");
  tab = b.dataset.tab;
  $("#buscar").value = "";
  cargar();
}));
$("#buscar").oninput = cargar;
$("#inactivos").onchange = (e) => { inactivos = e.target.checked; $("#btn-nuevo").hidden = inactivos; cargar(); };
$("#btn-nuevo").onclick = () => abrir();
$("#cancelar").onclick = () => $("#modal").close();

cargar();