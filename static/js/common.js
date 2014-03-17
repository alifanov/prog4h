/**
 * Created with PyCharm.
 * User: vampire
 * Date: 04.03.14
 * Time: 18:04
 * To change this template use File | Settings | File Templates.
 */
$(function(){
    $(".balance-up-form button").click(function(){
        $.ajax({
            url: '/get_new_signature/',
            type: 'POST',
            data: {summ: $('#id_OutSum').val(), oid: $("#id_InvId").val()},
            success: function(resp){
                updatePrice = true;
                $("#id_SignatureValue").val(resp);
                $(".balance-up-form").submit();
            }
        });
        return false;
    });

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