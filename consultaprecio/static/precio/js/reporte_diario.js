
function calculaGranTotal(data) {
	var total = 0;
	for (item in data) {
		totalTmp = data[item].total;
		total = total + totalTmp;  
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
                            field: 'total',
                            title: 'Total'
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
           total = calculaGranTotal(result);
           $('#ventaTabla').bootstrapTable('load',result);
           $tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
	});  
}

var $tableVenta = $('#ventaTabla');
$(document).ready(function() {
        inicializa_table_ventas();
	
	$( "#btnSearch" ).click(function() {
	     consultaResumenDiario() ;
             return false;
	});	
	
})
	
