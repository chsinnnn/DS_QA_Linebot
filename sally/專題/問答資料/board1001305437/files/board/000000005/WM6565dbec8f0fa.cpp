//撰寫程式碼指出影響插入排序insertion sort是否穩定stable的關鍵指令。
#include <iostream>

using namespace std;

int main() {
	int n;
	// input
	cin >> n;
	int *arr = new int[ n ];
	for ( int i = 0 ; i < n ; i++ ) {
		cin >> arr[ i ];
	}

	// insertion sort
	// n is the length of arr
	for ( int i = 1 ; i < n ; i++ ) {
		int key = arr[ i ];
		int j = i - 1;
		while ( j >= 0 && arr[ j ] > key ) {
			/*
			關鍵在while的條件，用 arr[ j ] > key 來判斷是否要將 arr[ j ] 往後移
			在遇到相同的數字時，會結束迴圈，把自己放在已經被排序過的數字（相同且位置在自己前面的數字）的後面
			這樣就不會改變相同數字的相對位置
			*/
			arr[ j + 1 ] = arr[ j ];
			j--;
		}
		arr[ j + 1 ] = key;
	}

	// output
	for ( int i = 0 ; i < n ; i++ ) {
		cout << arr[ i ] << " ";
	}
	cout << endl;

	return 0;
}