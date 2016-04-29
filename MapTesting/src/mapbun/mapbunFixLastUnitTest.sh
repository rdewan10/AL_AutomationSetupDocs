#!/bin/bash
### Unit Test for mapbunFixLast.py


### Series of test vectors to verify output
### NOTE: Test code can be improved by using test arrays in a loop

testId=1
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,2M" 7 1 100`
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,2" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

# HMW code review test-
# see if while i < len(lastItem)-1 : should be while i < len(lastItem) :
testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" 7 1 100`
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

# HMW code review test-
# confirm run.sh values were not tested
testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20MB94FG72CV48SL33                ^@^@^@^@^@^@^@^G0c01cfb4ff78865ebb94c7223fd12c44È^G^@^BV^U<9a>ñarclightcm" 3 1 5`
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED - num of parameters should be 7 and not 3"
fi

# Here are the correct values to PASS the test
testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20MB94FG72CV48SL33                ^@^@^@^@^@^@^@^G0c01cfb4ff78865ebb94c7223fd12c44È^G^@^BV^U<9a>ñarclightcm" 7 1 10000`
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi


testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,99997MB94FG72CV48SL33                ^@^@^@^@^@^@^@^G0c01cfb4ff78865ebb94c7223fd12c44È^G^@^BV^U<9a>ñarclightcm" 7 1 10000 `
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,9999" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

#Test the minimum
testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "18,11,133" 3 14 200`
echo $myresult
if [[ $myresult =~ "18,11,133" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "18,11,133" 3 2 132`
echo $myresult
if [[ $myresult =~ "18,11,13" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "18,11,2MB94FG72CV48SL33                ^@^@^@^@^@^@^@^G0c01cfb4ff78865ebb94c7223fd12c44È^G^@^BV^U<9a>ñarclightcm" 3 1 5 `
echo $myresult
if [[ $myresult =~ "18,11,2" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "18,11,38MB94FG72CV48SL33                ^@^@^@^@^@^@^@^G0c01cfb4ff78865ebb94c7223fd12c44È^G^@^BV^U<9a>ñarclightcm" 3 1 5 `
echo $myresult
if [[ $myresult =~ "18,11,3" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "18,11,38" 3 1 5 `
echo $myresult
if [[ $myresult =~ "18,11,3" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" 7 1 100 `
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20999999	" 7 1 100 `
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,20" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,2099999" 7 1 10000 `
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,2099" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,1" 7 1 100 `
echo $myresult
if [[ $myresult =~ "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,1" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

testId=`expr $testId + 1`
myresult=`./mapbunFixLast.py "18,11,389999" 3 1 1000 `
echo $myresult
if [[ $myresult =~ "18,11,389" ]]; then
    echo "Test $testId PASSED"
else
    echo "Test $testId FAILED"
fi

