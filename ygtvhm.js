var heatmap = function(divId, hmData, xAxis, yAxis) {
    let colors = ["#ffffff", "#ffffff", "#ffe5c1", "#ffe5c1", "#ffc672", "#ffc672", "#ff9352", "#ff9352", "#ff4e37", "#ff4e37", "#ff0000", "#ff0000", "#ff0000"];

    let margin = {top: 50, right: 30, bottom: 100, left: 110};
    let width = xAxis.length * 35;
    let height = yAxis.length * 35;

    let svg = d3.select(`#${divId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    let x = d3.scaleBand()
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

    let y = d3.scaleBand()
        .range([height, 0])
        .domain(yAxis)
        .padding(0.01);

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("font-weight", "bold")
        .style("font-size", 12);

    let maxSize = divId === "cybex" ? 9 : 12;

    let colorScale = d3.scaleQuantile()
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

var draw = function(data, type, yAxis) {
    let cybex = [];
    let cardio = [];
    let weight = [];

    let xAxisSet = new Set;
    let xAxis = [];

    Promise.all(data)
    .then(function(dataset) {
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
        xAxis.sort();
        console.log(weight);
        console.log(xAxis);
        console.log(yAxis);
        heatmap(`weight${type}`, weight, xAxis, yAxis);
        heatmap(`cybex${type}`, cybex, xAxis, yAxis);
        heatmap(`cardio${type}`, cardio, xAxis, yAxis);
    });
};

var yWeekday = ["6:45pm-8:00pm", "5:30pm-6:30pm", "4:15pm-5:15pm", "3:00pm-4:00pm", "10:00am-11:00am", "8:30am-9:45am", "7:00am-8:15am", "5:30am-6:45am"];
var yWeekend = ["9:00am-10:00am", "8:00am-9:00am", "7:00am-8:00am"];
var dataWeekday = [
d3.json("data/1601870400-1602388800.json"),
d3.json("data/1602475200-1602993600.json"),
d3.json("data/1603080000-1603598400.json"),
d3.json("data/1603684800-1604203200.json"),
d3.json("data/1604293200-1604811600.json"),
d3.json("data/1604898000-1605416400.json"),
d3.json("data/1605502800-1606021200.json"),
d3.json("data/1606107600-1606626000.json"),
d3.json("data/1606712400-1607230800.json"),
d3.json("data/1607317200-1607835600.json"),
d3.json("data/1607922000-1608440400.json"),
d3.json("data/1608526800-1609045200.json"),
d3.json("data/1609131600-1609650000.json"),
/* WEEKDAY */
];
var dataWeekend = [
d3.json("data/1601870400-1602388800s.json"),
d3.json("data/1602475200-1602993600s.json"),
d3.json("data/1603080000-1603598400s.json"),
d3.json("data/1603684800-1604203200s.json"),
d3.json("data/1604293200-1604811600s.json"),
d3.json("data/1604898000-1605416400s.json"),
d3.json("data/1605502800-1606021200s.json"),
d3.json("data/1606107600-1606626000s.json"),
d3.json("data/1606712400-1607230800s.json"),
d3.json("data/1607317200-1607835600s.json"),
d3.json("data/1607922000-1608440400s.json"),
d3.json("data/1608526800-1609045200s.json"),
/* WEEKEND */
];
draw(dataWeekday, "_weekday", yWeekday);
draw(dataWeekend, "_weekend", yWeekend);
