Webcam.set({
  width: 320,
  height: 240,
  image_format: 'jpeg',
  jpeg_quality: 90
});
Webcam.attach('#my_camera');

Webcam.snap(function (data_uri) {
  // display results in page
  document.getElementById('results').innerHTML =
    '<img src="' + data_uri + '"/>';
});