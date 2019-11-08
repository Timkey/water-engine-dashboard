var spedoScroll = function()
{
  this.stack = "";
  this.tr = "";
  this.th = "";
}

spedoScroll.prototype.add = function(name='', dock='')
{
  let mod = "";
  mod += "<span>"
  mod += "<div class='card card-default'>";
  mod += "<div class='card-body'>";
  mod += "<div id='"+dock+"'></div>";
  mod += "</div>";
  mod += "<div class='card-footer'>"+name+"</div>";
  mod += "</div>";
  mod += "</span>";

  //mod = "<div id='"+dock+"'>"+name+"</div>";
  this.th += "<th>"+name+"</th>";
  this.td += "<td><div id='"+dock+"'></div></td>";

  this.stack += mod;
}

spedoScroll.prototype.render = function(dock="gauges")
{
  let r = "";
  r += "<table>";
  r += "<tr>"+this.th+"</tr>";
  r += "<tr>"+this.td+"</tr>";
  r += "</table>";

  let markup = "<marquee behavior='alternate' scrolldelay='200'>"+r+"</marquee>";
  $("#"+dock).html(markup);
}
