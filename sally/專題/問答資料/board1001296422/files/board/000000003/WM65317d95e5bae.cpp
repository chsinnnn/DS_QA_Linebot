
/*
10942208 ���y�w ��|�A
�ϥΦѮv�W�ҩұ�iostream subclass => ofstream & ifstream
���K�m�߰ʺA�t�m�}�C 
*/ 
#include <iostream>
#include <string>
#include <fstream>
using namespace std;

int main()
{
	// �ϥ�iostream subclass 
	cout << "��J�ɮצW�� ex: 123.txt " << endl ;
	string fileName = "" ;
	cin >> fileName  ;
    int arraySize = 50 ;
    int *intArray = new int[arraySize];
    // �g�� ========================================================== 
    ofstream outFile(fileName.c_str()); 
    //.c_str() �bC++�A std::ofstream����const char�A�Ӥ��Ostring
    int i = 0 ;
    do{
    	outFile << i << endl ; // ��cout�ϥΤ�k���� 
    	i++; 
	}while( i <= 10 ) ;
	outFile.close();
	// �g�� ����======================================================
    // Ū�� ========================================================== 
    ifstream inFile(fileName.c_str()); 
    int number ; 
    i = 0 ;
    while( inFile >> number ) { // ��󵲧���^false 
    	*(intArray+i) = number ;
    	i++;
	} // while
	inFile.close();
	// Ū�� ����======================================================
	// �L�X�}�C���e 
	for( int j = 0 ; j < i ; j++ ) {
		cout << intArray[j] << endl ; // intArray[0] = *(intArray+0)  ;
	} // for
	delete[] intArray; // ����ʺA���t���s 
    return 0;
}

