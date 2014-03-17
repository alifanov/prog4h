$(function(){
    $(".balance-up-form button.btn").click(function(){
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
});