function updateDecorators(eventSource, bands, timeline) {
  var events = eventSource.getAllEventIterator();
  var decorateStart, decorateEnd;
  var total = 0;
  var threshold = 50;
  var lastDate, lastDifferentDate;
  while (events.hasNext()) {
    var event = events.next();

    if (event.getStart() != lastDate && lastDate) {
      total = 0;
    }
    total += parseInt(event.getDescription());

    if (total > threshold) {
      if (!decorateStart) {
        decorateStart = lastDifferentDate || event.getStart();
      }
      decorateEnd = event.getStart();
    } else if (decorateStart && decorateEnd) {
      for (var i = 0; i < bands.length; i++) {
        var decorator = new Timeline.SpanHighlightDecorator({
          startDate: decorateStart,
          endDate: decorateEnd,
          color: "#FFC000",
          //theme: theme,
          opacity: 50
        });
        decorator.initialize(timeline._bands[i], timeline);
        bands[i].decorators.push(decorator);
      }
      decorateStart = null;
      decorateEnd = null;
    }

    if (event.getStart() != lastDate && lastDate) {
      lastDifferentDate = lastDate;
    }
    lastDate = event.getStart();    
  }

  timeline.paint();
}

var tl;
function onLoad() {
  createTimeline(document.getElementById('email').value);
  
  document.getElementById('newtimeline').onclick = function() {
    createTimeline(document.getElementById('email').value);
  };
}

function createTimeline(email) {
  document.getElementById('tl').innerHtml = '';

  var eventSource = new Timeline.DefaultEventSource();
  
  var theme = Timeline.ClassicTheme.create();
  theme.event.bubble.width = 250;
  
  var bandInfos = [
    Timeline.createHotZoneBandInfo({
                                     width:          "80%", 
                                     intervalUnit:   Timeline.DateTime.MONTH,
                                     intervalPixels: 220,
                                     zones:          [],
                                     eventSource:    eventSource,
                                     theme:          theme
                                   }),
    Timeline.createHotZoneBandInfo({
                                     width:          "20%", 
                                     intervalUnit:   Timeline.DateTime.YEAR, 
                                     intervalPixels: 200,
                                     zones:          [], 
                                     eventSource:    eventSource,
                                     overview:       true,
                                     theme:          theme
                                   })
  ];
  bandInfos[1].syncWith = 0;
  bandInfos[1].highlight = true;
  
  for (var i = 0; i < bandInfos.length; i++) {
    bandInfos[i].decorators = [];
  }
  
  tl = Timeline.create(document.getElementById("tl"), bandInfos, Timeline.HORIZONTAL);
  tl.loadJSON("cgi-bin/myquery.cgi?user=" + email,
              function(data, url) {
                eventSource.loadJSON(data, url);
                try {
                  updateDecorators(eventSource, bandInfos, tl);
                } catch (x) {
                  console.error(x);
                }
              });            
}

var resizeTimerID = null;
function onResize() {
  if (resizeTimerID == null) {
    resizeTimerID = window.setTimeout(function() {
                                        resizeTimerID = null;
                                        tl.layout();
                                      }, 500);
  }
}
