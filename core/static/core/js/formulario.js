// formulario.js
// Valida el formulario de contacto antes de enviarlo

function mostrarError(campoId, errorId, mensaje) {
    document.getElementById(campoId).classList.add("invalido");
    document.getElementById(errorId).textContent = mensaje;
}

function limpiarError(campoId, errorId) {
    document.getElementById(campoId).classList.remove("invalido");
    document.getElementById(errorId).textContent = "";
}

function validarFormulario() {
    let esValido = true;

    // Nombre: mínimo 2 caracteres
    let nombre = document.getElementById("nombre").value;
    if (nombre.length < 2) {
        mostrarError("nombre", "error-nombre", "Ingresá tu nombre (mínimo 2 caracteres).");
        esValido = false;
    } else {
        limpiarError("nombre", "error-nombre");
    }

    // Email: debe tener @ y un punto después
    let email = document.getElementById("email").value;
    if (email.indexOf("@") == -1 || email.indexOf(".") == -1) {
        mostrarError("email", "error-email", "Ingresá un correo electrónico válido.");
        esValido = false;
    } else {
        limpiarError("email", "error-email");
    }

    // Mensaje: mínimo 10 caracteres
    let mensaje = document.getElementById("mensaje").value;
    if (mensaje.length < 10) {
        mostrarError("mensaje", "error-mensaje", "El mensaje debe tener al menos 10 caracteres.");
        esValido = false;
    } else {
        limpiarError("mensaje", "error-mensaje");
    }

    // Checkbox: debe estar marcado
    let acepto = document.getElementById("acepto").checked;
    if (!acepto) {
        document.getElementById("error-acepto").textContent = "Necesitamos tu confirmación para responderte.";
        esValido = false;
    } else {
        document.getElementById("error-acepto").textContent = "";
    }

    return esValido;
}

function manejarEnvio(evento) {
    evento.preventDefault();

    if (validarFormulario()) {
        document.getElementById("form-contacto").classList.add("oculto");
        document.getElementById("mensaje-exito").classList.remove("oculto");
    }
}

document.getElementById("nombre").addEventListener("blur", function() {
    if (this.value.length > 0 && this.value.length < 2) {
        mostrarError("nombre", "error-nombre", "Mínimo 2 caracteres.");
    } else if (this.value.length >= 2) {
        limpiarError("nombre", "error-nombre");
    }
});

document.getElementById("email").addEventListener("blur", function() {
    if (this.value.length > 0) {
        if (this.value.indexOf("@") == -1 || this.value.indexOf(".") == -1) {
            mostrarError("email", "error-email", "Formato de email incorrecto.");
        } else {
            limpiarError("email", "error-email");
        }
    }
});

document.getElementById("form-contacto").addEventListener("submit", manejarEnvio);
