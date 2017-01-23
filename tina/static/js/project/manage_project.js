/**
 * Created by dfitzgerald on 11/15/16.
 */
$(document).ready(function(){
    // This the delete 'animation' for flip cards
    $('.delete-button').click(function(){
        var $flipCardParent = $(this).parents('flip-card');
        $flipCardParent.children('header').css({
            transition: '0.2s',
            backgroundColor: 'red',
            backgroundImage: ''
        });

        $flipCardParent.find('flip-card-description')
                .children('div').contents().last()[0].textContent = 'This will delete everything associated ' +
                'with this project! Are you sure you want to delete?';

        $(this).parent().empty().append(
                $('<a>').attr({href: '#', onclick: 'return false;'}).text('No')
        ).append(
                $('<a>').attr('href', $flipCardParent.data('delete-url')).text('Yes')
        ).append(
                $('<a>').attr({href: '#', onclick: 'return false;'}).text('No')
        ).append(
                $('<a>').attr({href: '#', onclick: 'return false;'}).text('No')
        );
    });
});