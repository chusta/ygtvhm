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
d3.json("data/1609736400-1610254800.json"),
d3.json("data/1610341200-1610859600.json"),
d3.json("data/1610946000-1611464400.json"),
d3.json("data/1611550800-1612069200.json"),
d3.json("data/1612155600-1612674000.json"),
d3.json("data/1612760400-1613278800.json"),
d3.json("data/1613365200-1613883600.json"),
d3.json("data/1613970000-1614488400.json"),
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
d3.json("data/1609131600-1609650000s.json"),
d3.json("data/1609736400-1610254800s.json"),
d3.json("data/1610341200-1610859600s.json"),
d3.json("data/1610946000-1611464400s.json"),
d3.json("data/1611550800-1612069200s.json"),
d3.json("data/1612155600-1612674000s.json"),
d3.json("data/1612760400-1613278800s.json"),
d3.json("data/1613365200-1613883600s.json"),
/* WEEKEND */
];

draw(dataWeekday, "weekday", yWeekday);
draw(dataWeekend, "weekend", yWeekend);
