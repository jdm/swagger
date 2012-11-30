var startDate = '2011-01';

var xhr = new XMLHttpRequest();
xhr.open('GET', 'cgi-bin/query.cgi?start=2011-01', true);
xhr.onload = function() {
  createChart(JSON.parse(xhr.response));
};
xhr.send();

function createChart(data) {
  function nextMonth(d) {
    var y = parseInt(d.split('/')[0]);
    var m = parseInt(d.split('/')[1]) + 1;
    if (m > 12) {
      m = 1;
      y++;
    }
    return "" + y + "/" + m + "/" + "01";
  }

  var points = [];
  var start = startDate.split('-').join('/') + '/' + '01';
  for (var i in data) {
    points.push([new Date(start), data[i]]);
    start = nextMonth(start);
  }
  
  var max = Math.max.apply(Math, data) + 5;
  var min = Math.min.apply(Math, data) - 5;
  var ticks = [];
  var numTicks = 6;
  for (var i = 0; i < numTicks; i++) {
    ticks.push(min + (i * (max - min) / (numTicks - 1)));
  }
  
  var flotData = [
    { lines: { show: true },
      color: '#99ccff',
      data: points
    },
    { label: 'Commits by new contributors',
      points: { show: true, fillColor: "#3d7dbd" },
      color: '#3d7dbd',
      hoverable: true,
      data: points
    }
  ];
  
  var flotOptions = { 
    grid: {
      borderWidth: 1,
      hoverable: true
    },
    legend: {
      show: true
    },
    yaxis: {
      ticks: ticks,
      color: "#000000"
    },
    xaxis: { 
      mode: "time",
      timeformat: "%y/%m",
      color: "#000000",
      tickSize: [1, "month"]
    }
  };
  
  $.plot($("#flot_chart"), flotData, flotOptions);
  $("#flot_chart").bind("plothover", function (event, pos, item) {
    if (item) {
      $("#flot_chart_tooltip").remove();
      showTooltip(item.pageX, item.pageY, item.series.data[item.dataIndex][1]);
    } else {
      $("#flot_chart_tooltip").remove();
    }
});
}

function showTooltip(x, y, contents) {
  $('<div id="flot_chart_tooltip">' + contents + '</div>').css( {
    top: y + 5,
    left: x + 5,
  }).appendTo("body").fadeIn(200);
}