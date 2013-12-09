<?php

class App_Form_Request extends Zend_Form
{

    public function init()
    {
        $e = array();

        $e['start'] = new ZendX_JQuery_Form_Element_DatePicker('start');
        $e['start']->setLabel("Start-Datum:")
                ->setRequired();

        $e['end'] = new ZendX_JQuery_Form_Element_DatePicker('end');
        $e['end']->setLabel("End-Datum:")
                ->setRequired();

        $e['keywords'] = $this->createElement('Text', 'keywords')
                ->setLabel('Keywords:')
                ->setRequired()
                ->setDescription('Mehrere Keywords mit Komma trennen.');

        $e['submit'] = $this->createElement('Submit', 'Senden')
                ->setAttrib('class', 'btn btn-primary');

        $this->addElements($e);

    }


}

