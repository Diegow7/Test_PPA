const API_KEY = "cambia-esto";

async function validarVehiculo() {

    const placa = document.getElementById("placa").value;
    const fecha = document.getElementById("fecha").value;
    const hora = document.getElementById("hora").value;

    const response = await fetch("/validar", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },

        body: JSON.stringify({
            placa,
            fecha,
            hora
        })
    });

    const data = await response.json();

    document.getElementById("resultado").innerHTML =
        data.resultado;
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