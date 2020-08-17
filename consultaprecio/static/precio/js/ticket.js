
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
                        }, {
                            field: 'codigointerno',
                            title: '#Cod'
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

function requestMovimientoCount() {
  return Rx.Observable.fromPromise(db.movimientos.count())
}


function getProductoOnline (codigo) {
  return Rx.Observable.fromPromise(new Promise (function(resolve,reject) {
                $.ajax({
                      url : "/find_codigo/" + $.trim(codigo) + "/",
                      timeout: "4000",
                      error : function (err) {
                                 resolve(err);
                              },
                     success : function(result) {
                        resolve(result);
                     }
                });
         })); 
}

function getProductoOffline (codigo) {
  return Rx.Observable.fromPromise(db.productos.get($.trim(codigo)));
}

function getProductoByBarcode (codigo) {
   inline = true;
   if (inline)
     return getProductoOnline(codigo).catch (function (err) {
       return getProductoOffline(codigo); 
     }); //.OnErrorResumeNext(Rx.Observable.just({'description':'xxx', 'precio': 100 }));
     //return getProductoOnline(codigo).OnErrorResumeNext(getProductoOffline(codigo));
  return getProductoOffline(codigo); 
}

function on_line () {
   return new Promise(function(resolve, reject) {
                $.ajax({
                      url : "/on_line",
                      timeout: "2000",
                      error : function () {
                                 resolve({"on_line":false});
                              },
                     success : function(result) {
                        resolve(result);
                     }
                });

   });
}

		
function requestOnlineObservable() {
   return Rx.Observable.fromPromise(on_line())
}

function checkStatusInternet() {
  Rx.Observable.interval(5000).flatMap(requestOnlineObservable).subscribe(function(dato) {
    inline = dato.on_line;
    if (dato.on_line) {
      $("#status_online").css("color","#64dd17");
      $("#status_online2").css("color","#64dd17");
      sendMovOffline();  
    }else {
      $("#status_online").css("color","red");
      $("#status_online2").css("color","red");
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


function sendTicket (url, ticket) {

   ticket_promise  =  new Promise(function(resolve, reject) {
	            var jsonData = JSON.stringify(ticket);
		    $.ajax({
				type: 'POST', // Use POST with X-HTTP-Method-Override or a straight PUT if appropriate.
				dataType: 'json', // Set datatype - affects Accept header
				url: "/tickets/add", // A valid URL
				headers: {"X-HTTP-Method-Override": "PUT", "X-CSRFToken": $.cookie("csrftoken")}, // X-HTTP-Method-Override set to PUT.
				data: jsonData, // Some data e.g. Valid JSON as a string
				success: function (response) {
                                   resolve(ticket)
				},
				error: function (xhr, ajaxOptions, thrownError) {
                                   reject();
				}
			});
	});	  
 
   return Rx.Observable.fromPromise(ticket_promise);
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
                                        guardaTicketLocal(ticket);
				}
			});
		   
			return false;
}	

function defineDatabase() {
          db = new Dexie("tpv");
          db.version(1).stores({
              productos: 'barcode,description',
              movimientos: 'id++'
          });
}

function sendMovOffline() {
   if (envioEnProceso || inline == false)
      return;

   envioEnProceso = true;
   db.movimientos.toArray().then(function (tickets) {
       var totalMovsOffline = tickets.length;
       Rx.Observable.from(tickets).flatMap(function (ticket) {
          return sendTicket("",ticket);
       }).flatMap (function (ticket)  {
          return Rx.Observable.fromPromise(db.movimientos.delete(ticket.id));
       }).delay(1000).subscribe(function () {
          totalMovsOffline = totalMovsOffline - 1;
          paintUploadCount(totalMovsOffline);
       }, function (error) {
          envioEnProceso = false;
          alert("Error enviando ventas. Consulte al administrador");
       }, function () {
           envioEnProceso = false;
           console.log("Terminando de  enviar movimientos");
       }); 
   });

}


function paintUploadCount(contador) {
   $("#movsOffline").text(contador);
   if (contador == 0){
     setTimeout(function () {
      $("#divContador").css('visibility', 'hidden');
     },1500);
   }else {
      $("#divContador").css('visibility', 'visible');
   }
}


function guardaTicketLocal(ticket) {
   db.movimientos.put(ticket).then(function() {
      console.log("Producto id " + ticket.id);
      $('#ventaTabla').bootstrapTable('removeAll');
      total = 0;
      $("#ventaTabla").find("tfoot").find(".granTotal").text(Number(total).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
      requestMovimientoCount().subscribe(function(contador) {
         paintUploadCount(contador);
      });
      return db.movimientos.get(ticket.id); 
   }).then(function (ticket) {
      console.log("total : " + ticket.total);
      
   }).catch(function(error) {
      alert('No se logro guardar la venta: '+ error);
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
        defineDatabase();
        checkStatusInternet();

        requestMovimientoCount().subscribe(function(contador) {
          paintUploadCount(contador);
          //if (contador >0) {
          //  sendMovOffline();
          //}
        });

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
						//if (!/^[0-9]*$/.test(value)) {
					        //		return 'Ingrese una cantida correcta'
						//}
                                                var valid = !isNaN(value);
                                                if (!valid) {

                                                   return 'Ingrese una cantidad correcta'
                                                }
						var data = $('#ventaTabla').bootstrapTable('getData'),
							index = $(this).parents('tr').data('index');
						data[index].cantidad = parseFloat(value);
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
                        getProductoByBarcode(codigo).subscribe(function (result) {
				$('#descriptionProductoLabel').text(result.description);
				$('.precioProductoLabel').text(Number(result.precioVenta).toLocaleString('mx-MX', { style: 'currency', currency: 'MXN' }));
				ean = result;
				$("#myModal").modal({show:true, backdrop:'static', keyboard:false})
                                setTimeout(function() {
                                   $('#btnAdd').focus()
                                },300);

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


        $('#myModal').on('keypress',function(e) {
           if (e.which == 27) {
               $('#myModal').modal('hide')
               $('#codigobarras').val('')
               $('#codigobarras').focus()
           }
        })


        $('#myModal').on('keypress',function(e) {
           if (e.which == 27) {
               $('#myModal').modal('hide')
               $('#codigobarras').val('')
               $('#codigobarras').focus()
           }
        })


        $('#btnCancelModal').click(function() {
               $('#myModal').modal('hide')
               $('#codigobarras').val('')
               $('#codigobarras').focus()
        })

        $('#btnAdd').on('keypress',function(e) {
            if (e.which == 113 || e.which == 81) {  //tecla q y Q
               $('#myModal').modal('hide')
               $('#codigobarras').val('')
               $('#codigobarras').focus()
            }
            e.preventDefault()
        })


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
                $('#codigobarras').val('')
                $('#codigobarras').focus()
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
	
