/*
* jquery.tableutils
*
* Copyright (c) 2013 Kolge Pratik
*
* Licensed under MIT
* http://www.opensource.org/licenses/mit-license.php
* 
* http://docs.jquery.com/Plugins/Authoring
* jQuery authoring guidelines
*
* Launch  : June 2013 
* Version : 1.1.2
*/


/*
* The plug-in supports multiple tables on a single page. 
*/

(
	function( $ ) {
		
		// Holds the settings for all the tables being operated on. 
		var tableSettings = [];
		
		var settings = {

			// Temporary variable. 
			tableID: '',
			
			// Disables console msgs
			printLog: true,
			
			// Holds the information about all the columns on a table. 
			columns: [],
			
			// Options for fixing header. 
			fixHeaderOptions: { 
					required: false, 
					height: 200, 
				//	width: 600,					
					disableMessages: false,
					messages: [], 
					nextMessageIndex: 0,
					messageLoop: {},
					messageLoopInterval: 2000 
				},
				
			// Options for user controls. 
			buttons: {
					required: false
				},
				
			// Options for rowselect. 
			rowSelectOptions: {
					required: false,
					message: { type: 'rowSelect', message: '' }
				},
			
			// Options for filter table. 
			filterTableOptions: {
					required: false,
					customFilterType: false, 
					type: 'text', 
					activeFilters: [],
					fetchDelayTimeOut: 500,
					fetchDelayTimer: null, 
					message: { type: 'filterTable', message: '' }
				},
			
			// Options for mastercheckbox. 
			masterCheckBoxOptions: {
					required: false,
					columnIndex: 1,
					message: { type: 'masterCheckBox', message: '' }
				},
			
			// Options for sorting. 
			sortOptions: {
					required: false,
					customSortType: false, 
					type: 'alphanumeric', 
					sortingState: {},
					message: { type: 'sorting', message: '' }
				},
			
			// Options for pagination. 
			paginationOptions: { 
					availablePageSizes: [10, 20, 50, 100, 500, 1000], 
					currentPage: 1, 
					displayPagesCount: 5, 
					numberOfPageLinks: -1, 
					pageSize: 10,
					type: 'numeric', 
					serverSide: false, 
					columnIndex: 1,					
					pageMappings: [ 
						'-', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 
						'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 
						'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', 
						'3', '4', '5', '6', '7', '8', '9' 
					],
					preserveSelection: false, 
					previouslySelectedRecords: [], 
					resetPreviousSelection: false, 
					dynamicTypeChange: false,
					message: { type: 'pagination', message: '' }				
				},
			
			// Options for new record insertion.
			newRowOptions: {
					message: { type: 'newRecord', message: '' }
				},
				
			// Options for record deletion. 
			deleteRecordsOptions: {
					message: { type: 'deleteRecords', message: '' }
				}, 
			
			// Options for record editing. 
			editRecordOptions: {
					message: { type: 'editRecord', message: '' }
				},
			
			// Holds the context root of the application. 
			contextRoot: '',
			
			// The resources directory that holds the resources required for this plug-in. 
			resourcesDir: '/images', 
			
			// Page Size. 
			pageSize: 5,
			
			// Column number of the mastercheckBox column. 
			masterCheckBoxIndex: -1,
			
			// Holds the number of links present. 
			numberOfPageLinks: 1,
			
			// How many pages to display at once. 
			displayPagesCount: 5,
			
			// The current page number. 
			currentPage: 1, 
			
			// Is pagination required ? 
			paginationRequired: false,
			
			// Fix the header ? 
			fixedHeaderTable: '',
			
			// Height of the table. 
			height: 300,
			
			// Width of the table ( and of the corresponding containers. ). 
			globalWidth: -1,
			
			newRowOptions: {},
			
			// Update URL. 
			updateURL: '',
			
			newRow: {},
			
			// The available page sizes. 
			availablePageSizes: [5, 10, 20, 50, 100]
		};
		
		var defaultSettings = $.extend(true, {}, settings);
		
		/**
		* This variable holds all methods supported by this plugin. 
		*/
		var methods = {
			
			/**
			* Initializes the options and sets up some basic things. 
			*/
			init: function(options) {
				
				logOnConsole('Init function.');
				
				startTimer('init');
				
				if(this[0] != null) {
				
					var tableID = $(this).attr('id');							
					
					loadTableSettings(tableID);
					
					$.extend(settings, options);
					
					settings.contextRoot = methods.getContextRoot();
					
					// Get fix header options. 
					if(options.fixHeader) {
						if(options.fixHeader === true) {
							$.extend(settings.fixHeaderOptions, { required: true });
						} else {
							$.extend(settings.fixHeaderOptions, { required: true }, options.fixHeader);
						}					
					}
					
					// Add user controls. 
					if(options.buttons) {
						if(options.buttons === true) {
							$.extend(settings.buttons, { required: true });
						} else {
							$.extend(settings.buttons, { required: true }, options.buttons);
						}	
					}
					
					// Get rowselect options. 
					if(options.rowSelect) {
						if(options.rowSelect === true) {
							$.extend(settings.rowSelectOptions, { required: true });
						} else {
							$.extend(settings.rowSelectOptions, { required: true }, options.rowSelect);
						}
					}	
					
					// Get filter options. 
					if(options.filter != null) {
						logOnConsole('filtering for: ' + tableID);
						if(options.filter === true) {
							$.extend(settings.filterTableOptions, { required: true });
						} else {
							$.extend(settings.filterTableOptions, { required: true }, options.filter);
						}
					}							
					
					// Get sorting options. 
					if(options.sort) {	
						if(options.sort === true) {
							$.extend(settings.sortOptions, { required: true });
						} else {
							$.extend(settings.sortOptions, { required: true }, options.sort);
						}	
					}
					
					// Get pagination options. 
					if(options.paginate) {	
						if(options.paginate === true) {
							$.extend(settings.paginationOptions, { required: true });
						} else {
							$.extend(settings.paginationOptions, { required: true }, options.paginate);
						}
					}
					
					// Get mastercheckBox options. 
					if(options.masterCheckBox) {
						if(options.masterCheckBox === true) { 
							$.extend(settings.masterCheckBoxOptions, { required: true });
						} else {
							$.extend(settings.masterCheckBoxOptions, { required: true }, options.masterCheckBox);
						}
						
					}
					
					// Get new record options. 
					if(options.newRow) {	
						if(options.newRow === true) {
							$.extend(settings.newRowOptions, { required: true });
						} else {
							$.extend(settings.newRowOptions, { required: true }, options.newRow);
						}
					}
					
					// Get delete records options. 
					if(options.deleteRecords) {	
						if(options.deleteRecords === true) {
							$.extend(settings.deleteRecordsOptions, { required: true });
						} else {
							$.extend(settings.deleteRecordsOptions, { required: true }, options.deleteRecords);
						}
					}
					
					// Get edit record options. 
					if(options.editRow) {
						if(options.editRow === true) {
							$.extend(settings.editRecordOptions, { required: true });
						} else {
							$.extend(settings.editRecordOptions, { required: true }, options.editRow);
						}	
					}

					// Save settings for this table.  
					saveTableSettings(tableID);
					
					// Load settings for this table.  
					loadTableSettings(tableID);
					
					// Fix the header. 
					if(options.fixHeader) {
						methods.fixHeader(tableID);
					}
					
					// Add user controls. 
					if(options.buttons) {
						methods.addButtons(tableID);
					}
					
					// Row select. 
					if(options.rowSelect) {
						methods.rowSelect(tableID);
					}
					
					// Sorting. 
					if(options.sort) {
						methods.sort(tableID);
					}
					
					// Filtering. 
					if(options.filter) {
						methods.filterTable(tableID);					
					}
					
					// Mastercheckbox. 
					methods.masterCheckBox(tableID);
					
					// Pagination. 
					if(options.paginate) {
						methods.paginate(tableID);
					}
					
					// New Record. 
					if(options.newRow) {
						methods.newRecordInsertion(tableID);
					}
					
					// Edit Record. 
					if(options.editRow) {
						methods.editRecord(tableID);
					}
					
					// Delete Record. 
					if(options.deleteRecords) {
						methods.deleteRecords(tableID);
					}
					
					// Clean Up. 
					methods.finalSteps(tableID);					
					
				} else {
					logOnConsole('No table found.');
				}
				
				stopTimer('init');
			},
			
			
			/**
			* Generates a table dynamically. 
			*/
			buildDynamicTable: function(options) {
				var $table = $(this);
				
				var columns = new Array();
				
				// Make an ajax call to fetch the page. 
				$.ajax({
				
					url: options.loadURL, 
					
					data: options.params,	
					
					beforeSend: function() {	
						startTimer('buildDynamicTable ajax call');
					}, 	
					
					success: function(data) {
						stopTimer('buildDynamicTable ajax call');
						
						startTimer('buildDynamicTable process fetched records');
						
						var numOfColumns = data.columns.length;
						
						/* Create the column object. */
						var column = null;
						for(var i=0; i<numOfColumns; i++) {
							var c = data.columns[i];
							
							if(options.ignoreColumns) {
								if($.inArray(c.name, options.ignoreColumns) === -1) {
									column = new Object();
									column.label = c.name.split('_').join(' ');
									column.name = Number(i) + 1;
									column.value = c.name;
									column.type = c.type;
									
									columns.push(column);
								}
							} else {
								column = new Object();
								column.label = c.name.split('_').join(' ');
								column.name = Number(i) + 1;
								column.value = c.name;
								column.type = c.type;
																
								columns.push(column);
							}
						}
						
						/* Generate the table headers using the columns array. */						
						$table.append($('<thead></thead>'));
						var $tr = $('<tr></tr>');
						for(var i=0; i<columns.length; i++) {
							$tr.append($('<th>' + columns[i].label + '</th>'));
						}	
						$table.find('thead').append($tr);
						
						$table.append($('<tbody></tbody>'));
						
						stopTimer('buildDynamicTable process fetched records');
						
						/* Call the User's handler. */
						options.success(columns);
					}, 

					error: function(xhr, textStatus, error) {
						alert('The following error occurred while Building the table: ' + getAjaxErrorDescription(xhr, textStatus, error));
					},
					
					complete: function() {					
						if(options.complete) {
							options.complete(columns);
						}
					},
					
					dataType: 'json',
					
					cache: false
				});	
			},
			
			
			/**
			* Perform final cleanup steps. 
			*/ 
			finalSteps: function(tableID) {
				var $mainTable = $('#' + tableID);
				
				$mainTable.on('hideTable', function() {
					$('#outermostDiv_' + tableID).hide();
				});
				
				$mainTable.on('showTable', function() {
					$('#outermostDiv_' + tableID).show();
				});
				
				addProgessBar(tableID);
				
				hideProgess(tableID);
				
				applyTableStyling(tableID);
			},
			
			
			/**
			 * Returns the Context Root for the Application. 
			 */
			getContextRoot: function() {
				var basePath = window.location.pathname.split('/')[1];
				
				// Build the context path. 
				var root = window.location.protocol + "//" + window.location.host + "/" + basePath;
				
				return root;
			}, 
			
			
			/**
			 * Fixes the header for the table. 
			 *  
			 */			
			fixHeader: function(tableID) {
				logOnConsole('Fixing header for: ' + tableID);	
				
				startTimer('fixHeader');
				
				// Load table settings. 
				loadTableSettings(tableID);
				
				// This is the ID of the Table that contains the Fixed Header. 
				settings.fixHeaderOptions.fixedHeaderTable = 'fixedHeader_' + tableID;
				
				startTimer('cloning table');				
				var $mainTable = $('#' + tableID);
				// Clone the current table. 
				var $this = $mainTable;//.clone();
				stopTimer('cloning table');
				
				// The Main Container DIV. 
				var $outerMostDiv = $('<div></div>').attr('id', 'outermostDiv_' + tableID).addClass('tableUtils_mainContainer');
				
				// The Main table container DIV. 
				var $innerDiv = $('<div style="height: ' + settings.fixHeaderOptions.height + 'px; width: ' + settings.fixHeaderOptions.width + 'px;"></div>').attr('id', 'outerDiv_' + tableID).addClass('outer');
				
				// The Header table container DIV. 
				var $fixHeaderDiv = $('<div id="fixedTableWrapper_' + tableID + '"></div>').addClass('header');
				
				// The Main table container DIV. 
				var $mainTableDiv = $('<div id="mainTableWrapper_' + tableID + '"></div>').addClass('body');
								
				startTimer('cloning header table');
				// The fixed header table. 
				var $clonedTable = $($this[0].cloneNode()).attr('id', settings.fixHeaderOptions.fixedHeaderTable);
				$clonedTable.append($this.find('thead').clone());
				stopTimer('cloning header table');
				
				// Width of the table, that will be used by its containers. 
				settings.fixHeaderOptions.tableWidth = settings.fixHeaderOptions.width;
				
				// Apply Styling to the table if not already present. 								
				$this.addClass('tableUtils_table');
				$clonedTable.addClass('tableUtils_table');					 
				
				var $tempTable = $($this[0].cloneNode());
				$tempTable.append($('<tbody></tbody>'));
				
				// Append the Fixed header table to the Header Container DIV and the Main table to the Body Container DIV. 
				$fixHeaderDiv.append($clonedTable);				
				$mainTableDiv.append($tempTable);
				
				startTimer('removing headers and body');
				fastEmpty($this.find('thead'));
				stopTimer('removing headers and body');				
				
				// Append the fix header and body containers to the Main Table Container DIV. 
				$innerDiv.append($fixHeaderDiv);
				$innerDiv.append($mainTableDiv);
				
				// Append the main table container to the Main Container DIV. 
				$outerMostDiv.append($innerDiv);
								
				// The General Info and Additional Controls DIV (Same width as the main table's width.).
				var $generalInfoDiv = $('<div></div>').attr('id', 'generalInfo_' + tableID).addClass('tableUtils_generalInfoDiv').width(settings.fixHeaderOptions.width);
				
				// The table that will hold the controls and the messages. 
				var $generalInfoTable = $('<table style="width: 100%;"></table>').attr('id', 'generalInfoTable_' + tableID);
				
				// User controls. 
				var $userControlsContent = $('<td></td>').attr('id', 'userControls_' + tableID).addClass('tableUtils_userControls');
				
				// The additional controls area. 
				var $additionalControlsContent = $('<td></td>').attr('id', 'additionalControls_' + tableID).addClass('tableUtils_controls');
				
				// The messages area. 
				var $messageContent = $('<td></td>').attr('id', 'generalMessage_' + tableID).addClass('tableUtils_messages').hide();				
				
				// Append the areas to the General Info Container table and append the table to the Container DIV. 				
				$generalInfoTable.append('<tr class="tableUtils_controls_container"></tr>');
				$generalInfoTable.append('<tr class="tableUtils_messages_container"></tr>');
				$generalInfoTable.find('tr.tableUtils_controls_container').append($userControlsContent);
				$generalInfoTable.find('tr.tableUtils_controls_container').append($additionalControlsContent);
				$generalInfoTable.find('tr.tableUtils_messages_container').append($messageContent);				
				$generalInfoDiv.append($generalInfoTable);			

				// Prepend the General Info and Additional Controls DIV to the Main Container DIV. 
				$outerMostDiv.prepend($generalInfoDiv);
				
				
				// This is the ID of the Cell that contains the Messages. 
				settings.fixHeaderOptions.messagesArea = 'generalMessage_' + tableID;
				
				
				// Hide the Messages area if messages are disabled. 
				if(settings.disableMessages === true) {
					settings.fixHeaderOptions.disableMessages = true;
				} else {				
					// Create the messages loop. 
					settings.fixHeaderOptions.messageLoop = setInterval( function() {
							updateMessages(tableID);
						}, settings.fixHeaderOptions.messageLoopInterval );
				}
				
				startTimer('relacing tables');
				// Replace the main table with the Main Container DIV. 
				//$mainTable.replaceWith($outerMostDiv);
				fastReplace($mainTable[0], $outerMostDiv[0]);
				
				var $newTable = $.id(tableID);
				var allTableRows = backupRows($this);
				restoreTable(allTableRows, $newTable[0]);
				
				$this = $newTable;
				
				stopTimer('relacing tables');

				// Horizontally scroll the Header DIV alongwith the BODY DIV. 
				$mainTableDiv.scroll(function (e) {				  
					$fixHeaderDiv.css({
						left: -$mainTableDiv[0].scrollLeft + 'px'
					});
				});


				// Create a handler for the event when the main table's header is updated (i.e. when the Header table's DOM is manipulated.). This is just to adjust the 'top' property of the Main Table Container DIV. 								
				$this.on('tableHeaderUpdated', function() {
					// The table's ID. 
					var tableID = this.getAttribute('id');
					
					// Load table settings. 
					loadTableSettings(tableID);
					
					// Adjust the position (top) and height of the Main Table Container. 
					var fixHeaderWrapperHeight = $('#' + settings.fixHeaderOptions.fixedHeaderTable).height();
					$('#mainTableWrapper_' + tableID).css('top', fixHeaderWrapperHeight + 'px').height((settings.fixHeaderOptions.height - fixHeaderWrapperHeight - 5) + 'px');
					
					logOnConsole('Table Header was Updated.');
				});
				
				
				// Create a handler for the event when the main table itself is updated (i.e. is when the table is emptied and new rows are added.). 
				$this.on('tableUpdated', function() {
					// The table object. 
					var $this = $(this);
					
					// The table's ID. 
					var tableID = this.id;
										
					logOnConsole('Updating table: ' + tableID);
					
					// Load table settings. 
					loadTableSettings(tableID);
					
					// Rowselect. 
					if(settings.rowSelectOptions.required === true) {
						logOnConsole('Updating rowSelect');
						methods.rowSelect(tableID);
					}
					
					// Do nothing on sort for now. Might be needed in the future. 
					if(settings.sortOptions.required === true) {
						; 
					}
					
					// Filter table. 
					if(settings.filterTableOptions.required === true) {
						logOnConsole('Updating filter');
						fastAddClass($this.find('tbody tr').get(), 'filteredRow');
					}
					
					logOnConsole('Updating mastercheckbox');
					
					if(settings.masterCheckBoxOptions.required === true) {
						$('#' + settings.masterCheckBoxOptions.masterCheckBox).attr('checked', false);
					}
					
					// Get the Children checkboxes. 
					var $childCheckBoxes = $(this).find('tbody tr td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ') input:checkbox');
			
					// Add 'change' event handler to the checkbox in each row of the table.
					$childCheckBoxes.each(function() {						
						// Add the 'change' handler to the checkbox. 
						$(this).on('change', function() {
							var $this = $(this);
							if($this.is(':checked')) {
								$this.closest('tr').addClass('tableUtils_selectedRow');
							} else {
								$this.closest('tr').removeClass('tableUtils_selectedRow');
							}								
							childCheckBoxToggledHandler(tableID, this);						
						});					
					});
					
					// Pagination. 
					if(settings.paginationOptions.required === true) {
						logOnConsole('Updating pagination');
						//fastAddClass($this.find('tbody tr').get(), 'currentPageRow');
						settings.paginationOptions.linksCreated = false;
						resetToFirstPage(tableID);						
					}
				});
				
				
				// Create a handler for the event when the main table itself is updated (i.e. is when the table is emptied and new rows are added.). 
				$this.on('freeze', function() {				
					var tableID = $(this).attr('id');
					
					loadTableSettings(tableID);
					
					$('#' + settings.fixHeaderOptions.fixedHeaderTable).attr('disabled', true);
					$('#' + tableID).attr('disabled', true);
					
					if(settings.paginationOptions.required === true) {
						$('paginationDiv_' + tableID).attr('disabled', true);
					} 
				});
				
				
				// Create a handler for the event when the main table itself is updated (i.e. is when the table is emptied and new rows are added.). 
				$this.on('unFreeze', function() {
					var tableID = $(this).attr('id');
					
					loadTableSettings(tableID);
					
					$('#' + settings.fixHeaderOptions.fixedHeaderTable).attr('disabled', false);
					$('#' + tableID).attr('disabled', false); 
					
					if(settings.paginationOptions.required === true) {
						$('paginationDiv_' + tableID).attr('disabled', false);
					} 
				});
				
				
				// Trigger 'tableHeaderUpdated' event to update the Body Container's position. 
				$this.trigger('tableHeaderUpdated');
				
				// Save table settings. 
				saveTableSettings(tableID); 
								
				stopTimer('fixHeader');
			},
			
			
			/*
			* Add user controls to the table. 
			*/
			addButtons: function(tableID) {
				logOnConsole('Adding user controls for: ' + tableID);	
				
				startTimer('add buttons');
				
				// Load table settings. 
				loadTableSettings(tableID);
				
				var $userControlsArea = $('#userControls_' + tableID);
				
				// Add each button to the additional controls area. 
				$.each(settings.buttons, function(index, userButton) {
					if(userButton.id) {
						// Create a new button. 
						var $newButton = $('<button type="button"></button>').attr('id', userButton.id);

						// If the user wants custom class, then let him have it. 
						if(userButton.buttonClass) {
							$newButton.addClass(userButton.buttonClass);
						} else {
							// Else style the button according to the plugin. 
							$newButton.addClass('tableUtils_imageButton');
						}
						
						// If styling is required. 
						if(userButton.style) {
							$newButton.css(userButton.style);
						}
						
						// If the user wants to display text on the button, then assign the text. 
						if(userButton.text) {
							$newButton.html(userButton.text);
						} else {
							// Else if the user has given icon path, use the icon. 
							if(userButton.icon) {
								$newButton.append($('<img>').attr('src', settings.contextRoot + userButton.icon));
							} else {
								// Else use the default icon. 
								$newButton.append($('<img>').attr('src', settings.contextRoot + settings.resourcesDir + '/edit1.png'));
							}
						}
						
						// Show tooltip if any. 
						if(userButton.tooltip) {
							$newButton.attr('title', userButton.tooltip);
						} 
						
						// Attach the 'click' event handler for the button. 
						$newButton.on('click', userButton.callBack); 	

						// Append the button to the user controls area. 
						$userControlsArea.append($newButton);						
					}
				});	

				stopTimer('add buttons');				
			},
			
			
			/**
			 * Generate filters for the table. 
			 * 
			 */	
			filterTable: function(tableID) {
				logOnConsole('Filtering for: ' + tableID);	
				
				startTimer('filter');
				
				// Load table settings. 
				loadTableSettings(tableID);
				
				// The table object. 
				var $mainTable = $('#' + tableID);
				
				// The header table object. 
				var $headerTable = $('#' + settings.fixHeaderOptions.fixedHeaderTable);
				
				// The list of table headers. 
				var $headers = $headerTable.find('thead tr th');
				
				// If the filtering option 'type' is specified, then generate custom filters. 
				if($.isArray(settings.filterTableOptions.type)) {
					// Generate custom filters. 
					settings.filterTableOptions.customFilterType = true;
					
					// Get all the types of filters for each column. 
					var columnTypes = settings.filterTableOptions.type;
					
					// Generate the filters for columns. 
					$headers.each(function(index) {	
						// The Filter Element that will be added to the header column. 
						var $filterElement = $('');	
						
						// If the option for this column is an Object 
						if($.isPlainObject(columnTypes[index])) { 
							// If its a 'select' filter (Drop-down) 
							if(columnTypes[index].type === 'select') { 
								// Filter element is a Drop-down list. Add an empty option to the filter. 
								$filterElement = $('<select style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_selectFilter');
								$filterElement.append($('<option>', {
									text: '',
									value: ''
								})); 
								
								// The array that will hold the options for the filter. 
								var selectOptions = new Array();

								// If 'generateOptions' i.e. if we should generate values for the filter from the table data 
								if(columnTypes[index].options.generateOptions) {
									// Holds data from each row for the current header/column. 
									var $allValuesForColumn = $mainTable.find('tbody tr td:nth-child(' + (index + 1) + ')');
																								
									// For each column data, add the value to the filter Drop-down if it is not already present. 
									$allValuesForColumn.each(function(index) {
										// The column data. 
										var columnValue = $.trim($(this).text());
										
										// Remove value from the Drop-down options if already present. 
										selectOptions = $.grep(selectOptions, function(optionObject, index) {
											return ( optionObject.value === columnValue );
										}, true)
										
										// Add the new value to the Drop-down options. 
										selectOptions.push({
											name: columnValue,
											value: columnValue
										});
									});
									
									var optionsSortFunction = null;
									if(columnTypes[index].filterType === 'numeric') {
										optionsSortFunction = function(obj1, obj2) {
											return (obj1.value - obj2.value);
										};
									} else {
										optionsSortFunction = function(obj1, obj2) {
											return ((obj1.value === obj2.value) ? 0 : (obj1.value > obj2.value ? 1 : -1));
										};
									}
									
									selectOptions.sort(optionsSortFunction);
								} else {								
									// Else, add the values specified in the 'selectOptions' property to the Drop-down list. 
									selectOptions = columnTypes[index].options.selectOptions;									
								}
								
								// Add each filter value to the Drop-down filter. 
								$.each(selectOptions, function(index, option) {
									$filterElement.append($('<option>', {
										text: option.name,
										value: option.value
									}));
								});
									
								// Bind 'change' event handler to the Drop-down filter. 
								$filterElement.on('change', function() {
									var filterValue = $(this).find('option:selected').val();									
									updateFilter(tableID, index, filterValue, columnTypes[index].filterType);									
								});
							} else if(columnTypes[index].type === 'dateFilter') {	
								// Else if its a 'Date' filter, create a text-box for the filter. 							
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_dateFilter');
																
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'dateFilter');
								});
								
								// We use the jQuery Ui's DatePicker. Configure the DatePicker. 
								var opts = { onSelect: function(dateText) {									
									updateFilter(tableID, index, dateText, 'dateFilter');
								}};
								
								// If the user has supplied his own options for the DatePicker, use them. 
								$.extend(opts, columnTypes[index].options);		
								
								// Initialize the DatePicker. 
								$filterElement.datepicker(opts);								
							} else if(columnTypes[index].type === 'minDateFilter') {	
								// Else if its a 'Date' filter, create a text-box for the filter. 							
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_dateFilter');
																
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'minDateFilter');
								});
								
								// We use the jQuery Ui's DatePicker. Configure the DatePicker. 
								var opts = { onSelect: function(dateText) {									
									updateFilter(tableID, index, dateText, 'minDateFilter');
								}};
								
								// If the user has supplied his own options for the DatePicker, use them. 
								$.extend(opts, columnTypes[index].options);		
								
								// Initialize the DatePicker. 
								$filterElement.datepicker(opts);								
							} else if(columnTypes[index].type === 'maxDateFilter') {	
								// Else if its a 'Date' filter, create a text-box for the filter. 							
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_dateFilter');
																
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'maxDateFilter');
								});
								
								// We use the jQuery Ui's DatePicker. Configure the DatePicker. 
								var opts = { onSelect: function(dateText) {									
									updateFilter(tableID, index, dateText, 'maxDateFilter');
								}};
								
								// If the user has supplied his own options for the DatePicker, use them. 
								$.extend(opts, columnTypes[index].options);		
								
								// Initialize the DatePicker. 
								$filterElement.datepicker(opts);								
							}
						} else {
							// Else if the filter is not specified by an Object 
							if(columnTypes[index] === 'noFilter') {
								// Do not perform filtering on this column. 
								;
							} else if(columnTypes[index] === 'text') {
								// It's a simple text filter. Create a text-box for this filter. 
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_textFilter');
								
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'text');
								});
							} else if(columnTypes[index] === 'numeric') {
								// It's a simple text filter. Create a text-box for this filter. 
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_textFilter');
								
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'numeric');
								});
							} else if(columnTypes[index] === 'checkbox') {
								// It's a checkbox filter. Create a checkbox for this filter. 
								$filterElement = $('<input type="checkbox">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_checkboxFilter');
								
								// Bind 'change' event handler to the filter. 
								$filterElement.on('change', function() {
									updateFilter(tableID, index, $filterElement.is(':checked'), 'checkbox');
								});
							} else if(columnTypes[index] === 'dateFilter') {
								// Else if its a 'Date' filter, create a text-box for the filter. 
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_dateFilter');
								
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'dateFilter');
								});
								
								// We use the jQuery Ui's DatePicker. Configure the DatePicker. 
								var opts = { onSelect: function(dateText) {									
									updateFilter(tableID, index, dateText, 'dateFilter');
								}};
								
								// Initialize the DatePicker. 
								$filterElement.datepicker(opts);								
							} else if(columnTypes[index] === 'minDateFilter') {
								// Else if its a 'Date' filter, create a text-box for the filter. 
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_dateFilter');
								
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'minDateFilter');
								});
								
								// We use the jQuery Ui's DatePicker. Configure the DatePicker. 
								var opts = { onSelect: function(dateText) {									
									updateFilter(tableID, index, dateText, 'minDateFilter');
								}};
								
								// Initialize the DatePicker. 
								$filterElement.datepicker(opts);								
							} else if(columnTypes[index] === 'maxDateFilter') {
								// Else if its a 'Date' filter, create a text-box for the filter. 
								$filterElement = $('<input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_dateFilter');
								
								// Bind 'keyup' event handler to the filter. 
								$filterElement.on('keyup', function() {
									updateFilter(tableID, index, $(this).val(), 'maxDateFilter');
								});
								
								// We use the jQuery Ui's DatePicker. Configure the DatePicker. 
								var opts = { onSelect: function(dateText) {									
									updateFilter(tableID, index, dateText, 'maxDateFilter');
								}};
								
								// Initialize the DatePicker. 
								$filterElement.datepicker(opts);								
							}
						}
						
						// Append the '$filterElement' which contains a filter for the current header. 
						$(this).append($('<br>').add($filterElement));						
					});
				} else {
					/* If not type is specified, then we assume its a text filter for each header. */
				
					// The Filter Element that will be added to the header column. 
					var $filterElement = $('');
					
					// For each header 
					$headers.each(function(index) {						
						// Create a text-box for the filter. 
						$filterElement = $('<br><input type="text" style="width: 100%;">').attr('id', 'filter_' + tableID + '_' + index).addClass('tableUtils_textFilter');	
						
						var filterType = 'text';
						if(settings.paginationOptions.required && settings.paginationOptions.useDynamicData) {
							filterType = getColumnTypeForDB(settings.columns[index].type);
							if(filterType === 'alphanumeric') {
								filterType = 'text';
							}
						} 
						
						// Bind 'keyup' event handler to the filter. 						
						$filterElement.on('keyup', function() {
							updateFilter(tableID, index, $(this).val(), filterType);
						});
						
						// Append the '$filterElement' which contains a filter for the current header. 
						$(this).append($filterElement);					
					});
				}
				
				// Initially, add 'filteredRow' class to each row of the table. Each row that matches the active filters will have a 'filteredRow' class. 
				// The same class gets removed from the unmatched rows. 
				$mainTable.find('tbody tr').addClass('filteredRow');
				
				// Now, since we have added new elements to the header table, its height has changed. 
				// So we trigger the 'tableHeaderUpdated' event for this table, which updates the position of the Main Table Container DIV. 
				$mainTable.trigger('tableHeaderUpdated');
				
				// Save table settigns. 
				saveTableSettings(tableID);		

				stopTimer('filter');				
			}, 
			
			
			/**
			 * Create a mastercheckBox for the table. 
			 * 
			 */
			masterCheckBox: function(tableID) {
				startTimer('masterckbox');
				
				logOnConsole('Mastercheckbox for: ' + tableID);
				
				// Load table settigns. 
				loadTableSettings(tableID);					
				
				// The table object. 
				var $mainTable = $('#' + tableID);
				
				// The header table object. 
				var $headerTable = $('#' + settings.fixHeaderOptions.fixedHeaderTable);
				
				settings.masterCheckBoxOptions.columnIndex = (settings.masterCheckBoxOptions.columnIndex) ? settings.masterCheckBoxOptions.columnIndex : ((settings.rowSelectOptions.columnIndex) ? settings.rowSelectOptions.columnIndex : ((settings.paginationOptions.selectionColumnIndex) ? settings.paginationOptions.selectionColumnIndex : 1));
				
				// The column where we want to add the mastercheckBox. 
				var masterCheckBoxColumnNumber = settings.masterCheckBoxOptions.columnIndex;
				
				// Generate a jQuery Selector for selecting the eligible table rows from the main table. 
				var eligibleRowsSelector = 'tbody tr';
				if(settings.filterTableOptions.required === true) {
					eligibleRowsSelector += '.filteredRow';
				}
				
				if(settings.paginationOptions.required === true) {
					eligibleRowsSelector += '.currentPageRow';
				}
				
				settings.masterCheckBoxOptions.eligibleRowsSelector = eligibleRowsSelector;				
				
				if(settings.masterCheckBoxOptions.required) {
					// This is the ID of the mastercheckBox.  
					settings.masterCheckBoxOptions.masterCheckBox = 'masterCheckBox_' + tableID;
				
					// The header where the mastercheckBox will be appended. 
					var $masterCheckBoxCell = $headerTable.find('thead tr th:nth-child(' + masterCheckBoxColumnNumber + ')').empty();	
				
					// The mastercheckBox. 
					var $masterCheckBox = $('<input type="checkbox">').attr('id', settings.masterCheckBoxOptions.masterCheckBox).addClass('tableUtils_masterCheckBoxCell');

					// Bind 'change' event handler to the mastercheckBox. 
					$masterCheckBox.on('change', function() {
						toggleChildrenCheckBoxes(tableID, $(this).is(':checked'));
					});				
					
					// Append the mastercheckBox to the mastercheckBox header. 
					$masterCheckBoxCell.append($masterCheckBox);				
				}
				
				// Get the checkboxes in this column from all the rows of the table. 
				var $childCheckBoxes = $mainTable.find('tbody tr td:nth-child(' + masterCheckBoxColumnNumber + ') input:checkbox');
				
				// Bind the 'change' event to each of these checkboxes. 
				$childCheckBoxes.each(function() {
					var $this = $(this);
					$this.on('change', function() {
						var $this = $(this);
						if($this.is(':checked')) {
							$this.closest('tr').addClass('tableUtils_selectedRow');
						} else {
							$this.closest('tr').removeClass('tableUtils_selectedRow');
						}
						childCheckBoxToggledHandler(tableID, this);						
					});					
				});	
				
				if(settings.paginationOptions.required === true) { }
				
				// Save table settings. 
				saveTableSettings(tableID);	
				
				stopTimer('masterckbox');
			}, 
						
			
			/**
			 * Make the table columns sortable.  
			 *			 
			 */
			sort: function(tableID) {
			
				startTimer('sort');
			
				logOnConsole('Sorting for: ' + tableID);	
			
				// Load table settigns. 
				loadTableSettings(tableID);
				
				// The table object. 
				var $mainTable = $('#' + tableID);
				
				// The header table object. 
				var $headerTable = $('#' + settings.fixHeaderOptions.fixedHeaderTable);
				
				// The headers in the header table. 
				var $headers = $headerTable.find('thead tr th');
				
				// The context root of the Application. 
				var cntxRoot = settings.contextRoot; 			
				
				// Generate a jQuery Selector for selecting the eligible table rows from the main table. 
				var eligibleRowsSelector = 'tbody tr';
				if(settings.filterTableOptions.required === true) {
					eligibleRowsSelector += '.filteredRow';
				}
				
				settings.sortOptions.eligibleRowsSelector = eligibleRowsSelector;
				
				// If the 'type' option is an Array 
				if($.isArray(settings.sortOptions.type)) {
					// We have custom sorting on the table headers. 
					settings.sortOptions.customSortType = true;
					
					// Holds the sorting type for each header of the table. 
					var sortTypes = settings.sortOptions.type;
					
					// For each header 
					$headers.each(function(index) {	
						// Holds the current header. 
						var $this = $(this);
						
						// The content of the header (the text in the header column.).
						var headerName = $.trim($this.text());
						
						// The sorting link to be added to this header. 
						var $sortElement = $('<a href="#">' + headerName + '</a>').attr('id', 'sort_' + tableID + '_'+ index).addClass('tableUtils_sortLink');						
						
						// Bind 'click' event handler to the sorting link for this header depending on its sort type. 
						if(typeof sortTypes[index] === 'function') {
							logOnConsole('Custom sorting');
							$sortElement.on('click', function() {
								updateSortInfo(tableID, index, 'alphanumeric', sortTypes[index]);
								return false;
							});
						} else {
							if(sortTypes[index] === 'noSort') {
								$sortElement = $('<span>' + headerName + '</span>');
							} else if(sortTypes[index] === 'numeric') {							
								$sortElement.on('click', function() {
									updateSortInfo(tableID, index, 'numeric');
									return false;
								});
							} else if(sortTypes[index] === 'float') {
								$sortElement.on('click', function() {
									updateSortInfo(tableID, index, 'float');
									return false;
								});
							} else if(sortTypes[index] === 'alphanumeric') {
								$sortElement.on('click', function() {
									updateSortInfo(tableID, index, 'alphanumeric');
									return false;
								});								
							}		
						}
						
						// Remove any existing content from the header column and append the sorting link to the header column. 
						$this.empty().append($sortElement);
					});
				} else {
					/* If the 'type' option is not an array, we assume alphanumeric sorting on each header. */
					
					// The sorting link to be added to the header. 
					var $sortElement = $('');
					
					// For each header 
					$headers.each(function(index) {
						// Holds the current header. 
						var $this = $(this);
						
						// The content of the header (the text in the header column.).
						var headerName = $.trim($this.text());
						
						// Create the sorting link. 
						$sortElement = $('<a href="#">' + headerName + '</a>').attr('id', 'sort_' + tableID + '_'+ index).addClass('tableUtils_sortLink');						
						
						var columnType = 'alphanumeric';
						if(settings.paginationOptions.required && settings.paginationOptions.useDynamicData) {
							columnType = getColumnTypeForDB(settings.columns[index].type);
						} 
						logOnConsole('sorting columnType: ' + columnType);
						
						// Bind 'click' event handler to the sorting link for this header. 
						$sortElement.on('click', function() {
							updateSortInfo(tableID, index, columnType);
							return false;
						});
						
						// Remove any existing content from the header column and append the sorting link to the header column. 
						$this.empty().append($sortElement);
					});					
				}				
				
				// Now, since we have added new elements to the header table, its height has changed. 
				// So we trigger the 'tableHeaderUpdated' event for this table, which updates the position of the Main Table Container DIV.  
				$mainTable.trigger('tableHeaderUpdated');
				
				// Save table settings. 
				saveTableSettings(tableID);	
				
				stopTimer('sort');
			}, 
			
									
			/**
			 * Make the table rows as rowSelectors.  
			 *
			 * Options: 
			 *    - columnIndex: The column in which the checkbox that selects a row is present. 
			 *
			 */
			rowSelect: function(tableID) {
				
				startTimer('rowSelect');
				
				// Load table settigns. 
				loadTableSettings(tableID);
				
				// The table object. 
				var mainTable = document.getElementById(tableID);
				
				var tableRowsDOM = mainTable.rows;
				
				// The index of the column in which the selector checkbox is present. 
				var checkBoxColumn = settings.rowSelectOptions.columnIndex;
				
				for(var i=0; i<tableRowsDOM.length; i++) {
				//$tableRows.each(function(index) {
					// The current row. 
					var $this = $(tableRowsDOM[i]);
					
					// Add 'tableUtils_rowSelect' class to the row. 
					//$this.addClass('tableUtils_rowSelect');
					fastAddClass(tableRowsDOM[i], 'tableUtils_rowSelect');
					
					var elementSelector = 'input:checkbox';
					if(settings.rowSelectOptions.radio) {
						elementSelector = 'input:radio';
					}
					// The checkbox in the checkbox column of this row. 
					var $checkboxInThisRow = $this.find('td:nth-child(' +  checkBoxColumn + ') ' + elementSelector);					
					
					// change the event to 'click' if in future radio buttons do not work as expected. 
					if(settings.rowSelectOptions.radio) {						 
						$checkboxInThisRow.on('change', function() {
							logOnConsole('rows: ' + fastGetParent(this, 'table').rows.length);
							fastRemoveClass(fastGetParent(this, 'table').rows, 'tableUtils_selectedRow');
							if(this.checked) {								
								fastAddClass(fastGetParent(this, 'tr'), 'tableUtils_selectedRow');
							} 
						});
					}					
					
					var columnIndex = checkBoxColumn - 1;
					var rowColumnsDOM = tableRowsDOM[i].cells;
					for(var j=0; j<rowColumnsDOM.length; j++) {
						if(j != columnIndex) {							
							var $this = $(rowColumnsDOM[j]);
							
							$this.off('click.tableutils');
							
							// Bind the 'click' event handler to this column, so that it will select or de-select the row when it is clicked. 
							$this.on('click.tableutils', function() {
								logOnConsole('Rowselect clicked');
								
								// The TD that was clicked. 
								var $this = $(this);
								
								// The main table's ID. 
								var mainTableID = fastGetParent(this, 'table').id;
								
								// Load table settigns. 
								loadTableSettings(mainTableID);
								
								// The index of the column in which the selector checkbox is present. 
								var checkBoxColumnIndex = settings.rowSelectOptions.columnIndex;
								
								var elementSelector = 'input:checkbox';
								if(settings.rowSelectOptions.radio) {
									elementSelector = 'input:radio';
								}
								
								// The checkbox in the checkbox column of this row. 
								var $checkboxInThisRow = $this.closest('tr').find('td:nth-child(' +  checkBoxColumnIndex + ') ' + elementSelector);	
								
								// Toggle the value of the checkbox. 
								$checkboxInThisRow.attr('checked', !$checkboxInThisRow.attr('checked'));							
								
								// Trigger the checkbox's 'change' event. 
								$checkboxInThisRow.trigger('change');									
							});	
						}
					}
				}
				
				stopTimer('rowSelect');
			},			
			
			
			/**
			 * Paginate the table.  
			 *
			 * Options: 
			 *    - columnIndex: The column in which the checkbox that selects a row is present. 
			 *
			 */
			paginate: function(tableID) {				
				startTimer('paginate');
				
				loadTableSettings(tableID);
				
				var eligibleRowsSelector = 'tbody tr';
				if(settings.filterTableOptions.required === true) {
					eligibleRowsSelector += '.filteredRow';
				}				
				settings.paginationOptions.eligibleRowsSelector = eligibleRowsSelector;				
				
				var $paginationDiv = $('<div class="tableUtils_paginationDiv">').attr('id', 'paginationDiv_' + tableID).width(settings.fixHeaderOptions.width);
				
				var $paginationContentTable = $('<table class="tableUtils_paginationContentTable">').attr('id', 'paginationContentTable_' + tableID);
				
				var $paginationStats = $('<td>').attr('id', 'paginationStats_' + tableID);
				
				var $paginationLinks = $('<td>').attr('id', 'paginationLinks_' + tableID);
								
				$paginationStats.append($('<span>&nbsp;&nbsp;Page: </span>').attr('id', 'currentPageInfo_' + tableID));
				$paginationStats.append($('<span>&nbsp;&nbsp;Page Size: </span>').attr('id', 'pageSizeInfo_' + tableID));
				$paginationStats.append($('<span>&nbsp;&nbsp;Records: </span>').attr('id', 'recordsOnThisPageInfo_' + tableID).hide()).append();
				$paginationStats.append($('<span>&nbsp;&nbsp;Total Records: </span>').attr('id', 'totalRecordsInfo_' + tableID));
									
				$paginationContentTable.append($('<tr>').append($paginationLinks));
				
				$paginationContentTable.append($('<tr>').append($paginationStats));
				
				$paginationDiv.append($paginationContentTable);
				
				$('#outermostDiv_' + tableID).append($paginationDiv);
				
				logOnConsole('settings.pageSize: ' + settings.pageSize);				
				if($.inArray(settings.paginationOptions.pageSize, settings.paginationOptions.availablePageSizes) == -1) {
					settings.paginationOptions.availablePageSizes.push(settings.paginationOptions.pageSize);
					logOnConsole('appended page size');
				}
				
				settings.paginationOptions.availablePageSizes.sort(function(pageSize1, pageSize2) {
					return (pageSize1 > pageSize2) ? 1 : ((pageSize1 < pageSize2) ? -1 : 0);
				});
				
				logOnConsole('page sizes length: ' + settings.availablePageSizes.length);
				var $pageSizeSelectContent = $('<span class="tableUtils_label" id="pageSizeSelectSpan_' + tableID + '">&nbsp;&nbsp;Page Size: </span>');
				
				var $pageSizeSelect = $('<select></select>').attr('id', 'pageSizeSelect_' + tableID);
				$pageSizeSelect.on('change', function() {
					updatePageSize(tableID);
				});
				
				$.each(settings.paginationOptions.availablePageSizes, function(index, pageSize) {
					logOnConsole('adding page size: ' + this);
					$pageSizeSelect.append($('<option>', {
						text: pageSize, value: pageSize
					}));
				});
				
				$pageSizeSelect.val(settings.paginationOptions.pageSize);
				
				if(settings.paginationOptions.type !== 'numeric') {
					$pageSizeSelectContent.hide();
					$pageSizeSelect.hide();		
					
					$('#pageSizeInfo_' + tableID).hide();
					$('#recordsOnThisPageInfo_' + tableID).show();				
				}
				
				$paginationStats.append($pageSizeSelectContent, $pageSizeSelect);
				
				var $gotoPage = $('<span class="tableUtils_label">&nbsp;&nbsp;Go to Page: </span>');
				
				var $pageSelect = $('<select></select>').attr('id', 'pageSelect_' + tableID);
				$pageSelect.on('change', function() {
					goToPage(tableID, $(this).find('option:selected').val());
				});
				
//				$paginationStats.append($gotoPage, $pageSelect);				
				
				/* Change pagination type dynamically. */
				if(settings.paginationOptions.dynamicTypeChange) {
				
					var $changePaginationTypeSpan = $('<span class="tableUtils_label">&nbsp;&nbsp;Type: </span>');
					
					var $changePaginationTypeSelect = $('<select></select>').attr('id', 'paginationTypeSelect_' + tableID);
					$changePaginationTypeSelect.append($('<option></option>', { text: 'Change Pagination Type', value: '', selected: true }));
					$changePaginationTypeSelect.append($('<option></option>', { text: 'Numeric', value: 'numeric' }));
					$changePaginationTypeSelect.append($('<option></option>', { text: 'Alphabetic', value: 'alphabetic' }));
					$changePaginationTypeSelect.append($('<option></option>', { text: 'AlphaNumeric', value: 'alphanumeric' }));
					$changePaginationTypeSelect.on('change', function() {					
						if($(this).find('option:selected').val() !== 'numeric') {						
							$('#paginationColumnSpan_' + tableID).show();
							$('#paginationColumnSelect_' + tableID).show();						
						} else {
							loadTableSettings(tableID);
							settings.paginationOptions.type = $(this).find('option:selected').val();
							$(this).val('');
							settings.paginationOptions.linksCreated = false;
							saveTableSettings(tableID);
							resetToFirstPage(tableID);
						}
					});
					
					$paginationStats.append($changePaginationTypeSpan, $changePaginationTypeSelect);
				
				
					var $paginationColumnSpan = $('<span class="tableUtils_label" id="paginationColumnSpan_' + tableID + '">&nbsp;&nbsp;Column: </span>').hide();
					
					var $paginationColumnSelect = $('<select></select>').attr('id', 'paginationColumnSelect_' + tableID).hide();
					$paginationColumnSelect.append($('<option></option>', { text: 'Select Pagiantion Column', value: '', selected: true }));
					$.each(settings.columns, function(index, element) {
						if(!element.noAlphabeticPagination) {
							$paginationColumnSelect.append($('<option></option>', { text: element.label, value: index }));
						}
					});
					
					$paginationColumnSelect.on('change', function() {
						loadTableSettings(tableID);					
						settings.paginationOptions.type = $('#paginationTypeSelect_' + tableID).find('option:selected').val();
						settings.paginationOptions.columnIndex = Number($(this).find('option:selected').val()) + 1;
						$('#paginationTypeSelect_' + tableID).val('');
						$(this).val('');
						settings.paginationOptions.linksCreated = false;
						saveTableSettings(tableID);
						$(this).hide();
						$('#paginationColumnSpan_' + tableID).hide();
						logOnConsole('settings.paginationOptions.type: ' + settings.paginationOptions.type);
						logOnConsole('Setting columnIndex: ' + settings.paginationOptions.columnIndex);
						resetToFirstPage(tableID);
					});
					
					$paginationStats.append($paginationColumnSpan, $paginationColumnSelect); 
				}
				
				$paginationStats.append($('<span class="tableUtils_label">').attr('id', 'pageItemsInfo_' + tableID)); 
				
				saveTableSettings(tableID);
				
				resetToFirstPage(tableID);
				
				stopTimer('paginate');
			}, 
			
			
			/**
			* Indepenedent method. This method will return the selected records on the current page. 
			*/
			getSelectedRecordsOnPage: function(columnIndex, idOfTable) {
				var tableID = (idOfTable) ? idOfTable : this.attr('id');
				
				loadTableSettings(tableID);
				var $mainTable = $('#' + tableID);				
				var eligibleRowsSelector = '';
				if(settings.masterCheckBoxOptions.required === true) {
					eligibleRowsSelector = settings.masterCheckBoxOptions.eligibleRowsSelector;
				} else {
					eligibleRowsSelector = 'tbody tr';
				    if(settings.filterTableOptions.required === true) {
				     eligibleRowsSelector += '.filteredRow';
				    }				    
				    if(settings.paginationOptions.required === true) {
				     eligibleRowsSelector += '.currentPageRow';
				    }
				}
				
				var $rows = $mainTable.find(eligibleRowsSelector);
				var selectionColumn = (columnIndex) ? columnIndex: settings.masterCheckBoxOptions.columnIndex;
				var selection = new Array();
				
				var $selectedRecords = $rows.find('td:nth-child(' + selectionColumn + ') input:checkbox:checked');
				$selectedRecords.each(function(index) {
					selection.push($(this).val());
				});
				
				return selection;
			},
			
			
			/**
			* Indepenedent method. This method will return all the records on current page. 
			*/
			getAllRecordsOnPage: function(columnIndex) {
				var tableID = this.attr('id');
				
				loadTableSettings(tableID);
				var $mainTable = $('#' + tableID);				
				var eligibleRowsSelector = settings.masterCheckBoxOptions.eligibleRowsSelector;
				var $rows = $mainTable.find(eligibleRowsSelector);
				var selectionColumn = (!columnIndex) ? settings.masterCheckBoxOptions.columnIndex : columnIndex;
				var selection = new Array();
				
				var $selectedRecords = $rows.find('td:nth-child(' + selectionColumn + ') input:checkbox');
				$selectedRecords.each(function(index) {
					selection.push($(this).val());
				});
				
				return selection;
			},
			
			
			/**
			* Indepenedent method. This method will return the current pagination information. 
			*/
			getCurrentPageInfo: function() {
				var tableID = this.attr('id');
				
				loadTableSettings(tableID);
				
				var currentPageInfo = {				
					pageSize: settings.paginationOptions.pageSize,				
					currentPage: settings.paginationOptions.currentPage, 
					start: settings.paginationOptions.start,
					end: settings.paginationOptions.end,
					sortingDetails: settings.sortOptions.sortingState,	 				
					filteringDetails: settings.filterTableOptions.activeFilters,
					type: settings.paginationOptions.type,
					columnIndex: settings.paginationOptions.columnIndex,
					columnName: settings.columns[settings.paginationOptions.columnIndex - 1].value
				};				
				
				return currentPageInfo;
			},

			
			/**
			* Reset previously selected records. 
			*/
			resetPreviousSelection: function() {
				var tableID = this.attr('id');
				
				loadTableSettings(tableID);
				
				settings.paginationOptions.resetPreviousSelection = true;
				
				settings.paginationOptions.previouslySelectedRecords = new Array();
				
				updateSelectedRecords(tableID);
				
				saveTableSettings(tableID);
			},
			
			
			/**
			* Get the items selected on previous pages. 
			*/
			getPreviousSelection: function() {
				var tableID = this.attr('id');
				
				loadTableSettings(tableID);
				
				return settings.paginationOptions.previouslySelectedRecords;
			},
			
			
			/**
			* Get all selected items (previous selected + items selected on the current page) 
			*/
			getAllSelectedItems: function() {
				var tableID = this.attr('id');
				var selectedItemsOnCurrentPage = methods.getSelectedRecordsOnPage(null, tableID);
				for(var i=0; i<settings.paginationOptions.previouslySelectedRecords.length; i++) {
					if($.inArray(settings.paginationOptions.previouslySelectedRecords[i], selectedItemsOnCurrentPage) === -1) {
						selectedItemsOnCurrentPage.push(settings.paginationOptions.previouslySelectedRecords[i]);
					}
				}
				return selectedItemsOnCurrentPage;
			},
			
			
			/**
			* Add a new message to the table. 
			*/ 
			addMessage: function(message) {
				var $this = this;
				
				var tableID = $this.attr('id');
				
				loadTableSettings(tableID);
				
				logOnConsole('pushing message: ' + message.type);			
				settings.fixHeaderOptions.messages = $.grep(settings.fixHeaderOptions.messages, function(msg, msgIndex) {
					return (msg.type === message.type);
				}, true);
				
				settings.fixHeaderOptions.messages.push(message);
				
				saveTableSettings(tableID);
				
				setNextMessage(tableID, message);
				
				clearMessagesInterval(tableID);
				
				updateMessages(tableID);
			},
			
			
			/**
			* Add a new message to the table. 
			*/ 
			removeMessage: function(message) {
				var $this = this;
				
				var tableID = $this.attr('id');
				
				loadTableSettings(tableID);
				
				settings.fixHeaderOptions.messages = $.grep(settings.fixHeaderOptions.messages, function(msg, msgIndex) {
					return (msg.type === message.type);
				}, true);
				
				settings.fixHeaderOptions.nextMessageIndex = 0;
				
				saveTableSettings(tableID);
				
				clearMessagesInterval(tableID);
				
				updateMessages(tableID);
			},
			
			/**
			 * Adds a new row to the selected table. ^Optimized 
			 */
			addRow: function(options) {
                startTimer('addRow');
				if(options.tableID) {
					var $insertIn = $('#' + options.tableID);
				
					var $row;
					
					if(options.row) {
						// If a new row is to be added, then add a new row; else use existing row.
						if(options.row.props) {                  
							$row = $('<tr></tr>');
							$.each(options.row.props, function(name, value) {
								logOnConsole('Property: ' + name);
								if(name === 'style') {
									$row.css(value);
								} else {
									$row.attr(name, value);
								}
							});
						} else {
							$row = options.row;
						} 
					} else {
						$row = $('<tr></tr>');
					}
					
					// Add each column to the row.
					$.each(options.columns, function(index, value) {    
						// Create a new column.
						var $newCell = $('<td></td>');
						
						// If we need to assign properties to the column, assign the properties; else simply add the html.
						if(value && value.props) { 
							$.each(value.props, function(name, value) {
								if(name === 'style') {
									$newCell.css(value);
								} else {
									$newCell.attr(name, value);
								}
							});
							$newCell.html(value.html);
						} else {
							$newCell.html(value);
						}
						
						// Append the column to the row.
						$row.append($newCell);
					});
										
					$insertIn.append($row); 
				}
				stopTimer('addRow');
            },
			
			
			
			deleteRecords: function(tableID) {
				logOnConsole('Adding delete functionality.');
				
				var $mainTable = $('#' + tableID);
				
				loadTableSettings(tableID);	

				if(settings.masterCheckBoxOptions.required === true) {
				
					$mainTable.on('deleteRecords', function() {
						var tableID = $(this).attr('id');
						
						var selector = 'tbody tr';
						if(settings.filterTableOptions.required === true) {
							selector += '.filteredRow';
						}
						
						var $selectedRows = $mainTable.find(selector).find('td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ')').find('input:checkbox:checked'); 
						var totalSelectedRecords = $selectedRows.length;
						
						var selectedRecords = new Array();
						$selectedRows.each(function(index, record) {
							selectedRecords.push( { name: 'recordsToDelete', value: $(record).val()} );
						});
						
						if(totalSelectedRecords > 0) {			
							$.ajax({
								url: settings.deleteRecordsOptions.deleteURL, 
								
								data: selectedRecords,
								
								beforeSend: function() { return true; },
								
								success: function(data) {
									$selectedRows.each(function(index, record) {
										$(record).parent().parent().remove();
									});
									
									if(settings.paginationOptions.required === true) {
										resetToFirstPage(tableID);
									} 
									
									alert(totalSelectedRecords + ' Record(s) Deleted.');
								},
								
								error: function(msg) { alert('The following error occurred while Deleting the Selected Records: ' + msg.statusText); },
								
								dataType: 'json',
								
								cache: false
							});
						} else {
							alert('Please Select Atleast 1 Record.'); 
						}
						
					});
					
					var $deleteRecordsButtonsDiv = $('<span></span>').attr('id', 'deleteRecordsAdditionalControls_' + tableID);
					
					var $deleteButton = $('<button type="button"></button>').attr('id', 'deleteRecordButton_' + tableID).addClass('tableUtils_imageButton');
					$deleteButton.append($('<img title="Delete" alt="Delete">').attr('src', settings.contextRoot + settings.resourcesDir + '/delete1.png').addClass('tableUtils_imageButton'));
					
					$deleteButton.on('click', function() {
						$mainTable.trigger('deleteRecords');					
					});
									
					$deleteRecordsButtonsDiv.append($deleteButton);
					
					$('#additionalControls_' + tableID).append($deleteRecordsButtonsDiv); 
					
				} 
			},

			
			editRecord: function(tableID) {
				logOnConsole('Adding edit functionality.');
				
				var $mainTable = $('#' + tableID);
				
				loadTableSettings(tableID);					
				
				var $editRowButtonsDiv = $('<span></span>').attr('id', 'editRowAdditionalControls_' + tableID);
				
				var $editButton = $('<button type="button"></button>').attr('id', 'editRowAddButton_' + tableID).addClass('tableUtils_imageButton');
				var $saveEditButton = $('<button type="button"></button>').attr('id', 'editRowSaveButton_' + tableID).addClass('tableUtils_imageButton').hide();
				var $cancelEditButton = $('<button type="button"></button>').attr('id', 'editRowCancelButton_' + tableID).addClass('tableUtils_imageButton').hide();
				
				$editButton.append($('<img alt="Edit" title="Edit">').attr('src', settings.contextRoot + settings.resourcesDir + '/edit1.png').addClass('tableUtils_imageButton'));
				$saveEditButton.append($('<img alt="Save Edited Record" title="Save">').attr('src', settings.contextRoot + settings.resourcesDir + '/ok1.png').addClass('tableUtils_imageButton'));
				$cancelEditButton.append($('<img alt="Cancel" title="Cancel">').attr('src', settings.contextRoot + settings.resourcesDir + '/no1.png').addClass('tableUtils_imageButton'));
				
				$editButton.on('click', function() {
					$mainTable.trigger('startEditRow');
				});
				
				$saveEditButton.on('click', function() {
					$mainTable.trigger('endEditRow');
				});
				
				$cancelEditButton.on('click', function() {
					$mainTable.trigger('cancelEditRow');					
				});
				
				$editRowButtonsDiv.append($editButton);
				$editRowButtonsDiv.append($saveEditButton);
				$editRowButtonsDiv.append($cancelEditButton);
				
				$('#additionalControls_' + tableID).append($editRowButtonsDiv); 
								
				var newColumns = [];
				
				logOnConsole('Editing row.');
				
				$.each(settings.columns, function(index, column) {
					var $newCell = $('<span></span>');
					
					var $inputElement = null;
					if(column.type === 'text' || column.type === 'label') {
						$inputElement = $('<input>');
						$inputElement.attr('type', 'text');							
					} else if(column.type === 'select') {
						$inputElement = $('<select></select>');

						$.each(column.options, function(index, option) {
							$inputElement.append('<option>', {text: option.text, value: option.value});
						});
					}											
					
					$inputElement.attr('id', column.name);
					$inputElement.attr('title', 'Enter ' + column.label);
					
					$inputElement.css('width', '100%');					
					
					$inputElement.addClass('editRowField');
					
					$newCell.append($inputElement);
					
					if(column.editable === false) {
						$inputElement.hide();
						$newCell.append('<label></label>'); 
					}
					
					logOnConsole('New Cell to be added: ' + $newCell.html());
					
					var newColumn = null;
					
					var columnData = $newCell.html();
					
					if(column.style) {
						newColumn = new Object();
						newColumn.html = columnData;
						newColumn.props = column.style;
						
						logOnConsole('Styled Column ' + index + ' - ' + columnData);
					} else {
						newColumn = columnData;
						
						logOnConsole('Simple Column ' + index + ' - ' + columnData);
					}
					
					newColumns.push(newColumn);
				}); 
								
				methods.addRow({ tableID: tableID, row: { props: { id: 'editRow_' + tableID, style: { 'background-color': 'green' } } },  columns: newColumns });
				
				settings.editRecordOptions.row = $('#editRow_' + tableID).html();		

				$('#editRow_' + tableID).remove();
				
				$mainTable.on('clearEditRowColumns', function() {
					var tableID = $(this).attr('id');
					
					var $newRow = $('#editRow_' + tableID);
					
					$newRow.find('.editRowField').each(function(index) {
						if(!settings.columns[index].disabled) { 
							$(this).val('');
						}
					});
				});
				
				$mainTable.on('startEditRow', function() {
					logOnConsole('start row edit.');
					
					var tableID = $(this).attr('id');
					
					var selector = 'tbody tr';
					if(settings.filterTableOptions.required === true) {
						selector += '.filteredRow';
					}
					
					var $selectedRows = $mainTable.find(selector).find('td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ')').find('input:checkbox:checked'); 
					var totalSelectedRecords = $selectedRows.length;
					
					if(totalSelectedRecords == 1) {
						var $selectedRow = $selectedRows.eq(0).parent().parent();
						
						$selectedRow.addClass('editingRow_' + tableID).hide(); 
						
						var $editRow = $('<tr></tr>').html(settings.editRecordOptions.row).attr('id', 'editRow_' + tableID);
						
						$selectedRow.before($editRow);
						
						logOnConsole('iterating over columns of selected row. checkbox at ' + settings.masterCheckBoxOptions.columnIndex);
						$selectedRow.find('td').each(function(index, column) {
							logOnConsole('column: ' + $(this).html());							
							if(index != (settings.masterCheckBoxOptions.columnIndex - 1)) {								
								logOnConsole('setting value for column: ' + $editRow.find('.editRowField').eq(index).html());
								if(settings.columns[index].editable === true) {
									$editRow.find('.editRowField').eq(index).attr('value', $(this).html()); 
								} else {
									$editRow.find('.editRowField').eq(index).attr('value', $(this).html()); 
									$editRow.find('td').eq(index).find('label').html($(this).html()); 
								}
							} else {							
								$editRow.find('.editRowField').eq(index).attr('value', $selectedRows.val());  
							}
						});
						
						$('#editRowAddButton_' + tableID).hide();
						$('#editRowSaveButton_' + tableID).show();
						$('#editRowCancelButton_' + tableID).show();
						
					} else if(totalSelectedRecords > 1) {
						alert('Please Select Only 1 Record.');
					} else {
						alert('Please Select A Record To Update.');
					}			
					
				});
				
				$mainTable.on('cancelEditRow', function() {
					var tableID = $(this).attr('id');
					
					$(this).trigger('clearEditRowColumns');
					
					$('#editRow_' + tableID).remove(); 
					$(this).find('.editingRow_' + tableID).show(); 
					
					$('#editRowCancelButton_' + tableID).hide();				
					$('#editRowSaveButton_' + tableID).hide();
					$('#editRowAddButton_' + tableID).show();
				});
				
				
				
				$mainTable.on('endEditRow', function() {					
					var tableID = $(this).attr('id');
					
					var $editRow = $('#editRow_' + tableID);
					
					var $finalParams = [];
					
					var params = [];
					
					$.each($editRow.find('.editRowField'), function(index, value) {
						var field = new Object();
						field.name = $(value).attr('id');
						field.value = $(value).attr('value');	

						params.push(field);
					});
					
					if(settings.editRecordOptions.params) {
						finalParams = $.merge( $.merge([], params), settings.editRecordOptions.params);
					} else {
						finalParams = params;
					}					
					
					$.ajax({
						url: settings.editRecordOptions.editURL,
						
						data: finalParams,
						
						beforeSend: function() {
							if(settings.editRecordOptions.beforeSend) {
								return settings.editRecordOptions.beforeSend(params);
							}
						},
						
						success: function(data) {														
							$('#editRowCancelButton_' + tableID).hide();				
							$('#editRowSaveButton_' + tableID).hide();
							$('#editRowAddButton_' + tableID).show();
							
							var newColumns = [];
							$.each(params, function(index, param) {
								var newColProps = {};
								var generateValue = false;
								var colProps = false;
								
								$.each(settings.columns, function(index, columnValue) {
									if(columnValue.name == param.name && columnValue.style) {
										colProps = true;
										if(columnValue.generateStyle) {
											newColProps = columnValue.generateColProps(param.value, data);
										} else {
											newColProps = columnValue.style;
										}
									}
								});
								
								$.each(settings.columns, function(index, columnValue) {
									if(columnValue.name == param.name && columnValue.generate) {
										generateValue = true;
										if(colProps) {
											newColumns.push({html: columnValue.generate(data), props: newColProps });
										} else {
											newColumns.push(columnValue.generate(data));
										}
									}
								});
								
								if(!generateValue) {
									if(colProps) {
										newColumns.push({html: param.value, props: newColProps });
									} else {
										newColumns.push(param.value);
									}
								}
							});							
							
							if(settings.editRecordOptions.row.style) {
								if(settings.editRecordOptions.row.generateStyle) {
									methods.addRow({ tableID: tableID, row: {props: settings.editRecordOptions.row.generateStyle(data)}, columns: newColumns });
								} else {
									methods.addRow({ tableID: tableID, row: {props: rowProps}, columns: newColumns });
								}
							} else {							
								methods.addRow({ tableID: tableID, columns: newColumns });
							}
							
							$('#' + tableID).trigger('cancelEditRow').find('.editingRow_' + tableID).remove();
							
							if(settings.editRecordOptions.success) {
								settings.editRecordOptions.success(data);
							} else {
								alert('Record Saved Successfully.');								
							}
							
							if(settings.paginationOptions.required === true) {
								resetToFirstPage(tableID);
							} 
						},
						
						error: function(msg) {
							if(settings.editRecordOptions.error) {
								settings.editRecordOptions.error(msg);
							} else {
								alert('The following error occurred while saving changes to the record: ' + msg.statusText);
							}
						},
						
						complete: function() {
							if(settings.editRecordOptions.complete) {
								settings.editRecordOptions.complete();		
							}
						},

						dataType: 'json',
						
						cache: false
					});
				});
				
			},

			
			/**
			* Adds the functionality of inserting new rows into the table. 
			*/
			newRecordInsertion: function(tableID) {			
				logOnConsole('Adding new record functionality.');
				
				var $searchTable = $('#' + tableID);
				
				loadTableSettings(tableID);					
				
				var $newRowButtonsDiv = $('<span></span>').attr('id', 'newRowadditionalControls_' + tableID);
				
				var addButtonLabel = 'New';
				if(settings.newRowOptions.addButton) {
					addButtonLabel = settings.newRowOptions.addButton;
				}				
				
				var $addButton = $('<button type="button"></button>').attr('id', 'newRowAddButton_' + tableID).addClass('tableUtils_imageButton');
				var $saveButton = $('<button type="button"></button>').attr('id', 'newRowSaveButton_' + tableID).addClass('tableUtils_imageButton').hide();
				var $cancelButton = $('<button type="button"></button>').attr('id', 'newRowCancelButton_' + tableID).addClass('tableUtils_imageButton').hide();
				
				$addButton.append($('<img alt="New">').attr('title', addButtonLabel).attr('src', settings.contextRoot + settings.resourcesDir + '/add5.png').addClass('tableUtils_imageButton'));
				$saveButton.append($('<img alt="Save" title="Save">').attr('src', settings.contextRoot + settings.resourcesDir + '/ok1.png').addClass('tableUtils_imageButton'));
				$cancelButton.append($('<img alt="Cancel" title="Cancel">').attr('src', settings.contextRoot + settings.resourcesDir + '/no2.png').addClass('tableUtils_imageButton'));
				
				$addButton.on('click', function() {
					$searchTable.trigger('startNewRowInsert');
				});
				
				$saveButton.on('click', function() {
					$searchTable.trigger('endNewRowInsert');
				});
				
				$cancelButton.on('click', function() {
					$searchTable.trigger('cancelNewRowInsert');					
				});
				
				$newRowButtonsDiv.append($addButton);
				$newRowButtonsDiv.append($saveButton);
				$newRowButtonsDiv.append($cancelButton);
				
				$('#additionalControls_' + tableID).append($newRowButtonsDiv); 
								
				var newColumns = [];
				
				logOnConsole('Adding new row.');
				
				$.each(settings.columns, function(index, column) {
					var $newCell = $('<span></span>');
					
					var $inputElement = null;
					if(column.type === 'text' || column.type === 'label') {
						$inputElement = $('<input>');
						$inputElement.attr('type', 'text');							
					} else if(column.type === 'select') {
						$inputElement = $('<select></select>');
						
						$.each(column.options, function(index, option) {
							$inputElement.append('<option>', {text: option.text, value: option.value});
						});
					}											
					
					$inputElement.attr('id', column.name);
					$inputElement.attr('title', 'Enter ' + column.label);
					
					$inputElement.css('width', '100%');
					
					logOnConsole('Before Check Default value: ' + column.defaultValue);
					if(column.defaultValue) {
						$inputElement.attr('value', column.defaultValue); 
						logOnConsole('Default value: ' + column.defaultValue);
					}
					
					if(column.disabled) {
						$inputElement.attr('disabled', true);
					}
					
					$inputElement.addClass('newRowField');
					
					$newCell.append($inputElement);
					
					if(column.type === 'label') {
						$inputElement.hide();
						$newCell.append('<label>' + column.displayValue + '</label>');
					}
					
					var newColumn = null;
					
					var columnData = $newCell.html();
					
					if(column.style) {
						newColumn = new Object();
						newColumn.html = columnData;
						newColumn.props = column.style;
						
						logOnConsole('Styled Column ' + index + ' - ' + columnData);
					} else {
						newColumn = columnData;
						
						logOnConsole('Simple Column ' + index + ' - ' + columnData);
					}
					
					newColumns.push(newColumn);
				}); 
								
				methods.addRow({ tableID: tableID, row: { props: { id: 'newRow_' + tableID, style: { 'background-color': 'green' } } },  columns: newColumns });
				
				settings.newRowOptions.row = $('#newRow_' + tableID).html();		

				$('#newRow_' + tableID).remove();
				
				$searchTable.on('clearNewRowColumns', function() {
					var tableID = $(this).attr('id');
					
					var $newRow = $('#newRow_' + tableID);
					
					$newRow.find('.newRowField').each(function(index) {
						if(!settings.columns[index].defaultValue) { 
							$(this).val('');
						}
					});
				});
				
				$searchTable.on('cancelNewRowInsert', function() {
					var tableID = $(this).attr('id');
					
					$(this).trigger('clearNewRowColumns');
					
					$('#newRow_' + tableID).remove();
					
					$('#newRowCancelButton_' + tableID).hide();				
					$('#newRowSaveButton_' + tableID).hide();
					$('#newRowAddButton_' + tableID).show();
				});
				
				$searchTable.on('startNewRowInsert', function() {
					var tableID = $(this).attr('id');
					
					var $newRow = $('<tr></tr>').html(settings.newRowOptions.row).attr('id', 'newRow_' + tableID);
					
					$(this).prepend($newRow);
					
					$('#newRowAddButton_' + tableID).hide();
					$('#newRowSaveButton_' + tableID).show();
					$('#newRowCancelButton_' + tableID).show();
				});
				
				$searchTable.on('endNewRowInsert', function() {					
					var tableID = $(this).attr('id');
					
					var $newRow = $('#newRow_' + tableID);
					
					var $finalParams = [];
					
					var params = [];
					
					$.each($newRow.find('.newRowField'), function(index, value) {
						var field = new Object();
						field.name = $(value).attr('id');
						field.value = $(value).attr('value');	

						params.push(field);
					});
					
					if(settings.newRowOptions.params) {
						finalParams = $.merge( $.merge([], params), settings.newRowOptions.params);
					} else {
						finalParams = params;
					}					
					
					$.ajax({
						url: settings.newRowOptions.addURL,
						
						data: finalParams,
						
						beforeSend: function() {
							if(settings.newRowOptions.beforeSend) {
								return settings.newRowOptions.beforeSend(params);
							}
						},
						
						success: function(data) {														
							$('#newRowCancelButton_' + tableID).hide();				
							$('#newRowSaveButton_' + tableID).hide();
							$('#newRowAddButton_' + tableID).show();
							
							var newColumns = [];
							$.each(params, function(index, param) {
								var newColProps = {};
								var generateValue = false;
								var colProps = false;
								
								$.each(settings.columns, function(index, columnValue) {
									if(columnValue.name == param.name && columnValue.style) {
										colProps = true;
										if(columnValue.generateStyle) {
											newColProps = columnValue.generateColProps(param.value, data);
										} else {
											newColProps = columnValue.style;
										}
									}
								});
								
								$.each(settings.columns, function(index, columnValue) {
									if(columnValue.name == param.name && columnValue.generate) {
										generateValue = true;
										if(colProps) {
											newColumns.push({html: columnValue.generate(data), props: newColProps });
										} else {
											newColumns.push(columnValue.generate(data));
										}
									}
								});
								
								if(!generateValue) {
									if(colProps) {
										newColumns.push({html: param.value, props: newColProps });
									} else {
										newColumns.push(param.value);
									}
								}
							});							
							
							if(settings.newRowOptions.row.style) {
								if(settings.newRowOptions.row.generateStyle) {
									methods.addRow({ tableID: tableID, row: {props: settings.newRowOptions.row.generateStyle(data)}, columns: newColumns });
								} else {
									methods.addRow({ tableID: tableID, row: {props: rowProps}, columns: newColumns });
								}
							} else {							
								methods.addRow({ tableID: tableID, columns: newColumns });
							}
							
							$('#' + tableID).trigger('cancelNewRowInsert');
							
							if(settings.newRowOptions.success) {
								settings.newRowOptions.success(data);
							} else {
								alert('New Record Inserted Successfully.');								
							}
							
							if(settings.paginationOptions.required === true) {
								resetToFirstPage(tableID);
							} 
						},
						
						error: function(msg) {
							if(settings.newRowOptions.error) {
								settings.newRowOptions.error(msg);
							} else {
								alert('The following error occurred while inserting the new row: ' + msg.statusText);
							}
						},
						
						complete: function() {
							if(settings.newRowOptions.complete) {
								settings.newRowOptions.complete();		
							}
						},

						dataType: 'json',
						
						cache: false
					});
					
					
					
				});
				
				saveTableSettings(tableID);				
			}	
		};
		
		
		/**
		* Add a new filter. ^Optimized 
		*/
		updateFilter = function(tableID, index, filterValue, filterType) {
			logOnConsole('Updating filter for: ' + tableID + ', column: ' + index);
			
			loadTableSettings(tableID);
			
			var validRequest = true;
			if(filterValue.length > 0 && (filterType === 'numeric' || filterType === 'float')) {
				if(isNaN(filterValue) || $.trim(filterValue).length < 1) {
					validRequest = false;
				}
			}
			
			if(!validRequest) {				
				settings.filterTableOptions.message.block = true;
				settings.filterTableOptions.message.message = '<b>' + 'Invalid filter value. Please enter a numeric value to filter on: ' + settings.columns[index].label + '</b>';
				pushMessage(tableID, settings.filterTableOptions.message); 				
			} else {
				
				settings.filterTableOptions.activeFilters = $.grep(settings.filterTableOptions.activeFilters, function(filter, indexInArray) {
					return (index === filter.columnIndex);
				}, true);
				
				logOnConsole('After grep: ' + settings.filterTableOptions.activeFilters.length);
				
				if((filterType === 'checkbox' && filterValue === true) || (filterType !== 'checkbox' && filterValue.length > 0)) {
					var newFilter = {
						columnIndex: index,
						columnName: settings.columns[index].value,
						expr: filterValue,
						type: filterType
					};
					
					settings.filterTableOptions.activeFilters.push(newFilter);
					
					logOnConsole('Filter updated.');
				}
				
				var filters = new Array();
				for(var i=0; i<settings.filterTableOptions.activeFilters.length; i++) {
					filters.push(settings.columns[settings.filterTableOptions.activeFilters[i].columnIndex].label + '(' + settings.filterTableOptions.activeFilters[i].expr + ')'); 
				}
				
				var filtersList = filters.join(', ');
				
				saveTableSettings(tableID);
				
				logOnConsole(settings.filterTableOptions.activeFilters.length + ' active filters.');
				
				if(settings.filterTableOptions.activeFilters.length > 0) {
					settings.filterTableOptions.message.block = false;
					settings.filterTableOptions.message.message = '<b>' + settings.filterTableOptions.activeFilters.length + '</b> Filter(s) Active. Filtering on: <b>' + filtersList + '</b>.';
					pushMessage(tableID, settings.filterTableOptions.message); 
				} else {
					popMessage(tableID, settings.filterTableOptions.message);
				}
				
				loadTableSettings(tableID);
				if(settings.filterTableOptions.fetchDelayTimer != null) {
					logOnConsole('Clearing previous request');
					clearTimeout(settings.filterTableOptions.fetchDelayTimer);
					settings.filterTableOptions.fetchDelayTimer = null;
					logOnConsole('Setting new timer again');
					settings.filterTableOptions.fetchDelayTimer = setTimeout(function() {
						logOnConsole('Timed out: ' + tableID);
						if(settings.paginationOptions.serverSide === false) {				
							applyFilter(tableID);																					
						} else {					
							resetToFirstPage(tableID, true);						
						}
						settings.filterTableOptions.fetchDelayTimer = null;
					}, settings.filterTableOptions.fetchDelayTimeOut);				
				} else {
					logOnConsole('No previous request found. Setting timer.');
					settings.filterTableOptions.fetchDelayTimer = setTimeout(function() {
						logOnConsole('Timed out: ' + tableID);
						if(settings.paginationOptions.serverSide === false) {				
							applyFilter(tableID);																					
						} else {					
							resetToFirstPage(tableID, true);						
						}
						settings.filterTableOptions.fetchDelayTimer = null;
					}, settings.filterTableOptions.fetchDelayTimeOut);				
				}	
				
				saveTableSettings(tableID);
				
				$('#' + settings.masterCheckBoxOptions.masterCheckBox).attr('checked', false).trigger('hideControls');	
			} 
		};	


		/**
		* Update sorting. 
		*/ 
		updateSortInfo = function(tableID, index, sortType, sortFunction) {
			logOnConsole('Updating sort info for: ' + tableID + ', column: ' + index);
			startTimer('updateSortInfo');
			
			loadTableSettings(tableID);
			
			var sortingUp = true;
			
			if(settings.sortOptions.sortingState.columnIndex != 'null') {
				if(settings.sortOptions.sortingState.columnIndex == index) {
					logOnConsole('settings.sortOptions.sortingState.columnIndex: ' + settings.sortOptions.sortingState.columnIndex);
					logOnConsole('settings.sortOptions.sortingState.sortUp: ' + settings.sortOptions.sortingState.sortUp);
					sortingUp = !settings.sortOptions.sortingState.sortUp;
					logOnConsole('sortingUp: ' + sortingUp);
				}
			} else {
				logOnConsole('settings.sortOptions.sortingState.columnIndex is undefined');
			}		
			
			settings.sortOptions.sortingState = {
				columnIndex: index,
				columnName: settings.columns[index].value, 
				sortUp: sortingUp,
				type: sortType
			};
			
			if(sortFunction) {
				logOnConsole('Custom sorting function added.');
				settings.sortOptions.sortingState['sortFunction'] = sortFunction;
			}
			
			saveTableSettings(tableID);
			
			logOnConsole('sorting active on header: ' + settings.sortOptions.sortingState.columnIndex);			 
						
			if(settings.paginationOptions.serverSide === false) {
				settings.sortOptions.message.message = 'Sorting. Please wait.';
				settings.sortOptions.message.block = true;
				pushMessage(tableID, settings.sortOptions.message);
				applySort(tableID);	
				settings.sortOptions.message.block = false;				
			} else {
				resetToFirstPage(tableID, true);
			}			
			
			settings.sortOptions.message.message = 'Sorting on: <b>' + settings.columns[settings.sortOptions.sortingState.columnIndex].label + '</b>(' + ( (settings.sortOptions.sortingState.sortUp === true) ? 'Asc' : 'Desc') + ').';
			pushMessage(tableID, settings.sortOptions.message);
			
			stopTimer('updateSortInfo');
		};
		
		
		saveTableSettings = function(tableID) {
			for(var i=0; i<tableSettings.length; i++) {
				if(tableSettings[i].tableID === tableID) {					
					tableSettings.splice(i,1);
				}
			} 
			
			var settingsForTable = new Object();			
			
			settingsForTable.tableID = tableID;	
			settingsForTable.columns = settings.columns;
			settingsForTable.rowSelectOptions = settings.rowSelectOptions;
			settingsForTable.fixHeaderOptions = settings.fixHeaderOptions;
			settingsForTable.filterTableOptions = settings.filterTableOptions;
			settingsForTable.masterCheckBoxOptions = settings.masterCheckBoxOptions;
			settingsForTable.sortOptions = settings.sortOptions;
			settingsForTable.paginationOptions = settings.paginationOptions;			
			settingsForTable.newRowOptions = settings.newRowOptions;
			settingsForTable.deleteRecordsOptions = settings.deleteRecordsOptions;
			settingsForTable.editRecordOptions = settings.editRecordOptions;
			settingsForTable.contextRoot = settings.contextRoot;
			settingsForTable.resourcesDir = settings.resourcesDir;	
			settingsForTable.buttons = settings.buttons;
						
			tableSettings[tableSettings.length] = settingsForTable;			
		};
		
		
		printCurrentSettings = function() {			
			logOnConsole('tableID: ' + settings.tableID);	
			logOnConsole('pagination fetch url: ' + settings.paginationOptions.fetchUrl);			
		};
		
		
		printSettings = function() {	
			logOnConsole('settings.pageSize: ' + settings.rowSelectOptions);
			logOnConsole('settings.numberOfPageLinks: ' + settings.fixHeaderOptions);
			logOnConsole('settings.displayPagesCount: ' + settings.filterTableOptions);
			logOnConsole('settings.currentPage: ' + settings.masterCheckBoxOptions);
			logOnConsole('settings.availablePageSizes: ' + settings.sortOptions);
			logOnConsole('settings.fixedHeaderTable: ' + settings.paginationOptions);
			logOnConsole('settings.globalWidth: ' + settings.newRowOptions);
			logOnConsole('settings.updateURL: ' + settings.editRowOptions);
		};
		
		
		loadTableSettings = function(tableID) {			
			var settingsForTable = {};
			var settingsFound = false;
			
			for(var i=0; i<tableSettings.length; i++) {
				if(tableSettings[i].tableID === tableID) {
					settingsForTable = tableSettings[i];
					settingsFound = true;
					break;
				}
			}
			
			if(settingsFound === true) {
			
				settings.tableID = settingsForTable.tableID;
				settings.columns = settingsForTable.columns;
				settings.rowSelectOptions = settingsForTable.rowSelectOptions;
				settings.fixHeaderOptions = settingsForTable.fixHeaderOptions;
				settings.filterTableOptions = settingsForTable.filterTableOptions;
				settings.masterCheckBoxOptions = settingsForTable.masterCheckBoxOptions;
				settings.sortOptions = settingsForTable.sortOptions;
				settings.paginationOptions = settingsForTable.paginationOptions;
				settings.newRowOptions = settingsForTable.newRowOptions;
				settings.deleteRecordsOptions = settingsForTable.deleteRecordsOptions;				
				settings.editRecordOptions = settingsForTable.editRecordOptions;	
				settings.contextRoot = settingsForTable.contextRoot;
				settings.resourcesDir = settingsForTable.resourcesDir;	
				settings.buttons = settingsForTable.buttons;				
				
				return true;
			} else {
				settings = $.extend(true, {}, defaultSettings);
				logOnConsole('Settings not found for table: ' + tableID + '. Default settings tableID: ' + settings.tableID + ' - ' + settings.fixHeaderOptions.fixedHeaderTable);
				return false;
			}
			
		};
		
		
		/**
		* Faster alternative to jQuerys' $('#' + id) method. 
		*/
		$.id = function(elementID) {
			return $(document.getElementById(elementID));
		};
		
		
		/**
		* Faster alternative to jQuerys' removeClass() method. 
		*/
		removeClass = function(element, className) {
			if(element instanceof Array) {
				for(var i=0; i<element.length; i++) {
					element[i].className = element[i].className.replace(new RegExp('(^|\\s+)' + className + '(\\s+|$)', 'g'), '$1');
				}
			} else {
				element.className = element.className.replace(new RegExp('(^|\\s+)' + className + '(\\s+|$)', 'g'), '$1');
			}
		};
		
		
		/**
		* Faster alternative to jQuerys' removeClass() method. 
		*/
		fastRemoveClass = function(element, className) {
			startTimer('fastRemoveClass');			
			if(element) {
				var elmt = element.jquery ? element.get() : element;
				if(!elmt.className) {
					elmt.className = '';
					logOnConsole('className not found');
				}
				if(elmt && (elmt instanceof Array || elmt.length)) {
					logOnConsole('elmt size: ' + elmt.length);
					for(var i=0; i<elmt.length; i++) {
						elmt[i].className = elmt[i].className.replace(new RegExp('(^|\\s+)' + className + '(\\s+|$)', 'g'), '$1');
						logOnConsole('className: ' + elmt[i].className);
					}
				} else {
					elmt.className = elmt.className.replace(new RegExp('(^|\\s+)' + className + '(\\s+|$)', 'g'), '$1');
					logOnConsole('className: ' + elmt.className);
				}
			}
			stopTimer('fastRemoveClass');
		};
		
		/**
		* Faster alternative to jQuerys' addClass() method. 
		*/
		fastAddClass = function(element, className) {			
			startTimer('fastAddClass');			
			if(element) {
				var elmt = element.jquery ? element.get() : element;
				if(elmt instanceof Array) {
					for(var i=0; i<elmt.length; i++) {
						// Check if the class is already added to the element. 
						var regEx = new RegExp(className);
						
						if(regEx.exec(elmt[i].className) == null) {
							elmt[i].className = elmt[i].className + ' ' + className;
						} 
					}
				} else {
					// Check if the class is already added to the element. 
					var regEx = new RegExp(className);
					
					if(regEx.exec(elmt.className) == null) {
						elmt.className = elmt.className + ' ' + className;
					}
				}			
			}
			stopTimer('fastAddClass');
		};
		
		/**
		* Faster alternative to jQuerys' show() method.
		*/
		fastShow = function(elements) {
			startTimer('fastShow');			
			if(elements) {
				var elmt = elements.jquery ? elements.get() : elements;
				if(elmt instanceof Array) {
					var elementsLength = elmt.length;
					var elementDisplayStyle = 'block';
					if(elementsLength > 0) {
						if($(elmt[0]).is('tr')) {
							elementDisplayStyle = 'table-row';
						}
						
						for(var i=0; i<elementsLength; i++) {
							elmt[i].style.display = elementDisplayStyle;
						}
					}
				} else {
					if($(elmt).is('tr')) {
						elmt.style.display = 'table-row';
					} else {
						elmt.style.display = 'block';
					}
				}
			}	
			stopTimer('fastShow');			
		};
		
		/**
		* Faster alternative to jQuerys' hide() method.
		*/
		fastHide = function(elements) {
			startTimer('fastHide');			
			if(elements) {
				var elmt = elements.jquery ? elements.get() : elements;
				if(elmt instanceof Array) {
					for(var i=0; i<elmt.length; i++) {
						elmt[i].style.display = 'none';
					}
				} else {
					elmt.style.display = 'none';
				}
			}
			stopTimer('fastHide');
		};
		
		/**
		* Faster alternative to jQuerys' replaceWith() method. 
		*/
		fastReplace = function(elementToReplace, replaceWith) {
			var parentElement = elementToReplace.parentNode;
			parentElement.insertBefore(replaceWith, elementToReplace);
			parentElement.removeChild(elementToReplace);
		};
		
		/**
		* Faster alternative to jQuerys' closest() method. 
		*/		
		fastGetParent = function(element, parentNodeToFind) {
			var parentNode = null;
			if (element != null) {				
				if (element.nodeType == 1 && (element.tagName.toLowerCase() == parentNodeToFind.toLowerCase())) {
					parentNode = element;
				} else {
					parentNode = fastGetParent(element.parentNode, parentNodeToFind);
				}
			}
			return parentNode; 
		};
		
		
		/**
		* Copy attributes from one element to another. The includeList and excludeList feature is currently not implemented. 
		*/
		copyAllAttributes = function(copyFrom, copyTo, includeList, excludeList) {
			var attributes = copyFrom.attributes;
			for(var i=0; i<attributes.length; i++) {
				copyTo[attributes[i].name] = attributes[i].value;
			}
		};
		
		
		/**
		* Browser independent function to trigger an event on an element.  
		*/
		fireEvent = function(element, eventName) {
			if (document.createEventObject) {
				// dispatch for IE
				var event = document.createEventObject();
				if(element.fireEvent) {
					logOnConsole('firing event');
					return element.fireEvent('on' + eventName, event);
				} else if(element.dispatchEvent) {
					event = document.createEvent("HTMLEvents");
					event.initEvent(eventName, true, true );
					logOnConsole('dispatching for ie');
					return !element.dispatchEvent(event);
				}
			} else {
				// dispatch for firefox + others
				var event = document.createEvent("HTMLEvents");
				event.initEvent(eventName, true, true ); // event type,bubbling,cancelable
				logOnConsole('non-ie dispatch');
				return !element.dispatchEvent(event);
			}
		};
		
		/**
		* Apply filter. ^Optimized 
		*/
		applyFilter = function(tableID) {
			logOnConsole('Filtering callback: ' + tableID);
			
			startTimer('applyFilter');
			
			loadTableSettings(tableID);
			
			var $tableToFilter = $('#' + tableID);
			
			var tableDOM = $tableToFilter[0];
			
			startTimer('get rows, add class, and show them');
			
			var $rows = $tableToFilter.find('tbody tr');
			
			fastAddClass($rows, 'filteredRow');			
			fastShow($rows);
			stopTimer('get rows, add class, and show them');
			
			var numberOfActiveFilters = settings.filterTableOptions.activeFilters.length;
						
			var resetFilters = (numberOfActiveFilters > 0) ? false : true;
					
			if(resetFilters === true) {
				fastShow($rows);
				logOnConsole('No filters active.');
			} else {
				for(var j=0; j<numberOfActiveFilters; j++) {
					var filter = settings.filterTableOptions.activeFilters[j];
								
					var columnIndex = filter.columnIndex;
					
					logOnConsole('columnIndex: ' + columnIndex);
					for(var i=0; i<tableDOM.rows.length; i++) { 						
						if(filter.type === 'checkbox') {
							columnValue = $.trim(tableDOM.rows[i].cells[columnIndex].innerHTML);
							
							logOnConsole('Column value: ' + columnValue + '. Filter expr: ' + filter.expr);
							
							if(columnValue !== filter.expr) {								
								fastRemoveClass(tableDOM.rows[i], 'filteredRow');
								tableDOM.rows[i].style.display = 'none';								
							}						
						} else if(filter.type === 'numeric') {
							columnValue = $.trim(tableDOM.rows[i].cells[columnIndex].innerHTML);
							
							logOnConsole('Column value: ' + columnValue + '. Filter expr: ' + filter.expr);
							
							if(filter.expr != columnValue) {
								fastRemoveClass(tableDOM.rows[i], 'filteredRow');
								tableDOM.rows[i].style.display = 'none';
							}
						} else {
							columnValue = $.trim(tableDOM.rows[i].cells[columnIndex].innerHTML);
							
							logOnConsole('Column value: ' + columnValue + '. Filter expr: ' + filter.expr);
							
							var pattern = new RegExp(filter.expr, 'i');	
							
							if(pattern.test(columnValue) === false) {								
								fastRemoveClass(tableDOM.rows[i], 'filteredRow');
								tableDOM.rows[i].style.display = 'none';						
							}						
						}	
						
					}
				}
			}
						
			logOnConsole('resetFilters: ' + resetFilters);
			
			settings.paginationOptions.linksCreated = false;
			
			resetToFirstPage(tableID, true); 
			
			stopTimer('applyFilter');
		};
		
		
		
		/*
		* Adds progress icon for the table. 
		*/
		addProgessBar = function(tableID) {
			loadTableSettings(tableID);
			
			var height = settings.fixHeaderOptions.height;
			var width = settings.fixHeaderOptions.width;
			
			var $outerDIV = $('#outerDiv_' + tableID);			
			var $progressDIV = $('<div style="filter: alpha(opacity=70); position: absolute; background-color: white; height: ' + height + 'px; width: ' + width + 'px; z-index: 50" id="progressDiv_' + tableID + '"></div>');
			
			$progressDIV.append('<table width="100%" height= "100%"><tr><td valign="middle" align="center"><b>Loading, Please wait...</b></td></tr></table>');
			
			$outerDIV.append($progressDIV);
		};
		
		/*
		* Shows progress icon for the table. 
		*/
		showProgess = function(tableID) {
			$('#progressDiv_' + tableID).show();
		};
		
		
		/*
		* Hides the progress icon for the table. 
		*/
		hideProgess = function(tableID) {
			$('#progressDiv_' + tableID).hide();
		};
		
		/**
		* Get common attributes from the element. ^Optimized 
		*/ 
		getAttributes = function(element) {
			var attr_arr = [];
			
			var eligibleAttributes = ['id', 'align', 'width', 'class', 'style'];
			
			var elementAttributes = element.attributes;
			
			var attribute = null;
			var attributeName = null;
			for (var i = 0; i < eligibleAttributes.length; i++){
			    attribute = new Object();
				attributeName = eligibleAttributes[i];
			    attribute.name = attributeName;
			    attribute.value = element.getAttribute(attributeName);	    
			    
				attr_arr.push(attribute);
			}		
			
			return attr_arr;
		};
		
		/**
		* Set common attributes for the element. ^Optimized 
		*/ 
		applyAttributes = function(element, attributesList) {
			var elementDOM = element[0];
			var attribute = null;
			for(var i=0; i<attributesList.length; i++) {				
				attribute = attributesList[i];				
				elementDOM.setAttribute(attribute.name, attribute.value);
			}
		};
		
		
		/**
		* Faster alternative to jQuerys' empty() function. 
		* Refer: http://jsperf.com/removechildren/8
		*/
		fastEmpty = function(container){
			var containerDOM = container[0];
			
			if(containerDOM && containerDOM.childNodes) {
				var len = containerDOM.childNodes.length;
				while (len--) {
					containerDOM.removeChild(containerDOM.lastChild);
				};
			}
		};
		
		/**
		 * Convert object to html. 
		 */
		objectToTable = function(objectArray, table) {
			startTimer('objectToTable');
			
			var $table = table;
			
			var $body = $table.find('tbody');
			
			fastEmpty($body);
			
			var $tr = null;
			for (var i = 0; i < objectArray.length; i++){
				
				$tr = $('<tr></tr>');
				
				applyAttributes($tr, objectArray[i].rowAttributes);
				
				var cell = null;
				for (var j=0 ; j<objectArray[i].rowData.length ; j++){
					cell = $('<td></td>').html(objectArray[i].rowData[j].val);
					applyAttributes(cell, objectArray[i].rowData[j].attributes);
					$tr.append(cell);
				}
				
				$body.append($tr);				
			}
			
			stopTimer('objectToTable');
		};
		
		/**
		 * Convert html to object. ^Optimized 
		 */
		tableToObject = function(table) {
			startTimer('tableToObject');
			
			var $table = table;
		
			var objectArray = [];
			
			var row = null;
			var rowData = null;
			var rowAttributes = null;
			$table.find('tbody tr').each(function(i){
				var $this = $(this);
				
				row = new Object();
				rowData = [];				
				rowAttributes = getAttributes(this);
				
				var col = null;
				$this.find('td').each(function(index){
					col = new Object();
					
					col.val = $(this).html();
					col.attributes = getAttributes(this); 
					
					rowData[j] = col;		
				});
				
				row.rowData = rowData;
				row.rowAttributes = rowAttributes;
				
				objectArray.push(row);
			});	

			stopTimer('tableToObject');
			
			return objectArray;
		};
		
		/**
		 * Convert object to html. 
		 */
		restoreTable = function(newRows, table) {
			startTimer('restoreTable');
			
			if(newRows && newRows.length > 0) {
				var $body = $(table).find('tbody');
				
				var tableBodyDOM = $body[0];
				
				fastEmpty($body);
				
				for (var i=0; i<newRows.length; i++) { 
					tableBodyDOM.appendChild(newRows[i]);
				}	
			}
			
			stopTimer('restoreTable');
		};
		
		/**
		 * Convert html to object. ^Optimized 
		 */
		backupRows = function(table) {
			startTimer('backupRows');
			
			var newRows = null;
			
			var tableDOM = table[0];
			
			if(tableDOM.rows.length > 0) {	    	    			
				newRows = new Array();	    
				for (j=0; j<tableDOM.rows.length; j++) { 
					newRows[j] = tableDOM.rows[j];   	
				}								
			} 

			stopTimer('backupRows');
			
			return newRows;
		};
		
		
		/**
		* Apply sorting on the table. ^Optimized 
		*/ 
		applySort = function(tableID) {
			
			logOnConsole('Sorting callback: ' + tableID);
			
			startTimer('applySort');
			
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID);
			
			var $fixedHeaderTable = $('#' + settings.fixHeaderOptions.fixedHeaderTable);
			
			var $headers = $fixedHeaderTable.find('thead tr th');
							
			var sortingIndex = settings.sortOptions.sortingState.columnIndex;
			
			var sortingUp = settings.sortOptions.sortingState.sortUp;
			
			var $sortingHeaderLink = $headers.eq(sortingIndex).find('a');
			
			if(sortingUp === true) {
				$sortingHeaderLink.addClass('tableUtils_sortUp');
			} else {
				$sortingHeaderLink.addClass('tableUtils_sortDown');
			}
			
			logOnConsole('sortingUp: ' + sortingUp);
			
			var sortFunction = null;
			if(settings.sortOptions.sortingState.sortFunction) {
				logOnConsole('custom sorting');
				sortFunction = function(a, b) {
					var x = Number($.trim(String(a.cells[sortingIndex].innerHTML)));
					var y = Number($.trim(String(b.cells[sortingIndex].innerHTML)));
					
					logOnConsole('comparing: ' + x + ' - ' + y + '. x >= y: ' + (x >= y));
					
					if(sortingUp === true) {
						return (settings.sortOptions.sortingState.sortFunction(x, y));
					} else {
						return (-1 * settings.sortOptions.sortingState.sortFunction(x, y));
					}					
				};				
			} else {
				if(settings.sortOptions.sortingState.type === 'numeric') {
					logOnConsole('numeric sorting');
					sortFunction = function(a, b) {
						var x = Number($.trim(String(a.cells[sortingIndex].innerHTML)));
						var y = Number($.trim(String(b.cells[sortingIndex].innerHTML)));
						
						logOnConsole('comparing: ' + x + ' - ' + y + '. x >= y: ' + (x >= y));
						
						if(sortingUp === true) {
							return ((x < y) ? -1 : ((x > y) ? 1 : 0));
						} else {
							return ((x > y) ? -1 : ((x < y) ? 1 : 0));
						}					
					};
				} else if(settings.sortOptions.sortingState.type === 'float') {
					logOnConsole('float sorting');
					sortFunction = function(a, b) {
						var x = parseFloat($.trim(String(a.cells[sortingIndex].innerHTML)));					
						var y = parseFloat($.trim(String(b.cells[sortingIndex].innerHTML)));

						logOnConsole('comparing: ' + x + ' - ' + y + '. x >= y: ' + (x >= y));					
						
						if(sortingUp === true) {
							return ((x < y) ? -1 : ((x > y) ? 1 : 0));
						} else {
							return ((x > y) ? -1 : ((x < y) ? 1 : 0));
						}					
					};
				} else if(settings.sortOptions.sortingState.type === 'alphanumeric') {
					logOnConsole('alphanumeric sorting');
					sortFunction = function(a, b) {
						var x = $.trim(String(a.cells[sortingIndex].innerHTML).toLowerCase());
						var y = $.trim(String(b.cells[sortingIndex].innerHTML).toLowerCase());
						
						logOnConsole('comparing: ' + x + ' - ' + y + '. x >= y: ' + (x >= y));
						
						if(sortingUp === true) {
							return ((x < y) ? -1 : ((x > y) ? 1 : 0));
						} else {
							return ((x > y) ? -1 : ((x < y) ? 1 : 0));
						}		
					};
				}
			}
				
			var objectTable = backupRows($mainTable);
				
			objectTable.sort(sortFunction);	
				
			restoreTable(objectTable, $mainTable);
			
			$mainTable.trigger('tableUpdated');
			
			if(settings.filterTableOptions.required === true) {
				applyFilter(tableID);
			} else {
				resetToFirstPage(tableID, true);	
			}
			
			stopTimer('applySort');
		};
		
		
		
		selectAllItems = function(tableID) {
			loadTableSettings(tableID);			
			
			var selector = 'tbody tr';
			
			if(settings.filterTableOptions.required === true) {
				selector += '.filteredRow';
			}
			
			var $mainTable = $('#' + tableID);
			
			var $rows = $mainTable.find(selector);
			
			var $checkboxes = $rows.find('td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ')').find('input:checkbox');
			
			$checkboxes.each(function(index) {
				$(this).attr('checked', true);
				$(this).trigger('change'); 
			});	
			
			$('#' + settings.masterCheckBoxOptions.masterCheckBox).attr('checked', true);	

			updateSelectedRecords(tableID);	
			
			$('#selectAllItemsControl_' + tableID).hide();
			$('#deSelectAllItemsControl_' + tableID).show();				
		};
		
		
		
		deSelectAllItems = function(tableID) {
			startTimer('deSelectAllItems');
			
			loadTableSettings(tableID);			
			
			var selector = 'tbody tr';
			
			if(settings.filterTableOptions.required === true) {
				selector += '.filteredRow';
			}
			
			var $mainTable = $('#' + tableID);
			
			var $rows = $mainTable.find(selector);
			
			var $checkboxes = $rows.find('td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ')').find('input:checkbox');
			
			$checkboxes.each(function(index) {
				$(this).attr('checked', false).trigger('change'); 
			});	
			
			$('#' + settings.masterCheckBoxOptions.masterCheckBox).attr('checked', false);			

			updateSelectedRecords(tableID);	
			
			$('#deSelectAllItemsControl_' + tableID).hide();
			$('#masterCBAdditionalControls_' + tableID).hide();	

			stopTimer('deSelectAllItems');
		};
		
		
		
		
		updateSelectedRecords = function(tableID) {
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID);
			
			var selector = 'tbody tr';
			if(settings.filterTableOptions.required === true) {
				selector += '.filteredRow';
			}
			
			logOnConsole('selector: ' + selector + ' td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ') input:checkbox:checked');
			var $totalSelectedRecords = $mainTable.find(selector + ' td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ') input:checkbox:checked');
			var totalNoOfSelectedRecords = $totalSelectedRecords.length; 
			logOnConsole('settings.masterCheckBoxOptions.columnIndex: ' + settings.masterCheckBoxOptions.columnIndex + '. totalNoOfSelectedRecords: ' + totalNoOfSelectedRecords);
			
			if(settings.paginationOptions.preserveSelection) {
				for(var x=0; x<$totalSelectedRecords.length; x++) {
					logOnConsole('Checking: ' + $totalSelectedRecords[x].value + '. Checked: ' + $totalSelectedRecords[x].checked);
					if(($.inArray($totalSelectedRecords[x].value, settings.paginationOptions.previouslySelectedRecords) !== -1) && $totalSelectedRecords[x].checked) {
						totalNoOfSelectedRecords--;
						logOnConsole('Matching selection found.');
					}
				}
				logOnConsole('Selected records: ' + settings.paginationOptions.previouslySelectedRecords.length);
				totalNoOfSelectedRecords += settings.paginationOptions.previouslySelectedRecords.length;
			}
			
			logOnConsole('totalNoOfSelectedRecords: ' + totalNoOfSelectedRecords);
			if(totalNoOfSelectedRecords > 0) {			
				settings.masterCheckBoxOptions.message.message = '<b>' + totalNoOfSelectedRecords + '</b> Item(s) Selected.';
				pushMessage(tableID, settings.masterCheckBoxOptions.message); 
			} else {
				popMessage(tableID, settings.masterCheckBoxOptions.message); 
			}
			
			saveTableSettings(tableID);
		};
		
		
		
		updateChildrenCheckBoxes = function(tableID) {
			if(settings.masterCheckBoxOptions.required === true) {
				loadTableSettings(tableID);
				var isMasterCheckBoxChecked = $('#' + settings.masterCheckBoxOptions.masterCheckBox).is(':checked');
				if(isMasterCheckBoxChecked === true) {
					toggleChildrenCheckBoxes(tableID, isMasterCheckBoxChecked); 
				} 
			}
		}; 
		
		
		/**
		* Toggles children check boxes depending on the value of master check box. 		
		*/
		toggleChildrenCheckBoxes = function(tableID, isMasterCheckBoxChecked) {			
			logOnConsole('Master checkbox changed: ' + tableID);
			
			startTimer('toggleChildrenCheckBoxes');
			
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID);	
			
			var eligibleCheckBoxesRows = $mainTable.find(settings.masterCheckBoxOptions.eligibleRowsSelector).get();//.find('td:nth-child(' + (settings.masterCheckBoxOptions.columnIndex) + ')').find('input:checkbox');
			
			for(var i=0; i<eligibleCheckBoxesRows.length; i++) {
				var chckbox = eligibleCheckBoxesRows[i].cells[settings.masterCheckBoxOptions.columnIndex - 1].getElementsByTagName('input');
				if(chckbox && chckbox.length > 0) {
					for(var j=0; j<chckbox.length; j++) {
						if(chckbox[j].type === 'checkbox') {
							chckbox[j].checked = isMasterCheckBoxChecked;
							//$(chckbox[j]).trigger('change');
							fireEvent(chckbox[j], 'change');
							
							if(!chckbox[j].checked) {
								removeItemFromPreviousSelection(chckbox[j].value, tableID);
							}
							
							if(isMasterCheckBoxChecked) {								
								fastAddClass(fastGetParent(chckbox[j], 'tr'), 'tableUtils_selectedRow');
							} else {								
								fastRemoveClass(fastGetParent(chckbox[j], 'tr'), 'tableUtils_selectedRow');
							}
						}
					}
				}
				
			}
			
			updateSelectedRecords(tableID);

			saveTableSettings(tableID);
			
			stopTimer('toggleChildrenCheckBoxes');
		};
		
		
		/**
		* Callback function when a checkbox is value is toggled. 
		*/ 
		childCheckBoxToggledHandler = function(tableID, checkboxElement) {		
			logOnConsole('Children checkbox changed: ' + tableID);
			
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID);
			
			var $eligibleCheckBoxCells = $mainTable.find(settings.masterCheckBoxOptions.eligibleRowsSelector).find('td:nth-child(' + settings.masterCheckBoxOptions.columnIndex + ')');
			
			var $allCheckBoxes = $eligibleCheckBoxCells.find('input:checkbox');
			var $checkedCheckBoxes = $eligibleCheckBoxCells.find('input:checkbox:checked');
			
			var $masterCheckBox = $('#' + settings.masterCheckBoxOptions.masterCheckBox);
			
			var totalNumberOfRecords =  $allCheckBoxes.length; 
			var numberOfSelectedRecords = $checkedCheckBoxes.length;
			
			if(numberOfSelectedRecords == 0) {
				$masterCheckBox.attr('checked', false);
			} else if(numberOfSelectedRecords == totalNumberOfRecords) {
				$masterCheckBox.attr('checked', true);
			} else {
				$masterCheckBox.attr('checked', false);
			}					
			
			if(checkboxElement && !checkboxElement.checked) {
				removeItemFromPreviousSelection(checkboxElement.value, tableID);
			}
			
			updateSelectedRecords(tableID);	
			
			saveTableSettings(tableID);
		}; 
		
		radioButtonClickEvent = function() {
			methods.getSelectedItem();			
		};
				
		resetToFirstPage = function(tableID, stayOnCurrentPage) {
			logOnConsole('Resetting to page 1 for table: ' + tableID);
			goToPage(tableID, 1, stayOnCurrentPage); 
			updateSelectedRecords(tableID);
		};
			
		updatePageSize = function(tableID) {
			loadTableSettings(tableID);
			settings.paginationOptions.pageSize = $('#pageSizeSelect_' + tableID).find('option:selected').val();
			settings.paginationOptions.linksCreated = false;
			if(settings.masterCheckBoxOptions.required === true) {
				$('#' + settings.masterCheckBoxOptions.masterCheckBox).attr('checked', false).trigger('hideControls');
			}						
			logOnConsole('new page size: ' + settings.pageSize);
			saveTableSettings(tableID);
			
			resetToFirstPage(tableID);
		};	
		
		updatePageLinks = function(tableID) {
			startTimer('updatePageLinks');
		
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID);
				
			var numRows = $mainTable.find(settings.paginationOptions.eligibleRowsSelector).length;
		
			if(settings.paginationOptions.serverSide === true) {
				numRows = settings.paginationOptions.totalRows;
			}
			
			var recordsOnThisPage = $mainTable.find(settings.paginationOptions.eligibleRowsSelector + '.currentPageRow').length;
		
			var numberOfPageLinks = settings.paginationOptions.numberOfPageLinks;
		
			var currentPage = settings.paginationOptions.currentPage; 

			var firstPage = ( ((currentPage-1) - ((currentPage-1)%settings.paginationOptions.displayPagesCount)) + 1 );	// The first page to display. 
			var lastPage = ( firstPage + settings.paginationOptions.displayPagesCount - 1);	// The last page to display.
			
			for(var page=1; page<=numberOfPageLinks; page++) {
				var $pageLinkContent = $('#paginationPage_' + tableID + '_' + page);
				if(page>=firstPage && page<=lastPage) {					
					$pageLinkContent.show();
				} else {
					$pageLinkContent.hide();
				}
				
				if(page == currentPage) {
					$pageLinkContent.removeClass('tableUtils_paginationLink');
					$pageLinkContent.addClass('tableUtils_paginationLinkSelected');
				} else {
					$pageLinkContent.removeClass('tableUtils_paginationLinkSelected');
					$pageLinkContent.addClass('tableUtils_paginationLink');
				}
			}
			

			if(currentPage == 1) {
				logOnConsole('first page. prev link: ' + $('#prevLink_' + tableID).html());
				$('#prevLink_' + tableID).find('a').attr('disabled', true);
			} else { 
				$('#prevLink_' + tableID).find('a').attr('disabled', false);
			}
			
			if(currentPage == settings.paginationOptions.numberOfPageLinks) {
				logOnConsole('last page. next link: ' + $('#nextLink_' + tableID).html());
				$('#nextLink_' + tableID).find('a').attr('disabled', true);
			} else { 
				$('#nextLink_' + tableID).find('a').attr('disabled', false);
			}
			
			logOnConsole('settings.paginationOptions.type: ' + settings.paginationOptions.type);
			if(settings.paginationOptions.type !== 'numeric') {
				if(settings.paginationOptions.serverSide) {
					$('#recordsOnThisPageInfo_' + tableID).html('&nbsp;&nbsp;Records: <b>' + numRows + '</b>').show(); 					
					$('#totalRecordsInfo_' + tableID).hide();
				} else {
					$('#recordsOnThisPageInfo_' + tableID).html('&nbsp;&nbsp;Records: <b>' + recordsOnThisPage + '</b>').show();
					$('#totalRecordsInfo_' + tableID).html('&nbsp;&nbsp;Total Records: <b>' + numRows + '</b>').show();
				}
				$('#pageSizeSelectSpan_' + tableID).hide();
				$('#pageSizeSelect_' + tableID).hide();
				$('#pageSizeInfo_' + tableID).hide();
			} else {
				logOnConsole('recordsOnThisPage: ' + recordsOnThisPage);
				$('#recordsOnThisPageInfo_' + tableID).hide(); 				
				$('#pageSizeSelectSpan_' + tableID).show();
				$('#pageSizeSelect_' + tableID).val(settings.paginationOptions.pageSize).show();
				$('#pageSizeInfo_' + tableID).html('&nbsp;&nbsp;Page Size: <b>' + settings.paginationOptions.pageSize + '</b>').show(); 
				$('#totalRecordsInfo_' + tableID).html('&nbsp;&nbsp;Total Records: <b>' + numRows + '</b>').show(); 
			}
			
			$('#currentPageInfo_' + tableID).html('&nbsp;&nbsp;Page: <b>' + currentPage + '</b> of ' + numberOfPageLinks); 						
		
			saveTableSettings(tableID);	
			
			stopTimer('updatePageLinks');
			
		};
		
		
		createLinks = function(tableID) {
			logOnConsole('creating links for: ' + tableID);
			
			startTimer('createLinks');
			
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID);
			
			var $rows = $mainTable.find(settings.paginationOptions.eligibleRowsSelector);
			
			logOnConsole('settings.paginationOptions.eligibleRowsSelector: ' + settings.paginationOptions.eligibleRowsSelector);
			
			var $links = $('<span></span>');
			
			var numRows = $rows.length;
				
			if(settings.paginationOptions.serverSide === true) {
				numRows = settings.paginationOptions.totalRows; 
			}
			
			//if(numRows > 0) {
				if(settings.paginationOptions.type === 'numeric') {				
					logOnConsole('total rows: ' + numRows);
					
					var pageSize = settings.paginationOptions.pageSize;
				
					var numberOfPageLinks = Math.ceil(numRows / pageSize);
					
					settings.paginationOptions.numberOfPageLinks = numberOfPageLinks;
									
					var $prevLinkContent = $('<span class="tableUtils_paginationLink"></span>').attr('id', 'prevLink_' + tableID);
					var $prevLink = $('<a href="#">Prev</a>');
					$prevLink.on('click', function(e) {
						e.preventDefault();
						previousPage(tableID);
					});
					$prevLinkContent.append($prevLink);				
					$links.append($prevLinkContent);
					
					
					for(var page=1; page<=numberOfPageLinks; page++) {
						logOnConsole('creating page link: ' + page);
						var $pageLinkContent = $('<span class="tableUtils_paginationLink"></span>').attr('id', 'paginationPage_' + tableID + '_' + page);
						var $pageLink = $('<a href="#" onclick="return goToPage(\'' + tableID + '\', '+ page + ');">' + page + '</a>');
						
						$pageLinkContent.append($pageLink);				
						$links.append($pageLinkContent);						
					}
					
					
					var $nextLinkContent = $('<span class="tableUtils_paginationLink"></span>').attr('id', 'nextLink_' + tableID);
					var $nextLink = $('<a href="#">Next</a>');
					$nextLink.on('click', function(e) {
						e.preventDefault();
						nextPage(tableID);
					});
					$nextLinkContent.append($nextLink);				
					$links.append($nextLinkContent);
					
					var $pageSelect = $('#pageSelect_' + tableID);
					$pageSelect.empty();
					for(var page = 1; page<= numberOfPageLinks; page++) {
						$pageSelect.append($('<option>', {
							text: page, value: page
						}));
					}				
					$pageSelect.val(settings.paginationOptions.currentPage);
					
				} else if(settings.paginationOptions.type === 'alphabetic' || settings.paginationOptions.type === 'alphanumeric') {
								
					var numberOfPageLinks = 26;
					if(settings.paginationOptions.type === 'alphanumeric') {
						numberOfPageLinks = 36;
					} 
					
					logOnConsole('no of pages: ' + numberOfPageLinks);
					
					settings.paginationOptions.numberOfPageLinks = numberOfPageLinks;				
					
					var $prevLinkContent = $('<span class="tableUtils_paginationLink"></span>').attr('id', 'prevLink_' + tableID);
					var $prevLink = $('<a href="#">Prev</a>');
					$prevLink.on('click', function(e) {
						e.preventDefault();
						previousPage(tableID);
					});
					$prevLinkContent.append($prevLink);				
					$links.append($prevLinkContent);
					
					
					for(var page=1; page<=numberOfPageLinks; page++) {
						var $pageLinkContent = $('<span class="tableUtils_paginationLink"></span>').attr('id', 'paginationPage_' + tableID + '_' + page);
						var $pageLink = $('<a href="#" onclick="return goToPage(\'' + tableID + '\', '+ page + ');">' + settings.paginationOptions.pageMappings[page] + '</a>');
						
						$pageLinkContent.append($pageLink);				
						$links.append($pageLinkContent);						
					}
					
					
					var $nextLinkContent = $('<span class="tableUtils_paginationLink"></span>').attr('id', 'nextLink_' + tableID);
					var $nextLink = $('<a href="#">Next</a>');
					$nextLink.on('click', function(e) {
						e.preventDefault();
						nextPage(tableID);
					});
					$nextLinkContent.append($nextLink);				
					$links.append($nextLinkContent);
					
					var $pageSelect = $('#pageSelect_' + tableID);
					$pageSelect.empty();
					for(var page = 1; page<= numberOfPageLinks; page++) {
						$pageSelect.append($('<option>', {
							text: settings.paginationOptions.pageMappings[page], value: page
						}));
					}
					$pageSelect.val(settings.paginationOptions.currentPage);
				}	
				
				$('#paginationLinks_' + tableID).empty().append($links);
				
				$('#paginationStats_' + tableID).show();
				
				logOnConsole(numRows + ' records found.');
				
				settings.paginationOptions.message.message = '<b>' + numRows + '</b> record(s) found.';
				pushMessage(tableID, settings.paginationOptions.message); 
				
				settings.paginationOptions.linksCreated = true;
			//} else {

			if(numRows < 1) {
				if(settings.paginationOptions.type === 'numeric') {
					$('#paginationLinks_' + tableID).empty();
				} 
								
				logOnConsole('No records found.');
				
				settings.paginationOptions.message.message = '<b>No records found.</b>';
				pushMessage(tableID, settings.paginationOptions.message); 
				
				settings.paginationOptions.linksCreated = false;
			}
						
			saveTableSettings(tableID);
			stopTimer('createLinks');
			
		};
		
		
		goToPage = function(tableID, pageNumber, stayOnCurrentPage) {
			loadTableSettings(tableID);
			var goToPageNumber = pageNumber;
			logOnConsole('stayOnCurrentPage: ' + stayOnCurrentPage + '. settings.paginationOptions.type: ' + settings.paginationOptions.type);
			if(stayOnCurrentPage && settings.paginationOptions.type !== 'numeric') {
				goToPageNumber = settings.paginationOptions.currentPage;
			}
			logOnConsole('Going to page: ' + goToPageNumber + ' for table: ' + tableID + '. Current page: ' + settings.paginationOptions.currentPage);
			
			if(settings.paginationOptions.required === true) {
				if(settings.paginationOptions.serverSide === false) {								
					logOnConsole('links created: ' + settings.paginationOptions.linksCreated);
					if(!settings.paginationOptions.linksCreated) {
						logOnConsole('Creating links');
						createLinks(tableID);
						logOnConsole('End creating links');
					}					
					showPage(tableID, pageNumber);					
					applyTableStyling(tableID); 
				} else {
					fetchPage(tableID, goToPageNumber); 
				}				
			} else {
				applyTableStyling(tableID); 
			}
			return false;
		};
		
		var timers = new Array();		
		startTimer = function(task) {
			var depth = '';
			for(var i=0; i<=timers.length; i++) {
				depth += '> ';
			}
			logOnConsole(depth + 'Starting: ' + task);
			var start = new Date().getTime();
			timers.push(start);			
		};
		
		stopTimer = function(task) {
			if(timers.length > 0) {
				var end = new Date().getTime();
				var start = timers.pop();
				var depth = '';
				for(var i=0; i<=timers.length; i++) {
					depth += '< ';
				}
				logOnConsole(depth + 'Complete: ' + task + ' in ' + (end - start) + ' ms.');				
			} else {
				logOnConsole('No active timers found.');
			}
		};
		
		showPage = function(tableID, pageNumber) {
			startTimer('showPage');
						
			logOnConsole('showing page: ' + pageNumber + ' for: ' + tableID);
			
			loadTableSettings(tableID);
			
			var rowsOnPage = 0;
			
			logOnConsole('no of pages: ' + settings.paginationOptions.numberOfPageLinks);
			if(pageNumber > 0 && pageNumber <= settings.paginationOptions.numberOfPageLinks) {
				
				
				settings.paginationOptions.currentPage = pageNumber;				
				
				var $mainTable = $('#' + tableID); 
			
				var $rows = $mainTable.find(settings.paginationOptions.eligibleRowsSelector);
				
				var numRows = $rows.length;
				
				var pageSize = settings.paginationOptions.pageSize;
				
				logOnConsole('numRows: ' + numRows);
				
				if(settings.paginationOptions.type === 'numeric') {					
					var startRow = ((pageNumber - 1) * pageSize) + 1;
					logOnConsole('startRow: ' + startRow);
					
					var endRow = Number(startRow) + Number(pageSize);
					logOnConsole('endRow: ' + endRow);
					
					for(var i=0; i<numRows; i++) {
						if((i+1)>=startRow && (i+1)<endRow) {
							$rows.eq(i).addClass('currentPageRow');
							$rows.eq(i).show();
							rowsOnPage++;
						} else {
							$rows.eq(i).removeClass('currentPageRow');
							$rows.eq(i).hide();
						}
					}					
				} else if(settings.paginationOptions.type === 'alphabetic' || settings.paginationOptions.type === 'alphanumeric') {					
					logOnConsole('alphanumeric filtering');
					
					var pageMappings = settings.paginationOptions.pageMappings;
					
					
					for(var i=0; i<numRows; i++) {
						logOnConsole('row: ' + i);
						var columnValue = $.trim($rows.eq(i).find('td:nth-child(' + settings.paginationOptions.columnIndex + ')').text()).substring(0, 1).toUpperCase();
						logOnConsole(settings.paginationOptions.columnIndex + ' column value: ' + columnValue);
						if(columnValue === pageMappings[pageNumber]) {
							$rows.eq(i).addClass('currentPageRow');
							$rows.eq(i).show();
							rowsOnPage++;
						} else {
							$rows.eq(i).removeClass('currentPageRow');
							$rows.eq(i).hide();
						}
					}
				}
				
				saveTableSettings(tableID);
				
				updatePageLinks(tableID);				
			}
			
			stopTimer('showPage');
			
			return rowsOnPage;
		};
		
		
		previousPage = function(tableID) {
			loadTableSettings(tableID);
			
			goToPage(tableID, Number(settings.paginationOptions.currentPage) - 1);
		};
		
		
		nextPage = function(tableID) {
			loadTableSettings(tableID);
			
			goToPage(tableID, Number(settings.paginationOptions.currentPage) + 1);
		};
		
		
		firstPage = function(tableID) {
			goToPage(tableID, 1);
		};
		
		
		lastPage = function(tableID) {
			loadTableSettings(tableID);
			
			goToPage(tableID, settings.paginationOptions.numberOfPageLinks);
		};
		
		
		/**
		* Fetches a page of record. 
		*/
		fetchPage = function(tableID, page) {
			startTimer('fetchPage');
			logOnConsole('Fetching page: ' + page + ' for table: ' + tableID);
			loadTableSettings(tableID);
			
			logOnConsole('settings.paginationOptions.columnIndex - 1: ' + (settings.paginationOptions.columnIndex - 1));
			
			// The parameters we need to pass for fetching the page. 
			var fetchQueryParameters = {
				pageSize: settings.paginationOptions.pageSize,				
				currentPage: page, 
				start: (((page-1) * settings.paginationOptions.pageSize) + 1),
				end: (page * settings.paginationOptions.pageSize),
				sortingDetails: settings.sortOptions.sortingState,	 				
				filteringDetails: settings.filterTableOptions.activeFilters,
				type: settings.paginationOptions.type,
				columnName: settings.columns[settings.paginationOptions.columnIndex - 1].value, 
				columnIndex: settings.paginationOptions.columnIndex 		
			};
			
			var additionalParams = new Array();
			if(settings.paginationOptions.params) {
				additionalParams = settings.paginationOptions.params;
			}
			
			var finalParams = new Object();
			finalParams.params = JSON.stringify(fetchQueryParameters);
			for(var i=0; i<additionalParams.length; i++) {
				finalParams[additionalParams[i].name] = additionalParams[i].value;
			}
						
			// Make an ajax call to fetch the page. 
			$.ajax({
			
				url: settings.paginationOptions.fetchUrl, 
				
				data: finalParams,	
				
				beforeSend: function() {	
					if(!settings.paginationOptions.beforeSend || (settings.paginationOptions.beforeSend && (settings.paginationOptions.beforeSend() === true))) {
						settings.paginationOptions.message.message = '<i>Fetching Records, please wait...</i>';
						settings.paginationOptions.message.block = true;
						pushMessage(tableID, settings.paginationOptions.message); 
					} else {
						return false;
					}
					
					saveCurrentSelection(tableID);
					
					showProgess(tableID);
					
					startTimer('fetchPage ajax call');
				}, 	
				
				success: function(data) {
					settings.paginationOptions.message.block = false;
					popMessage(tableID, settings.paginationOptions.message);
					
					stopTimer('fetchPage ajax call');
					
					startTimer('process fetched records');

					logOnConsole('Got page: ' + page + ' for table: ' + tableID);
					loadTableSettings(tableID);
					
					settings.paginationOptions.currentPage = fetchQueryParameters.currentPage;
					settings.paginationOptions.start = fetchQueryParameters.start;
					settings.paginationOptions.end = fetchQueryParameters.end;										
					settings.paginationOptions.fetchedData = data; 
					
					if(settings.paginationOptions.useDynamicData) {
						settings.paginationOptions.totalRows = data.totalRows;
					} else {
						if(data && data.length>0) {						
							settings.paginationOptions.totalRows = data[0].totalRows; 
						} else {
							settings.paginationOptions.totalRows = 0; 
						}
					}
					
					logOnConsole('totalRows: ' + settings.paginationOptions.totalRows);
					
					saveTableSettings(tableID);
					
					createLinks(tableID); 
					
					updatePageLinks(tableID);
					
					if(settings.paginationOptions.useDynamicData) {
						populateDynamicTable(tableID, data); 
					} else {
						populateTable(tableID, data); 
					}
					
					$('#' + tableID).trigger('tableUpdated');
					
					applyTableStyling(tableID); 
					
					updateSelectedRecords(tableID);
					
					stopTimer('process fetched records');
				}, 	
				
				error: function(xhr, textStatus, error) {
					popMessage(tableID, settings.paginationOptions.message);
					settings.paginationOptions.message.message = '<b>The following error occurred while loading data: ' + getAjaxErrorDescription(xhr, textStatus, error) + '</b>.';
					pushMessage(tableID, settings.paginationOptions.message); 
				},
				
				complete: function() {					
					if(settings.paginationOptions.complete) {
						settings.paginationOptions.complete();
					}
										
					restorePreviousSelection(tableID);
					
					hideProgess(tableID);
					
					stopTimer('fetchPage');
					//$('#outermostDiv_' + tableID).attr('disabled', false);
				},
				
				// Type of data to be returned from server. 
				dataType: 'json',
				
				// Do not cache the request. 
				cache: false
			});		

			
		};
		
		
		getIndexedProperty = function(obj, propString) {
			if (!propString) { 
				return obj;
			} else {
				var prop, props = propString.split('.');

				for (var i = 0, iLen = props.length - 1; i < iLen; i++) {
					prop = props[i];
					if (typeof obj == 'object' && obj !== null && prop in obj) {
						obj = obj[prop];
					} else {
						break;
					}
				}
				return obj[props[i]];
			}
		};
		/**
		* Populates the table with newly fetced rows. 
		*/
		populateTable = function(tableID, data) {			 			
			startTimer('populateTable');
			
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID); 
						
			logOnConsole('Rows before populating table: ' + $mainTable.find('tbody tr').length);
			
			$mainTable.find('tbody').empty();
			
			logOnConsole('Rows before clearing table: ' + $mainTable.find('tbody tr').length);
			
			if(data && data.length > 0) {			
				$.each(data, function(index, row) {
					var newColumns = [];
					
					logOnConsole('Creating row: ' + index);
					
					$.each(settings.columns, function(index, column) {
						logOnConsole('Column label: ' + column.label + '. Name: ' + column.name);
						
						var newColumn = null;
						
						var columnData = '';
						if(column.generate) {
							columnData = column.generate(row);
						} else {
							if(column.name.indexOf('.') != -1) {
								columnData = getIndexedProperty(row, column.name);
							} else {
								columnData = row[column.name];
							}
						}
						
						if(column.style) {
							newColumn = new Object();
							newColumn.html = columnData;
							if(column.style) {
								newColumn.props = column.style;
							}
							
							logOnConsole('Styled Column ' + index + ' - ' + columnData);
						} else {
							newColumn = columnData;
							
							logOnConsole('Simple Column ' + index + ' - ' + columnData);
						}
						
						newColumns.push(newColumn);
					}); 
									
					methods.addRow({ tableID: tableID, columns: newColumns });
				});	
			}

			stopTimer('populateTable');
		};
		
		
		/**
		* Populates the table with newly fetced rows. 
		*/
		populateDynamicTable = function(tableID, data) {			 			
			startTimer('populateTable');
			
			loadTableSettings(tableID);
			
			var $mainTable = $('#' + tableID); 
						
			logOnConsole('Rows before populating table: ' + $mainTable.find('tbody tr').length);
			
			$mainTable.find('tbody').empty();
			
			logOnConsole('Rows before clearing table: ' + $mainTable.find('tbody tr').length);			
			
			$.each(data.rows, function(index, row) {
				var newColumns = [];
				
				logOnConsole('Creating row: ' + index);
								
				$.each(settings.columns, function(index, column) {
					logOnConsole('Column label: ' + column.label + '. Name: ' + column.name);
					
					var newColumn = null;
					
					newColumn = row.row[column.name];
						
					logOnConsole('Simple Column ' + index + ' - ' + newColumn);
					
					newColumns.push(newColumn);
				}); 
								
				methods.addRow({ tableID: tableID, columns: newColumns });
			});	

			stopTimer('populateTable');
		};
		
		
		
		clearMessagesInterval = function(tableID) {
			loadTableSettings(tableID);
			
			if(!settings.fixHeaderOptions.disableMessages) {
			
				clearInterval(settings.fixHeaderOptions.messageLoop);
				
				settings.fixHeaderOptions.messageLoop = setInterval( function() { updateMessages(tableID); }, settings.fixHeaderOptions.messageLoopInterval);
				
				saveTableSettings(tableID);
			}
		};
		
		
		setNextMessage = function(tableID, message) {
			loadTableSettings(tableID);
			
			if(!settings.fixHeaderOptions.disableMessages) {
			
				var nextMsgIndex = -1;
				$.each(settings.fixHeaderOptions.messages, function(index, msg) {
					if(message.type === msg.type) {
						nextMsgIndex = index;
					}
				});
				
				settings.fixHeaderOptions.nextMessageIndex = nextMsgIndex;
				
				saveTableSettings(tableID);			
			}
		}; 
				
		
		/**
		* Push a message into the messages loop and update the messages. 
		*/
		pushMessage = function(tableID, message) {
			loadTableSettings(tableID);
			
			if(!settings.fixHeaderOptions.disableMessages) {			
				logOnConsole('pushing message: ' + message.type);			
				settings.fixHeaderOptions.messages = $.grep(settings.fixHeaderOptions.messages, function(msg, msgIndex) {
					return (msg.type === message.type);
				}, true);
				
				settings.fixHeaderOptions.messages.push(message);
				
				saveTableSettings(tableID);
				
				setNextMessage(tableID, message);
				
				clearMessagesInterval(tableID);
				
				updateMessages(tableID);
			}
			
		}; 
		
		
		/**
		* Pop out a message from the messages loop and update the messages. 
		*/ 
		popMessage = function(tableID, message) {
			loadTableSettings(tableID);
			
			if(!settings.fixHeaderOptions.disableMessages) {
			
				settings.fixHeaderOptions.messages = $.grep(settings.fixHeaderOptions.messages, function(msg, msgIndex) {
					return (msg.type === message.type);
				}, true);
				
				settings.fixHeaderOptions.nextMessageIndex = 0;
				
				saveTableSettings(tableID);
				
				clearMessagesInterval(tableID);
				
				updateMessages(tableID);
			}
		}; 
		
		/**
		* Save selection on the current page if any. 
		*/
		saveCurrentSelection = function(tableID) {
			loadTableSettings(tableID);
			if(settings.paginationOptions.preserveSelection) {
				var ids = methods.getSelectedRecordsOnPage(null, tableID);
				
				if(settings.paginationOptions.resetPreviousSelection) {
					settings.paginationOptions.previouslySelectedRecords = new Array();
					settings.paginationOptions.resetPreviousSelection = false;
				}
				
				for(var x=0; x<ids.length; x++) {
					if($.inArray(ids[x], settings.paginationOptions.previouslySelectedRecords) === -1) {
						settings.paginationOptions.previouslySelectedRecords.push(ids[x]);
					}
				}
				
				logOnConsole('Total items selected previously: ' + settings.paginationOptions.previouslySelectedRecords.length);
				saveTableSettings(tableID);
			}
		};
		
		/**
		* Restore selections on previous pages. 
		*/
		restorePreviousSelection = function(tableID) {					
			loadTableSettings(tableID);
			if(settings.paginationOptions.preserveSelection) {
				logOnConsole('Restoring: ' + settings.paginationOptions.previouslySelectedRecords.length + ' items.');
				for(var x=0; x<settings.paginationOptions.previouslySelectedRecords.length; x++) {							
					$(settings.paginationOptions.getCheckboxSelector(settings.paginationOptions.previouslySelectedRecords[x])).attr('checked', true).trigger('change');
				}
			}
		};
		
		
		/**
		* Remove the given item from selection. 		
		*/ 
		removeItemFromPreviousSelection = function(itemValue, tableID) {
			loadTableSettings(tableID);
			if(settings.paginationOptions.preserveSelection) {
				printArray(settings.paginationOptions.previouslySelectedRecords);
				var indexOfItem = $.inArray(itemValue, settings.paginationOptions.previouslySelectedRecords);
				logOnConsole('itemValue: ' + itemValue + '. indexOfItem: ' + indexOfItem);
				if(indexOfItem !== -1) {
					settings.paginationOptions.previouslySelectedRecords.splice(indexOfItem, 1);
					logOnConsole(itemValue + ' removed from previous selection.');
				}
				printArray(settings.paginationOptions.previouslySelectedRecords);				
				saveTableSettings(tableID);
			}
		};
		
		
		/**
		* Print all previously selected items. 
		*/
		printArray = function(arr, toStringFunction) {
			for(var i=0; i<arr.length; i++) {
				if(toStringFunction) {
					logOnConsole(toStringFunction(arr[i]));
				} else {
					logOnConsole(arr[i] + ' ');
				}
			}
		};
		
		
		/**
		* Update messages for the table. ^Optimized 
		*/
		updateMessages = function(tableID) {
			loadTableSettings(tableID);
			
			if(!settings.fixHeaderOptions.disableMessages) {
			
				var msgs = settings.fixHeaderOptions.messages;
				
				var numMsgs = msgs.length;
				
				//logOnConsole('Total msgs in queue: ' + numMsgs);
				
				var $messagesArea = $('#' + settings.fixHeaderOptions.messagesArea);
				
				//logOnConsole('messagesArea for: ' + tableID + ' - ' + settings.fixHeaderOptions.messagesArea);
				
				if(numMsgs > 0) {
					var nextMsgIndex = settings.fixHeaderOptions.nextMessageIndex;
					
					//logOnConsole('Showing msg: ' + nextMsgIndex);
					
					$messagesArea.show().html(msgs[nextMsgIndex].message);					
					
					if(msgs[nextMsgIndex].block) {
						//logOnConsole('Message: ' + nextMsgIndex + ' blocked');
						settings.fixHeaderOptions.nextMessageIndex = nextMsgIndex;
					} else {
						nextMsgIndex = (nextMsgIndex + 1) % numMsgs;
						settings.fixHeaderOptions.nextMessageIndex = nextMsgIndex;
					}
					
					//logOnConsole('Next msg: ' + nextMsgIndex);
					
					if(numMsgs == 1) {
						clearInterval(settings.fixHeaderOptions.messageLoop);
					}
					
					saveTableSettings(tableID);
				} else {
					//logOnConsole('No more msgs'); 
					$messagesArea.empty().hide();
					clearInterval(settings.fixHeaderOptions.messageLoop);
				}
				
				saveTableSettings(tableID);
			}	
		};
		
		
		/**
		* Returns the selector for all elegible rows for the current table. 
		*/
		getAllEligibleRowsFilter = function(tableID) {
			loadTableSettings(tableID);
			var eligibleRowsSelector = '';
			if(settings.masterCheckBoxOptions.required === true) {
				eligibleRowsSelector = settings.masterCheckBoxOptions.eligibleRowsSelector;
			} else {
				eligibleRowsSelector = 'tbody tr';
				if(settings.filterTableOptions.required === true) {
				 eligibleRowsSelector += '.filteredRow';
				}				    
				if(settings.paginationOptions.required === true) {
				 eligibleRowsSelector += '.currentPageRow';
				}
			}
			return eligibleRowsSelector;
		}
					
		
		/**
		* Apply styling to table. ^Optimized 
		*/
		applyTableStyling = function(tableID) {
			startTimer('Applying style');
			
			var rows = $('#' + tableID).find(getAllEligibleRowsFilter(tableID)).get();
			fastRemoveClass(rows, 'evenRow');
			fastRemoveClass(rows, 'oddRow');
			for(var i=0; i<rows.length; i++) {
				fastAddClass(rows[i], 'evenRow');
				i++;
				fastAddClass(rows[i], 'oddRow');
			}		
			
			stopTimer('Applying style');
		};	
		
		
		/**
		 * Check if console is available. If yes, print, else ignore.
		 */
		logOnConsole = function(msg) {
			/*if(settings.printLog && console) {
				console.log(msg);
			}*/
		};
		
		
		/**
		 * Get the type of column from the given Column type ID and DB type ID. 
		 */
		getColumnTypeForDB = function(columnTypeID, dbTypeID) {
			var columnType = 'alphanumeric';
			var type = Number(columnTypeID);
			logOnConsole('type: ' + type);
			if(type == 4 || type == 5 || type == -5) {
				columnType = 'numeric';
			} 
			logOnConsole('columnType: ' + columnType);
			return columnType;
		};
		
		
		/**
		 * Get the description of an AJAX error. 
		 * @param xhr The jQuery XMLHttpRequest (jqXHR) object. 
		 * @param textStatus A string describing the type of error that occurred. Possible values null, "timeout", "error", "abort", and "parsererror". 
		 * @param error Exception object, if an exception occurred.
		 * @returns {String}
		 */
		getAjaxErrorDescription = function(xhr, textStatus, error) {
			return xhr.responseText; 
		};
		
		
		/**
		* This is where calls from pages come. Calls requested functions appropriately. 
		*/ 
		$.fn.tableutils = function( method ) {
			// If the method parameter is present, then call the method, else call the default method i.e. init. 
			if( methods[method] ) {
				return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
			} else if ( !method || typeof method === 'object' ) {
				return methods.init.apply(this, arguments); 
			} else {
				$.error('Method ' + method + ' does not exist on jQuery.tableutils');
			}
		}; 
	}
) (jQuery) ;

