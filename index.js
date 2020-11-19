const path = require('/Users/askar/Documents/Bots/CryptoBot/index.py')
const {spawn} = require('child_process')


function runScript(){
  return spawn('python', [
    "-u",
    path.join(__dirname, 'script.py'),
    "--foo", "some value for foo",
  ]);
}

const subprocess = runScript()

// print output of script
subprocess.stdout.on('data', (data) => {
  console.log(`data:${data}`);
});
subprocess.stderr.on('data', (data) => {
  console.log(`error:${data}`);
});
subprocess.on('close', () => {
  console.log("Closed");
});


















// <script src="/js/jquery-1.2.6.min.js"></script>
// <script src="/js/jquery-ui-personalized-1.5.2.packed.js"></script>
// <script src="/js/sprinkle.js"></script>
// // <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
//
//
// // <script src="http://code.jquery.com/jquery-1.10.2.js"></script>
// // <script src="http://code.jquery.com/ui/1.11.2/jquery-ui.js"></script>
// // <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
//
// $.ajax({
//   type: "POST",
//   url: "~/tracker_cg.py",
//   data: { param: text}
// }).done(function( o ) {
//    // do something
// });
