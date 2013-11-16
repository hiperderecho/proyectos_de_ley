$( 'form' ).submit(function(e) {
    e.preventDefault();
    var keyword = $("input:first").val();
    if( keyword != "" ) {
        //console.log(keyword);
        $("#contenido").html("");
        var out = '<h1>Resultados de búsqueda</h1>\n';
        $("#contenido").append(out);

        var out = '';
        $.getJSON( "http:/{% base_url %}proyectos_data.json", function( data ) {
            $.each(data, function(i, v) {
        
                if( v.titulo.search(new RegExp(keyword, 'i')) != -1 ) {
                    out += '\n<p>' + v.titulo;
                    if( v.pdf_url ) {
                        out += ' <span class="glyphicon glyphicon-cloud-download"></span>';
                        out += ' <a href="' + v.pdf_url + '">PDF</a>';
                    }
                    else {
                        out += ' [sin PDF]';
                    }
                    if( v.link_to_pdf ) {
                        out += ' <span class="glyphicon glyphicon-link"></span>';
                        out += ' <a href="' + v.link_to_pdf + '">Expediente</a>';
                    }
                    else {
                        out += ' [sin Expediente]';
                    }
                    out += '</p>'
                    //console.log(v);
                    //console.log(v.titulo);
                    //console.log(out);
                }
            });
            $("h2").remove();
            $("h1#proyectos_de_ley").remove();
            $("div#page-selection").remove();
            $("#contenido").append(out);
        });
    }
});
