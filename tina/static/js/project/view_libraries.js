// TODO: Clickable table to make box that gives more information
// TODO: Searchable
// TODO: Advanced search
// TODO: Sort by Project/Bid/Status, keep other sorts intact

// $('tbody').sortable();

// Draginng and sorting stuff
 $(document).on("click", '.done',function(){
    $(this).parents('td').parents('tr').css({
        transition: '0.8s',
        width: '5%',
        height: '25px',
        position: 'relative',
        zIndex: '0'
    });

    // $( ".show-content").css("visibility", "visible");
    // $(this).parents('td').empty().addClass('view');
    $(this).parents('td').empty().append($('<a>').attr({href: '#', class: 'view'}).text('More Details'));
});


$(document).on("click", '.view',function(){
       $(this).parents('td').parents('tr').css({
        transition: '0.8s',
        width: '40%',
        height: '200px',
        position: 'relative',
        zIndex: '2'
    });

    // $( ".show-content").css("visibility", "hidden");
    // $(this).parents('td').empty().addClass('done');
    $(this).parents('td').empty().append($('<a>').attr({href: '#', class: 'done'}).text('Less Details'));
});

// Table sorter
$(document).ready(function()
    {
        $("#libraryTable").tablesorter();
    }
);


$(document).on("keyup", '#librarySearch',function(){

    // Change so you see only items in selected map

    var search = $('#librarySearch').val();

    if(search === ''){
        $('tr').css({visibility: 'visible', position: 'relative'});
    }else{
        $('tr').css({visibility: 'hidden', position: 'absolute'});
    }
    // var re = new RegExp(search);
    $( "td[class*=" + search + "]" ).parents('tr').css({
            position: 'relative',
            visibility: 'visible'
        });

});