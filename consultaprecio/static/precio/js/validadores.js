
function handle_validate(isValid, componentId, mensajeError) {
   if (isValid) {
		$('#' + componentId).next().text('');
		$('#' + componentId).next().css("visibility", 'hidden');
		$('#' + componentId).closest('div .row').find('span').removeClass(
				'form-text-error');
		$('#' + componentId).removeClass('form-control-error'); 
 
   }else  {
 		$('#' + componentId).addClass('form-control-error');
		$('#' + componentId).closest('div .row').find('span').addClass(
				'form-text-error');
		$('#' + componentId).next().html(mensajeError);
		$('#' + componentId).next().css("visibility", 'visible');  
   }
}


function isValidEmpty(componentId, mensajeError, handleValidate) {
	var campo = $('#' + componentId).val();
	if (campo == '') {
        handleValidate(false,componentId,mensajeError);
		return false;
	}
    handleValidate(true, componentId, mensajeError);
	return true;
}

function isValidEmptyCombo(componentId, mensajeError, handleValidate) {
	var campo = $('#' + componentId).val();
	if (campo == '0') {
	    handleValidate(false,componentId,mensajeError);
		return false;
	}
    handleValidate(true, componentId, mensajeError);
	return true;
}

function isValidSoloNumeros(componentId, mensajeError, handleValidate) {
	var campo = $('#' + componentId).val();
	if (!/^([0-9])*$/.test(campo)) {
		handleValidate(false,componentId,mensajeError);
		return false;
	}
	handleValidate(true,componentId,mensajeError);
	return true;
}

function isValidSelect(componentId, mensajeError, handleValidate) {

             if($.trim($('input[name="' + componentId + '"]:checked').val()) == ''){
                  handleValidate(false,componentId,mensajeError);
                  return false;
             }
             handleValidate(true,componentId,mensajeError);
             return true;
}

function isValidFloat(componentId, mensajeError, handleValidate) {
	var campo = $('#' + componentId).val();
	if (!/^[+-]?\d+(\.\d+)?$/.test(campo)) {
		handleValidate(false,componentId,mensajeError);
		return false;
	}
	handleValidate(true,componentId,mensajeError);
	return true;
}


function isValidSoloLetras(componentId, mensajeError, handleValidate) {
	var campo = $('#' + componentId).val();

	if (campo == '')
		return true;

	if (!/^[a-zA-Z\u00E0-\u00FC\u00C0-\u00DC\u00f1\u00d1\s]+(\s*[a-zA-Z\u00E0-\u00FC\u00C0-\u00DC\u00f1\u00d1\s]*)*[a-zA-Z\u00E0-\u00FC\u00C0-\u00DC\u00f1\u00d1\s]+$/
			.test(campo)) {
		handleValidate(false,componentId,mensajeError);
		return false;
	}
	handleValidate(true,componentId,mensajeError);
	return true;

}

function isValidForm(validators) {
	var i = 0;
	var result = true;
	for (i = 0; i < validators.length; i++) {
		var idx = 0;
		var tmp = false;
		for (idx = 0; idx < validators[i].validate.length; idx++) {
			var validador = validators[i].validate[idx];
			var tmpHandleValidate = handle_validate;
			if (validators[i].handleValidate)
			    tmpHandleValidate = validators[i].handleValidate;
			tmp = validador(validators[i].componentId,
					validators[i].mensajeError[idx], tmpHandleValidate);
			if (tmp == false)
				break;
		}

		result = result && tmp;
	}
	return result;
}

