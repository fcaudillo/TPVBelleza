

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

$(document).ready(function() {
	
	$( "#btnRecarga" ).click(function() {
	     recargaTAE() ;
             return false;
	});	
	
})
	
