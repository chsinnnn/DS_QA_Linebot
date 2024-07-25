
/*
10942208 陳洺安 資四乙
使用老師上課所教iostream subclass => ofstream & ifstream
順便練習動態配置陣列 
*/ 
#include <iostream>
#include <string>
#include <fstream>
using namespace std;

int main()
{
	// 使用iostream subclass 
	cout << "輸入檔案名稱 ex: 123.txt " << endl ;
	string fileName = "" ;
	cin >> fileName  ;
    int arraySize = 50 ;
    int *intArray = new int[arraySize];
    // 寫檔 ========================================================== 
    ofstream outFile(fileName.c_str()); 
    //.c_str() 在C++， std::ofstream接受const char，而不是string
    int i = 0 ;
    do{
    	outFile << i << endl ; // 跟cout使用方法類似 
    	i++; 
	}while( i <= 10 ) ;
	outFile.close();
	// 寫檔 結束======================================================
    // 讀檔 ========================================================== 
    ifstream inFile(fileName.c_str()); 
    int number ; 
    i = 0 ;
    while( inFile >> number ) { // 文件結束返回false 
    	*(intArray+i) = number ;
    	i++;
	} // while
	inFile.close();
	// 讀檔 結束======================================================
	// 印出陣列內容 
	for( int j = 0 ; j < i ; j++ ) {
		cout << intArray[j] << endl ; // intArray[0] = *(intArray+0)  ;
	} // for
	delete[] intArray; // 釋放動態分配內存 
    return 0;
}

