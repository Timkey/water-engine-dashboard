var rock = function(path='')
{
  this.path = path;
  this.access = new access(path);
}

rock.prototype.flip = async function()
{
  await this.access.get();
  let d = await this.access.data;

  this.next(0, d);
}

rock.prototype.next = async function(ad=0, d = [])
{
  let len = d.length;

  if (len > 0 && ad < len)
  {
    $('#Head').html('Flow Rate : '+d[ad]);
    let url = 'countyboxplot/'+d[ad];
    let p = new access(url);
    await p.get();
    let nD = await p.data;
    await this.boxplot(nD);
    //console.log(nD);

    let inter = this;
    setTimeout(function(){
      console.log('At '+nD.title);
      if (ad + 1 < len){
        ad++;
        inter.next(ad, d);
      }
      else
      {
          inter.next(0, d);
      }
    }, 30000*((nD.siteNames.length % 10) + 1));
  }
}

rock.prototype.boxplot = async function(mod={})
{
  let layout = {
    title:mod.title+' Yield Daily',
    legend: {
      y: 1,
      x: 1.1,
      bgcolor: 'transparent',
    }
  };

  this.redo(mod, 10, 0);

}

rock.prototype.redo = async function(mod = {}, count=10, pointer=0)
{
  let layout = {
    title:mod.title+' Yield Daily',
    legend: {
      y: 1,
      x: 1.1,
      bgcolor: 'transparent',
    }
  };

  console.log(count+' <= counter');
  let maxYield = 100;
  let data = [];
  let dataSpedo = [];
  let spedo = new spedoScroll();
  let groups = [];
  let groupData = [];

  while (pointer < count)
  {
    let siteName = mod.siteNames[pointer];
    let trace = {
      y : mod.sites[siteName]['data'],
      type: 'box',
      name : mod.sites[siteName]['name']
    };

    let trace2 = {
      yieldDaily : mod.sites[siteName]['data'][0],
      addr : 'gauge-'+pointer,
      name : mod.sites[siteName]['name'],
      maxYield: mod.maxYield,
      households: mod.sites[siteName]['households']
    };

    if (maxYield < Math.max.apply(null, trace.y))
    {
      maxYield = Math.max.apply(null, trace.y);
    }

    spedo.add(trace2.name, trace2.addr);

    data.push(trace);
    dataSpedo.push(trace2);

    groups.push(trace2.name);
    groupData.push(trace2.households);

    //increment data
    pointer++;
  }

  spedo.render();
  this.spedo(dataSpedo, maxYield);
  this.barplot(groups, groupData);
  this.pieplot(mod.st.status, mod.st.data);

  Plotly.newPlot('myDiv', data, layout);
  let inter = this;

  setTimeout(function () {
    if( count+10 < mod.siteNames.length )
    {
      count += 10;
      inter.redo(mod, count, pointer);
    }
    else if(pointer < mod.siteNames.length) {
      count = mod.siteNames.length;
      inter.redo(mod, count, pointer);
    }

  }, 30000);
 }

rock.prototype.barplot = async function(groups, groupData)
{
  var dataBar = [{
    type: 'bar',
    x: groupData,
    y: groups,
    orientation: 'h'
  }];

  var layout = {
    height: 300,
    width: 320,
    margin: {"t": 0, "b": 15, "l": 100, "r": 0},
    showlegend: false
  }

  Plotly.newPlot('population', dataBar, layout);
}

rock.prototype.pieplot = async function(groups, groupData)
{
  var data = [{
    type: "pie",
    values: groupData,
    labels: groups,
    //textinfo: "label+percent",
    textposition: "outside",
    automargin: true,
    hole: .6
  }]

  var layout = {
    height: 300,
    width: 370,
    margin: {"t": 0, "b": 0, "l": 0, "r": 0},
    showlegend: true
    }

  Plotly.newPlot('expertStatus', data, layout)
}

rock.prototype.spedo = async function(d=[], maxYield=500)
{
  console.log('internal spedo reached maxYield: '+maxYield);
  console.log(d);

  for (let x = 0; x < d.length; x++)
  {
    let trace = d[x];
    let f = new spedo(size=200, clipWidth=200, clipHeight=122, ringWidth=30, maxValue=maxYield);
    f.spool('#'+trace.addr);
    f.updateReadings(trace.yieldDaily);
  }
}
