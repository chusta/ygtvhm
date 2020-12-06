var heatmap = function(divId, hmData, xAxis, yAxis) {
    var colors = ["#ffffff", "#ffffff", "#ffe5c1", "#ffe5c1", "#ffc672", "#ffc672", "#ff9352", "#ff9352", "#ff4e37", "#ff4e37", "#ff0000", "#ff0000", "#ff0000"];
    var hmWidth = xAxis.length * 35;
    var hmHeight = yAxis.length * 50;

    var margin = {top: 50, right: 30, bottom: 100, left: 110},
        width = hmWidth - margin.left - margin.right,
        height = hmHeight - margin.top - margin.bottom;

    var svg = d3.select(`#${divId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    var x = d3.scaleBand()
        .range([0, width])
        .domain(xAxis)
        .padding(0.01);

    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("text-anchor", "end")
        .style("font-size", 12)
        .style("font-weight", "bold")
        .attr("transform", "rotate(-45)");

    var y = d3.scaleBand()
        .range([height, 0])
        .domain(yAxis)
        .padding(0.01);

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("font-weight", "bold")
        .style("font-size", 12);

    var maxSize = divId === "cybex" ? 9 : 12;

    var colorScale = d3.scaleQuantile()
        .domain([0, maxSize])
        .range(colors);

    svg.append("text")
        .attr("x", 0)
        .attr("y", -10)
        .attr("text-anchor", "left")
        .style("font-size", "24px")
        .style("font-family", "monospace")
        .text(divId);

    svg.selectAll()
        .data(hmData)
        .enter()
        .append("rect")
        .attr("x", function(d) { return x(d.date) })
        .attr("y", function(d) { return y(d.slot) })
        .attr("width", x.bandwidth() )
        .attr("height", y.bandwidth() )
        .style("fill", function(d) { return colorScale(d.used); })
        .style("stroke-width", 4)
        .style("stroke", "none")
        .style("opacity", 0.8);
};

var cybex = [];
var cardio = [];
var weight = [];

var xAxisSet = new Set;
var yAxis = ["6:45pm-8:00pm", "5:30pm-6:30pm", "4:15pm-5:15pm", "3:00pm-4:00pm", "10:00am-11:00am", "8:30am-9:45am", "7:00am-8:15am", "5:30am-6:45am"];
var xAxis = [];

Promise.all([

]).then(function(dataset) {
    dataset.forEach (function(data) {
        data.forEach (function(item) {
            xAxisSet.add(item.date);
            switch(item.room) {
                case "free": weight.push(item); break;
                case "cybex": cybex.push(item); break;
                case "cardio": cardio.push(item); break;
            }
        })
    });
    xAxis = Array.from(xAxisSet);
    heatmap("weight", weight, xAxis, yAxis);
    heatmap("cybex", cybex, xAxis, yAxis);
    heatmap("cardio", cardio, xAxis, yAxis);
});
