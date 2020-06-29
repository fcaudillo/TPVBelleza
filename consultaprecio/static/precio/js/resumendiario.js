
function calculaGranTotal(data) {
	var totalVenta = 0;
        var totalCosto = 0;
        var totalGanancia = 0;
	for (item in data) {
		totalVenta = totalVenta + data[item].totalVenta;  
                totalCosto = totalCosto + data[item].totalCosto;
                totalGanancia = totalGanancia + (totalVenta - totalCosto);
	}	
	return {'totalCosto':totalCosto,'totalVenta': totalVenta,'totalGanancia': totalGanancia}
}

function inicializa_table_ventas() {

		$('#ventaTabla').bootstrapTable({
			columns: [{
				field: 'fecha',
				title: 'fecha'
			}, {
                            field: 'TipoMovimiento',
                            title: 'Movimiento'
                        },{
                          field: 'totalCosto',
                          title: 'Total costo'
                          }, {
                            field: 'totalVenta',
                            title: 'Total Venta'
			  }, {
                            field: 'totalGanancia',
                            title: 'Total ganancia'
                           }
                        ],
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
           totales  = calculaGranTotal(result);
           $('#ventaTabla').bootstrapTable('load',result);
           $tableVenta.find("tfoot").find(".granTotalCosto").text(Number(totales.totalCosto).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
           $tableVenta.find("tfoot").find(".granTotalVenta").text(Number(totales.totalVenta).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
           $tableVenta.find("tfoot").find(".granTotalGanancia").text(Number(totales.totalGanancia).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
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
	
