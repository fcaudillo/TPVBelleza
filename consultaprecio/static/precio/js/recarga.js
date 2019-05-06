
function handleValidatePlan(isValid,componentId,mensajeError) {
  if  (isValid) {
     $('#errorMonto').css("visibility", 'hidden');
     $('#errorMonto').removeClass('form-control-error');
  }else {
     $('#errorMonto').html(mensajeError);
     $('#errorMonto').css("visibility", 'visible');
  }
}

function isValidTelefonos(componentId, mensajeError, handleValidate) {
        var campo = $('#telefono1').val();
        var campo2 = $('#telefono2').val();

        if (campo != campo2) {
                handleValidate(false,componentId,mensajeError);
                return false;
        }

        handleValidate(true, componentId, mensajeError);
        return true;
}


var validadores = [
                {
                        "componentId" : "compania",
                        "mensajeError" : [ "Este campo es obligatorio" ],
                        "validate" : [ isValidEmptyCombo ]
                },
                {
                        "componentId": "plan",
                        "mensajeError": ["El plan es  obligatorio"],
                        "validate" : [ isValidSelect ],
                        "handleValidate": handleValidatePlan 
                },
                {
                        "componentId" : "telefono1",
                        "mensajeError" : [ "Este campo es obligatorio",
                                        "Solo admite numeros" ],
                        "validate" : [ isValidEmpty, isValidFloat ]
                },
                
                {
                        "componentId" : "telefono2",
                        "mensajeError" : [ "Este campo es obligatorio",
                                        "Solo admite numeros",
                                        "Los dos numeros de telefono no coinciden" ],
                        "validate" : [ isValidEmpty, isValidFloat, isValidTelefonos ]
                }]

function encuentraplan(plan, planes) {
  for (var i = 0; i < planes.length; i++) {
     if (planes[i].plan == plan) 
        return planes[i]
  }
  return null;
}

function recargaTAE() {
        var compania = $('#compania').val()
        var plan = $('input[name="plan"]:checked').val(); 
        var telefono = $('#telefono1').val()

        var opciones = planes[$("#compania").val()]
        var planObj = encuentraplan(plan,opciones)

        if (planObj == null) {
            alert('Plan invalido. Consulte al administrador')
            return;
        }

        var monto = planObj['monto']

        $('#dlgMensaje').modal('hide') 
        $('#waitDialog').modal('show')

	$.getJSON("/recargatae/" + compania + "/" + plan + "/" + telefono + "/" + monto + "/", function(result){
             if (result.rcode != 0) {
                 $("#lblEstadoRecarga").text("Fallo al recargar el celular")
                 $("#lblCelularExitoso").text($("#telefono2").val())
                 $("#lblRespuesta").text(result.rcode_description)
             }else {

                 $("#lblEstadoRecarga").text("Recarga Exitosa")
                 $("#lblCelularExitoso").text($("#telefono2").val())
                 $("#lblRespuesta").text("Codigo autorizacion" + result.op_authorization)
             }
             $('#waitDialog').modal('hide')
             $('#dlgResult').modal('show')
             $('#plan').prop("checked", false)
             $('#telefono1').val("")
             $('#telefono2').val("")
	}).fail(function(jqXHR, textStatus, errorThrown) { 
             $('#waitDialog').modal('hide')
             $('#plan').prop("checked", false)
             $('#telefono1').val("")
             $('#telefono2').val("")
             console.log('getJSON request failed! ' + textStatus); 
        });
}

function refrescaPlanes() {
  var opciones = planes[$("#compania").val()]
  var bloque = "";
  $("#bloque0").empty();
  $("#bloque1").empty();
  $("#plan").val("");
  for (var i = 0; i < opciones.length; i++) {
     bloque = "#bloque0"
     if (i > (opciones.length / 2))
       bloque = "#bloque1"
     tmp_desc = '$' + opciones[i].monto
     if (pantalla == 'recargadatos')
        tmp_desc = opciones[i].description
     $(bloque).append("<label><input type='radio' name='plan' id='plan' value='" + opciones[i].plan + "'> " + tmp_desc + "</label><br/>")
  }

}



$(document).ready(function() {

        $("#compania").val($("#compania option:first").val());

        refrescaPlanes()
        $("#compania").change(function() {
           refrescaPlanes()
        });

        $('#btnAceptar').on('click', function (event) {
          recargaTAE();
          event.preventDefault();
        });
	
	$( "#btnRecarga" ).click(function(event) {

             if (!isValidForm(validadores)) {
                return false;
             }
             $("#imgCarrier").attr("src",$("#img" + $("#compania").val()).attr("src"));
             $('#lblCarrier').text( $("[name='compania'] option:selected").text())
             $('#lblCelular').text($("#telefono1").val())
             $('#lblMonto').text($('input[name="plan"]:checked').parent().text())
             $('#dlgMensaje').modal('show')
	    event.preventDefault(); 
	});	
	
})
	
