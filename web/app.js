window.onload = function () {
    console.log("✅ Página completamente cargada, iniciando WAMP...");

    var connection = new autobahn.Connection({
        url: "ws://localhost:60001",
        realm: "default"
    });

    connection.onopen = function (session) {
        console.log("✅ Conexión abierta con WAMP.");

        let statusElement = document.getElementById("status");
        let messagesDiv = document.getElementById("messages");

        if (!statusElement || !messagesDiv) {
            console.error("❌ ERROR: No se encontraron los elementos necesarios en el DOM.");
            return;
        }

        statusElement.innerText = "✅ Conectado a WAMP";
        statusElement.style.color = "green";

        session.subscribe("link16.data", function (args) {
            console.log("📥 Datos recibidos en WAMP:", args);

            if (!args || args.length === 0) {
                console.error("❌ ERROR: Mensaje vacío o nulo recibido.");
                return;
            }

            try {
                let message = args[0]; 
                console.log("📌 JSON recibido correctamente:", message);
                displayMessage(message);
            } catch (error) {
                console.error("❌ ERROR al procesar el mensaje:", error);
            }
        });

        console.log("📡 Suscripción exitosa al tópico 'link16.data'");
    };

    connection.onclose = function (reason) {
        let statusElement = document.getElementById("status");
        if (statusElement) {
            statusElement.innerText = "❌ Desconectado de WAMP";
            statusElement.style.color = "red";
        }
        console.warn("❌ Conexión cerrada:", reason);
    };

    connection.open();

    function displayMessage(data) {
        let messagesDiv = document.getElementById("messages");

        if (!messagesDiv) {
            console.error("❌ ERROR: No se encontró el contenedor de mensajes en el DOM.");
        }
    }
};
