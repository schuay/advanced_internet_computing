<?php

class IndexController extends Zend_Controller_Action {

  public function init() {
    /* Initialize action controller here */
  }

  public function indexAction() {

    $rest = Zend_Registry::get("REST");

    $tasks = array();
    $res = $rest->restGet('/api/tasks');
    if ($res->isSuccessful()) {
      $tasks = json_decode($res->getBody());
    }

    $this->view->tasks = $tasks->tasks;


    /*


      $twitterData = new App_Model_TwitterData();

      $sentiment = new AIC_Sentiment();

      $i = 0;
      $examples = array();
      while ($i++ < 100) {
      $examples[] = $twitterData->getLine()->text;
      }

      foreach ($examples as $key => $example) {

      echo '<div class="example">';
      echo "<h2>Example $key</h2>";
      echo "<blockquote>$example</blockquote>";

      echo "Scores: <br />";
      $scores = $sentiment->score($example);

      echo "<ul>";
      foreach ($scores as $class => $score) {
      $string = "$class -- <i>$score</i>";
      if ($class == $sentiment->categorise($example)) {
      $string = "<b class=\"$class\">$string</b>";
      }
      echo "<ol>$string</ol>";
      }
      echo "</ul>";
      echo '</div>';
      }

      echo "<hr/>";
     */
  }

  public function detailAction() {
    if (!is_null($task_id = $this->getRequest()->getParam("task"))) {
      $rest = Zend_Registry::get("REST");
      $res = $rest->restGet('/api/tasks/' . $task_id);
      if ($res->isSuccessful()) {
        $task = json_decode($res->getBody());
        $this->view->task = $task->tasks;
        return $this;
      }
    }
    return $this->forward('index');
  }

  public function newAction() {
    $frm = new App_Form_Request();

    if ($this->getRequest()->isPost() && $frm->isValid($_POST)) {

      $task = new stdClass;
      $task->start = date("Ymd", strtotime($frm->getValue('start')));
      $task->end = date("Ymd", strtotime($frm->getValue('end')));
      $task->keywords = explode(',', $frm->getValue('keywords'));
      if ($task->end > $task->start) {
        $client = Zend_Rest_Client::getHttpClient();

        $res = $client->setRawData(json_encode($task))
                ->setEncType('application/json')
                ->setUri(Bootstrap::SERVICE_URI . "/api/tasks")
                ->request('POST');


        if ($res->isSuccessful()) {
          $task = json_decode($res->getBody());
          return $this->_redirect('/');
        } else {
          Zend_Debug::dump($res->getBody());
        }
      } else {
        Zend_Debug::dump("Start-Datum leigt nicht vor End-Datum.");
      }
    }

    $this->view->form = $frm;
  }

  public function deleteAction() {
    if (!is_null($task_id = $this->getRequest()->getParam("id"))) {


      $client = Zend_Rest_Client::getHttpClient();

      $res = $client->setRawData(json_encode($task))
              ->setEncType('application/json')
              ->setUri(Bootstrap::SERVICE_URI . "/api/tasks/" . $task_id)
              ->request('DELETE');
      if ($res->isSuccessful()) {
        $task = json_decode($res->getBody());
      }
    }
    return $this->_redirect("/");
  }

}
