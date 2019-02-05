
function calculaGranTotal(data) { var producto = null; var total = 0;
	for (item in data) {
		producto = data[item];
		total = total + (producto.cantidad * producto.precioCompra)  
	}	
	return total;
}


function inicializa_table_products() {

               $('#testTabla').bootstrapTable({
			columns: [{
				field: 'agregar',
				
				formatter: function(value, row, index) {
							//return '<i class="glyphicon glyphicon-ok-sign" onclick="agregar($(this))" ></i>';
							return '<i class="glyphicon glyphicon-shopping-cart" data-barcode="' + row.barcode + '" ></i>';
						  },
				
				title: 'codebar'
			}, {  
                                field: 'existencia',
                                title: 'existencia'
                        },  {
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
				field: 'precioCompra',
				sortable: true,
				title: 'Precio compra',
				formatter: function(value, row, index) {
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }) + '</div>';
						  }
			}, {
                           
				field: 'precioVenta',
				sortable: true,
				title: 'Precio venta',
				formatter: function(value, row, index) {

			                                return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }) + '</div>';
			                  }

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


function fill_table_products() {
 
        $('#testTabla').bootstrapTable('removeAll');
	$.getJSON("find/", function(result){
	   $('#testTabla').bootstrapTable('load', result);	
	});  
}

$(document).ready(function() {
        $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-MX']);
        inicializa_table_products();

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
						data[index].total = data[index].cantidad * data[index].precioCompra;
						$tableVenta.bootstrapTable('updateRow', {
							index: parseInt(index),
							row: data[index]
						});	
					}
				}
			}, {
				field: 'description',
				sortable: true,
				title: 'Descripcion',


				editable: {
					type: 'text',
					title: 'Descripcion',
					send: 'never',
					url: '',
					validate: function (value) {
						value = $.trim(value);
						if (!value) {
							return 'La descripcion es requerida';
						}
  
						var data = $('#ventaTabla').bootstrapTable('getData'),
						index = $(this).parents('tr').data('index');
						data[index].description = value;
						$tableVenta.bootstrapTable('updateRow', {
							index: parseInt(index),
							row: data[index]
						});	
					}
				}

			}, {


				field: 'precioCompra',
				sortable: true,
				title: 'Precio compra',


				editable: {
					type: 'text',
					title: 'Precio compra',
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
							return 'El precio es requerido';
						}
						if (!/^[+]?([0-9]+(?:[\.][0-9]*)?|\.[0-9]+)$/.test(value)) {
							return 'Ingrese una cantida correcta'
						}
						var data = $('#ventaTabla').bootstrapTable('getData'),
							index = $(this).parents('tr').data('index');
						data[index].precioCompra = parseFloat(value);
						data[index].total = data[index].cantidad * data[index].precioCompra;
						$tableVenta.bootstrapTable('updateRow', {
							index: parseInt(index),
							row: data[index]
						});	
					}
				}

                        },{
				field: 'precioVenta',
				sortable: true,
				title: 'Precio venta',

				editable: {
					type: 'text',
					title: 'Precio venta',
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
							return 'El precio es requerido';
						}
						if (!/^[+]?([0-9]+(?:[\.][0-9]*)?|\.[0-9]+)$/.test(value)) {
							return 'Ingrese una cantida correcta'
						}
						var data = $('#ventaTabla').bootstrapTable('getData'),
							index = $(this).parents('tr').data('index');
						data[index].precioVenta = parseFloat(value);
						data[index].total = data[index].cantidad * data[index].precioCompra;
						$tableVenta.bootstrapTable('updateRow', {
							index: parseInt(index),
							row: data[index]
						});	
					}
				}


			}, {
				field: 'total',
				sortable: true,
				title: 'Total COMPRA',
				formatter: function(value, row, index) {
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }) + '</div>';
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
	 
        fill_table_products();
	
	
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
						description: $el.description,
                                                precioCompra: $el.precioCompra,
						precioVenta: $el.precioVenta,
						total: $el.precioCompra * 1
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
	

        $('#btnCrearProducto').click(function() {
           $('#modalCrearProducto').modal('show'); 
        });

        $('#btnInsertarProduto').click(function() {

			var producto = {
                           barcode : $('#c_codigobarras').val(),
                           codigoproveedor: $('#c_codigoproveedor').val(),
                           descripcion : $('#c_descripcion').val(),
                           categoria : $('#c_categoria').val(),
                           precioCompra : $('#c_precioCompra').val(),
                           precioVenta : $('#c_precioVenta').val(),
                           puntoreorden : $('#c_puntoreorden').val(),
                           maximoexist: $('#c_maximoexist').val(),
                           ubicacion : $('#c_ubicacion').val()
			}
			var jsonData = JSON.stringify(producto);
		    $.ajax({
				type: 'POST', // Use POST with X-HTTP-Method-Override or a straight PUT if appropriate.
				dataType: 'json', // Set datatype - affects Accept header
				url: "/producto/add", // A valid URL
				headers: {"X-HTTP-Method-Override": "PUT", "X-CSRFToken": $.cookie("csrftoken")}, // X-HTTP-Method-Override set to PUT.
				data: jsonData, // Some data e.g. Valid JSON as a string
				success: function (response) {
                                        fill_table_products();
					alert("Producto agregado ");
				},
				error: function (xhr, ajaxOptions, thrownError) {
					alert(xhr.status);
					alert(thrownError);
				}
			});
		   

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
			   tipo_movimiento : $('#tipoMov').val(),
			   total : calculaGranTotal(data),
                           descripcion : $('#mov_description').val(),
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
					$('#ventaTabla').bootstrapTable('removeAll');
					var data = $tableVenta.bootstrapTable('getData');
			                total = calculaGranTotal(data);
			                $tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'USD' }));
                                        fill_table_products();
					alert("Movimiento  registrado");
				},
				error: function (xhr, ajaxOptions, thrownError) {
					alert(xhr.status);
					alert(thrownError);
				}
			});
		   
			return false;
	});	

})
	
