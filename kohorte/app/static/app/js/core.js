


function notification(){
        $.notify({
            message: "Combinaison mot de passe / pseudo erronnée"

        },{
            type: 'danger',
            timer: 4000,
            placement: {
                from: 'top',
                align: 'center'
            }
        });
    };

function show_posts(id){
    var a = $('#c_' + id);
    var h = $('#h_' + id);
    var s = $('#s_' + id);
    if (a.is(":visible")){
        a.hide(100);
        h.hide();
        s.show();

    } else {
        a.show(100);
        s.hide();
        h.show();

    }



};


