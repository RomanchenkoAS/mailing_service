function updateRealTimeStats() {
    $.ajax({
        url: "{% url 'real_time_stats' dispatch.pk %}",
        success: function (data) {
            $('#recipients_count_id').text(data.recipients_count);
            $('#sent_times_count_id').text(data.sent_times);
        }
    });
}

$(document).ready(function () {
    setInterval(updateRealTimeStats, 5000);  // Update stats every 5 seconds
});