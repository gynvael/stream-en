<?php
header("X-XSS-Protection: 1");
?>

<html>
<body>
  <script src="main.js"></script>
  <script>var x=5;</script>
  <script>x=8;</script>
  <script>
    // if(x == 5) { send_password_to_attacker(); }

  console.log(x);</script>
</body>
</html>
