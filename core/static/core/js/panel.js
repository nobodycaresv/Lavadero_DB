// Funciones compartidas por todas las pantallas del panel.

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Aviso emergente arriba a la derecha. tipo: 'ok' (por defecto) o 'error'.
function avisar(texto, tipo = 'ok') {
    let caja = document.getElementById('avisos');
    if (!caja) {
        caja = document.createElement('div');
        caja.id = 'avisos';
        document.body.appendChild(caja);
    }
    const aviso = document.createElement('div');
    aviso.className = 'aviso-toast' + (tipo === 'error' ? ' error' : '');
    aviso.textContent = texto;
    caja.appendChild(aviso);
    setTimeout(() => {
        aviso.classList.add('salir');
        setTimeout(() => aviso.remove(), 300);
    }, 3500);
}

// Llama a la API. Devuelve el JSON, true (sin contenido) o null si hubo error.
// Uso: const lista = await api('/api/empleados');
//      await api('/api/empleados', 'POST', { nombre: 'Ana' });
async function api(url, metodo = 'GET', datos = null) {
    try {
        const res = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: datos ? JSON.stringify(datos) : null
        });
        if (!res.ok) {
            avisar('Error del servidor: ' + await res.text(), 'error');
            return null;
        }
        return res.status === 204 ? true : await res.json();
    } catch (e) {
        avisar('Error al comunicarse con la API.', 'error');
        return null;
    }
}

// Números que cuentan hasta su valor: <strong data-contar="12">0</strong>
document.querySelectorAll('[data-contar]').forEach(el => {
    const meta = parseFloat(el.dataset.contar) || 0;
    const prefijo = el.dataset.prefijo || '';
    const inicio = performance.now();
    function paso(ahora) {
        const t = Math.min((ahora - inicio) / 900, 1);
        const valor = meta * (1 - Math.pow(1 - t, 3));
        el.textContent = prefijo + Math.round(valor).toLocaleString('es-AR');
        if (t < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
});

// Marca en el menú el link de la página actual.
document.querySelectorAll('aside a').forEach(a => {
    if (a.pathname === location.pathname) a.classList.add('activo');
});
