//
//  ClassifierConfiguration.h
//  TwitSenBench
//
//  Created by sPooKee on 17.01.14.
//  Copyright (c) 2014 Christian Proske. All rights reserved.
//

#ifndef __TwitSenBench__ClassifierConfiguration__
#define __TwitSenBench__ClassifierConfiguration__

#include <iostream>
#include <fstream>
#include <string>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include "ClassifierOutput.h"

using namespace std;

class ClassifierConfiguration {

private:
    //time_t _begin;
    //time_t _end;
    string _transformer;
    string _classifier;
    string _featureSelector;
    int _cutOff;
    int _nGram;

    void buildClassifier();
    ClassifierOutput* handleOutput();
    void writeToCSV(ClassifierOutput *);

    // Multithreading
    pthread_t _thread;
    static void *staticEntryPoint(void *c);
    void entryPoint();
    void terminateThread();
    int _threadNum;

    // Helper
    bool fileExists(string);
    void log(string);
    void logln(string);
    double stringToDouble(const string&);
    int stringToInt(const string&);
    void replaceAll(string&, const string&, const string&);
    string replaceAll2(string, const string&, const string&);

public:
    ClassifierConfiguration(){};
    ClassifierConfiguration(string,string,string,int,int,string);
    string getPickleName();
    string getCommand();
    void start();

    string outputFilename;
    string positivesFile;
    string negativesFile;
    string benchmarkNr;

    string getTransformer(){ return _transformer; }
    string getFeatureSelector(){ return _featureSelector; }
    string getClassifier(){ return _classifier; }

};

#endif /* defined(__TwitSenBench__ClassifierConfiguration__) */
