let retriveJWT = function () {
  return localStorage.getItem('token')
}
let parseJwt = function () {
  token = retriveJWT()
  var base64Url = token.split('.')[1];
  var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  var jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);

  }).join(''));

  return JSON.parse(jsonPayload);
};

let getUserId = function () {
  token = parseJwt()
  return token['user_id']
}

let validToken = function () {
  parsedToken = parseJwt()
  console.log(Date.now() >= parsedToken['exp'] * 1000);
  if (Date.now() >= parsedToken['exp'] * 1000)
    return false;
}


export { getUserId, validToken };



