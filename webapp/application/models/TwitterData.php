<?php

class App_Model_TwitterData
{
  private $fh;

  public function __construct() {
    $this->fh = fopen(APPLICATION_PATH."/models/tweets.json", "rb");
    if(!$this->fh){
      throw new Exception("Tweet Data could not be opened!");
    }
  }

  public function getLine(){
    return json_decode(fgets($this->fh));
  }


  public function __destruct() {
    fclose($this->fh);
  }

}

