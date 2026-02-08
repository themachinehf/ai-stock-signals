/**
 * Simple Test Handler
 */

module.exports = async (req, res) => {
  const url = (req.url || '/').split('?')[0];
  
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  if (url === '/' || url === '') {
    return res.status(200).send(JSON.stringify({
      status: 'ok',
      message: 'THE MACHINE is watching',
      time: Date.now()
    }));
  }
  
  return res.status(200).send(JSON.stringify({ status: 'ok', path: url }));
};
