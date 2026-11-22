// catalogo.js
// Carga dinámicamente los servicios activos desde la API de Django (/api/servicios -> catalogos.models.Servicio)
// Ordenados del más reciente al más antiguo para que los nuevos aparezcan primero.

const API_SERVICIOS_URL = "/api/servicios";

function formatearPrecio(numero) {
    return "$" + Number(numero).toLocaleString("es-AR");
}

function crearCard(servicio, delay) {
    const card = document.createElement("article");
    card.classList.add("producto-card", "card-entrada");
    card.style.animationDelay = delay + "ms";

    card.innerHTML = `
        <div class="producto-imagen" aria-hidden="true"></div>
        <div class="producto-info">
            <p class="producto-categoria">Duración estimada: ${servicio.duracion} min</p>
            <h3 class="producto-nombre">${servicio.nombre_servicio}</h3>
            <p class="producto-descripcion">Servicio profesional de estética y cuidado vehicular ejecutado con productos de alta gama.</p>
            <p class="producto-precio">${formatearPrecio(servicio.precio)}</p>
            <button class="btn-agregar" type="button">Reservar turno</button>
        </div>
    `;

    const btnConsultar = card.querySelector(".btn-agregar");
    btnConsultar.addEventListener("click", function () {
        document.getElementById("contacto").scrollIntoView({ behavior: "smooth" });
        document.getElementById("interes").value = "pedido";
        document.getElementById("mensaje").value =
            'Hola, me gustaría reservar turno para "' + servicio.nombre_servicio + '" (' + servicio.duracion + ' min). ¿Qué disponibilidad tienen?';
    });

    return card;
}

async function cargarCatalogoDesdeAPI() {
    const grilla = document.getElementById("grilla-productos");
    grilla.innerHTML = '<p style="color: #C8C8C8;">Cargando servicios disponibles...</p>';

    try {
        const res = await fetch(API_SERVICIOS_URL);
        if (!res.ok) throw new Error("Error HTTP " + res.status);
        const servicios = await res.json();
        const activos = servicios
            .filter(s => s.activo)
            .sort((a, b) => b.id_servicio - a.id_servicio);

        grilla.innerHTML = "";
        if (activos.length === 0) {
            grilla.innerHTML = '<p style="color: #C8C8C8;">No hay servicios activos cargados en este momento.</p>';
            return;
        }

        activos.forEach((servicio, i) => {
            const card = crearCard(servicio, i * 80);
            grilla.appendChild(card);
        });
    } catch (error) {
        console.error("Error al cargar servicios desde la API:", error);
        grilla.innerHTML = '<p style="color: #ff4d47;">No se pudieron cargar los servicios desde el servidor.</p>';
    }
}

cargarCatalogoDesdeAPI();
