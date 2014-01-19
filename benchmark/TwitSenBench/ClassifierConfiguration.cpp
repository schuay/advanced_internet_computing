//
//  ClassifierConfiguration.cpp
//  TwitSenBench
//
//  Created by sPooKee on 17.01.14.
//  Copyright (c) 2014 Christian Proske. All rights reserved.
//

#include "ClassifierConfiguration.h"
#include <regex>
#include <sstream>

ClassifierConfiguration::ClassifierConfiguration(string transformer, string featureSelector, string classifier, int cutOff, string bNr)
{
    _transformer = transformer;
    _featureSelector = featureSelector;
    _classifier = classifier;
    _cutOff = cutOff;
    benchmarkNr = bNr;

    outputFilename = "outfiles/" + getPickleName() + ".out";

}

string ClassifierConfiguration::getPickleName() {
    string tmp(benchmarkNr+"-classifier-"+_classifier + "-" + _transformer + "-" + _featureSelector + "-" + to_string(_cutOff) + ".pickle");
    return tmp;
}

string ClassifierConfiguration::getCommand(){
    string cutOffPercentage = "0.5";
    if(_cutOff == 3) {
        cutOffPercentage = "0.66";
    }
    else if(_cutOff == 4) {
        cutOffPercentage = "0.75";
    }

    replaceAll(_transformer, "+", " -r ");
    return "classifier.py -p "+positivesFile+" -n "+negativesFile+" -s classifier/" + getPickleName() + " -f " + _featureSelector +  " -r " + _transformer + " -t " + _classifier + " -c " + cutOffPercentage;
}

void ClassifierConfiguration::start(){
    extern volatile int running_threads;
    extern pthread_mutex_t running_mutex;

    pthread_mutex_lock(&running_mutex);
    running_threads++;
    pthread_mutex_unlock(&running_mutex);

    logln("Thread started.");

    _threadNum = running_threads;

    pthread_create(&_thread, NULL, ClassifierConfiguration::staticEntryPoint, this);
}

void *ClassifierConfiguration::staticEntryPoint(void *c){
    ((ClassifierConfiguration *)c)->entryPoint();
    return NULL;
}

void ClassifierConfiguration::entryPoint(){

    _begin = time(0);
    if(!fileExists(outputFilename)){
        buildClassifier();
    }else{
        logln("Output already exists: " + outputFilename);
    }
    _end = time(0);

    ClassifierOutput *clOut = handleOutput();

    writeToCSV(clOut);


    return terminateThread();
}


void  ClassifierConfiguration::buildClassifier(){
    FILE *in;
    char buff[512];
    //string command = "python " + getCommand();
    string command = "./" + getCommand();

    fstream output;
    logln("Running: " + command);
    logln("Write output to: " + outputFilename);
    if(!(in = popen(command.c_str(), "r"))){
        cout << "I'm out!" << endl;
        return;
    }

    output.open(outputFilename.c_str(), fstream::out);

    while(fgets(buff, sizeof(buff), in)!=NULL){
        output << buff;
        log(buff);
    }
    pclose(in);

    output.close();

    remove(string("classifier/"+getPickleName()).c_str());

}

ClassifierOutput* ClassifierConfiguration::handleOutput(){
    logln("Handle output:" + outputFilename);

    ClassifierOutput *co = new ClassifierOutput();

    std::regex rxAccuracy("accuracy: (.*)");
    std::regex rxPosPrecision("pos precision: (.*)");
    std::regex rxPosRecall("pos recall: (.*)");
    std::regex rxNegPrecision("neg precision: (.*)");
    std::regex rxNegRecall("neg recall: (.*)");

    ifstream input(outputFilename);
    std::string line;
    while(std::getline(input, line)){
        std::cmatch res;
        if(regex_search(line.c_str(), res, rxAccuracy)){
            co->accuracy = stringToDouble(res[1]);
        }
        if(regex_search(line.c_str(), res, rxNegPrecision)){
            co->negPrecision = stringToDouble(res[1]);
        }
        if(regex_search(line.c_str(), res, rxNegRecall)){
            co->negRecall = stringToDouble(res[1]);
        }
        if(regex_search(line.c_str(), res, rxPosPrecision)){
            co->posPrecision = stringToDouble(res[1]);
        }
        if(regex_search(line.c_str(), res, rxPosRecall)){
            co->posRecall = stringToDouble(res[1]);
        }
    }

    input.close();

    return co;
}

void ClassifierConfiguration::writeToCSV(ClassifierOutput *clOutput){
    extern pthread_mutex_t csv_mutex;

    string csvFilename("classifier-benchmark.csv");
    pthread_mutex_lock(&csv_mutex);
    bool printHeader = !fileExists(csvFilename);
    ofstream output(csvFilename, fstream::app);
    if(printHeader) {
        output << "Nr.;Classifier;Transformers;Feature Selector;Trainingset/Testset Ratio;Accuracy;Precision (Positive);Recall (Positive);Precision (Negative);Recall (Negative);Duration (sec)" << endl;
    }
    string cutOffRatio = "1:1";
    if(_cutOff == 3) {
        cutOffRatio = "2:1";
    }
    else if(_cutOff == 4) {
        cutOffRatio = "3:1";
    }
    output << benchmarkNr << ";" << getClassifier() << ";" << getTransformer() << ";" << getFeatureSelector() << ";" << cutOffRatio << ";" << clOutput->accuracy << ";" << clOutput->posPrecision << ";" << clOutput->posRecall << ";" << clOutput->negPrecision << ";" << clOutput->negRecall << ";" << (_end - _begin) << endl;
    output.close();
    pthread_mutex_unlock(&csv_mutex);
}


// HELPER:

double ClassifierConfiguration::stringToDouble(const string& value){
    std::istringstream i(value);
    double x;
    if(!(i >> x))
        return .0;
    return x;
}

bool ClassifierConfiguration::fileExists(string filename){
    ifstream ifile(filename.c_str());
    return (bool)ifile;
}

void ClassifierConfiguration::logln(string string){
    time_t now;

    time(&now);
    char buf[sizeof "2000-01-01T00:00:00Z"];
    strftime(buf, sizeof buf, "%FT%TZ", gmtime(&now));
    log(std::string(buf) + "#T" + to_string(_threadNum) + ": " + string + "\n");
}

void ClassifierConfiguration::log(string string){
    extern pthread_mutex_t cout_mutex;
    pthread_mutex_lock(&cout_mutex);
    cout << string;
    pthread_mutex_unlock(&cout_mutex);
}

void ClassifierConfiguration::terminateThread(){
    extern pthread_mutex_t running_mutex;
    extern volatile int running_threads;
    pthread_mutex_lock(&running_mutex);
    running_threads--;
    pthread_mutex_unlock(&running_mutex);
    logln("Thread ended! Still running: " + to_string(running_threads));
}

// http://stackoverflow.com/questions/3418231/replace-part-of-a-string-with-another-string
void ClassifierConfiguration::replaceAll(string& str, const string& from, const string& to) {
    if(from.empty())
        return;
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length();
    }
}