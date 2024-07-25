#include <iostream>
using namespace std;
int Ackr( int m , int n ) {
    if ( m==0 ) {
        //cout << n + 1;
        return n + 1;
    }
    else if ( m > 0 and n == 0  ) {
        cout << "= Ackr( " << m << "," << n << " )"<< endl;
        return Ackr(m - 1, 1);
    }
    else if ( m>0 and n>0 ) {
        cout << "= Ackr( " << m -1  << ", Ackr(" << m << "," << n - 1 << ") )" << endl;
        return Ackr(m-1, Ackr(m,n-1));
    }
    return 0 ;
}
int main(){
    cout << "Ackr(2,3)" << endl;
    int a = Ackr(2,3);
    cout << "= " << a << endl;
}
