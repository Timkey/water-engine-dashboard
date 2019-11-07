var y0=[],y1=[]
for ( i = 0; i < 50; i ++)
{
    y0[i] = Math.random();
    y1[i] = Math.random();
}

var trace1 = {
  y: y0,
  type: 'box'
};

var trace2 = {
  y: y1,
  type: 'box'
};

var data = [trace1, trace2];

Plotly.newPlot('myDiv', data, {}, {showSendToCloud: true});

$('#shit').html('Testing in progress ...........');

var access = function(path='', data={})
{
  this.path = path;
  this.data = JSON.stringify(data);

}

access.prototype.get = async function()
{
  let path = this.path;

  if (path.length > 0)
  {
      this.url = "/" + path;
  }
  var j = await $.ajax({
      type: "GET",
      url: this.url,
      contentType: 'application/json'
  });

  this.data = j['data'];
  console.log(this.data);
}

access.prototype.post = async function()
{
  let path = this.path;
  let data = this.path;

  if (path.length > 0)
  {
      this.url = "/" + path;
  }

  var j = await $.ajax({
      type: "POST",
      url: this.url,
      data: this.data,
      contentType: 'application/json'
  });

  this.data = j['data'];
  console.log('working');

};

// let t = new access('counties');
// t.get();

let t = new rock('counties');
t.flip();
