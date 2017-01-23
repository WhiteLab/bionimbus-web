/**
 * Created by dfitzgerald on 1/18/17.
 *
 * A big advantage to having a built-in spreadsheet is that it's easy to duplicate values across columns and
 * many people are used to dealing with spreadsheets
 *
 * A big problem is how to make sure the submitted values actually match up to values the software will understand.
 * For example, the assay RNAseq might be valid by DOMseq probably is not. How can I either restrict the user to
 * use only valid values, or validate after entry that those values are valid?
 *
 * My strategy is to do that second thing, let the user enter whatever he/she wants and then tell the user whether
 * that is a valid option. If it's not, the cell will background orange. Now the question is, how do I present all
 * valid options to the user?
 */
function isValidEntry(entry, colName) {
    return false;
}

$(document).ready(function() {
    var $submitTable = $('#submit-handsontable'),
        colHeaders = ['Name', 'Assay', 'Barcode', 'Sequencing Protocol', 'Read Length', 'Platform'],
        toastCommonOptions = {
            heading: 'Validation Warning',
            bgColor: '#F4D35E',
            textColor: '#333',
            position: 'bottom-right',
            hideAfter: 10000,
            loader: false
        };

    $submitTable.handsontable({
        colHeaders: colHeaders,
        stretchH: 'all',
        minSpareRows: 1,
        afterChange: function(changes, source) {
            /*
             * changes is an array of every change, where each change is an array of size 4:
             *      0: 0-indexed Y-coordinate, starting in the top left
             *      1: 0-indexed X-coordinate, starting in the top left
             *      2: old cell content
             *      3: new cell content
             */
            if(source == 'edit' || source == 'autofill'){
                var warningCoordinates = [],
                    failedEntries = new Set();

                for(var i = 0, len = changes.length; i < len; i++) {
                    var cell = changes[i],
                        x = cell[1],
                        y = cell[0],
                        oldContent = cell[2],
                        newContent = cell[3].trim(),
                        colName = colHeaders[x],
                        cellContentId = colName + ':' + newContent;

                    // Validate entry, take action if validation doesn't pass
                    if (!isValidEntry(newContent.toLowerCase(), colName)) {
                        // Color invalid cells
                        $submitTable.handsontable('getCell', y, x).style.background = '#F4D35E';

                        // Create one toast message per column-entry combination
                        if (!failedEntries.has(cellContentId)) {
                            failedEntries.add(cellContentId);
                            $.toast(extend(toastCommonOptions, {
                                text: '{} is not recognized as a valid entry for {}'.format(
                                    newContent,
                                    colName
                                )
                            }));
                        }
                    }
                }
            }

            console.debug(changes);
            console.debug(source);
        }
    });
});