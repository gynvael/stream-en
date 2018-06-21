<?php
$SECRET = "secret781623876123lanmsdkln";

header("X-XSS-Protection: 0");

echo("<pre>");
var_dump($_GET['error']);
echo("</pre><br />");

if (isset($_GET['error']) && is_string($_GET['error']) &&
    isset($_GET['hmac']) && is_string($_GET['hmac'])) {
  $usr_hash = $_GET['hmac'];
  $act_hash = hash('md5', $SECRET . $_GET['error']);

  if ($usr_hash !== $act_hash) {
    die("a horrible death");
  }

  echo("<b>error:</b> " . $_GET['error']);
}

echo("<br />normal website");

// Location: ?error=Incorrectly field form&hmac=9812736123

?>
<!--
1 bit variable
p q p+q p^q
0 0  0   0
0 1  1   1
1 0  1   1
1 1  0   0
-->

