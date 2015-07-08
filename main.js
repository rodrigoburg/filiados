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
    data = dimple.filterData(data,"ano",anos);
    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(margin_left, margin_top, width-margin_left*4, height-margin_top*3);
    myChart.addMeasureAxis("y", variavel);
    var y = myChart.addTimeAxis("x", "ano","%Y","%Y");
    y.title = ""
    series = myChart.addSeries("partido", dimple.plot.line);
    series.lineWeight = 7;
    series.interpolation = "cardinal";
    series.getTooltipText = function (e) {
        if (variavel == "var_perc") {
            cy = formata_perc(e.cy);
        } else {
            cy = formata_numero(e.cy);
        }
        cx = new Date(e.cx);
        cx = cx.getFullYear();
        return [];
    };

    for (var cor in cores) {
        myChart.assignColor(cor,acha_cor(cor),acha_cor(cor));
    }
    myChart.draw(2000);
    adiciona_eventos()
}

function inicializa() {
    $.getJSON( "estoque_partido_ano.json", function( dados ) {
        data = dados
        variavel = "estoque"
        desenha_grafico()
    })
}

function adiciona_eventos() {
    $("path").each(function (i,d) {
        if ($(d).attr("class").indexOf("dimple-line") > -1) {
            //primeiro colore todos de ccinza
            acinzenta(d)
            $(d).bind("mouseover", d, destaca)
            $(d).bind("mousemove", d, move)
            $(d).bind("mouseout", d, acinzenta)
        }
    })
    $("circle").each(function (i,d) {
        if ($(d).attr("class").indexOf("dimple-marker") > -1) {
            var partido = $(d).attr("id").split("_")[0]
            $(d).bind("mouseover","#"+partido,destaca)
            $(d).bind("mouseout","#"+partido,acinzenta)
        }
    })

    //agora da lista que muda os graficos
    var lista = ["estoque","var_perc","var_abs"]
    for (var d in lista) {
        $("#"+lista[d]).click(function (e) { muda_grafico(e)})
    }
}

function move(event) {
    $(".tooltip").css({
        left: event.clientX - 15,
        top: event.clientY - 20,
    });
}

function destaca(event) {
    target = $(event.target);
    var elemento = event.data;
    $(elemento).css(
        {"stroke": acha_cor($(elemento).attr("id")),
            "opacity": 0.9
        })
    //agora aparece a tooltip
    $(".tooltip").css({});
    $(".tooltip").css({
        opacity: 1,
        left: event.clientX - 15,
        top: event.clientY - 20,
        "border-color": acha_cor($(elemento).attr("id"))
    });
    $("#topo").css({background: acha_cor($(elemento).attr("id"))})

    if (target.is("circle")) {
        $("#resto").show()
    } else {
        $("#resto").hide()
    }
    var topo = "<b>"+$(elemento).attr("id")+"</b>"
    var resto = "<b><p>Ano:</b> "+cx+"</p>" +
        "<b><p>Filiados:</b> "+cy+"</p>"
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
    d3.select("svg").remove();
    variavel = $(e.target).attr("id")
    desenha_grafico()

}

