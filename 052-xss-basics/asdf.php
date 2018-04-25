<?php
  session_start();
  header("X-XSS-Protection: 1");
?>

<html>
  <head>
    <meta charset='utf-8' />
  </head>

  <body>
    <p><?php echo $_GET['x']; ?></p>
    <input id=asdf value="<?php echo $_GET['y']; ?>" />

    <script>
      var x = '<?php echo $_GET['z']; ?>';
    </script>

    <style>
      body { background-color: <?php echo $_GET['z']; ?>; }
    </style>




    <p id="asdf">x</p>
    <img src="captcha.png" />

    <!--<script>
      let x = location.hash;
      let p = document.getElementById("asdf");
      p.innerHTML = decodeURIComponent(x);

    </script>-->
  </body>
</html>
