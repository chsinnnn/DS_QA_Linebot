# include <stdio.h>
# include <iostream>

using namespace std;


int Acker( int m, int n );

int main() {
  int m = 0;
  int n = 0;

  cout << "Input number(m) :" ;
  cin >> m ;
  cout << "Input number(n) :" ;
  cin >> n ;

  cout << "Acker( " << m << ", " << n << " ) " << endl;
  cout << Acker( m, n ) << endl;

}  // main()

int Acker( int m, int n ) {

  if ( m == 0 ) {
    cout << "= Acker( " << m << ", " << n << " )" << endl;
    return n + 1;
  } // if
  else if ( n == 0 ) {
    cout << "= Acker( " << m - 1 << ", 1 )" << endl;
    return Acker( m -1, 1 );
  } // if
  else {
    cout << "= Acker( " << m - 1 << ", Acker( " << m << ", " << n - 1 << " ) )" << endl;
    return Acker( m - 1, Acker( m, n - 1 ) );
  } //else

}  // Acker()
