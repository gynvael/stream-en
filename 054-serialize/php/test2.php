<?php

class Test {
  public $func = "var_dump";
  public $arg = "text";

  function callme() {
    echo "callme\n";
  }

  function __construct() {
    echo "__construct\n";
  }

  function __destruct() {
    $this->callme();
    echo "1: "; ($this->func)($this->arg);
    echo "2: "; call_user_func($this->func, "[Destruct] {$this->arg}" );
  }

  function __wakeup() {
    var_dump($this);
  }
}

# O:4:"Test":2:{s:4:"func";s:8:"var_dump";s:3:"arg";s:4:"text";}


$v = new Test();
echo serialize($v);

$k = unserialize('O:4:"Test":3:{s:4:"func";s:6:"system";s:3:"arg";s:6:"x;date";s:6:"callme";s:8:"yyyyyyyy";}');

var_dump($k);

echo "\n";
