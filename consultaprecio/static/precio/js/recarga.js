
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

function recargaTAE() {
        var compania = $('#compania').val()
        var plan = $('#plan').val(); 
        var telefono = $('#telefono1').val()
        var monto = '10'
 
	$.getJSON("/recargatae/" + compania + "/" + plan + "/" + telefono + "/" + monto + "/", function(result){
             alert("Regreso de la llamada")
             alert(result)
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
     $(bloque).append("<label><input type='radio' name='plan' id='plan' value='" + opciones[i].plan + "'> $" + opciones[i].monto + "</label><br/>")
  }

}



$(document).ready(function() {

        $("#compania").val($("#compania option:first").val());

        refrescaPlanes()
        $("#compania").change(function() {
           refrescaPlanes()
        });
	
	$( "#btnRecarga" ).click(function() {

             if (!isValidForm(validadores)) {
                return false;
             }

             msg = validaInfo()
             if( msg != ''){
                 $('#msgText').text(msg)
                 $('#dlgMensaje').modal('show')
                 return false;
             }
	     recargaTAE() ;
             return false;
	});	
	
})
	
