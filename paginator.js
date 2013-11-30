var loc = window.location.pathname;
if (loc.indexOf("congresista") >= 0) {
    //console.log(loc);
    // load html.doc
    $.getJSON( 'html.json', function(data) {
        var myarray = [];
        $.each( data, function(key,val) {
            myarray.push(val);
        });
        myarray.sort().reverse();
        //console.log(myarray);
        $("#contenido").html(myarray.slice(0,20));

        // number of pages (20 items per page)
        var n_pages = parseInt(myarray.length / 20) + 1;
        //
        // init bootpag
        $('#page-selection').bootpag({
            total: n_pages,
            page: 1,
            maxVisible: 20
        }).on("page", function(event, /* page number here */ num){
            var start = 20;
            var end = start*num;
            //console.log(myarray.slice(end - 20, end));
            $("#contenido").fadeOut("fast", function() {
            $("#contenido").fadeIn("slow", function(){}).html(myarray.slice(end - 20, end)); // some ajax content loading...
            $('html, body').animate({ scrollTop: 0 }, 0);
        });
      });
   });
}
else if (loc.indexOf("/p/") >= 0) {
    console.log("permalink");
}
else {

    $.getJSON( "http://{% base_url %}data_handler.py", { start: '0', end: '20' } )
    .done(function(data) {
        //console.log(data);
        $("#contenido").html(data.output);
    });

    $.getJSON( "http://{% base_url %}data_handler.py", { get: "number_of_pages" } )
        .done(function(data) {
            var myarray = data.number_of_pages;
            var n_pages = parseInt(myarray / 20) + 1;
            // init bootpag
            $('#page-selection').bootpag({
                total: n_pages,
                page: 1,
                maxVisible: 20
            }).on("page", function(event, /* page number here */ num) {
                //console.log(num);
                var start = 20;
                var end = start*num;
                //console.log(end - 20);
                //console.log(end);

                $.getJSON( "http://{% base_url %}data_handler.py", { start: end - 20, end: end } )
                    .done(function(data) {
                        //console.log(myarray.slice(end - 20, end));
                        $("#contenido").fadeOut("fast", function() {
                        $("#contenido").fadeIn("slow", function(){}).html(data.output); // some ajax content loading...
                        $('html, body').animate({ scrollTop: 0 }, 0);
                        });
                    });
            });
        });
}
