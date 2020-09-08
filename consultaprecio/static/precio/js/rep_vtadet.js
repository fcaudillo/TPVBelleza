
function calculaGranTotal(data) {
	var total = 0;
	for (item in data) {
		totalTmp = data[item].total;
		total = total + totalTmp;  
	}	
	return total;
}

function inicializa_table_reporte() {

		$('#reporteTabla').bootstrapTable({
			columns: [{
                                field: 'folio',
                                title: 'Folio'
                        },{
				field: 'fecha',
				title: 'fecha'
			}, {
                            field: 'tipomovimiento',
                            title: 'Movimiento'
                        },{
                            field: 'username',
                            title: 'Usuario'
                        }, {
                            field: 'codigo',
                            title: 'Codigo',
                        }, {
                            field: 'descripcion',
                            title: 'Descripcion',
                        },{
                            field: 'cantidad',
                            title: 'Cantidad'
                        }, {
                            field: 'precioventa',
                            title: 'Precio Venta',
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

function consultaReporte() {
        $('#reporteTabla').bootstrapTable('removeAll');   
        var fini = $('#fechaIni').val()
        var ffin = $('#fechaFin').val(); 
	$.getJSON("reporte_vtadet/" + fini + "/" + ffin + "/", function(result){
           total = calculaGranTotal(result);
           $('#reporteTabla').bootstrapTable('load',result);
           $tableReporte.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
	});  
}

var $tableReporte = $('#reporteTabla');
$(document).ready(function() {
        inicializa_table_reporte();
	
	$( "#btnSearch" ).click(function() {
	     consultaReporte() ;
             return false;
	});	
	
})
	
