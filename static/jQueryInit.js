jQuery.browser = {};


(function () {
    jQuery.browser.msie = false;
    jQuery.browser.version = 0;
    if (navigator.userAgent.match(/MSIE ([0-9]+)\./)) {
        jQuery.browser.msie = true;
        jQuery.browser.version = RegExp.$1;
    }
})();

<!----------------- CARGA DE CRFTOKEN PARA CONSULTAS AJAX-------------------->
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


<!----------------- FUNCIONES REUTILIZABLES -------------------->
function bloqueointerface() {
    if (!$(".blockUI").length) {
        $.blockUI({
            message: `
             <div class="d-flex flex-column align-items-center justify-content-center p-4">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3 text-secondary">Procesando...</p>
            </div>
            `,
            css: {
                backgroundColor: 'transparent',
                border: '0',
                zIndex: 9999999
            },
            overlayCSS: {
                backgroundColor: '#fff',
                opacity: 0.8,
                zIndex: 9999990
            }
        });
    }
}

<!----------------- MENSAJES FLOTANTES SWEETALERT 2 -------------------->
function mensajeSuccess(titulo, mensaje) {
    Swal.fire(titulo, mensaje, 'success')
}

function mensajeWarning(titulo, mensaje) {
    Swal.fire(titulo, mensaje, 'warning')
}

function mensajeDanger(titulo, mensaje) {
    Swal.fire(titulo, mensaje, 'error')
}

function alertaSuccess(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        type: 'success',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

function alertaWarning(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        type: 'warning',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

function alertaDanger(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        type: 'error',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

function alertaInfo(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        type: 'info',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

<!----------------- FUNCIONES AJAX -------------------->

function eliminarajax(pk, nombre, accion, url = '{{ request.path }}', titulo = 'Estás por eliminar este registro:') {
    Swal.fire({
        icon: 'question',
        title: `${titulo}`,
        html: `<b>${titulo}</b> ${nombre}<br><small>Esta acción es irreversible</small>`,
        showCancelButton: true,
        allowOutsideClick: false,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, deseo hacerlo',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            bloqueointerface();
            $.ajax({
                type: 'POST',
                url: '{{ request.path }}',
                data: {
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    action: accion,
                    id: pk,
                },
                dataType: "json",
                beforeSend: function () {
                    bloqueointerface();
                }
            }).done(function (data) {
                setTimeout($.unblockUI, 1);
                if (!data.error) {
                    if (data.to) {
                        location.href = data.to;
                    } else if (data.refresh) {
                        refreshElement(data);
                    } else {
                        location.reload();
                    }
                } else {
                    mensajeWarning(data.message);
                }
            }).fail(function () {
                setTimeout($.unblockUI, 1);
                mensajeWarning('Error en el servidor', 'Advertencia!', 10000);
            });
        }
    });
}