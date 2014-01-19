//
//  ClassifierOutput.h
//  TwitSenBench
//
//  Created by sPooKee on 18.01.14.
//  Copyright (c) 2014 Christian Proske. All rights reserved.
//

#ifndef __TwitSenBench__ClassifierOutput__
#define __TwitSenBench__ClassifierOutput__

#include <iostream>

class ClassifierOutput{

private:

public:
    ClassifierOutput(){};

    double accuracy = .0;
    double posPrecision = .0;
    double negPrecision = .0;
    double posRecall = .0;
    double negRecall = .0;
    int startTime = 0;
    int stopTime = 0;

    int getDuration();

};

#endif /* defined(__TwitSenBench__ClassifierOutput__) */
