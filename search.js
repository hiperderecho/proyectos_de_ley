$( 'form' ).submit(function(e) {
    e.preventDefault();
    var keyword = $("input:first").val();
    if( keyword != "" ) {
        console.log(keyword);
        $("#contenido").html("");
        var out = '<h1>Resultados de búsqueda</h1>\n';
        $("#contenido").append(out);

        var out = '';
        $.getJSON( "proyectos_data.json", function( data ) {
            $.each(data, function(i, v) {
        
                if( v.titulo.search(new RegExp(keyword, 'i')) != -1 ) {
                    out += '\n<p>' + v.titulo;
                    out += ' <span class="glyphicon glyphicon-cloud-download"></span>';
                    out += ' <a href="' + v.pdf_url + '">PDF</a>';
                    out += ' <span class="glyphicon glyphicon-link"></span>';
                    out += ' <a href="' + v.link_to_pdf + '">Expediente</a>';
                    out += '</p>'
                    //console.log(v);
                    //console.log(v.titulo);
                    console.log(out);
                }
            });
            $("#contenido").append(out);
        });
    }
});
