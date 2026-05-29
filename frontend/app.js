const API_KEY = "cambia-esto";

const placaInput = document.getElementById("placa");
const fechaInput = document.getElementById("fecha");
const horaInput = document.getElementById("hora");
const btnConsultar = document.getElementById("btn-consultar");
const mensaje = document.getElementById("mensaje");
const resultado = document.getElementById("resultado");

function setMensaje(texto, tipo) {
    mensaje.textContent = texto;
    mensaje.classList.remove("mensaje--error", "mensaje--ok", "mensaje--warn");

    if (tipo === "error") {
        mensaje.classList.add("mensaje--error");
    }

    if (tipo === "ok") {
        mensaje.classList.add("mensaje--ok");
    }

    if (tipo === "warn") {
        mensaje.classList.add("mensaje--warn");
    }
}

function setLoading(estado) {
    btnConsultar.disabled = estado;
    btnConsultar.textContent = estado ? "Consultando..." : "Consultar";
    placaInput.disabled = estado;
    fechaInput.disabled = estado;
    horaInput.disabled = estado;
}

function normalizarPlaca(valor) {
    return valor.trim().toUpperCase().replace("-", "");
}

function validarPlaca(valor) {
    const placa = normalizarPlaca(valor);

    if (!placa) {
        return "La placa es obligatoria";
    }

    if (!/^[A-Z0-9]+$/.test(placa)) {
        return "La placa solo permite letras y numeros";
    }

    if (placa.length !== 6 && placa.length !== 7) {
        return "Longitud invalida: 6 (moto) o 7 (carro)";
    }

    if (/^[A-Z]{3}[0-9]{4}$/.test(placa)) {
        return "";
    }

    if (/^[A-Z]{2}[0-9]{3}[A-Z]$/.test(placa)) {
        return "";
    }

    return "Formato invalido. Usa AAA1111 o AA111A";
}

function validarFecha(valor) {
    if (!valor) {
        return "La fecha es obligatoria";
    }

    return "";
}

function validarHora(valor) {
    if (!valor) {
        return "La hora es obligatoria";
    }

    const partes = valor.split(":");
    if (partes.length !== 2) {
        return "Hora invalida";
    }

    const horas = Number(partes[0]);
    const minutos = Number(partes[1]);
    if (Number.isNaN(horas) || Number.isNaN(minutos)) {
        return "Hora invalida";
    }

    const totalMinutos = horas * 60 + minutos;
    const inicio = 5 * 60;
    const fin = 12 * 60;
    if (totalMinutos < inicio || totalMinutos > fin) {
        return "Hora fuera de rango: 05:00 a 12:00";
    }

    return "";
}

function validarFormulario() {
    const errores = [];
    const errorPlaca = validarPlaca(placaInput.value);
    const errorFecha = validarFecha(fechaInput.value);
    const errorHora = validarHora(horaInput.value);

    setFieldState(placaInput, errorPlaca);
    setFieldState(fechaInput, errorFecha);
    setFieldState(horaInput, errorHora);

    if (errorPlaca) {
        errores.push(errorPlaca);
    }

    if (errorFecha) {
        errores.push(errorFecha);
    }

    if (errorHora) {
        errores.push(errorHora);
    }

    if (errores.length) {
        setMensaje(errores[0], "error");
        return false;
    }

    setMensaje("", "");
    return true;
}

function setFieldState(input, error) {
    const wrap = input.closest(".input-wrap");
    const field = input.closest(".field");
    const mensajeCampo = field ? field.querySelector(".field-message") : null;
    const tieneValor = input.value.trim().length > 0;
    const esValido = !error && tieneValor;

    input.classList.toggle("is-invalid", Boolean(error));
    input.classList.toggle("is-valid", esValido);

    if (!wrap) {
        return;
    }

    wrap.classList.toggle("input-wrap--invalid", Boolean(error));
    wrap.classList.toggle("input-wrap--valid", esValido);

    if (mensajeCampo) {
        if (esValido) {
            mensajeCampo.textContent = "Listo";
            mensajeCampo.classList.add("field-message--visible");
        } else {
            mensajeCampo.textContent = "";
            mensajeCampo.classList.remove("field-message--visible");
        }
    }
}

async function validarVehiculo() {
    if (!validarFormulario()) {
        resultado.textContent = "";
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/validar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            },
            body: JSON.stringify({
                placa: placaInput.value,
                fecha: fechaInput.value,
                hora: horaInput.value
            })
        });

        let data = null;
        try {
            data = await response.json();
        } catch {
            data = null;
        }

        if (!response.ok) {
            let detalle = data && data.detail ? data.detail : "Error al consultar";
            if (detalle && typeof detalle === "object") {
                const valores = Array.isArray(detalle)
                    ? detalle
                    : Object.values(detalle);
                detalle = valores.length ? valores[0] : "Error al consultar";
            }
            setMensaje(detalle, "error");
            resultado.textContent = "";
            return;
        }

        if (data.advertencia) {
            setMensaje(data.advertencia, "warn");
        } else {
            setMensaje("Consulta exitosa", "ok");
        }
        resultado.textContent = data.resultado;
    } catch (error) {
        setMensaje("No se pudo conectar al servidor", "error");
        resultado.textContent = "";
    } finally {
        setLoading(false);
    }
}

function setDefaults() {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");
    const hh = String(now.getHours()).padStart(2, "0");
    const min = String(now.getMinutes()).padStart(2, "0");

    document.getElementById("fecha").value = `${yyyy}-${mm}-${dd}`;
    document.getElementById("hora").value = `${hh}:${min}`;
}

document.addEventListener("DOMContentLoaded", setDefaults);
placaInput.addEventListener("input", validarFormulario);
fechaInput.addEventListener("change", validarFormulario);
horaInput.addEventListener("change", validarFormulario);