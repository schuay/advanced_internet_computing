//
//  main.cpp
//  TwitSenBench
//
//  Created by sPooKee on 17.01.14.
//  Copyright (c) 2014 Christian Proske. All rights reserved.
//

#include <iostream>
#include <string>
#include <array>
#include <vector>
#include <pthread.h>
#include "ClassifierConfiguration.h"
#include <unistd.h>


volatile int running_threads = 0;
pthread_mutex_t running_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t cout_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t csv_mutex = PTHREAD_MUTEX_INITIALIZER;

// Configuration:
std::string negativeSentiments = "sentiment.neg";
std::string positiveSentiments = "sentiment.pos";
std::string shufPath = "/opt/local/bin/gshuf";

std::string generateSentimenFile(std::string sentimentFile, int cutOff, string benchmarkNr){

    std::string outputFile("sentiments/" + benchmarkNr + "-" + to_string(cutOff) + "-" + sentimentFile);
    std::cout << "Parts for "<< outputFile << std::endl;
    std::string command(shufPath + " -o " + outputFile + " -n $( expr $( sed -n '$=' " + sentimentFile + " ) / 4 \\* " + to_string(cutOff) + " ) " + sentimentFile);
    //cout << command << endl;
    system(command.c_str());
    return outputFile;
}

std::vector<std::string> getTransformCombinations(std::array<std::string, 4> transformers, int iteration) {
    std::vector<std::string> list;
    std::vector<bool> v(transformers.size());
    std::fill(v.begin() + iteration, v.end(), true);

    do {
        std::string tmp = "";
        for (int i = 0; i < transformers.size(); ++i) {
            if (!v[i]) {
                if(tmp != "") {
                    tmp = tmp + "+";
                }
                tmp = tmp + transformers[i];
            }
        }
        list.push_back(tmp);
    } while (std::next_permutation(v.begin(), v.end()));

    if(iteration < transformers.size()) {
        std::vector<std::string> nlist;
        nlist = getTransformCombinations(transformers, iteration+1);
        for(std::string s : nlist) {
            list.push_back(s);
        }
    }

    return list;
}

bool fileExists(string filename){
    ifstream ifile(filename.c_str());
    return (bool)ifile;
}

bool checkRequirements(){
    bool error = false;
    if(!fileExists("classifier/") || !fileExists("sentiments/") || !fileExists("outfiles/")){
        cout << "Error: Please make sure you have these directories: sentiments/, classifier/ and outfiles/." << endl;
        error = true;
    }
    if(!fileExists(positiveSentiments)) {
        cout << "Error: Positive Sentiment File not found!" << endl;
        error = true;
    }
    if(!fileExists(negativeSentiments)) {
        cout << "Error: Negative Sentiment File not found!" << endl;
        error = true;
    }
    if(!fileExists(shufPath)) {
        cout << "Error: 'shuf'-Path not found!" << endl;
        error = true;
    }
    return !error;
}

int main(int argc, const char * argv[])
{

#ifdef DEBUG
    cout << "DEBUG!!! DEBUG !!! DEBUG !!!" << endl;
    cout << "WORKING TREE: " << DEBUG_CHDIR << endl;
    if(!fileExists(DEBUG_CHDIR)){
        cout << "Error: Working Tree not found!!" << endl;
        exit(0);
    }
    chdir(DEBUG_CHDIR);
#endif

    if(argc == 2 && string(argv[1]) == string("-h")){
        cout << "Usage: " << argv[0] << " ["<< positiveSentiments <<"] [" << negativeSentiments << "] [" << shufPath << "]" << endl;
        cout << "       1. Argument: Path to positive Sentiments File" << endl;
        cout << "       2. Argument: Path to negative Sentiments File" << endl;
        cout << "       3. Argument: Path to (g)shuf binary" << endl;
        exit(0);
    }

    if(argc >= 2){
        positiveSentiments = string(argv[1]);
    }
    if(argc >= 3){
        negativeSentiments = string(argv[2]);
    }
    if(argc >= 4){
        shufPath = string(argv[3]);
    }

    if (!checkRequirements()){
        cout << "Usage: " << argv[0] << " ["<< positiveSentiments <<"] [" << negativeSentiments << "] [" << shufPath << "]" << endl;
        exit(0);
    }

    std::time_t benchmarkNr = std::time(0);

//    std::array<std::string, 4> transformers = {"id","url","user","mchar"};
//    std::vector<std::string> transf = getTransformCombinations(transformers, 1);
    std::array<std::string, 4> t = {"id","url","user","mchar"};
    std::vector<std::string> transformers = getTransformCombinations(t, 1);
    std::array<std::string, 4> featureSelectors = {"aes","ae","a","as"};
    std::array<std::string, 2> classifiers = {"bayes","svm"};
    std::array<int, 3> cutOffs = {2, 3, 4};
    std::array<string, 3> negativeFiles;
    std::array<string, 3> positiveFiles;

    int i = 0;
    for(auto& cutOff : cutOffs){
        negativeFiles[i] = generateSentimenFile(negativeSentiments, cutOff, to_string(benchmarkNr));
        positiveFiles[i] = generateSentimenFile(positiveSentiments, cutOff, to_string(benchmarkNr));
        i++;
    }

    //std::array<ClassifierConfiguration*, transformers.size()*featureSelectors.size()*classifiers.size()*cutOffs.size()> baseConfigurations;
    std::vector<ClassifierConfiguration*> baseConfigurations;
    //int bc = 0;

    for(auto& transformer : transformers) {
        for(auto& featureSelector : featureSelectors){
            for(auto& classifier : classifiers){
                for(auto& cutOff : cutOffs){
                    //std::cout << "python classifier -f " << featureSelector << " -r " << transformer << " -t " << classifier << " -c " << cutOff << "\n";

                    ClassifierConfiguration *cc = new ClassifierConfiguration(transformer, featureSelector, classifier, 0+cutOff, to_string(benchmarkNr));
                    cc->positivesFile = positiveFiles[cutOff-2]; // -2 weil der cutoff mit 2 beginnt
                    cc->negativesFile = negativeFiles[cutOff-2];
                    //baseConfigurations[bc++] = cc;
                    baseConfigurations.push_back(cc);
                }
            }
        }
    }

    std::cout << "Pickles to create: " << baseConfigurations.size()  << "\n";

    for(auto bc : baseConfigurations){
        while (running_threads > 4) {
            sleep(1);
        }
        bc->start();
    }

    //std::cout << "Pickles to create: " << baseConfigurations.size()  << "\n";

    while(running_threads > 0){
        sleep(1);
    }

    return 0;
}

