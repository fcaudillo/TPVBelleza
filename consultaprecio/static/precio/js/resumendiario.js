
function calculaGranTotal(data) {
	var producto = null;
	var total = 0;
	for (item in data) {
		producto = data[item];
		total = total + (producto.cantidad * producto.precioVenta)  
	}	
	return total;
}

function inicializa_table_ventas() {

		$('#ventaTabla').bootstrapTable({
			columns: [{
				field: 'fecha',
				title: 'fecha'
			}, {
                            field: 'TipoMovimiento',
                            title: 'Movimiento'
                        }, {
                            field: 'Total',
                            title: 'total.'
			}],
			//data: result,
			search : true,
			pagination: true,
			sortOrder: 'desc',
			showColumns: true,
			showToggle: true,
			showToggle: true,
			showRefresh: true,
			striped: true,
			showColumns: true,
			sortable : true
			
		});
}

function consultaResumenDiario() {
        $('#ventaTabla').bootstrapTable('removeAll');   
        var fini = $('#fechaIni').val()
        var ffin = $('#fechaFin').val(); 
	$.getJSON("resumenmovimiento/" + fini + "/" + ffin + "/", function(result){
          $('#ventaTabla').bootstrapTable('load',result);
	});  
}

$(document).ready(function() {
        inicializa_table_ventas();
	
	$( "#btnSearch" ).click(function() {
	     consultaResumenDiario() 
	});	
	
})
	
