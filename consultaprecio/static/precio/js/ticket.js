
function calculaGranTotal(data) {
	var producto = null;
	var total = 0;
	for (item in data) {
		producto = data[item];
		total = total + (producto.cantidad * producto.precioVenta)  
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
                        }, {
                            field: 'ubicacion',
                            title: 'ubicacion'
                        },
                        {
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
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }) + '</div>';
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

function cargaInventarioSyncOld() {
        $('#testTabla').bootstrapTable('removeAll');    
	$.getJSON("find/", function(result){
          $('#testTabla').bootstrapTable('load',result);
	});  
}


function cargaInventario() {
   cargaInventarioAsync()
}

function solicitaPagina (pagina) {
   return new Promise(function(resolve, reject) {
		$.getJSON("find_products/?page=" + pagina, function(result){
			resolve(result);
		});

   });
}
		
		
function requestPageObservable(pagina) {
   return Rx.Observable.fromPromise(solicitaPagina(pagina))
}


function on_line () {
   return new Promise(function(resolve, reject) {
		$.getJSON("/on_line", function(result){
			resolve(result);
		},function () {
                   console.log("fn1");
                   resolve({"on_line":false});
                },function(jqXHR, textStatus, errorThrown) {
                        resolve({"on_line":false});
                });

   });
}

		
function requestOnlineObservable() {
   return Rx.Observable.fromPromise(on_line())
}

function checkStatusInternet() {
  Rx.Observable.interval(5000).flatMap(requestOnlineObservable).subscribe(function(dato) {
    console.log ("Ejecutando cada 5 segundos");
    if (dato.on_line) {
      $("#status_online").css("color","#64dd17");
    }else {
      $("#status_online").css("color","red");
    }
  });
}

function cargaInventarioAsync() {
        $('#testTabla').bootstrapTable('removeAll');
        var arr_productos = []
        $.getJSON("find_products/", function(result){
          total_pages = result['num_pages']
          pagina = 1
          arr_productos = result.productos;
          console.log("total paginas : " + total_pages)
          if (total_pages > 1) {
             incremento = 100 / total_pages
             $('#myBar').width(incremento + "%");
             $('#myProgreso').modal("show"); 
             addProductos(arr_productos);
             Rx.Observable.range(2,total_pages - 1).flatMap(requestPageObservable).subscribe(function(dato) {
               console.log("pagina: " + dato.current_page + " de : " + dato.num_pages); 
               pagina ++;
               arr_productos = arr_productos.concat(dato.productos);
               addProductos(dato.productos);
               $('#myBar').width((pagina * incremento) + "%");
             }, function (e) {
               console.log(e);
             }, function () {
                 $('#testTabla').bootstrapTable('load',arr_productos);
                 setTimeout(function() {
                    $('#myProgreso').modal("hide");
                 },1200);
             });
          }else {
             $('#testTabla').bootstrapTable('load',arr_productos);
          }
        });
}


function registrarVenta(tipo_impresion) {
                    var $tableVenta = $('#ventaTabla');
		    var data = $tableVenta.bootstrapTable('getData');
			var ticket = {
			   tipo_movimiento : venta_tipo_mov,
			   total : calculaGranTotal(data),
                           descripcion : 'Venta al publico',
                           tipo_impresion : tipo_impresion,
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
			                $tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
                                        cargaInventario();
                                        $("#myModalPrint").modal('hide')
				},
				error: function (xhr, ajaxOptions, thrownError) {
                                        $("#myModalPrint").modal('hide')
					alert(xhr.status);
					alert(thrownError);
				}
			});
		   
			return false;
}	

function defineDatabase() {
          db = new Dexie("tpv");
          db.version(1).stores({
              productos: 'barcode,description',
              movimiento: 'id++'
          });
}

function addProductos(productos) {
  productos.forEach((producto) => {
    db.productos.put(producto).then(function() {
      return db.productos.get(producto.barcode);
    }).then(function(producto) {
       console.log("codigo barras " + producto.barcode + " descricion: " + producto.description);
    }).catch(function(error) {
        alert("opps " + error);
    });
  });

}


$(document).ready(function() {
        console.log("1..");
        defineDatabase();
        checkStatusInternet();
        console.log("2..");
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

                                field: 'ubicacion',
                                title: 'ubicacion'
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
					   $tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
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
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }) + '</div>';
						  }
			}, {
				field: 'total',
				sortable: true,
				title: 'Total',
				formatter: function(value, row, index) {
							return '<div align="right" data-field="' + this.field + '">' + Number(value).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }) + '</div>';
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
	 
        cargaInventario();
	
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
                                                ubicacion: $el.ubicacion,
						description: 'Item ' + $el.description,
                                                precioCompra: $el.precioCompra,
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
			$tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));

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
			$tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));

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
				$('.precioProductoLabel').text(Number(result.precioVenta).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
				ean = result;
				$("#myModal").modal('show')
			});
	  
			return false;
	});	

        $('#btnVentaConTicket').click(function() {
            VENTA_CON_TICKET = 1
            registrarVenta(VENTA_CON_TICKET)
        });	


        $('#btnVentaSinTicket').click(function() {
            VENTA_SIN_TICKET = 0
            registrarVenta(VENTA_SIN_TICKET)
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
                                precioCompra: ean.precioCompra,
				total: ean.precioVenta * 1
			}
		});	
		var data = $tableVenta.bootstrapTable('getData');
		total = calculaGranTotal(data);
		$tableVenta.find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
		$tableVenta.bootstrapTable('scrollTo', 'bottom');
		$("#myModal").modal('hide');
		evt.stopPropagation();
	});

        $("#btnClear").click(function() {
           $('#ventaTabla').bootstrapTable('removeAll');
        });
	
	$( "#btnCobrar" ).click(function() {
          var data = $tableVenta.bootstrapTable('getData');
	  total = calculaGranTotal(data);
          $('#totalLabel').text("Total : " + total);
          $("#myModalPrint").modal('show')
	});	

})
	
