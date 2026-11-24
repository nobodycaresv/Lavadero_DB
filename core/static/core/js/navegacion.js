// navegacion.js
// Marca el link activo en el nav y aplica el efecto de scroll al header

let header = document.getElementById("site-header");
let secciones = document.getElementsByTagName("section");
let links = document.getElementsByClassName("nav-link");

function actualizarHeader() {
    if (window.scrollY > 50) {
        header.classList.add("scrolled");
    } else {
        header.classList.remove("scrolled");
    }
}

function actualizarNavActivo() {
    let seccionActual = "";

    for (let i = 0; i < secciones.length; i++) {
        if (window.scrollY >= secciones[i].offsetTop - 100) {
            seccionActual = secciones[i].id;
        }
    }

    for (let i = 0; i < links.length; i++) {
        links[i].classList.remove("activo");
        if (links[i].getAttribute("href") == "#" + seccionActual) {
            links[i].classList.add("activo");
        }
    }
}

window.addEventListener("scroll", function() {
    actualizarHeader();
    actualizarNavActivo();
});

// Ejecutar al cargar la página
actualizarHeader();
actualizarNavActivo();
