var div = $(".tooltip"),
    cy,
    cx,
    data,
    variavel;

width = $(window).width()
height = 700
margin_left = 70
margin_top = 30
anos = ["2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015"]
cores = {
    "PT"       :["#a00200"],
    "PST"      :["#a51001"],
    "PL"       :["#aa1d01"],
    "PTC"      :["#b02b01"],
    "PCdoB"    :["#b53901"],
    "PP"       :["#ba4601"],
    "PPB"       :["#ba4601"],
    "PRB"      :["#bf5301"],
    "PSL"      :["#c46102"],
    "PPL"      :["#ca6f03"],
    "PSB"      :["#cf7d03"],
    "PMDB"     :["#d48b03"],
    "PROS"     :["#d99803"],
    "PRTB"     :["#dea604"],
    "PTB"      :["#e4b304"],
    "PRP"      :["#e9c104"],
    "PDT"      :["#eece04"],
    "PHS"      :["#f3dc05"],
    "PR"       :["#f4e509"],
    "PTN"     :["#f4e509"],
    "PSC"      :["#eae116"],
    "PMR"      :["#dfdd24"],
    "PTdoB"    :["#d5d931"],
    "PV"       :["#cad63e"],
    "PMN"      :["#c0d24b"],
    "PSD"      :["#b6ce58"],
    "PEN"      :["#abc966"],
    "SDD"      :["#a1c673"],
    "PSOL"     :["#97c281"],
    "PPS"      :["#8cbe8e"],
    "DEM"      :["#82ba9b"],
    "PFL_DEM"  :["#77b6a8"],
    "PSDB"     :["#6db3b6"],
    "PRONA"    :["#62afc3"],
    "PAN"      :["#58abd0"],
    "PSDC"     :["#4da7de"]
}


function acha_cor(partido) {
    return cores[partido]
}

function desenha_grafico() {
    var svg = dimple.newSvg("#candidatos", width, height);
    $("svg").each(function (i,d) {
        if (!($(d).attr("id"))) {
            $(d).attr("id","grafico_"+variavel)
        }
    });

    data = dimple.filterData(data,"ano",anos);
    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(margin_left, margin_top, width-margin_left*4, height-margin_top*3);
    var y = myChart.addMeasureAxis("y", variavel);
    if (variavel == "var_abs") {
        y.title = "Variação absoluta no número de filiados em relação ao ano anterior"
    } else {
        y.title = "Estoque de filiados no ano"
    }
    var x = myChart.addTimeAxis("x", "ano","%Y","%Y");
    x.title = ""
    series = myChart.addSeries("partido", dimple.plot.line);
    series.lineMarker = true;
    series.lineWeight = 7;
    series.interpolation = "cardinal";
    series.addEventHandler("mouseover", function (e) {
        if (variavel == "var_perc") {
            cy = formata_perc(e.yValue);
        } else {
            cy = formata_numero(e.yValue);
        }
        cx = new Date(e.xValue);
        cx = cx.getFullYear();

    });

    for (var cor in cores) {
        myChart.assignColor(cor,acha_cor(cor),acha_cor(cor));
    }
    myChart.draw(2000);
    adiciona_eventos();
    arruma_eixos();
}

function arruma_eixos() {
    $(".dimple-custom-axis-label").each(function (i,d) {
        var texto = $(d).html()
        if (texto.indexOf("k") > -1) {
            $(d).html(texto.replace("k"," mil"))
        }
        d3.select(d)
            .attr("transform", function(d) {
            return "rotate(-35)"
            });

    })
}
function inicializa() {
    $.getJSON( "estoque_partido_ano.json", function( dados ) {
        data = dados
        variavel = "estoque"
        desenha_grafico()
    })
}

function adiciona_eventos() {
    setTimeout(function () {
        d3.selectAll("circle")
            .transition()
            .duration(1000)
            .style("fill","gray")
            .attr("r","2px");

    },2000);

    $(".dimple-line").each(function (i,d) {
        //primeiro colore todos de ccinza
        acinzenta(d)
        var partido = $(d).attr("id");
        $(d).bind("mouseover", "."+partido, destaca);
        $(d).bind("mousemove", "."+partido, move);
        $(d).bind("mouseout", "."+partido, acinzenta);
    })

    $(".dimple-marker").each(function (i,d) {
        acinzenta(d)
        var partido = $(d).attr("id").split("-")[1]
        $(d).bind("mouseover",".dimple-"+partido.toLowerCase(),destaca)
        $(d).bind("mouseout",".dimple-"+partido.toLowerCase(),acinzenta)
    })

    //agora da lista que muda os graficos
    var lista = ["estoque","var_perc","var_abs"]
    for (var d in lista) {
        $("#"+lista[d]).click(function (e) { muda_grafico(e)})
    }
}

function move(event) {
    $(".tooltip").css({
        left: event.pageX - 15,
        top: event.pageY - 20
    });
}

function destaca(event) {
    var circulo = $(event.target).is("circle"); //checa se é circulo
    var partido = $(event.data).attr("id").split("-")[1].toUpperCase();
    var elemento = $(event.data) //pega círculos e linhas
    elemento.css(
        {"stroke": acha_cor(partido),
            "opacity": 0.9
        })

    //agora aparece a tooltip
    $(".tooltip").css({});
    $(".tooltip").css({
        opacity: 1,
        left: event.pageX - 15,
        top: event.pageY - 20,
        "border-color": acha_cor(partido)
    });
    $("#topo").css({background: acha_cor(partido)})

    if (circulo) {
        $("#resto").show()
        $("circle"+event.data).css({"fill": acha_cor(partido)})
    } else {
        $("#resto").hide()
    }

    var nome = "Estoque de filiados no ano"
    if (variavel == "var_abs") {
        nome = "Variação de filiados no ano"
    }

    var topo = "<b>"+partido+"</b>"
    var resto = "<b><p>Ano:</b> "+cx+"</p>" +
        "<b><p>"+nome+":</b> "+cy+"</p>"
    $("#topo").html(topo);
    $("#resto").html(resto);
}

function acinzenta(event) {
    if (event.data) {
        var elemento = event.data;
    } else {
        var elemento = event
    }

    $(elemento).css(
        {"stroke":"gray",
            "opacity":0.3
        })

    $(".tooltip").css({opacity: 0});
}

function formata_numero(num) {
    num = ""+num
    var tamanho = num.length;
    var milhao;
    if (tamanho == 7) {
        if (num[0] == "1") {
            milhao = "milhão";
        } else {
            milhao = "milhões";
        }
        return num[0]+","+num[1]+num[2]+" "+milhao;
    } else if (tamanho > 3) {
        return num.substring(0,tamanho-3) + " mil"
    }
    else return num
}

function formata_perc(num) {
    return num + " %"
}

function muda_grafico(e) {
    $("button").text($(e.target).text());
    $("#grafico_"+variavel).hide();
    variavel = $(e.target).attr("id");
    if ($("#grafico_"+variavel).length > 0) {
        $("#grafico_"+variavel).show();
    } else {
        desenha_grafico()
    }
}

