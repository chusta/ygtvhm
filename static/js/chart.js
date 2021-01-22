function show(hm) {
    function on(e, a) {
        e.style.display = "block";
        e.style.visibility = "visible";
        a.style.borderBottom = "4px solid red";
    }
    function off(e, a) {
        e.style.display = "none";
        e.style.visibility = "hidden";
        a.style.borderBottom = "0px";
    }

    let options = ["weight", "cardio", "cybex"];
    for (o of options) {
        let e = document.getElementById(o);
        let a = document.getElementById("id_"+o);
        (o === hm) ? on(e, a) : off(e, a);
    }
}

function heatmap(divId, hmType, hmData, xAxis, yAxis) {
    let margin = {top: 60, bottom: 60, left: 110, right: 30};
    let width = xAxis.length * 30;
    let height = yAxis.length * 30;

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
        .style("font-size", 10)
        .style("font-weight", 600)
        .attr("transform", "rotate(-45)");

    let y = d3.scaleBand()
        .range([height, 0])
        .domain(yAxis)
        .padding(0.01);

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("font-weight", 600)
        .style("font-size", 10);

    let maxSize = divId.startsWith("cybex") ? 9 : 12;

    let colorScale = d3.scaleLinear()
        .range(["white", "#e00000"])
        .domain([0, maxSize]);

    svg.append("text")
        .attr("x", 0)
        .attr("y", -10)
        .attr("text-anchor", "left")
        .style("font-size", "18px")
        .style("font-family", "monospace")
        .text(hmType);

    let tooltip = d3.select("#tooltip")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background-color", "white")
        .style("border", "solid")
        .style("font-family", "monospace")
        .style("font-size", "10")
        .style("border-width", "2px")
        .style("border-radius", "2px")
        .style("overflow", "hidden")
        .style("white-space", "nowrap")
        .style("padding", "10px");

    function mouseover() {
        tooltip.transition()
            .duration(60)
            .style("opacity", 0.9);
    }

    function mouseleave() {
        tooltip.style("opacity", 0);
    }

    function mousemove(e, x) {
        tooltip.html(`${x.used} / ${maxSize}`)
            .style("left", (e.pageX - 50) + "px")
            .style("top", (e.pageY - 50) + "px");
    }

    svg.selectAll()
        .data(hmData)
        .enter()
        .append("rect")
        .attr("x", function(d) { return x(d.date) })
        .attr("y", function(d) { return y(d.slot) })
        .attr("width", x.bandwidth())
        .attr("height", y.bandwidth())
        .style("fill", function(d) { return colorScale(d.used) })
        .style("stroke-width", 4)
        .style("stroke", "none")
        .style("opacity", 1)
        .on("mouseover", mouseover)
        .on("mousemove", mousemove)
        .on("mouseleave", mouseleave);

    document.getElementById(`${divId}`)
            .appendChild(document.createElement("br"));
}

function draw(data, type, yAxis) {
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
        xAxis.sort().reverse()
        heatmap("weight", type, weight, xAxis, yAxis);
        heatmap("cybex", type, cybex, xAxis, yAxis);
        heatmap("cardio", type, cardio, xAxis, yAxis);
    });
}
