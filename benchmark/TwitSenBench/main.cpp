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
#include <pthread.h>
#include "ClassifierConfiguration.h"
#include <unistd.h>


volatile int running_threads = 0;
pthread_mutex_t running_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t cout_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t csv_mutex = PTHREAD_MUTEX_INITIALIZER;

std::string generateSentimenFile(std::string sentimentFile, int cutOff, string benchmarkNr){

    std::string outputFile("sentiments/" + benchmarkNr + "-" + to_string(cutOff) + "-" + sentimentFile);
    std::cout << "Parts for "<< outputFile << std::endl;
    std::string command("/opt/local/bin/gshuf -o " + outputFile + " -n $( expr $( sed -n '$=' " + sentimentFile +" ) / 4 \\* " + to_string(cutOff) + " ) " + sentimentFile);
    //cout << command << endl;
    system(command.c_str());
    return outputFile;
}

int main(int argc, const char * argv[])
{
    std::time_t benchmarkNr = std::time(0);
    chdir("/Users/spookee/Dropbox/Master - TUWien/AIC/Übung/Repository/src/");

    std::array<std::string, 4> transformers = {"id","url","user","mchar"};
    std::array<std::string, 4> featureSelectors = {"aes","ae","a","as"};
    std::array<std::string, 2> classifiers = {"bayes","svm"};
    std::array<int, 4> cutOffs = {1, 2, 3, 4};
    std::string negativeSentiments = "sentiment.neg";
    std::string positiveSentiments = "sentiment.pos";
    std::array<string, 4> negativeFiles;
    std::array<string, 4> positiveFiles;

    int i = 0;
    for(auto& cutOff : cutOffs){
        negativeFiles[i] = generateSentimenFile(negativeSentiments, cutOff, to_string(benchmarkNr));
        positiveFiles[i] = generateSentimenFile(positiveSentiments, cutOff, to_string(benchmarkNr));
        i++;
    }

    std::array<ClassifierConfiguration*, transformers.size()*featureSelectors.size()*classifiers.size()*cutOffs.size()> baseConfigurations;
    int bc = 0;
    for(auto& transformer: transformers){
        for(auto& featureSelector : featureSelectors){
            for(auto& classifier : classifiers){
                for(auto& cutOff : cutOffs){
                    //std::cout << "python classifier -f " << featureSelector << " -r " << transformer << " -t " << classifier << " -c " << cutOff << "\n";
                    ClassifierConfiguration *cc = new ClassifierConfiguration(transformer, featureSelector, classifier, cutOff, to_string(benchmarkNr));
                    cc->positivesFile = positiveFiles[cutOff];
                    cc->negativesFile = negativeFiles[cutOff];
                    baseConfigurations[bc++] = cc;
                }
            }
        }
    }

    std::cout << "Pickles to create: " << baseConfigurations.size()  << "\n";
//    return 0;

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
