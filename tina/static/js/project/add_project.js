/**
 * Created by dfitzgerald on 11/10/16.
 */
$(document).ready(function(){

    var $projectMetadataTable = $('#project-metadata-handsontable');

    $projectMetadataTable.handsontable({
        data: [['test', 'one']],
        colHeaders: ['Key', 'Value'],
        stretchH: 'all',
        minSpareRows: 1
    });

    var $libraryMetadataTable = $('#library-metadata-handsontable');

    $libraryMetadataTable.handsontable({
        data: [['fly_stage', '']],
        colHeaders: ['Key', 'Value (optional)'],
        stretchH: 'all',
        minSpareRows: 1
    });

    $('form').submit(function(){
        $('<input>').attr({
            type: 'hidden',
            name: 'project_other_metadata',
            value: JSON.stringify($projectMetadataTable.handsontable('getData'))
        }).appendTo(this);

        $('<input>').attr({
            type: 'hidden',
            name: 'library_metadata',
            value: JSON.stringify($libraryMetadataTable.handsontable('getData'))
        }).appendTo(this);
    });
});