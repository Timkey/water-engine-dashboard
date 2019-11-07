var rock = function(path='')
{
  this.path = path;
  this.access = new access(path);
}

rock.prototype.flip = async function()
{
  await this.access.get();
  let d = await this.access.data;
  for (let c=0; c < d.length; c++)
  {
    let url = 'countyboxplot/'+d[c];
    let p = new access(url);
    await p.get();
    let nD = await p.data;
    await this.disp(nD);
    //console.log(nD);


    break;
  }
}

rock.prototype.disp = async function(mod={})
{
  let data = [];
  let layout = {
    title:mod.title,
    legend: {
      y: 1,
      x: 1.1,
      bgcolor: 'transparent',
    }
  };
  
  //mod.siteNames.length
  for (let f=0; f < 10; f++)
  {
    let siteName = mod.siteNames[f];
    let trace = {
      y : mod.sites[siteName]['data'],
      type: 'box',
      name : mod.sites[siteName]['name']
    };

    data.push(trace);
  }

  Plotly.newPlot('myDiv', data, layout); //, {showSendToCloud: true}
}
