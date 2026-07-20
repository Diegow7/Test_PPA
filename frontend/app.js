const API_KEY = (document.querySelector('meta[name="api-key"]')?.content ?? "").trim();
const API_KEY_PLACEHOLDER = "cambia-esto";

const placaInput = document.getElementById("placa");
const fechaInput = document.getElementById("fecha");
const horaInput = document.getElementById("hora");
const btnConsultar = document.getElementById("btn-consultar");
const mensaje = document.getElementById("mensaje");
const resultado = document.getElementById("resultado");
const statusRegion = document.querySelector(".status");
const resumenErrores = document.getElementById("resumen-errores");
const historial = document.getElementById("historial");
const buscarHistorialInput = document.getElementById("buscar-historial");
const historyMatchCount = document.getElementById("history-match-count");
const btnExportarHistorial = document.getElementById("btn-exportar-historial");
const btnLimpiarHistorial = document.getElementById("btn-limpiar-historial");
const btnRestaurarHistorial = document.getElementById("btn-restaurar-historial");
const btnCopiarResultado = document.getElementById("btn-copiar-resultado");
const btnLimpiarFormulario = document.getElementById("btn-limpiar-formulario");
const guardarHistorialCheckbox = document.getElementById("guardar-historial");
const restriccionesDia = document.getElementById("restricciones-dia");
const statTotal = document.getElementById("stat-total");
const statOk = document.getElementById("stat-ok");
const statError = document.getElementById("stat-error");

const PREFIJOS_CARRO = ["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "XYZ"];
const PREFIJOS_MOTO = ["AB", "CD", "EF", "GH", "JK", "LM", "NP", "QR", "ST", "UV"];
const HISTORY_KEY = "ppa_historial_consultas";
const HISTORY_LIMIT = 20;
const RESTRICCIONES = {
	"Monday": [1, 2],
	"Tuesday": [3, 4],
	"Wednesday": [5, 6],
	"Thursday": [7, 8],
	"Friday": [9, 0]
};
const FRANJAS_RESTRINGIDAS = ["07:00-09:30", "16:00-19:30"];
const DIA_ES = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miercoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sabado",
    "Sunday": "domingo"
};
let historialBorradoTemporal = null;

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

function tieneApiKeyConfigurada() {
    const apiKey = API_KEY.trim();
    return apiKey.length > 0 && apiKey !== API_KEY_PLACEHOLDER;
}

function limpiarFormulario() {
    placaInput.value = "";
    setDefaults();
    mostrarResumenErrores([]);
    setMensaje("Formulario limpio.", "ok");
    resultado.textContent = "";
    resultado.classList.remove("resultado--ok", "resultado--error");
    actualizarEstadoBotonCopiarResultado();

    [placaInput, fechaInput, horaInput].forEach((input) => {
        input.classList.remove("is-invalid", "is-valid");
        input.removeAttribute("aria-invalid");

        const wrap = input.closest(".input-wrap");
        const field = input.closest(".field");
        const mensajeCampo = field ? field.querySelector(".field-message") : null;

        if (wrap) {
            wrap.classList.remove("input-wrap--invalid", "input-wrap--valid");
        }

        if (mensajeCampo) {
            mensajeCampo.textContent = "";
            mensajeCampo.classList.remove("field-message--visible");
        }
    });
}

async function copiarResultado() {
    const texto = resultado.textContent.trim();
    if (!texto) {
        setMensaje("No hay resultado para copiar.", "error");
        return;
    }

    try {
        await navigator.clipboard.writeText(texto);
        setMensaje("Resultado copiado.", "ok");
    } catch {
        setMensaje("No se pudo copiar el resultado.", "error");
    }
}

function setLoading(estado) {
    btnConsultar.disabled = estado;
    btnConsultar.textContent = estado ? "Consultando..." : obtenerTextoBotonConsulta();
    placaInput.disabled = estado;
    fechaInput.disabled = estado;
    horaInput.disabled = estado;
    btnConsultar.setAttribute("aria-busy", estado);
    if (statusRegion) {
        statusRegion.setAttribute("aria-busy", String(estado));
    }

    if (!btnCopiarResultado) {
        return;
    }

    if (estado) {
        btnCopiarResultado.disabled = true;
        btnCopiarResultado.setAttribute("aria-disabled", "true");
        return;
    }

    actualizarEstadoBotonCopiarResultado();
}

function obtenerTextoBotonConsulta() {
    return guardarHistorialCheckbox && !guardarHistorialCheckbox.checked
        ? "Simular estado"
        : "Consultar estado";
}

function actualizarTextoBotonConsulta() {
    if (!btnConsultar || btnConsultar.disabled) {
        return;
    }

    btnConsultar.textContent = obtenerTextoBotonConsulta();
}

function actualizarEstadoBotonConsultaPorApiKey() {
    if (!btnConsultar) {
        return;
    }

    const apiKeyConfigurada = tieneApiKeyConfigurada();
    btnConsultar.disabled = !apiKeyConfigurada;
    btnConsultar.setAttribute("aria-disabled", String(!apiKeyConfigurada));

    if (!apiKeyConfigurada) {
        btnConsultar.textContent = "Configura API key";
        return;
    }

    actualizarTextoBotonConsulta();
}

function actualizarEstadoBotonCopiarResultado() {
    if (!btnCopiarResultado) {
        return;
    }

    const deshabilitado = resultado.textContent.trim().length === 0;
    btnCopiarResultado.disabled = deshabilitado;
    btnCopiarResultado.setAttribute("aria-disabled", String(deshabilitado));
}

function normalizarPlaca(valor) {
    return String(valor ?? "").trim().toUpperCase().replace(/[-\s]/g, "");
}

function escapeHtml(valor) {
    return String(valor)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
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
        const prefijo = placa.slice(0, 3);
        if (!PREFIJOS_CARRO.includes(prefijo)) {
            return `Prefijo no reconocido para carro: ${prefijo}`;
        }
        return "";
    }

    if (/^[A-Z]{2}[0-9]{3}[A-Z]$/.test(placa)) {
        const prefijo = placa.slice(0, 2);
        if (!PREFIJOS_MOTO.includes(prefijo)) {
            return `Prefijo no reconocido para moto: ${prefijo}`;
        }
        return "";
    }

    return "Formato invalido. Usa AAA1111 o AA111A";
}

function validarFecha(valor) {
    if (!valor) {
        return "La fecha es obligatoria";
    }

    if (!/^\d{4}-\d{2}-\d{2}$/.test(valor)) {
        return "Formato invalido: usa YYYY-MM-DD";
    }

    const fechaIngresada = new Date(`${valor}T00:00:00`);
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    if (fechaIngresada > hoy) {
        return "La fecha no puede ser futura";
    }

    return "";
}

function validarHora(valor) {
    if (!valor) {
        return "La hora es obligatoria";
    }

    if (!/^\d{2}:\d{2}$/.test(valor)) {
        return "Formato invalido: usa HH:MM";
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
    const fin = 19 * 60 + 30;
    if (totalMinutos < inicio || totalMinutos > fin) {
        return "Hora fuera de rango: 05:00 a 19:30";
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
        mostrarResumenErrores(errores);
        return false;
    }

    setMensaje("", "");
    mostrarResumenErrores([]);
    return true;
}

function mostrarResumenErrores(errores) {
    if (!resumenErrores) {
        return;
    }

    if (!errores.length) {
        resumenErrores.textContent = "";
        resumenErrores.classList.remove("error-summary--visible");
        return;
    }

    resumenErrores.textContent = `Revisa: ${errores.join(" · ")}`;
    resumenErrores.classList.add("error-summary--visible");
}

function setFieldState(input, error) {
    const wrap = input.closest(".input-wrap");
    const field = input.closest(".field");
    const mensajeCampo = field ? field.querySelector(".field-message") : null;
    const tieneValor = input.value.trim().length > 0;
    const esValido = !error && tieneValor;

    input.classList.toggle("is-invalid", Boolean(error));
    input.classList.toggle("is-valid", esValido);
    input.setAttribute("aria-invalid", Boolean(error));

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
    resultado.classList.remove("resultado--ok", "resultado--error");
    if (!validarFormulario()) {
        resultado.textContent = "";
        actualizarEstadoBotonCopiarResultado();
        return;
    }

    if (!tieneApiKeyConfigurada()) {
        setMensaje("Configura la API key para consultar.", "error");
        resultado.textContent = "";
        resultado.classList.add("resultado--error");
        actualizarEstadoBotonCopiarResultado();
        return;
    }

    mostrarResumenErrores([]);

    setLoading(true);

    try {
        const endpoint = guardarHistorialCheckbox && guardarHistorialCheckbox.checked ? "/validar" : "/simular";
        const response = await fetch(endpoint, {
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
            resultado.classList.add("resultado--error");
            actualizarEstadoBotonCopiarResultado();
            return;
        }

        setMensaje("Consulta lista", "ok");
        resultado.textContent = data.resultado;
        resultado.classList.add("resultado--ok");
        actualizarEstadoBotonCopiarResultado();
        
        if (guardarHistorialCheckbox && guardarHistorialCheckbox.checked) {
            guardarConsultaLocal({
                placa: placaInput.value,
                fecha: fechaInput.value,
                hora: horaInput.value,
                resultado: data.resultado,
                timestamp: new Date().toISOString().slice(0, 19)
            });
            cargarHistorial();
        } else {
            setMensaje("Consulta simulada (sin guardar)", "ok");
        }
    } catch (error) {
        setMensaje("No se pudo conectar. Intenta de nuevo.", "error");
        resultado.textContent = "";
        resultado.classList.add("resultado--error");
        actualizarEstadoBotonCopiarResultado();
    } finally {
        setLoading(false);
    }
}

function obtenerHistorialLocal() {
    try {
        const raw = localStorage.getItem(HISTORY_KEY);
        if (!raw) {
            return [];
        }

        const data = JSON.parse(raw);
        return Array.isArray(data) ? data : [];
    } catch {
        return [];
    }
}

function guardarConsultaLocal(consulta) {
    const historialLocal = obtenerHistorialLocal();
    historialLocal.unshift(consulta);

    if (historialLocal.length > HISTORY_LIMIT) {
        historialLocal.length = HISTORY_LIMIT;
    }

    localStorage.setItem(HISTORY_KEY, JSON.stringify(historialLocal));
}

function limpiarHistorialLocal() {
    historialBorradoTemporal = obtenerHistorialLocal();
    localStorage.removeItem(HISTORY_KEY);
}

async function limpiarHistorialServidor() {
    if (!tieneApiKeyConfigurada()) {
        return false;
    }

    try {
        const response = await fetch("/historial/limpiar", {
            method: "POST",
            headers: {
                "X-API-Key": API_KEY
            }
        });

        if (!response.ok) {
            return false;
        }

        return true;
    } catch {
        return false;
    }
}

function restaurarHistorialLocal() {
    if (!historialBorradoTemporal || !historialBorradoTemporal.length) {
        return false;
    }

    localStorage.setItem(HISTORY_KEY, JSON.stringify(historialBorradoTemporal));
    historialBorradoTemporal = null;
    return true;
}

function actualizarBotonRestaurar() {
    if (!btnRestaurarHistorial) {
        return;
    }

    const mostrar = Boolean(historialBorradoTemporal && historialBorradoTemporal.length);
    btnRestaurarHistorial.classList.toggle("is-hidden", !mostrar);
}

function actualizarEstadoBotonLimpiarHistorial() {
    if (!btnLimpiarHistorial) {
        return;
    }

    const total = obtenerHistorialLocal().length;
    const deshabilitado = total === 0;
    btnLimpiarHistorial.disabled = deshabilitado;
    btnLimpiarHistorial.setAttribute("aria-disabled", String(deshabilitado));
}

function actualizarEstadoBotonExportarHistorial() {
    if (!btnExportarHistorial) {
        return;
    }

    const total = obtenerHistorialLocal().length;
    const deshabilitado = total === 0;
    btnExportarHistorial.disabled = deshabilitado;
    btnExportarHistorial.setAttribute("aria-disabled", String(deshabilitado));
}

function exportarHistorialCSV() {
    const data = obtenerHistorialLocal();
    if (!data.length) {
        setMensaje("No hay historial para exportar.", "error");
        return;
    }

    const encabezado = ["placa", "fecha", "hora", "resultado", "timestamp"];
    const filas = data.map((item) => [
        item.placa,
        item.fecha,
        item.hora,
        item.resultado,
        item.timestamp
    ]);
    const contenido = [encabezado, ...filas]
        .map((fila) => fila.map((valor) => `"${String(valor).replace(/"/g, '""')}"`).join(","))
        .join("\n");

    const blob = new Blob(["\uFEFF", contenido], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = "historial_pico_y_placa.csv";
    document.body.appendChild(enlace);
    enlace.click();
    document.body.removeChild(enlace);
    URL.revokeObjectURL(url);

    setMensaje("Historial exportado en CSV.", "ok");
}

function cargarHistorial() {
    if (!historial) {
        return;
    }

    const data = obtenerHistorialLocal();
    actualizarEstadoBotonLimpiarHistorial();
    actualizarEstadoBotonExportarHistorial();
    const termino = buscarHistorialInput
        ? buscarHistorialInput.value.trim().toLowerCase()
        : "";

    const dataFiltrada = termino
        ? data.filter((item) => {
            const contenido = `${item.placa} ${item.fecha} ${item.hora} ${item.resultado} ${item.timestamp}`
                .toLowerCase();
            return contenido.includes(termino);
        })
        : data;

    actualizarEstadisticas(data);
    if (historyMatchCount) {
        historyMatchCount.textContent = termino
            ? `Mostrando ${dataFiltrada.length} de ${data.length} consultas.`
            : `Mostrando ${data.length} consultas.`;
    }

    if (!dataFiltrada.length) {
        historial.innerHTML = "<div class=\"history-item\">Sin consultas aun.</div>";
        return;
    }

    historial.innerHTML = dataFiltrada.map((item) => {
        const clase = item.resultado === "Puede circular"
            ? "history-item history-item--ok"
            : "history-item history-item--error";
        return `
            <div class="${clase}">
                <strong>${escapeHtml(item.resultado)}</strong>
                <span>${escapeHtml(item.placa)} · ${escapeHtml(item.fecha)} · ${escapeHtml(item.hora)}</span>
                <span>${escapeHtml(item.timestamp)}</span>
            </div>
        `;
    }).join("");
}

function actualizarEstadisticas(data) {
    if (!statTotal || !statOk || !statError) {
        return;
    }

    const total = data.length;
    const ok = data.filter((item) => item.resultado === "Puede circular").length;
    const error = total - ok;

    statTotal.textContent = String(total);
    statOk.textContent = String(ok);
    statError.textContent = String(error);
}

function renderizarRestriccionesDia(nombreDia, restriccionesActuales, franjasActuales) {
    const restringidas = restriccionesActuales[nombreDia];
    const diaTexto = DIA_ES[nombreDia] || nombreDia;

    if (!restringidas) {
        restriccionesDia.textContent = "Hoy no hay restricciones de pico y placa.";
        restriccionesDia.classList.remove("restricciones-dia--empty");
        return;
    }

    const digitosTexto = restringidas.join(", ");
    const franjasTexto = franjasActuales.join(" y ");
    restriccionesDia.textContent = `Hoy (${diaTexto}) estan restringidas las placas terminadas en: ${digitosTexto}. Horarios: ${franjasTexto}.`;
    restriccionesDia.classList.remove("restricciones-dia--empty");
}

async function mostrarRestriccionesDia() {
	if (!restriccionesDia) {
		return;
	}

	const hoy = new Date();
	const dias = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
	const nombreDia = dias[hoy.getDay()];

    if (!tieneApiKeyConfigurada()) {
        renderizarRestriccionesDia(nombreDia, RESTRICCIONES, FRANJAS_RESTRINGIDAS);
        return;
    }

    let restriccionesActuales = RESTRICCIONES;
    let franjasActuales = FRANJAS_RESTRINGIDAS;

    try {
        const response = await fetch("/reglas", {
            headers: {
                "X-API-Key": API_KEY
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (Array.isArray(data.restricciones_por_dia)) {
                restriccionesActuales = data.restricciones_por_dia.reduce((acc, item) => {
                    if (item && item.dia && Array.isArray(item.digitos)) {
                        acc[item.dia] = item.digitos;
                    }
                    return acc;
                }, {});
            }

            if (Array.isArray(data.franjas_restringidas) && data.franjas_restringidas.length) {
                franjasActuales = data.franjas_restringidas;
            }
        }
    } catch {
        restriccionesActuales = RESTRICCIONES;
        franjasActuales = FRANJAS_RESTRINGIDAS;
    }

    renderizarRestriccionesDia(nombreDia, restriccionesActuales, franjasActuales);
}
function setDefaults() {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");
    const minutosActuales = now.getHours() * 60 + now.getMinutes();
    const minimoPermitido = 5 * 60;
    const maximoPermitido = 19 * 60 + 30;
    const minutosAjustados = Math.min(Math.max(minutosActuales, minimoPermitido), maximoPermitido);
    const hh = String(Math.floor(minutosAjustados / 60)).padStart(2, "0");
    const min = String(minutosAjustados % 60).padStart(2, "0");

    const hoy = `${yyyy}-${mm}-${dd}`;
    document.getElementById("fecha").value = hoy;
    document.getElementById("fecha").max = hoy;
    document.getElementById("hora").value = `${hh}:${min}`;
    document.getElementById("hora").min = "05:00";
    document.getElementById("hora").max = "19:30";
}

document.addEventListener("DOMContentLoaded", setDefaults);
document.addEventListener("DOMContentLoaded", cargarHistorial);
document.addEventListener("DOMContentLoaded", mostrarRestriccionesDia);
placaInput.addEventListener("input", validarFormulario);
fechaInput.addEventListener("change", validarFormulario);
horaInput.addEventListener("change", validarFormulario);

if (btnExportarHistorial) {
    btnExportarHistorial.addEventListener("click", exportarHistorialCSV);
}

if (btnLimpiarHistorial) {
    btnLimpiarHistorial.addEventListener("click", async () => {
        limpiarHistorialLocal();
        cargarHistorial();
        const limpiadoServidor = await limpiarHistorialServidor();
        if (limpiadoServidor) {
            setMensaje("Historial local y servidor limpiados.", "ok");
        } else {
            setMensaje("Historial local limpiado.", "warn");
        }
        actualizarBotonRestaurar();
    });
}

if (buscarHistorialInput) {
    buscarHistorialInput.addEventListener("input", cargarHistorial);
}

if (btnRestaurarHistorial) {
    btnRestaurarHistorial.addEventListener("click", () => {
        const restaurado = restaurarHistorialLocal();
        if (restaurado) {
            cargarHistorial();
            setMensaje("Historial restaurado.", "ok");
        } else {
            setMensaje("No hay historial para restaurar.", "error");
        }
        actualizarBotonRestaurar();
    });
}

if (btnCopiarResultado) {
    btnCopiarResultado.addEventListener("click", copiarResultado);
}

if (btnLimpiarFormulario) {
    btnLimpiarFormulario.addEventListener("click", limpiarFormulario);
}

if (guardarHistorialCheckbox) {
    guardarHistorialCheckbox.addEventListener("change", actualizarTextoBotonConsulta);
}

document.addEventListener("keydown", (event) => {
    const activeElement = document.activeElement;
    const isTypingField = activeElement && (
        activeElement.tagName === "INPUT"
        || activeElement.tagName === "TEXTAREA"
        || activeElement.isContentEditable
    );

    if (event.key === "Enter" && isTypingField && !btnConsultar.disabled) {
        event.preventDefault();
        validarVehiculo();
    }

    if (event.key === "Escape" && isTypingField && !btnConsultar.disabled) {
        event.preventDefault();
        limpiarFormulario();
    }
});

actualizarBotonRestaurar();
actualizarTextoBotonConsulta();
actualizarEstadoBotonConsultaPorApiKey();
actualizarEstadoBotonLimpiarHistorial();
actualizarEstadoBotonExportarHistorial();
actualizarEstadoBotonCopiarResultado();