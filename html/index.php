<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
       "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
<title>HeatpumpMonitor</title>
<style type="text/css">
  body {
    color: black; background-color: white;
    font-size: 100.01%;
    font-family: Helvetica,Arial,sans-serif;
    margin: 0; padding: 1em 0;
    text-align: center;  /* Zentrierung im Internet Explorer */
  }

  div#Seite {
    text-align: left;    /* Seiteninhalt wieder links ausrichten */
    margin: 0 auto;      /* standardkonforme horizontale Zentrierung */
    margin-top: 50px;
    width: 90%;
    padding: 0.5em;
    border: 2px ridge silver;
  }

  ul#Navigation {
    font-size: 0.91em;
    float: left; width: 18em;
    margin: 0; padding: 0;
    border: 1px dashed silver;
  }
  ul#Navigation li {
    list-style: none;
    margin: 0; padding: 0.5em;
  }
  ul#Navigation a {
    display: block;
    padding: 0.2em;
    font-weight: bold;
  }
  ul#Navigation a:link {
    color: black; background-color: #eee;
  }
  ul#Navigation a:visited {
    color: #666; background-color: #eee;
  }
  ul#Navigation a:hover {
    color: black; background-color: white;
  }
  ul#Navigation a:active {
    color: white; background-color: gray;
  }

  div#Inhalt {
    margin-left: 18em;
    padding: 0 1em;
    border: 1px dashed silver;
  }
  div#Inhalt h1 {
    font-size: 1.5em;
    margin: 0 0 1em;
  }
  div#Inhalt h2 {
    font-size: 1.2em;
    margin: 0 0 1em;
  }
  div#Inhalt p {
    font-size:1em;
    margin: 1em 0;
  }
</style>
</head>
<body>

<div align="right" style="margin-right: 30px;">
    <img src="images/heatpumpMonitor_logo_400x45.png" width="400" height="45" align="right" border="0">
</div>

<div id="Seite">
<ul id="Navigation">
<?php
    $files = array(enduser_temperatures, humidity, fans, internaltemps);
    $sizes = array(small, big);
    $times = array("3hours", "halfday", "day", "week", "month", "year");

    foreach ($sizes as $size) {
        echo $size;
        foreach ($times as $time) {
            echo "<li><a href=\"index.php?time=$time&size=$size\">$time</a></li>\n";
       }
    }
?>

</ul>    
  
<div id="Inhalt">
<?php
    import_request_variables("gP", "rvar_");
        if ($rvar_size == "big") {
            $width=897;
            $height=479;
        }
        else {
            $width=497;
            $height=193;
            $size = "small";
        }

    foreach ($files as $i) {
        $img = "graphs/".$i."_".$rvar_time."_".$rvar_size.".png";
        if (file_exists($img)) {
            echo "<img src=\"$img\" width=\"".$width."\" height=\"".$height."\" align=\"middle\" border=\"0\">\n" ;
       echo "<br><br>";
        }
}
?>
</div>
</div>

</body>
</html>
