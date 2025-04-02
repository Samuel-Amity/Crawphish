$(document).ready(function() {
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // AJAX setup for CSRF
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Create form submission
    $('#templateForm').submit(function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        $.ajax({
            url: $(this).attr('action'),
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if(response.success) {
                    $('#createTemplateModal').modal('hide');
                    location.reload();
                } else {
                    alert('Error: ' + response.errors);
                }
            },
            error: function(xhr) {
                alert('Error: ' + xhr.responseJSON.errors);
            }
        });
    });

    // Edit button handler
    $(document).on('click', '.edit-btn', function() {
        const templateId = $(this).data('id');
        $.get(`/email-templates/edit/${templateId}/`, function(data) {
            $('#editTemplateModal').html(data).modal('show');
        });
    });

    // Delete button handler
    $(document).on('click', '.delete-btn', function() {
        const templateId = $(this).data('id');
        if (confirm('Are you sure you want to delete this template?')) {
            $.ajax({
                url: `/email-templates/delete/${templateId}/`,
                type: "POST",
                success: function(response) {
                    if(response.success) {
                        location.reload();
                    }
                },
                error: function(xhr) {
                    alert('Error: ' + xhr.responseJSON.error);
                }
            });
        }
    });

    // Copy button handler
    $(document).on('click', '.copy-btn', function() {
        const templateId = $(this).data('id');
        $.ajax({
            url: `/email-templates/copy/${templateId}/`,
            type: "POST",
            success: function(response) {
                if(response.success) {
                    location.reload();
                }
            },
            error: function(xhr) {
                alert('Error: ' + xhr.responseJSON.error);
            }
        });
    });
});