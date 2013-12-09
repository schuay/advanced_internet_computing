<?php

class Bootstrap extends Zend_Application_Bootstrap_Bootstrap {

  const SERVICE_URI = "http://127.0.0.1:5000";

  /**
   *
   * @var \Zend_View
   */
  protected $_view;


    /**
   * Check where user comes from and set locale.
   * @return \Zend_Locale
   */
  protected function _initLocale() {
    //$session = new Zend_Session_Namespace('config');
    try {
      $locale = new Zend_Locale('browser');
    } catch (Zend_Locale_Exception $e) {
      $locale = new Zend_Locale('de_DE');
    }
    Zend_Registry::set('Zend_Locale', $locale);
    return $locale;
  }

  /**
   * Setup Zend_Cache, used for Images, Translation, Locale
   * @return \Zend_Cache
   */
  protected function _initCache() {
    Zend_Locale::setDefault(Zend_Registry::get('Zend_Locale'));
    $frontendOptions = array('lifetime' => 43200, 'automatic_serialization' => true);
    $backendOptions = array('cache_dir' => APPLICATION_PATH . '/../data/cache');
    $cache = Zend_Cache::factory('Core', 'File', $frontendOptions, $backendOptions);
    Zend_Registry::set('Zend_Cache', $cache);
    Zend_Locale::setCache($cache);
    Zend_Db_Table_Abstract::setDefaultMetadataCache('Zend_Cache');
    /**
     * If in development/testing Environment -> clear Cache
     */
    if ((APPLICATION_ENV == 'development' || APPLICATION_ENV == 'testing') && time() % 10 == 0) {
      $cache->clean();
    }
    return $cache;
  }

  /**
   * Set up Zend_View
   * @return \Zend_View
   */
  protected function _initView() {
    $this->_view = new Zend_View($this->getOptions());
    $this->_view->headTitle()->setSeparator(' :: ')->prepend('AIC Twitter Sentiment Analysis');
    $this->_view->headMeta()->appendName('viewport', 'width=device-width,initial-scale=1.0');
    $this->_view->headMeta()->appendHttpEquiv('X-UA-Compatible', 'IE=edge');
    $this->_view->headLink()->headLink(array(
                'rel' => 'shortcut icon favicon',
                'href' => '/ico/favicon.png',
                'PREPEND'
            ))->appendStylesheet('/css/bootstrap.css')
            ->appendStylesheet('/css/navbar-fixed-top.css')
            ->appendStylesheet('//code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css')
            ->appendStylesheet('/css/style.css');

    $this->_view->headScript()->appendFile('//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js', 'text/javascript', array('conditional' => 'lt IE 9'))
            ->appendFile('//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js', 'text/javascript', array('conditional' => 'lt IE 9'))
            ->appendFile('/js/bootstrap.min.js');

    $this->_view->doctype(Zend_View_Helper_Doctype::HTML5);
    $viewRenderer = Zend_Controller_Action_HelperBroker::getStaticHelper('ViewRenderer');
    $viewRenderer->setView($this->_view);
    Zend_Registry::set('Zend_View', $this->_view);

    $this->_view->placeholder('bodyClass')->setSeparator(' ');

    return $this->_view;
  }

  public function _initRestClient(){
    $jc = new Zend_Rest_Client(Bootstrap::SERVICE_URI);
    Zend_Registry::set("REST", $jc);

  }

    /**
   * Register View Helper, and ZendX_JQuery
   */
  protected function _initViewHelpers() {
    //$this->_view->setHelperPath('BA/View/Helper');
    ZendX_JQuery::enableView($this->_view);
  }


}
