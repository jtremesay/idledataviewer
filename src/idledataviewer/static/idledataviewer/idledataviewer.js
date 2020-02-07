(function() {
    "use strict";

    document.addEventListener('DOMContentLoaded', (event) => {
        var req = new XMLHttpRequest();
        req.addEventListener("load", function() {
            var players = JSON.parse(this.responseText);

            var chart_data = [];

            for (let player_name in players) {
                let player_data = players[player_name];

                var level_data = {
                    legendName: "level " + player_name,
                    showInLegend: true, 
                    type: "line",
                    legendName: "level " + player_name,
                    dataPoints: []
                };
                chart_data.push(level_data)
                var remaining_time_data = {
                    name: "remaining time " + player_name,
                    showInLegend: true, 
                    axisYType: "secondary",
                    type: "line",
                    legendName: "remaining time " + player_name,
                    dataPoints: []
                };
                chart_data.push(remaining_time_data)
                for (let event_index in player_data.events) {
                    let event = player_data.events[event_index];

                    let date = new Date(event.timestamp)

                    level_data.dataPoints.push({
                        x: date,
                        y: event.level
                    });

                    remaining_time_data.dataPoints.push({
                        x: date,
                        y: event.remaining_time / (24 * 60 * 60)
                    });
                }
            }

            var chart = new CanvasJS.Chart(
                "idledataviewer-container",
                {
                    title: { text: "Idle Data Viewer" },
                    axisX: {      
                        title: "Date time",
                        labelAngle: -50
                    },
                    axisY: {
                        title: "Level"
                    },
                    axisY2: {
                        title: "Remaing time (days)",
                        minimum: 0
                    },
                    animationEnabled: true,
                    zoomEnable: true,
                    data: chart_data
                }
            )
            chart.render();
        });
        req.open("GET", "/api/players");
        req.send();
    });
})();