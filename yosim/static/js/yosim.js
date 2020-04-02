/* Main project Javascript */

$(document).ready(function() {

    // var TIME_ZONE = "{{ TIME_ZONE }}";
    var TIME_ZONE = "Asia/Ho_Chi_Minh";
    $(".timestamp").each(function(index) {
        var timestamp = parseInt($(this).text());
        var formatDatetime = moment.unix(timestamp).tz(TIME_ZONE).format("MM/DD/YYYY HH:mm:ss A");
        $(this).html(formatDatetime)
    });

    var previousData = $('#previous_data');
    if (previousData.length > 0) {
        var previousDataJson = $.parseJSON(previousData.val());
        for (key in previousDataJson) {
            if (key == 'daterange') {
                var dateRange = previousDataJson[key].split(' - ');
                $("input[name='daterange']").daterangepicker({
                    timePicker: true,
                    showCustomRangeLabel: false,
                    locale: {
                        format: 'DD/MM/YYYY h:mm A'
                    },
                    startDate: dateRange[0],
                    endDate: dateRange[1],
                    ranges: {
                       'Today': [moment().startOf('day'), moment().endOf('day')],
                       'Yesterday': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
                       'Last 7 Days': [moment().subtract(6, 'days').startOf('day'), moment().endOf('day')],
                       'Last 30 Days': [moment().subtract(29, 'days').startOf('day'), moment().endOf('day')],
                       'This Month': [moment().startOf('month'), moment().endOf('month')],
                       'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
                    }
                });
            } else if (key == 'fpatterns') {
                $("input[name='fpatterns']").val(previousDataJson[key]);
            } else {
                var selectData = previousDataJson[key].split(', ');
                $("select[name='" + key + "']").selectpicker('val', selectData);
            }
        }
    }

    $.fn.dataTable.moment('MM/DD/YYYY HH:mm:ss A');
    // Enable syscheck datatables
    var syschkTable = $('#syschecks-table').DataTable({
        responsive: true,
        "order": [[ 4, "desc" ]],
        // group by filename
        // "rowGroup": {
        //     dataSrc: '1'
        // },
        // // export buttons
        // dom: 'Bfrtip',
        // // lengthChange: false,
        // buttons: [
        //     'excel', {
        //         extend: 'pdfHtml5',
        //         download: 'open'
        //     },
        //     'colvis'
        // ],
        keys: true,
        select: true,
        fixedHeader: true
    });

    // syschkTable.buttons().container()
    //     .appendTo('#syschecks-table_wrapper .col-sm-6:eq(0)');

    // Enable alert datatables
    var alertTable = $('#alerts-table').DataTable({
        "order": [[ 5, "desc" ]],
        // export buttons
        dom: 'Bfrtip',
        // lengthChange: false,
        buttons: ['excel', 'pdf', 'colvis'],
        keys: true,
        select: true,
        fixedHeader: true,
        // fixedColumns: true,
    });

    // Enable agents datatables
    var agentTable = $('#agents-table').DataTable({
        keys: true,
        select: true,
        fixedHeader: true,
        responsive: true,
    });

    // Enable rules datatables
    var ruleTable = $('#rules-table').DataTable({
        keys: true,
        select: true,
        fixedHeader: true,
        responsive: true,
    });

    // // Enable daterangepicker
    // $('input[name="daterange"]').daterangepicker({
    //     "showCustomRangeLabel": false,
    //     locale: {
    //         format: 'DD/MM/YYYY h:mm A'
    //     },
    //     ranges: {
    //        'Today': [moment(), moment()],
    //        'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
    //        'Last 7 Days': [moment().subtract(6, 'days'), moment()],
    //        'Last 30 Days': [moment().subtract(29, 'days'), moment()],
    //        'This Month': [moment().startOf('month'), moment().endOf('month')],
    //        'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
    //     }
    // });

});
