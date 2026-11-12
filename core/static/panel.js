(function() {
  const tokenCsrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  
  const configuracionModulos = {
    proveedores: {
      url: "/api/proveedores/",
      id: "id_proveedor",
      nombre: "proveedor",
      campos: [
        { clave: "nombre", etiqueta: "Nombre", tipo: "text" },
        { clave: "telefono", etiqueta: "Teléfono", tipo: "text" },
        { clave: "email", etiqueta: "Email", tipo: "email" }
      ]
    },
    insumos: {
      url: "/api/insumos/",
      id: "id_insumo",
      nombre: "insumo",
      campos: [
        { clave: "nombre", etiqueta: "Nombre", tipo: "text" },
        { clave: "unidad_medida", etiqueta: "Unidad de medida", tipo: "text" },
        { clave: "stock_actual", etiqueta: "Stock actual", tipo: "number" },
        { clave: "stock_minimo", etiqueta: "Stock mínimo", tipo: "number" },
        { clave: "costo_unitario", etiqueta: "Costo unitario", tipo: "number" },
        { clave: "activo", etiqueta: "Activo", tipo: "checkbox" }
      ]
    }
  };

  let moduloActual = "proveedores";
  let itemEditando = null;
  let temporizadorBusqueda;

  const obtenerElemento = id => document.getElementById(id);

  function mostrarNotificacion(mensaje) {
    const toast = obtenerElemento("notificacion-toast");
    toast.textContent = mensaje;
    toast.style.display = "block";
    setTimeout(() => { toast.style.display = "none"; }, 2500);
  }

  async function realizarPeticionApi(metodo, url, datosCuerpo) {
    const opciones = {
      method: metodo,
      credentials: "same-origin",
      headers: { "Accept": "application/json", "X-CSRFToken": tokenCsrf }
    };
    if (datosCuerpo) {
      opciones.headers["Content-Type"] = "application/json";
      opciones.body = JSON.stringify(datosCuerpo);
    }
    const respuesta = await fetch(url, opciones);
    let datosJson = null;
    try { datosJson = await respuesta.json(); } catch (e) {}
    return { ok: respuesta.ok, status: respuesta.status, data: datosJson };
  }

  async function cargarDatos() {
    const cfg = configuracionModulos[moduloActual];
    const parametros = new URLSearchParams();
    
    if (obtenerElemento("buscador").value.trim()) {
      parametros.set("search", obtenerElemento("buscador").value.trim());
    }
    if (moduloActual === "insumos" && obtenerElemento("check-inactivos").checked) {
      parametros.set("activo", "false");
    }

    const resultado = await realzarPeticionConFiltro(cfg.url, parametros);
    
    if (!resultado.ok) {
      obtenerElemento("grilla-elementos").innerHTML = `<div class="vacio">${resultado.status === 403 ? "Sin permisos. Iniciá sesión en /admin." : "Error al cargar (" + resultado.status + ")"}</div>`;
      return;
    }

    const listaItems = Array.isArray(resultado.data) ? resultado.data : (resultado.data.results || []);
    if (!listaItems.length) {
      obtenerElemento("grilla-elementos").innerHTML = `<div class="vacio">No hay datos para mostrar.</div>`;
      return;
    }

    obtenerElemento("grilla-elementos").innerHTML = listaItems.map(item => {
      let infoExtra = "";
      
      if (moduloActual === "proveedores") {
        infoExtra = `<div class="fila-dato"><span>Teléfono</span><b>${item.telefono}</b></div>
                     <div class="fila-dato"><span>Email</span><b>${item.email}</b></div>`;
      } else {
        const actualStock = parseFloat(item.stock_actual);
        const minimoStock = parseFloat(item.stock_minimo);
        const porcentaje = minimoStock > 0 ? Math.min(100, (actualStock / (minimoStock * 3)) * 100) : 100;
        
        let badgeEstado = !item.activo 
          ? `<span class="badge badge-dado-baja">DADO DE BAJA</span>` 
          : (actualStock <= minimoStock 
              ? `<span class="badge badge-stock-bajo">STOCK BAJO</span>` 
              : `<span class="badge badge-stock-ok">STOCK OK</span>`);
        
        infoExtra = `<div class="fila-dato"><span>Unidad</span><b>${item.unidad_medida}</b></div>
                     <div class="fila-dato"><span>Stock</span><b>${item.stock_actual} / mín. ${item.stock_minimo}</b></div>
                     <div class="barra-stock-track"><div class="barra-stock-fill" style="width:${porcentaje}%"></div></div>
                     <div class="fila-dato"><span>Costo</span><b>$ ${item.costo_unitario}</b></div>
                     <div>${badgeEstado}</div>`;
      }

      const botonDarBaja = (item.activo !== false || moduloActual === "proveedores")
        ? `<button class="btn btn-rojo" onclick="window.eliminarItem(${item[cfg.id]}, '${item.nombre}')">${moduloActual === "insumos" ? "Dar de baja" : "Eliminar"}</button>`
        : "";

      return `<div class="tarjeta">
                <span class="id-etiqueta">#${item[cfg.id]}</span>
                <h3>${item.nombre}</h3>
                ${infoExtra}
                <div class="acciones-tarjeta">
                  <button class="btn" onclick='window.abrirModal(${JSON.stringify(item)})'>Editar</button>
                  ${botonDarBaja}
                </div>
              </div>`;
    }).join("");
  }

  async function realzarPeticionConFiltro(urlBase, params) {
    const query = params.toString();
    return await realzarPeticionDirecta(urlBase + (query ? "?" + query : ""));
  }

  async function realzarPeticionDirecta(urlCompleta) {
    return await realizarPeticionApi("GET", urlCompleta);
  }

  window.abrirModal = function(item) {
    const cfg = configuracionModulos[moduloActual];
    itemEditando = item;
    obtenerElemento("mensaje-error").textContent = "";
    obtenerElemento("titulo-modal").textContent = (item ? "Editar " : "Nuevo ") + cfg.nombre;

    obtenerElemento("contenedor-campos").innerHTML = cfg.campos.map(campo => {
      const valorActual = item ? item[campo.clave] : (campo.tipo === "checkbox" ? true : "");
      const inputHtml = campo.tipo === "checkbox"
        ? `<input type="checkbox" name="${campo.clave}" ${valorActual ? "checked" : ""}>`
        : `<input type="${campo.tipo}" name="${campo.clave}" value="${valorActual}" ${campo.tipo === "number" ? 'step="0.01"' : ""}>`;
      return `<div class="campo"><label>${campo.etiqueta}</label>${inputHtml}</div>`;
    }).join("");

    obtenerElemento("modal-formulario").showModal();
  };

  window.eliminarItem = async function(id, nombre) {
    if (!confirm(`¿Confirmás la baja de «${nombre}»?`)) return;
    const cfg = configuracionModulos[moduloActual];
    const resultado = await realizarPeticionApi("DELETE", cfg.url + id + "/");
    if (!resultado.ok) {
      mostrarNotificacion("Error al eliminar");
      return;
    }
    mostrarNotificacion("Operación exitosa");
    cargarDatos();
  };

  obtenerElemento("formulario-principal").onsubmit = async function(evento) {
    evento.preventDefault();
    const cfg = configuracionModulos[moduloActual];
    const datosCuerpo = {};
    
    cfg.campos.forEach(campo => {
      const input = obtenerElemento("contenedor-campos").querySelector(`[name=${campo.clave}]`);
      datosCuerpo[campo.clave] = campo.tipo === "checkbox" ? input.checked : input.value;
    });

    const resultado = itemEditando
      ? await realizarPeticionApi("PUT", cfg.url + itemEditando[cfg.id] + "/", datosCuerpo)
      : await realizarPeticionApi("POST", cfg.url, datosCuerpo);

    if (!resultado.ok) {
      obtenerElemento("mensaje-error").textContent = "Error al guardar los datos.";
      return;
    }

    obtenerElemento("modal-formulario").close();
    mostrarNotificacion(itemEditando ? "Modificado con éxito" : "Creado con éxito");
    cargarDatos();
  };

  document.querySelectorAll(".pestana").forEach(boton => {
    boton.onclick = function() {
      document.querySelectorAll(".pestana").forEach(x => x.classList.remove("activa"));
      boton.classList.add("activa");
      moduloActual = boton.dataset.tipo;
      obtenerElemento("buscador").value = "";
      obtenerElemento("check-inactivos").checked = false;
      obtenerElemento("contenedor-filtro-baja").hidden = moduloActual !== "insumos";
      cargarDatos();
    };
  });

  obtenerElemento("btn-nuevo").onclick = () => window.abrirModal(null);
  obtenerElemento("btn-cancelar").onclick = () => obtenerElemento("modal-formulario").close();
  obtenerElemento("check-inactivos").onchange = cargarDatos;

  obtenerElemento("buscador").oninput = function() {
    clearTimeout(temporizadorBusqueda);
    temporizadorBusqueda = setTimeout(cargarDatos, 300);
  };

  cargarDatos();
})();