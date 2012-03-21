class Admin

    constructor: ->

        $('#broadcast').submit ->
            $.post '/broadcast',
                $(this).serialize(),
                (data, textStatus, jqXHR) =>
                    $(':input', this).not(':button, :submit, :reset, :hidden').val('')
                
            false

        $.get 'users', (data) ->
            _.each data, (user) ->
                $('#users ul').append "<li>" + user.name + "</li>"


window.initializeAdmin = () ->
    new Admin
