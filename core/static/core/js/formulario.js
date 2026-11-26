// formulario.js
// Gestión y validación de reserva de turnos del lado del cliente

(function () {
    const URL_TURNOS = "/api/turnos";
    const URL_SERVICIOS = "/api/servicios";

    const EXPR_NOMBRE = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$/;
    const EXPR_VEHICULO = /^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]+)*$/;
    const EXPR_PATENTE = /^[A-Z0-9]{6,8}$/;
    const EXPR_TELEFONO = /^\+?[0-9]{6,15}$/;
    const EXPR_EMAIL = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

    let fechaMinimaISO = "";
    let fechaMaximaISO = "";
    let ultimaFechaConsultada = "";
    let formularioTocado = false;

    const $ = id => document.getElementById(id);

    async function llamarApi(url, metodo = "GET", datos = null) {
        if (typeof window.api === "function") {
            return window.api(url, metodo, datos);
        }
        const opciones = {
            method: metodo,
            headers: { "Content-Type": "application/json" }
        };
        if (datos !== null) {
            opciones.body = JSON.stringify(datos);
        }
        const respuesta = await fetch(url, opciones);
        if (!respuesta.ok) {
            const errJson = await respuesta.json().catch(() => ({}));
            const detalle = errJson.detail || errJson.error || Object.values(errJson).flat().join(" ") || `Error ${respuesta.status}`;
            throw new Error(detalle);
        }
        if (respuesta.status === 204) return null;
        return respuesta.json();
    }

    function notificar(mensaje) {
        if (typeof window.avisar === "function") {
            window.avisar(mensaje);
        }
    }

    function marcarError(campoId, errorId, mensaje) {
        const campo = $(campoId);
        const cajaError = $(errorId);
        if (campo) campo.classList.add("invalido");
        if (cajaError) cajaError.textContent = mensaje;
    }

    function limpiarError(campoId, errorId) {
        const campo = $(campoId);
        const cajaError = $(errorId);
        if (campo) campo.classList.remove("invalido");
        if (cajaError) cajaError.textContent = "";
    }

    function obtenerHoyLocalISO() {
        const ahora = new Date();
        const y = ahora.getFullYear();
        const m = String(ahora.getMonth() + 1).padStart(2, "0");
        const d = String(ahora.getDate()).padStart(2, "0");
        return `${y}-${m}-${d}`;
    }

    function isoAPartes(iso) {
        if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return null;
        const [anio, mes, dia] = iso.split("-");
        return { dia, mes, anio };
    }

    function validarYConvertirFecha(diaStr, mesStr, anioStr) {
        if (!diaStr || !mesStr || !anioStr) {
            return { error: "Completá día (DD), mes (MM) y año (AAAA)." };
        }
        if (!/^\d{1,2}$/.test(diaStr) || !/^\d{1,2}$/.test(mesStr) || !/^\d{4}$/.test(anioStr)) {
            return { error: "Usá 2 dígitos para día, 2 para mes y 4 para año." };
        }

        const dia = parseInt(diaStr, 10);
        const mes = parseInt(mesStr, 10);
        const anio = parseInt(anioStr, 10);

        if (mes < 1 || mes > 12) {
            return { error: "El mes debe estar entre 01 y 12." };
        }
        if (dia < 1 || dia > 31) {
            return { error: "El día debe estar entre 01 y 31." };
        }

        const fechaCheck = new Date(Date.UTC(anio, mes - 1, dia));
        if (
            fechaCheck.getUTCFullYear() !== anio ||
            fechaCheck.getUTCMonth() !== mes - 1 ||
            fechaCheck.getUTCDate() !== dia
        ) {
            return { error: `La fecha ${String(dia).padStart(2, "0")}/${String(mes).padStart(2, "0")}/${anio} no existe en el calendario.` };
        }

        const iso = `${anio}-${String(mes).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;
        const textoFecha = `${String(dia).padStart(2, "0")}/${String(mes).padStart(2, "0")}/${anio}`;

        if (fechaMinimaISO && iso < fechaMinimaISO) {
            const pMin = isoAPartes(fechaMinimaISO);
            return { error: `No podés elegir una fecha anterior a hoy (${pMin.dia}/${pMin.mes}/${pMin.anio}).` };
        }
        if (fechaMaximaISO && iso > fechaMaximaISO) {
            const pMax = isoAPartes(fechaMaximaISO);
            return { error: `Solo se toman turnos hasta el ${pMax.dia}/${pMax.mes}/${pMax.anio}.` };
        }

        return { iso, textoFecha };
    }

    function separarNombreYApellido(nombreCompleto) {
        const partes = nombreCompleto.trim().replace(/\s+/g, " ").split(" ");
        if (partes.length === 1) {
            return { nombre: partes[0], apellido: partes[0] };
        }
        return {
            nombre: partes[0],
            apellido: partes.slice(1).join(" ")
        };
    }

    function validarFormulario(mostrarMensajes = true) {
        const listaErrores = [];

        const nombre = $("nombre").value.trim().replace(/\s+/g, " ");
        const email = $("email").value.trim().toLowerCase();
        const telefono = $("telefono").value.trim();
        const patente = $("patente").value.trim().toUpperCase();
        const vehiculo = $("vehiculo").value.trim().replace(/\s+/g, " ");
        const servicioId = $("servicio").value;
        const hora = $("hora-turno").value;
        const acepto = $("acepto").checked;

        // 1. Nombre completo
        if (!nombre) {
            listaErrores.push("Nombre completo: es obligatorio.");
            if (mostrarMensajes) marcarError("nombre", "error-nombre", "Ingresá tu nombre y apellido.");
        } else if (nombre.length < 3 || !EXPR_NOMBRE.test(nombre)) {
            listaErrores.push("Nombre completo: solo letras y espacios simples (mínimo 3 caracteres).");
            if (mostrarMensajes) marcarError("nombre", "error-nombre", "Usá solo letras y espacios simples (mínimo 3 caracteres).");
        } else {
            limpiarError("nombre", "error-nombre");
        }

        // 2. Correo electrónico
        if (!email) {
            listaErrores.push("Correo electrónico: es obligatorio.");
            if (mostrarMensajes) marcarError("email", "error-email", "Ingresá tu correo electrónico.");
        } else if (email.startsWith("@") || email.startsWith(".") || !EXPR_EMAIL.test(email)) {
            listaErrores.push("Correo electrónico: formato inválido.");
            if (mostrarMensajes) marcarError("email", "error-email", "Ingresá un correo válido (ej: nombre@dominio.com).");
        } else {
            limpiarError("email", "error-email");
        }

        // 3. Teléfono / WhatsApp
        if (!telefono) {
            listaErrores.push("Teléfono / WhatsApp: es obligatorio.");
            if (mostrarMensajes) marcarError("telefono", "error-telefono", "Ingresá tu número de teléfono o WhatsApp.");
        } else if (!EXPR_TELEFONO.test(telefono)) {
            listaErrores.push("Teléfono / WhatsApp: debe tener entre 6 y 15 dígitos.");
            if (mostrarMensajes) marcarError("telefono", "error-telefono", "Ingresá entre 6 y 15 números sin espacios (opcional + al inicio).");
        } else {
            limpiarError("telefono", "error-telefono");
        }

        // 4. Patente
        if (!patente) {
            listaErrores.push("Patente: es obligatoria.");
            if (mostrarMensajes) marcarError("patente", "error-patente", "Ingresá la patente del vehículo.");
        } else if (!EXPR_PATENTE.test(patente)) {
            listaErrores.push("Patente: debe tener 6 a 8 letras/números sin espacios.");
            if (mostrarMensajes) marcarError("patente", "error-patente", "Ingresá entre 6 y 8 caracteres alfanuméricos sin espacios (ej: AB123CD).");
        } else {
            limpiarError("patente", "error-patente");
        }

        // 5. Vehículo / Marca
        if (!vehiculo) {
            listaErrores.push("Vehículo / Marca: es obligatorio.");
            if (mostrarMensajes) marcarError("vehiculo", "error-vehiculo", "Ingresá la marca o modelo del vehículo.");
        } else if (vehiculo.length < 2 || !EXPR_VEHICULO.test(vehiculo)) {
            listaErrores.push("Vehículo / Marca: mínimo 2 caracteres sin espacios dobles.");
            if (mostrarMensajes) marcarError("vehiculo", "error-vehiculo", "Ingresá al menos 2 caracteres válidos (ej: Fiat Cronos).");
        } else {
            limpiarError("vehiculo", "error-vehiculo");
        }

        // 6. Servicio
        if (!servicioId) {
            listaErrores.push("Servicio: elegí una opción del listado.");
            if (mostrarMensajes) marcarError("servicio", "error-servicio", "Seleccioná el servicio que querés realizar.");
        } else {
            limpiarError("servicio", "error-servicio");
        }

        // 7. Fecha DD / MM / AAAA
        const resFecha = validarYConvertirFecha(
            $("fecha-dia").value.trim(),
            $("fecha-mes").value.trim(),
            $("fecha-anio").value.trim()
        );
        if (resFecha.error) {
            listaErrores.push(`Fecha: ${resFecha.error}`);
            if (mostrarMensajes) {
                $("fecha-dia").classList.add("invalido");
                $("fecha-mes").classList.add("invalido");
                $("fecha-anio").classList.add("invalido");
                $("error-fecha").textContent = resFecha.error;
            }
        } else {
            $("fecha-dia").classList.remove("invalido");
            $("fecha-mes").classList.remove("invalido");
            $("fecha-anio").classList.remove("invalido");
            $("error-fecha").textContent = "";
        }

        // 8. Bloque horario
        const opcionHora = $("hora-turno").selectedOptions[0];
        if (!hora) {
            listaErrores.push("Horario: seleccioná un bloque disponible.");
            if (mostrarMensajes) marcarError("hora-turno", "error-hora", "Elegí un bloque horario disponible.");
        } else if (opcionHora && opcionHora.disabled) {
            listaErrores.push("Horario: el bloque elegido ya está ocupado.");
            if (mostrarMensajes) marcarError("hora-turno", "error-hora", "Ese horario ya está ocupado, elegí otro bloque.");
        } else {
            limpiarError("hora-turno", "error-hora");
        }

        // 9. Check de WhatsApp
        if (!acepto) {
            listaErrores.push("Confirmación por WhatsApp: marcá la casilla para continuar.");
            if (mostrarMensajes) $("error-acepto").textContent = "Marcá la casilla para enviar la confirmación por WhatsApp.";
        } else {
            $("error-acepto").textContent = "";
        }

        const esValido = listaErrores.length === 0;
        $("btn-enviar").disabled = !esValido;

        const cajaErrores = $("resumen-errores");
        if (mostrarMensajes && !esValido && formularioTocado) {
            cajaErrores.classList.remove("oculto");
            cajaErrores.innerHTML =
                "<strong>Revisá los siguientes puntos para habilitar el botón:</strong><ul>" +
                listaErrores.map(err => `<li>${err}</li>`).join("") +
                "</ul>";
        } else {
            cajaErrores.classList.add("oculto");
            cajaErrores.innerHTML = "";
        }

        return {
            esValido,
            nombre,
            email,
            telefono,
            patente,
            vehiculo,
            servicioId,
            resFecha,
            hora
        };
    }

    function formatearRangoBloque(horaStr) {
        const hh = parseInt((horaStr || "09:00").slice(0, 2), 10);
        const inicio = `${String(hh).padStart(2, "0")}:00`;
        const fin = `${String((hh + 2) % 24).padStart(2, "0")}:00`;
        return `${inicio} a ${fin}`;
    }

    function limpiarSinEspecificar(texto) {
        return (texto || "")
            .replace(/\s*sin especificar\s*/gi, " ")
            .replace(/ {2,}/g, " ")
            .trim();
    }

    function armarMensajeWhatsApp({ nombre, telefono, email, vehiculo, patente, servicioNombre, fechaTexto, hora }) {
        return [
            `Hola ${limpiarSinEspecificar(nombre)}! Recibimos tu solicitud de turno en el lavadero:`,
            `- Cliente: ${limpiarSinEspecificar(nombre)}`,
            `- Teléfono: ${limpiarSinEspecificar(telefono)}`,
            `- Correo: ${limpiarSinEspecificar(email)}`,
            `- Vehículo: ${limpiarSinEspecificar(vehiculo)} (${limpiarSinEspecificar(patente)})`,
            `- Servicio: ${limpiarSinEspecificar(servicioNombre)}`,
            `- Fecha: ${fechaTexto}`,
            `- Horario (bloque de 2 hs): ${formatearRangoBloque(hora)}`,
            `- Estado actual: Pendiente`,
            `Respondé CONFIRMAR para validar tu turno.`
        ].join("\n");
    }

    function bloquesBaseFallback() {
        const horas = ["09:00", "11:00", "13:00", "15:00", "17:00"];
        return horas.map(inicio => {
            const hh = parseInt(inicio.slice(0, 2), 10);
            const fin = `${String(hh + 2).padStart(2, "0")}:00`;
            return {
                inicio,
                fin,
                etiqueta: `${inicio} a ${fin}`,
                disponible: true,
                ocupado: false
            };
        });
    }

    async function cargarServiciosSiFaltan() {
        const selectServicio = $("servicio");
        if (!selectServicio || selectServicio.options.length > 1) return;
        try {
            const lista = await llamarApi(URL_SERVICIOS);
            const activos = (Array.isArray(lista) ? lista : (lista?.results || [])).filter(s => s.activo !== false);
            selectServicio.innerHTML =
                '<option value="">-- Elegí una opción --</option>' +
                activos.map(s => {
                    const id = s.id_servicio ?? s.id;
                    const nom = s.nombre_servicio ?? s.nombre;
                    return `<option value="${id}" data-nombre="${nom}">${nom} (${s.duracion} min - $${s.precio})</option>`;
                }).join("");
        } catch (err) {
            marcarError("servicio", "error-servicio", "No se pudieron cargar los servicios.");
        }
    }

    async function consultarDisponibilidad(fechaISO = "", inicializarConHoy = false) {
        const hoyISO = obtenerHoyLocalISO();
        const query = fechaISO ? `?fecha=${encodeURIComponent(fechaISO)}` : "";
        try {
            const data = await llamarApi(`${URL_TURNOS}/disponibilidad${query}`);

            fechaMinimaISO = data?.hoy || fechaMinimaISO || hoyISO;
            fechaMaximaISO = data?.fecha_maxima || fechaMaximaISO;

            const pMin = isoAPartes(fechaMinimaISO);
            const pMax = isoAPartes(fechaMaximaISO);
            if (pMin && pMax && $("ayuda-rango-fecha")) {
                $("ayuda-rango-fecha").textContent =
                    `Desde hoy (${pMin.dia}/${pMin.mes}/${pMin.anio}) hasta ${pMax.dia}/${pMax.mes}/${pMax.anio}.`;
            }

            if (inicializarConHoy && pMin) {
                $("fecha-dia").value = pMin.dia;
                $("fecha-mes").value = pMin.mes;
                $("fecha-anio").value = pMin.anio;
                ultimaFechaConsultada = fechaMinimaISO;
                if (data?.fecha && data.fecha !== fechaMinimaISO) {
                    return consultarDisponibilidad(fechaMinimaISO, false);
                }
            }

            const bloques = (Array.isArray(data?.bloques) && data.bloques.length)
                ? data.bloques
                : bloquesBaseFallback();

            const horaSeleccionadaAntes = $("hora-turno").value;

            $("hora-turno").innerHTML =
                 '<option value="">Elegí un bloque de horario:</option>' +
                bloques.map(b => {
                    const valorHora = `${b.inicio}:00`;
                    const estaOcupado = Boolean(b.ocupado) || (b.disponible === false);
                    const texto = estaOcupado ? `${b.etiqueta} (OCUPADO)` : b.etiqueta;
                    return `<option value="${valorHora}" ${estaOcupado ? "disabled" : ""}>${texto}</option>`;
                }).join("");

            if (horaSeleccionadaAntes) {
                const sigueDisponible = Array.from($("hora-turno").options).some(
                    opt => opt.value === horaSeleccionadaAntes && !opt.disabled
                );
                $("hora-turno").value = sigueDisponible ? horaSeleccionadaAntes : "";
            }
        } catch (err) {
            console.warn("No se pudo consultar /api/turnos/disponibilidad:", err);
            const bloques = bloquesBaseFallback();
            $("hora-turno").innerHTML =
                '<option value="">Elegí un bloque de horario:</option>' +
                bloques.map(b => `<option value="${b.inicio}:00">${b.etiqueta}</option>`).join("");
        }
    }

    function alCambiarFecha() {
        const res = validarYConvertirFecha(
            $("fecha-dia").value.trim(),
            $("fecha-mes").value.trim(),
            $("fecha-anio").value.trim()
        );
        if (res.iso && res.iso !== ultimaFechaConsultada) {
            ultimaFechaConsultada = res.iso;
            consultarDisponibilidad(res.iso, false).then(() => validarFormulario(formularioTocado));
            return;
        }
        validarFormulario(formularioTocado);
    }

    function conectarPreseleccionDesdeTarjetas() {
        document.querySelectorAll(".producto-card .btn-agregar").forEach(boton => {
            boton.addEventListener("click", () => {
                const tarjeta = boton.closest(".producto-card");
                const nombreTarjeta = tarjeta?.querySelector(".producto-nombre")?.textContent.trim().toLowerCase();
                if (nombreTarjeta && $("servicio")) {
                    const opciones = Array.from($("servicio").options);
                    const encontrada = opciones.find(o => (o.dataset.nombre || o.textContent).toLowerCase().includes(nombreTarjeta));
                    if (encontrada) {
                        $("servicio").value = encontrada.value;
                        formularioTocado = true;
                        validarFormulario(true);
                    }
                }
                $("contacto")?.scrollIntoView({ behavior: "smooth" });
            });
        });
    }

    // Eventos de sanitización y validación en tiempo real
    $("nombre").addEventListener("input", function () {
        formularioTocado = true;
        this.value = this.value
            .replace(/^\s+/, "")
            .replace(/\s{2,}/g, " ")
            .replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g, "");
        validarFormulario(true);
    });

    $("email").addEventListener("input", function () {
        formularioTocado = true;
        this.value = this.value.replace(/\s+/g, "");
        validarFormulario(true);
    });

    $("telefono").addEventListener("input", function () {
        formularioTocado = true;
        let val = this.value.replace(/\s+/g, "");
        val = val.startsWith("+")
            ? "+" + val.slice(1).replace(/[^0-9]/g, "")
            : val.replace(/[^0-9]/g, "");
        this.value = val;
        validarFormulario(true);
    });

    $("patente").addEventListener("input", function () {
        formularioTocado = true;
        this.value = this.value.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
        validarFormulario(true);
    });

    $("vehiculo").addEventListener("input", function () {
        formularioTocado = true;
        this.value = this.value
            .replace(/^\s+/, "")
            .replace(/\s{2,}/g, " ")
            .replace(/[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ ]/g, "");
        validarFormulario(true);
    });

    $("servicio").addEventListener("change", () => {
        formularioTocado = true;
        validarFormulario(true);
    });

    $("hora-turno").addEventListener("change", () => {
        formularioTocado = true;
        validarFormulario(true);
    });

    $("acepto").addEventListener("change", () => {
        formularioTocado = true;
        validarFormulario(true);
    });

    ["fecha-dia", "fecha-mes", "fecha-anio"].forEach((id, indice, campos) => {
        $(id).addEventListener("input", function () {
            formularioTocado = true;
            this.value = this.value.replace(/[^0-9]/g, "");
            const largoMax = parseInt(this.getAttribute("maxlength"), 10);
            if (this.value.length >= largoMax && indice < campos.length - 1) {
                $(campos[indice + 1]).focus();
                $(campos[indice + 1]).select();
            }
            alCambiarFecha();
        });
        $(id).addEventListener("blur", alCambiarFecha);
    });

    $("form-contacto").addEventListener("submit", async function (evento) {
        evento.preventDefault();
        formularioTocado = true;

        const estado = validarFormulario(true);
        if (!estado.esValido || !estado.resFecha.iso) return;

        const { nombre, apellido } = separarNombreYApellido(estado.nombre);
        const optServicio = $("servicio").selectedOptions[0];
        const servicioNombre = optServicio ? (optServicio.dataset.nombre || optServicio.textContent) : "";

        const payload = {
            nombre,
            apellido,
            email: estado.email,
            telefono: estado.telefono,
            patente: estado.patente,
            marca: estado.vehiculo,
            servicio_id: parseInt(estado.servicioId, 10),
            fecha: estado.resFecha.iso,
            hora: estado.hora
        };

        $("btn-enviar").disabled = true;

        try {
            const respuesta = await llamarApi(URL_TURNOS, "POST", payload);

            const mensajeBackend = respuesta?.validacion_whatsapp?.mensaje;
            const mensajeFinal = mensajeBackend
                ? limpiarSinEspecificar(mensajeBackend)
                : armarMensajeWhatsApp({
                    nombre: estado.nombre,
                    telefono: estado.telefono,
                    email: estado.email,
                    vehiculo: estado.vehiculo,
                    patente: estado.patente,
                    servicioNombre,
                    fechaTexto: estado.resFecha.textoFecha,
                    hora: estado.hora
                });

            const telSoloNumeros = estado.telefono.replace(/[^0-9]/g, "");
            const urlWhatsApp = respuesta?.validacion_whatsapp?.whatsapp_url
                || `https://wa.me/${telSoloNumeros}?text=${encodeURIComponent(mensajeFinal)}`;

            $("detalle-whatsapp").textContent = mensajeFinal;
            $("btn-abrir-whatsapp").href = urlWhatsApp;

            $("form-contacto").classList.add("oculto");
            $("mensaje-exito").classList.remove("oculto");
            notificar("Solicitud de turno registrada");

            // Refrescamos disponibilidad para bloquear el horario recién tomado
            ultimaFechaConsultada = "";
            await consultarDisponibilidad(estado.resFecha.iso, false);
        } catch (err) {
            const cajaErrores = $("resumen-errores");
            cajaErrores.classList.remove("oculto");
            cajaErrores.innerHTML = `<strong>No se pudo registrar el turno:</strong> ${err.message || "verificá los datos o la disponibilidad."}`;
            $("btn-enviar").disabled = false;
        }
    });

    $("btn-nuevo-turno").addEventListener("click", async () => {
        $("mensaje-exito").classList.add("oculto");
        $("form-contacto").classList.remove("oculto");
        $("hora-turno").value = "";
        $("acepto").checked = false;
        formularioTocado = false;
        await consultarDisponibilidad(fechaMinimaISO || obtenerHoyLocalISO(), true);
        validarFormulario(false);
    });

    // Inicialización al cargar la página
    async function iniciarFormularioTurnos() {
        const pHoy = isoAPartes(obtenerHoyLocalISO());
        if (pHoy) {
            $("fecha-dia").value = pHoy.dia;
            $("fecha-mes").value = pHoy.mes;
            $("fecha-anio").value = pHoy.anio;
        }
        conectarPreseleccionDesdeTarjetas();
        await cargarServiciosSiFaltan();
        await consultarDisponibilidad("", true);
        validarFormulario(false);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarFormularioTurnos);
    } else {
        iniciarFormularioTurnos();
    }

    function obtenerCsrfToken() {
        const matchCookie = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        if (matchCookie) {
            return decodeURIComponent(matchCookie[1]);
        }
        const inputToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return inputToken ? inputToken.value : "";
    }

    async function llamarApi(url, metodo = "GET", datos = null) {
        const metodoUpper = metodo.toUpperCase();
        const csrfToken = obtenerCsrfToken();

        if (typeof window.api === "function" && metodoUpper === "GET") {
            return window.api(url, metodoUpper, datos);
        }

        const cabeceras = {
            "Content-Type": "application/json"
        };
        if (metodoUpper !== "GET" && csrfToken) {
            cabeceras["X-CSRFToken"] = csrfToken;
        }

        const opciones = {
            method: metodoUpper,
            headers: cabeceras,
            credentials: "same-origin"
        };
        if (datos !== null) {
            opciones.body = JSON.stringify(datos);
        }

        const respuesta = await fetch(url, opciones);
        if (!respuesta.ok) {
            const errJson = await respuesta.json().catch(() => ({}));
            const detalle =
                errJson.detail ||
                errJson.error ||
                Object.values(errJson).flat().join(" ") ||
                `Error ${respuesta.status}`;
            throw new Error(detalle);
        }
        if (respuesta.status === 204) return null;
        return respuesta.json();
    }
})();