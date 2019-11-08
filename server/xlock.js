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

}

// let t = new access('counties');
// t.get();

let t = new rock('counties');
t.flip();

let f = new spedo();
f.spool('#flow-gauge');
f.updateReadings(Math.random() * 100);

let f2 = new spedo();
f2.spool('#flow-gauge2');
f2.updateReadings(Math.random() * 100);
