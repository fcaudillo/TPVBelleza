
function calculaGranTotal(data) {
	var total = 0;
	for (item in data) {
             if (data[item].estatus == 'OK') {
		totalTmp = data[item].monto;
		total = total + totalTmp;  
             }
	}	
	return total;
}

function inicializa_table_reporterecarga() {

		$('#reporterecarga').bootstrapTable({
			columns: [{
				field: 'fecha',
				title: 'fecha'
			}, {
                            field: 'descripcion',
                            title: 'Plan'
                        }, {
                            field: 'telefono',
                            title: 'telefono'
                        }, {
                            field: 'monto',
                            title: 'monto'
                        }, {
                            field: 'codigoautorizacion',
                            title: 'autorizacion'
                        }, {
                            field: 'estatus',
                            title: 'estatus'
                        }, {
                            field: 'error',
                            title: 'error'
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

function consultaReporteRecarga() {
        $('#reporterecarga').bootstrapTable('removeAll');   
        var fini = $('#fechaIni').val()
        var ffin = $('#fechaFin').val(); 
	$.getJSON("recargas_periodo/" + fini + "/" + ffin + "/", function(result){
           total = calculaGranTotal(result);
           $('#reporterecarga').bootstrapTable('load',result);
           $tableReporte.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
	});  
}

var $tableReporte = $('#reporterecarga');
$(document).ready(function() {
        inicializa_table_reporterecarga();
        consultaReporteRecarga();	
	$( "#btnSearch" ).click(function() {
	     consultaReporteRecarga() ;
             return false;
	});	
	
})
	
