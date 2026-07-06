/* SGRSI - Cronos | JavaScript principal */

// Cierra alertas automáticamente después de 4 segundos
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelectorAll('.alert.fade.show').forEach(function (alerta) {
            var bsAlerta = bootstrap.Alert.getOrCreateInstance(alerta);
            if (bsAlerta) bsAlerta.close();
        });
    }, 4000);
});
