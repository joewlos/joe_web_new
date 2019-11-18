// Parsers for the data
var parseDateLong = d3.time.format("%Y-%m-%d %H:%M").parse;
var parseDateShort = d3.time.format("%Y-%m").parse;
var bisectDate = d3.bisector(function(d) { return d.DateExecuted; }).left;

// Function for drawing the line graph
function lineGraph(fromFlask) {
	var data = fromFlask;

	// Set the dimensions of the svg
	var margin = {top: 30, right: 50, bottom: 30, left: 50};
	var svgWidth = 1000;
	var svgHeight = 333;
	var graphWidth = svgWidth - margin.left - margin.right;
	var graphHeight = svgHeight - margin.top - margin.bottom;

	// Define the x and y axis
	var x = d3.time.scale().range([0, graphWidth]);
	var y = d3.scale.linear().range([graphHeight, 0]);
	var xAxis = d3.svg.axis()
		.scale(x).orient("bottom").ticks(12);
	var yAxis = d3.svg.axis()
		.scale(y).orient("left").ticks(5)
		.tickFormat( function(d) { return "$" + d } );

	// Add the line for total
	var totalLine = d3.svg.line()
		.x(function(d) { return x(d.DateExecuted); })
		.y(function(d) { return y(d.Total); });

	// Add the line for starting cash
	var startLine = d3.svg.line()
		.x(function(d) { return x(d.DateExecuted); })
		.y(function(d) { return y(d.Start); });

	// Add the canvas to the HTML
	var svg = d3.select("#lineDiv")
		.append("svg")
			.attr('width', svgWidth)
			.attr('height', svgHeight)
			.call(responsivefy)
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	// Add the focus to the chart
	var focus = svg.append("g")
		.style("display", "none");

	// Parse the data
	data.forEach(function(d) {
		d.DateExecuted = parseDateLong(d.DateExecuted);
		d.Total = +d.Total;
		d.Start = +50;
	});

	// Scale the range of the data
	x.domain(d3.extent(data, function(d) { return d.DateExecuted; }));
	y.domain([d3.min(data, function(d) {
		return Math.round((Math.min(d.Total) - 10) / 10) * 10 }),
	d3.max(data, function(d) {
		return Math.round((Math.max(d.Total) + 10) / 10) * 10 })]);

	// Add the total as a blue line
	svg.append("path")
		.style("stroke", "#089fba")
		.style("fill", "none")
		.attr("class", "line")
		.attr("d", totalLine(data));

	// Add the start as a dashed line
	svg.append("path")
		.style("stroke", "#253b40")
		.style("stroke-dasharray", ("5, 10"))
		.attr("class", "line")
		.attr("d", startLine(data));

	// Add the x axis
	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + graphHeight + ")")
		.call(xAxis);
	
	// Add the y axis
	svg.append("g")
		.attr("class", "y axis")
		.call(yAxis);

	// Append the circle at the intersection               
	focus.append("circle")                                 
		.attr("class", "y")                                
		.style("fill", "none")                             
		.style("stroke", "#089fba")
		.style("stroke-width", "2px")                        
		.attr("r", 4);                                     

	// Place the text value at the intersection
	focus.append("text")
		.attr("class", "y1")
		.style("stroke", "white")
		.style("stroke-width", "3.5px")
		.style("opacity", 0.8)
		.attr("dx", 8)
		.attr("dy", "1rem");
	focus.append("text")
		.attr("class", "y2")
		.attr("dx", 8)
		.attr("dy", "1rem");

	// Append the rectangle to capture mouse               
	svg.append("rect")                                     
		.attr("width", graphWidth)                              
		.attr("height", graphHeight)                            
		.style("fill", "none")                             
		.style("pointer-events", "all")                    
		.on("mouseover", function() { focus.style("display", null); })
		.on("mouseout", function() { focus.style("display", "none"); })
		.on("mousemove", mousemove);                       

	// Function for capturing mouse movement
	function mousemove() {                                 
		var x0 = x.invert(d3.mouse(this)[0]),             
			i = bisectDate(data, x0, 1),   
			d0 = data[i - 1],                          
			d1 = data[i],                              
			d = x0 - d0.DateExecuted > d1.DateExecuted - x0 ? d1 : d0;   

		// Add the circle and text
		focus.select("circle.y")
			.attr("transform", "translate(" + x(d.DateExecuted) + "," + y(d.Total) + ")");
		focus.select("text.y1")
			.attr("transform", "translate(" + x(d.DateExecuted) + "," + y(d.Total) + ")")
			.text("$" + d.Total.toFixed(2));
		focus.select("text.y2")
			.attr("transform", "translate(" + x(d.DateExecuted) + "," + y(d.Total) + ")")
			.text("$" + d.Total.toFixed(2));
	} 

	// Make the graph size responsive - https://benclinkinbeard.com/d3tips/
	function responsivefy(svg) {

		// Get the aspect ratio
		const container = d3.select(svg.node().parentNode),
		width = parseInt(svg.style('width'), 10),
		height = parseInt(svg.style('height'), 10),
		aspect = width / height;

		// Set viewbox to initial size
		svg.attr('viewBox', `0 0 ${width} ${height}`)
			.attr('preserveAspectRatio', 'xMinYMid')
			.call(resize);

		// Add a listener so the chart will be resized
		d3.select(window).on(
			'resize.' + container.attr('id'), 
			resize
		);

		// Function to resize the chart
		function resize() {
			const w = parseInt(container.style('width'));
			svg.attr('width', w);
			svg.attr('height', Math.round(w / aspect));
		}
	}
}

// Function for drawing the line graph
function barGraph(fromFlask) {
	var data = fromFlask;

	// Set the dimensions of the svg using the month table so they are the same size
	var margin = {top: 30, right: 50, bottom: 30, left: 50};
	var svgWidth = parseInt(d3.select(".month-table").style("width"));
	var svgHeight = parseInt(d3.select(".month-table").style("height"));
	var graphWidth = svgWidth - margin.left - margin.right;
	var graphHeight = svgHeight - margin.top - margin.bottom;

	// Define the x and y axis
	var x = d3.time.scale().range([0, graphWidth]);
	var yPerf = d3.scale.linear().range([graphHeight, 0]);
	var yVolume = d3.scale.linear().range([graphHeight, 0]);
	var xAxis = d3.svg.axis()
		.scale(x).orient("bottom").ticks(3);
	var yAxisPerf = d3.svg.axis()
		.scale(yPerf).orient("right").ticks(8)
		.tickFormat( function(d) { return d + "%" } );
	var yAxisVolume = d3.svg.axis()
		.scale(yVolume).orient("left").ticks(8)
		.tickFormat( function(d) { return "$" + d } );

	// Add the line for performance
	var performanceLine = d3.svg.line()
		.x(function(d) { return x(d.Month); })
		.y(function(d) { return yPerf(d.MonthReturn); });

	// Remove the svg if it exists
	d3.select("#barGraph").remove();

	// Add the canvas to the HTML
	var svg = d3.select("#barDiv")
		.append("svg")
			.attr('width', svgWidth)
			.attr('height', svgHeight)
			.attr('id', 'barGraph')
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	// Parse the data
	data.forEach(function(d) {
		d.Month = parseDateShort(d.Month);
		d.MonthReturn = +d.MonthReturn * 100.0;
		d.Volume = +d.Volume;
	});

	// Scale the range of the data
	x.domain(d3.extent(data, function(d) { return d.Month; }));
	yPerf.domain([d3.min(data, function(d) {
		return Math.round((Math.min(d.MonthReturn) - 10) / 10) * 10 }),
	d3.max(data, function(d) {
		return Math.round((Math.max(d.MonthReturn) + 15) / 10) * 10 })]);
	yVolume.domain([d3.min(data, function(d) {
		return 0 }),
	d3.max(data, function(d) {
		return Math.round((Math.max(d.Volume) + 25) / 10) * 10 })]);

	// Add a tooltip to the graph
	var tooltip = d3.select("body").append("div").attr("class", "toolTip");

	// Add bars as blue rects
	svg.selectAll("bar")
		.data(data)
		.enter().append("rect")
			.style("fill", "#089fba")
			.attr("x", function(d) { return x(d.Month); })
			.attr("width", 10)
			.attr("transform", "translate(-5,0)")
			.attr("y", function(d) { return yVolume(d.Volume); })
			.attr("height", function(d) { return graphHeight - yVolume(d.Volume); })
			.on("mousemove", function(d){
        		tooltip.style("left", d3.event.pageX - 50 + "px")
          			.style("top", d3.event.pageY - 70 + "px")
          			.style("display", "inline-block")
          			.html("Volume: $" + Math.round(d.Volume) + "<br>Return: " +
          				Math.round(d.MonthReturn,2) + "%");
    		})
			.on("mouseout", function(d){ tooltip.style("display", "none");});

	// Add the perf as a grey line
	svg.append("path")
		.style("stroke", "#253b40")
		.style("fill", "none")
		.attr("class", "line")
		.attr("d", performanceLine(data));

	// Add the x axis
	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + graphHeight + ")")
		.call(xAxis);
	
	// Add the y axis
	svg.append("g")
		.attr("class", "y axis")
		.attr("transform", "translate(" + (graphWidth + 5) + " , 0)")	
		.call(yAxisPerf);
	svg.append("g")
		.attr("class", "y axis")
		.attr("transform", "translate(-5 , 0)")	
		.call(yAxisVolume);
}