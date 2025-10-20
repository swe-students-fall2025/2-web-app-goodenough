function applyFilters() {
        const searchForm = $('#searchForm')[0];
        const mediumFilter = $('#mediumFilter').val();
        const yearFilter = $('#yearFilter').val();


        $(searchForm).find('input[name="medium"], input[name="year"]').remove();

        if (mediumFilter) {
            $('<input>').attr({
                type: 'hidden',
                name: 'medium',
                value: mediumFilter
            }).appendTo(searchForm);
        }

        if (yearFilter) {
            $('<input>').attr({
                type: 'hidden',
                name: 'year',
                value: yearFilter
            }).appendTo(searchForm);
        }

        searchForm.submit();
    }

$(document).ready(function() {
    $('input[name="q"]').keypress(function(e) {
        if (e.which === 13) {
            $(this).closest('form').submit();
        }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const medium = urlParams.get('medium');
    const year = urlParams.get('year');

    if (medium) $('#mediumFilter').val(medium);
    if (year) $('#yearFilter').val(year);

    // Like button AJAX
    $('.like-btn').click(function() {
        const btn = $(this);
        const artworkId = btn.data('artwork-id');

        $.ajax({
            url: `/api/artwork/${artworkId}/like`,
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    if (response.liked) {
                        btn.addClass('liked');
                        btn.find('i').addClass('liked');
                    } else {
                        btn.removeClass('liked');
                        btn.find('i').removeClass('liked');
                    }
                    btn.find('.likes-count').text(response.likes_count);
                } else {
                    alert('Error: ' + (response.error || 'Failed to like.'));
                }
            },
            error: function(xhr) {
                if (xhr.status === 401) {
                    alert('Please log in to like artworks.');
                } else {
                    alert('Error: ' + xhr.responseText);
                }
            }
        });
    });
    $('#profileTabs a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('.artwork-card').on('click', function(e) {
        if (!$(e.target).closest('.like-btn').length && !$(e.target).is('.like-btn')) {
            window.location = $(this).find('a').attr('href');
        }
    });



});
