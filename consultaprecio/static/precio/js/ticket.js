
function calculaGranTotal(data) {
	var producto = null;
	var total = 0;
	for (item in data) {
		producto = data[item];
		total = total + (producto.cantidad * producto.precioVenta)  
	}	
	return total;
}

$(document).ready(function() {

	$('#ventaTabla').bootstrapTable({
			columns: [{
				field: 'eliminar',
				
				formatter: function(value, row, index) {
							return '<i class="glyphicon glyphicon-remove" data-barcode="' + row.barcode + '" ></i>';
						  },
				
				title: 'eliminar'
			}, {
				field: 'barcode',
				
				formatter: function(value, row, index) {
							return '<div data-field="' + this.field + '">' + value + '</div>';;
						  },
				
				title: 'codebar'
			}, {
				field: 'cantidad',
				title: 'Cantidad',
				editable: {
					type: 'text',
					title: 'Cantidad',
					send: 'never',
					url: '',
					success : function (response, newValue) {
					   var data = $('#ventaTabla').bootstrapTable('getData');
					   total = calculaGranTotal(data);
					   $tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }));
					},
					validate: function (value) {
						value = $.trim(value);
						if (!value) {
							return 'Cantidad es requerida';
						}
						if (!/^[0-9]*$/.test(value)) {
							return 'Ingrese una cantida correcta'
						}
						var data = $('#ventaTabla').bootstrapTable('getData'),
							index = $(this).parents('tr').data('index');
						data[index].cantidad = parseInt(value);
						data[index].total = data[index].cantidad * data[index].precioVenta;
						$tableVenta.bootstrapTable('updateRow', {
							index: parseInt(index),
							row: data[index]
						});	
					}
				}
			}, {
				field: 'description',
				sortable: true,
				title: 'Descripcion'
			}, {
				field: 'precioVenta',
				sortable: true,
				title: 'Precio venta',
				formatter: function(value, row, index) {
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('en-US', { style: 'currency', currency: 'USD' }) + '</div>';
						  }
			}, {
				field: 'total',
				sortable: true,
				title: 'Total',
				formatter: function(value, row, index) {
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('en-US', { style: 'currency', currency: 'USD' }) + '</div>';
						  }
			}],
			data: [],
			search : true,
			sortOrder: 'desc',
			showColumns: true,
			showToggle: true,
			showToggle: true,
			showRefresh: true,
			striped: true,
			showColumns: true,
			sortable : true,
			height: 250
			
		}); 
	 
	
	$.getJSON("find/", function(result){
		$('#testTabla').bootstrapTable({
			columns: [{
				field: 'agregar',
				
				formatter: function(value, row, index) {
							//return '<i class="glyphicon glyphicon-ok-sign" onclick="agregar($(this))" ></i>';
							return '<i class="glyphicon glyphicon-shopping-cart" data-barcode="' + row.barcode + '" ></i>';
						  },
				
				title: 'codebar'
			}, {
				field: 'barcode',
				
				formatter: function(value, row, index) {
							return '<div data-field="' + this.field + '">' + value + '</div>';;
						  },
				
				title: 'codebar'
			}, {
				field: 'description',
				sortable: true,
				title: 'Descripcion'
			}, {
				field: 'precioVenta',
				sortable: true,
				title: 'Precio venta',
				formatter: function(value, row, index) {
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }) + '</div>';
						  }
			}],
			data: result,
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
	});  
	
	$.fn.editable.defaults.mode = 'inline';
	var $tableVenta = $('#ventaTabla');
	
	 $("#testTabla").on("click-cell.bs.table", function (field, value, row, $el) {
		if (value =="agregar"){
				
			var data = $tableVenta.bootstrapTable('getData');
			var index_item = $tableVenta.find("[data-barcode='" + $el.barcode + "']").closest("tr").attr('data-index');
			if (typeof(index_item) == 'undefined') {
				$tableVenta.bootstrapTable('insertRow', {
					index: data.length,
					row: {
						cantidad: 1,
						barcode: $el.barcode,
						description: 'Item ' + $el.description,
						precioVenta: $el.precioVenta,
						total: $el.precioVenta * 1
					}
				});	
                $tableVenta.bootstrapTable('scrollTo', 'bottom');
				
			
			}else {
				
				var producto = null;
				for (item in data) {
					producto = data[item];
					if (producto.barcode == $el.barcode) {
					   break;
					}   
				}
				$tableVenta.bootstrapTable('updateRow', {
					index: parseInt(index_item),
					row: {
						cantidad: parseInt(producto.cantidad) + 1,
						barcode: $el.barcode,
						precioVenta: $el.precioVenta,
						total: (producto.cantidad + 1) * $el.precioVenta
					}
				});							
			
			}
			
			total = calculaGranTotal(data);
			$tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }));

		}
	 });	

	 $("#ventaTabla").on("click-cell.bs.table", function (field, value, row, $el) {
		if (value =="eliminar"){
			
			var index_item = $tableVenta.find("[data-barcode='" + $el.barcode + "']").closest("tr").attr('data-index');
			if (typeof(index_item) != 'undefined') {
				//var del_data = { field:'id', values : [parseInt(index_item)] };
				var del_data = { field:'barcode', values : [$el.barcode] };
				$tableVenta.bootstrapTable('remove', del_data);					
			}
			var data = $tableVenta.bootstrapTable('getData');
			total = calculaGranTotal(data);
			$tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }));

		}
	 });	

	  $("#ventaTabla").find(".editable-submit").click(function(e){
		console.log('clicked the button.');
		return false;
	  });			 
	

   
    var ean = null;
	$( "#btnSearch" ).click(function() {
		    ean = null;
			var codigo = $( "#codigobarras" ).val()
			$.getJSON("/find/" + $.trim(codigo) + "/", function(result){
				$('#descriptionProductoLabel').text(result.description);
				$('.precioProductoLabel').text(Number(result.precioVenta).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }));
				ean = result;
				$("#myModal").modal('show')
			});
	  
			return false;
	});	
	
	$('#btnAdd').on('click', function(evt) {
		var data = $tableVenta.bootstrapTable('getData');
		if (ean == null) {
		   alert ('No se puede agregar al ticket');
           return;		   
		}
		$tableVenta.bootstrapTable('insertRow', {
			index: data.length,
			row: {
				cantidad: 1,
				barcode: ean.barcode,
				description: ean.description,
				precioVenta: ean.precioVenta,
				total: ean.precioVenta * 1
			}
		});	
		var data = $tableVenta.bootstrapTable('getData');
		total = calculaGranTotal(data);
		$tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }));
		$tableVenta.bootstrapTable('scrollTo', 'bottom');
		$("#myModal").modal('hide');
		evt.stopPropagation();
	});
	
	$( "#btnCobrar" ).click(function() {
		    var data = $tableVenta.bootstrapTable('getData');
			var ticket = {
			   tipo_movimiento : venta_tipo_mov,
			   total : calculaGranTotal(data),
			   items : data
			}
			var jsonData = JSON.stringify(ticket);
		    $.ajax({
				type: 'POST', // Use POST with X-HTTP-Method-Override or a straight PUT if appropriate.
				dataType: 'json', // Set datatype - affects Accept header
				url: "/tickets/add", // A valid URL
				headers: {"X-HTTP-Method-Override": "PUT", "X-CSRFToken": $.cookie("csrftoken")}, // X-HTTP-Method-Override set to PUT.
				data: jsonData, // Some data e.g. Valid JSON as a string
				success: function (response) {
					
					alert("Details saved successfully!!!");
				},
				error: function (xhr, ajaxOptions, thrownError) {
					alert(xhr.status);
					alert(thrownError);
				}
			});
		   
			return false;
	});	

})
	