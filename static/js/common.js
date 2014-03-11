/**
 * Created with PyCharm.
 * User: vampire
 * Date: 04.03.14
 * Time: 18:04
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $(".call-order-form").submit(function(){
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serializeArray(),
            success: function(){
                $(".call-order-form input[type!='hidden']").val('');
                $(".call-order").modal('hide');
                $(".thx").modal('show');
            }
        });
        return false;
    });
    $(".footer-call-order-form").submit(function(){
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serializeArray(),
            success: function(){
                $(".footer-call-order-form input[type!='hidden']").val('');
                $(".thx").modal('show');
            }
        });
        return false;
    });
    $(".order-form").submit(function(){
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serializeArray(),
            success: function(){
                $(".order-form input[type!='hidden']").val('');
                $(".thx").modal('show');
            }
        });
        return false;
    });
});